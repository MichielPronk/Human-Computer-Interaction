from tkinter.filedialog import askopenfilename

import tweepy
import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk
import threading
import queue
from geopy.geocoders import Nominatim
import time
import pickle
from nltk.sentiment.vader import SentimentIntensityAnalyzer


class MainProgram(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        # Initialize notebook
        parent.title('Twitter bot')
        self.notebook = ttk.Notebook(self)

        self.tweet_extractor = TweetExtractor(self.notebook)
        self.sentiment_analysis = SentimentAnalysis(self.notebook)

        # Add tabs to the notebook
        self.notebook.add(self.tweet_extractor, text="Tweet Extractor")
        self.notebook.add(self.sentiment_analysis, text="Sentiment Analysis")

        # Initialize menubar
        self.menubar = tk.Menu(parent)
        parent.config(menu=self.menubar)

        # Makes sure each menu does not appear as its own window
        self.option_add('*tearOff', False)

        # Create File menu
        self.menu_file = tk.Menu(self.menubar)
        self.menubar.add_cascade(menu=self.menu_file, label='File')

        # Add Exit option to File
        self.menu_file.add_command(label="Exit", command=lambda: self.quitProgram(parent))

        # Add Credentials option to File
        self.menu_file.add_command(label='Change Credentials', command=self.tweet_extractor.changeCredentials)

        # Add Open option to File
        self.menu_file.add_command(label="Open", command=lambda: self.sentiment_analysis.openFile())

        # Add event handler to notebook to handle the menubar options
        self.notebook.bind("<<NotebookTabChanged>>", self.switchMenu)

        # Initialize the grid
        self.grid(column=0, row=0, sticky='NESW')
        tk.Grid.rowconfigure(parent, 0, weight=1)
        tk.Grid.columnconfigure(parent, 0, weight=1)
        tk.Grid.rowconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 0, weight=1)
        self.notebook.grid(column=0, row=0, columnspan=1, rowspan=1, sticky='NESW')

    def switchMenu(self, event):
        active_tab_id = self.notebook.select()
        active_tab = self.notebook.index(active_tab_id)
        if active_tab == 0:
            self.menu_file.entryconfigure('Open', state=tk.DISABLED)
        else:
            self.menu_file.entryconfigure('Open', state=tk.NORMAL)

    def quitProgram(self, parent):
        """Stops the program"""
        self.tweet_extractor.myStream.disconnect()
        parent.destroy()


class popUpWindow(object):
    def __init__(self, master):
        top = self.top = tk.Toplevel(master)
        self.top.title('Change Credentials')
        # Create API key input
        self.api_key_label = tk.Label(top, text="Enter API key (25 characters)")
        self.api_key = tk.Entry(top, width=70)
        self.api_key_label.pack()
        self.api_key.pack()
        # Create API secret input
        self.api_secret_label = tk.Label(top, text="Enter API secret (50 characters)")
        self.api_secret = tk.Entry(top, width=70)
        self.api_secret_label.pack()
        self.api_secret.pack()
        # Create access token input
        self.access_token_label = tk.Label(top, text="Enter access token (50 character)")
        self.access_token = tk.Entry(top, width=70)
        self.access_token_label.pack()
        self.access_token.pack()
        # Create access secret input
        self.access_secret_label = tk.Label(top, text="Enter access secret (45 characters)")
        self.access_secret = tk.Entry(top, width=70)
        self.access_secret_label.pack()
        self.access_secret.pack()

        self.b = tk.Button(top, text='Submit', command=self.cleanup, width=30)
        self.c = tk.Button(top, text='Cancel', command=self.quitProgram, width=30)
        self.b.pack()
        self.c.pack()

    def cleanup(self):
        error_message = ''
        if self.api_key.get() == '' or self.api_secret.get() == '' or self.access_token.get() == '' or self.access_secret.get() == '':
            tk.messagebox.showerror('error', 'Not all fields are filled in!')
        if len(self.api_key.get()) != 25:
            error_message += 'API key is not 25 characters\n'
        if len(self.api_secret.get()) != 50:
            error_message += 'API secret is not 50 characters\n'
        if len(self.access_token.get()) != 50:
            error_message += 'Access token is not 50 characters\n'
        if len(self.access_secret.get()) != 45:
            error_message += 'Access secrect is not 45 characters\n'
        if error_message != '':
            tk.messagebox.showerror('error', error_message)
        else:
            with open('credentials', 'w') as infile:
                infile.write(self.api_key.get() + '\n' +
                             self.api_secret.get() + '\n' +
                             self.access_token.get() + '\n' +
                             self.access_secret.get())
            self.quitProgram()

    def quitProgram(self):
        self.top.destroy()

class TweetExtractor(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        # Initial state of the stream
        self.is_paused = True

        # Initialize Sentiment Analyzer
        self.sid = SentimentIntensityAnalyzer()

        # Initialize conversation queue
        self.convo_queue = queue.Queue()

        # Initialize conversation dictionary
        self.conversation_dict = {}

        # Initialize variables
        self.language = ""

        # Create stream frame
        self.conversation_tree = ttk.Treeview(self)

        # Create control panel frame
        self.control_panel = tk.Frame(self)

        # Create stop and start button
        self.stream_button_text = tk.StringVar()
        self.stream_button_text.set("Start stream")
        self.stream_button = tk.Button(self.control_panel, textvariable=self.stream_button_text,
                                       command=self.start_stop)
        self.stream_button.config(font='Helvetica 20')

        # Create drop down menu
        self.option_list = ['English', 'Spanish', 'Italian', 'French', 'Japanese', 'Russian', 'Tamil']
        self.option = tk.StringVar(self)
        self.option.set(self.option_list[0])
        self.language_menu = tk.OptionMenu(self.control_panel, self.option, *self.option_list)
        self.language_menu.config(width=8, font="Helvetica 20")

        # Create label for drop down menu
        self.lang_label = tk.Label(self.control_panel, text='Choose language', font="Helvetica 20")

        # Create filter list
        self.filter_list_internal = []
        self.filter_list = ttk.Treeview(self.control_panel, columns=1)
        self.filter_list.heading("1", text="Filters")
        self.filter_list.column("1", anchor=tk.CENTER)
        self.filter_list['show'] = 'headings'

        # Create entry field for filter list
        self.filter_bar = tk.Entry(self.control_panel, font="Helvetica 20", justify="center")
        self.filter_bar.bind('<Return>', self.check_filter_input)

        # Create label for entry field for filter list
        self.filter_label = tk.Label(self.control_panel, text="Enter filter terms", font="Helvetica 20")

        # Create entry field for location
        self.location_input = tk.Entry(self.control_panel, font="Helvetica 20", justify="center")
        self.location_input.bind('<Return>', self.check_location_input)

        # Create label for location
        self.loc_label = tk.Label(self.control_panel, text="Specify location", font="Helvetica 20")

        # Create label for current location
        self.location = tk.StringVar()
        self.location.set("Enter a location")
        self.loc_cur_label = tk.Label(self.control_panel, textvariable=self.location, font="Helvetica 10")
        self.loc_cur_label.config(width=60, fg="black")

        # Create scale for location radius
        self.radius = tk.IntVar()
        self.radius.set(int(50))
        self.radius_bar = tk.Scale(self.control_panel, from_=1, to=100, resolution=1, orient=tk.HORIZONTAL,
                                   variable=self.radius)
        self.radius_bar.config(width=30, length=200)

        # Create label for location radius bar
        self.radius_label = tk.Label(self.control_panel, text="Specify radius (km)", font="Helvetica 20")

        # Create location queue
        self.location_queue = queue.Queue()

        # Create longitude and latitude variables
        self.longitude = float()
        self.latitude = float()

        # Create delete button
        self.delete_button = tk.Button(self.control_panel, text="Delete", font="Helvetica 20", command=self.delete)

        # Create informative label for stream button
        self.warning = tk.Label(self.control_panel, text="You cannot change the settings once the stream is running.",
                                font="Helvetica 16")

        # Initialize weights for the main frame
        self.grid(column=0, row=0, sticky='NESW')
        tk.Grid.rowconfigure(parent, 0, weight=1)
        tk.Grid.columnconfigure(parent, 0, weight=1)
        tk.Grid.rowconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 0, weight=1)
        for columns in range(5):
            tk.Grid.columnconfigure(self, columns, weight=1)

        # Insert stream frame into main frame
        self.conversation_tree.grid(column=0, row=0, columnspan=5, rowspan=1, sticky='NESW')

        # Insert control panel into main frame
        self.control_panel.grid(column=5, row=0, columnspan=1, rowspan=1, sticky='NESW')

        # Initialize weights for control panel frame
        tk.Grid.rowconfigure(self.control_panel, 0, weight=1)
        tk.Grid.columnconfigure(self.control_panel, 0, weight=1)
        for columns in range(7):
            tk.Grid.columnconfigure(self.control_panel, columns, weight=1)
        for rows in range(50):
            tk.Grid.rowconfigure(self.control_panel, rows, weight=1)

        # Initialize scrollbar
        self.scrollbar = tk.Scrollbar(self.conversation_tree, orient="vertical", command=self.conversation_tree.yview)
        self.conversation_tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

        # Insert control panel options
        self.filter_list.grid(column=1, row=0, columnspan=5, rowspan=26, sticky='NSEW')
        self.delete_button.grid(column=3, row=27)
        self.filter_label.grid(column=3, row=28)
        self.filter_bar.grid(column=3, row=29)
        self.loc_label.grid(column=3, row=33)
        self.location_input.grid(column=3, row=34)
        self.loc_cur_label.grid(column=3, row=35)
        self.radius_label.grid(column=3, row=36)
        self.radius_bar.grid(column=3, row=37)
        self.lang_label.grid(column=3, row=38)
        self.language_menu.grid(column=3, row=39)
        self.stream_button.grid(column=3, row=41, sticky='EW')
        self.warning.grid(column=3, row=43)


    def getCredentials(self):
        with open("credentials", "r") as infile:
            return infile.readlines()


    def changeCredentials(self):
        self.windows = popUpWindow(self.master)

    def loginTwitter(self):
        credentials = self.getCredentials()

        # Login to twitter
        auth = tweepy.OAuthHandler(credentials[0].rstrip(), credentials[1].rstrip())
        auth.set_access_token(credentials[2].rstrip(), credentials[3].rstrip())
        self.api = tweepy.API(auth)

        # Initialize stream listener
        self.myStreamListener = MyStreamListener()
        self.myStream = tweepy.Stream(auth=self.api.auth, listener=self.myStreamListener)


    def twitterStream(self):
        if self.myStream.running and self.is_paused:
            self.myStream.disconnect()
        elif not self.myStream.running and not self.is_paused:
            self.language = self.getLanguage()
            location = self.getLocation()
            if location is None:
                self.myStream.filter(is_async=True, track=self.filter_list_internal, languages=[self.language])
            else:
                self.myStream.filter(is_async=True, track=self.filter_list_internal, languages=[self.language],
                                     locations=location)

    def start_stop(self):
        if self.is_paused:
            if not self.filter_list_internal:
                tk.messagebox.showerror("Error", "Please specify at least one filter in the filter list")
            else:
                self.is_paused = False
                self.loginTwitter()
                self.twitterStream()
                self.delete_button.config(state=tk.DISABLED)
                self.filter_bar.config(state=tk.DISABLED)
                self.location_input.config(state=tk.DISABLED)
                self.radius_bar.config(state=tk.DISABLED)
                self.language_menu.config(state=tk.DISABLED)
                self.stream_button_text.set("Stop stream")
        else:
            self.is_paused = True
            self.convo_queue.queue.clear()
            self.myStreamListener.tweet_queue.queue.clear()
            self.twitterStream()
            self.saveDictionary()
            self.delete_button.config(state=tk.NORMAL)
            self.filter_bar.config(state=tk.NORMAL)
            self.filter_bar.delete(0, tk.END)
            self.location_input.config(state=tk.NORMAL)
            self.location_input.delete(0, tk.END)
            self.radius_bar.config(state=tk.NORMAL)
            self.language_menu.config(state=tk.NORMAL)

            self.filter_list_internal = []
            self.filter_list.delete(*self.filter_list.get_children())

            self.longitude = float()
            self.latitude = float()

            self.location.set("Enter a location")
            self.loc_cur_label.config(fg="black")

            self.stream_button_text.set("Start stream")
            self.after(100, self.conversation_tree.delete(*self.conversation_tree.get_children()))

    def check_filter_input(self, event):
        input = self.filter_bar.get()
        self.filter_bar.delete(0, tk.END)
        if input == "":
            tk.messagebox.showerror("Error", "Filter field is empty")
        elif input in self.filter_list_internal:
            tk.messagebox.showerror("Error", "Filter already exists")
        else:
            self.filter_list_internal.append(input)
            self.filter_list.insert("", tk.END, text=input, values=(input,))

    def check_location_input(self, event):
        input = self.location_input.get()
        self.location_input.delete(0, tk.END)
        if input == "":
            tk.messagebox.showerror("Error", "Location field is empty")
        elif input == self.location:
            tk.messagebox.showerror("Error", "Location is the same as the set location")
        else:
            self.location_queue.put(input)

    def startLocationChecker(self):
        threading.Thread(target=self.location_checker).start()

    def location_checker(self):
        geolocator = Nominatim(user_agent="JeMiBot")
        while True:
            try:
                item = self.location_queue.get(block=False)
                try:
                    location = geolocator.geocode(item)
                    self.longitude = location.longitude
                    self.latitude = location.latitude
                    self.location.set(location.address)
                    self.loc_cur_label.config(fg="green")
                except AttributeError:
                    self.location.set("Location was not found")
                    self.loc_cur_label.config(fg="red")
            except queue.Empty:
                time.sleep(0.5)

    def delete(self):
        row_id = self.filter_list.focus()
        node_name = self.filter_list.item(row_id)['text']
        try:
            self.filter_list.delete(row_id)
            self.filter_list_internal.remove(node_name)
        except tk.TclError:
            pass

    def getLanguage(self):
        selected = self.option.get()
        codes = {'English': 'en', 'Italian': 'it', 'French': 'fr', 'Spanish': 'es', 'Russian': 'ru', 'Japanese': 'jp',
                 'Tamil': 'ta'}
        return codes[selected]

    def getLocation(self):
        if self.longitude == 0 and self.latitude == 0:
            return None
        else:
            east_west = self.radius.get() * 1000 * 0.5 / 0.999984984 / 111111
            north_south = self.radius.get() * 1000 * 0.866025 / 111111
            return [self.longitude - north_south - east_west, self.latitude - north_south - east_west,
                    self.longitude + north_south + east_west, self.latitude + north_south + east_west]

    def startProcessingTweets(self):
        threading.Thread(target=self.processTweets).start()

    def processTweets(self):
        while True:
            try:
                tweet = self.myStreamListener.getfromQueue()
                participants = set()
                if tweet is not None:
                    try:
                        conversation = [(tweet.extended_tweet["full_text"], tweet.id)]
                        participants.add(tweet.user.screen_name)
                    except AttributeError:
                        conversation = [(tweet.text, tweet.id)]
                        participants.add(tweet.user.screen_name)
                    while tweet.in_reply_to_status_id is not None:
                        try:
                            tweet = self.api.get_status(tweet.in_reply_to_status_id)
                            try:
                                conversation.insert(0, (tweet.extended_tweet["full_text"], tweet.id))
                                participants.add(tweet.user.screen_name)
                            except AttributeError:
                                conversation.insert(0, (tweet.text, tweet.id))
                                participants.add(tweet.user.screen_name)
                        except tweepy.error.TweepError:
                            break
                    if 2 < len(conversation) < 11:
                        min_pos, min_neg = self.getSentimentScores(conversation)
                        self.conversation_dict[conversation[0][1]] = {'conversation': conversation, 'participants': len(set(participants)), 'turns': len(conversation), 'min_pos': min_pos, 'min_neg': min_neg}
                        self.convo_queue.put(conversation)
            except AttributeError:
                pass

    def getSentimentScores(self, conversation):
        neg = []
        pos = []
        for sentence in conversation:
            ss = self.sid.polarity_scores(sentence[0])
            neg.append(ss['neg'])
            pos.append(ss['pos'])
        return min(neg), min(pos)

    def insertConversations(self):
        try:
            conversation = self.convo_queue.get(block=False)
            try:
                self.conversation_tree.insert('', tk.END, iid=conversation[0][1],
                                              text=conversation[0][0].replace('\n', ' '), open=True)
                parent_id = conversation[0][1]
                for i in range(1, len(conversation)):
                    self.conversation_tree.insert(parent_id, tk.END, iid=conversation[i][1],
                                                  text=conversation[i][0].replace('\n', ' '))
            except tk.TclError:
                self.conversation_tree.insert(conversation[0][1], tk.END, iid=conversation[-1][1],
                                              text=conversation[-1][0].replace('\n', ' '))
        except queue.Empty:
            pass
        self.after(100, self.insertConversations)

    def saveDictionary(self):
        if self.location.get() == "Enter a location" or "Location was not found":
            file_name = "{0}_{1}".format(self.filter_list_internal, self.language)
        else:
            file_name = "{0}_{1}_{2}km_{3}".format(self.filter_list_internal, self.language, self.location.get(),
                                                   self.radius.get())
        with open(file_name, 'wb') as infile:
            pickle.dump(self.conversation_dict, infile)
        self.conversation_dict = {}


class MyStreamListener(tweepy.StreamListener):
    def __init__(self):
        tweepy.StreamListener.__init__(self)
        self.tweet_queue = queue.Queue()

    def getfromQueue(self):
        try:
            tweet = self.tweet_queue.get(block=False)
            return tweet
        except queue.Empty:
            pass

    def on_status(self, tweet):
        if tweet.in_reply_to_status_id is not None:
            self.tweet_queue.put(tweet)


class SentimentAnalysis(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        # Create class variables
        self.conversation_dict = {}

        # Create tree queue
        self.tree_queue = queue.Queue()

        # Create treeview for conversations
        self.conversation_tree = ttk.Treeview(self)
        self.conversation_tree.pack(side=tk.BOTTOM, expand=1, fill=tk.BOTH)

        # Create the control panel
        self.control_panel = tk.Frame(self)
        self.control_panel.pack(side=tk.TOP, fill=tk.BOTH)

        # Create label for minimum participants dropdown
        self.minimum_part_menu_label = tk.Label(self.control_panel, text="Minimum participants")

        # Create minimum participants dropdown
        self.minimum_part_list = ['2', '3', '4', '5', '6', '7', '8', '9', '10']
        self.minimum_part = tk.StringVar(self)
        self.minimum_part.set(self.minimum_part_list[0])
        self.minimum_part_menu = tk.OptionMenu(self.control_panel, self.minimum_part, *self.minimum_part_list)

        # Create label for maximum participants dropdown
        self.maximum_part_menu_label = tk.Label(self.control_panel, text="Maximum participants")

        # Create maximum participants dropdown
        self.maximum_part_list = ['2', '3', '4', '5', '6', '7', '8', '9', '10']
        self.maximum_part = tk.StringVar(self)
        self.maximum_part.set(self.maximum_part_list[8])
        self.maximum_part_menu = tk.OptionMenu(self.control_panel, self.maximum_part, *self.maximum_part_list)

        # Create label for minimum turns dropdown
        self.minimum_turn_menu_label = tk.Label(self.control_panel, text="Minimum turns")

        # Create minimum turns dropdown
        self.minimum_turn_list = ['2', '3', '4', '5', '6', '7', '8', '9', '10']
        self.minimum_turn = tk.StringVar(self)
        self.minimum_turn.set(self.minimum_turn_list[0])
        self.minimum_turn_menu = tk.OptionMenu(self.control_panel, self.minimum_turn, *self.minimum_turn_list)

        # Create label for maximum turns dropdown
        self.maximum_turn_menu_label = tk.Label(self.control_panel, text="Maximum turns")

        # Create maximum turns dropdown
        self.maximum_turn_list = ['2', '3', '4', '5', '6', '7', '8', '9', '10']
        self.maximum_turn = tk.StringVar(self)
        self.maximum_turn.set(self.maximum_turn_list[8])
        self.maximum_turn_menu = tk.OptionMenu(self.control_panel, self.maximum_turn, *self.maximum_turn_list)

        # Create label for minimum turns bar
        self.minimum_positive_sentiment_bar_label = tk.Label(self.control_panel, text="Minimum positive sentiment score")

        # Create scalebar for minimum positive sentiment
        self.minimum_positive_sentiment = tk.StringVar()
        self.minimum_positive_sentiment.set(float(0.10))
        self.minimum_positive_sentiment_bar = tk.Scale(self.control_panel, from_=0, to=1, resolution=0.01, orient=tk.HORIZONTAL,
                                                       variable=self.minimum_positive_sentiment)

        # Create label for maximum turns bar
        self.minimum_negative_sentiment_bar_label = tk.Label(self.control_panel, text="Minimum negative sentiment score")

        # Create scalebar for minimum negative sentiment
        self.minimum_negative_sentiment = tk.StringVar()
        self.minimum_negative_sentiment.set(float(0.10))
        self.minimum_negative_sentiment_bar = tk.Scale(self.control_panel, from_=0, to=1, resolution=0.01, orient=tk.HORIZONTAL,
                                                       variable=self.minimum_negative_sentiment)

        # Create submit button
        self.submit = tk.Button(self.control_panel, text="Use filters", command=self.applyFilters)

        # Initialize scrollbar
        self.scrollbar = tk.Scrollbar(self.conversation_tree, orient="vertical", command=self.conversation_tree.yview)
        self.conversation_tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

        # Initialize the grid
        tk.Grid.rowconfigure(self.control_panel, 0, weight=1)
        tk.Grid.columnconfigure(self.control_panel, 0, weight=1)
        for columns in range(12):
            tk.Grid.columnconfigure(self.control_panel, columns, weight=1)
        for rows in range(2):
            tk.Grid.rowconfigure(self.control_panel, rows, weight=1)
        self.minimum_part_menu_label.grid(column=0, row=0)
        self.minimum_part_menu.grid(column=0, row=1)

        self.maximum_part_menu_label.grid(column=1, row=0)
        self.maximum_part_menu.grid(column=1, row=1)

        self.minimum_turn_menu_label.grid(column=3, row=0)
        self.minimum_turn_menu.grid(column=3, row=1)

        self.maximum_turn_menu_label.grid(column=4, row=0)
        self.maximum_turn_menu.grid(column=4, row=1)

        self.minimum_positive_sentiment_bar_label.grid(column=6, row=0)
        self.minimum_positive_sentiment_bar.grid(column=6, row=1)

        self.minimum_negative_sentiment_bar_label.grid(column=7, row=0)
        self.minimum_negative_sentiment_bar.grid(column=7, row=1)

        self.submit.grid(column=9, row=0, rowspan=2)

    def insertConversations(self):
        try:
            conversation = self.tree_queue.get(block=False)
            self.conversation_tree.insert('', tk.END, iid=conversation[0][1],
                                          text=conversation[0][0].replace('\n', ' '), open=True)
            parent_id = conversation[0][1]
            for i in range(1, len(conversation)):
                self.conversation_tree.insert(parent_id, tk.END, iid=conversation[i][1],
                                              text=conversation[i][0].replace('\n', ' '))
        except queue.Empty:
            pass
        self.after(100, self.insertConversations)

    def applyFilters(self):
        if self.checkConditions():
            if self.conversation_dict != {}:
                self.conversation_tree.delete(*self.conversation_tree.get_children())
                for conversation_id in self.conversation_dict:
                    if (int(self.minimum_part.get()) <= self.conversation_dict[conversation_id]['participants'] <= int(self.maximum_part.get())) and (int(self.minimum_turn.get()) <= self.conversation_dict[conversation_id]['turns'] <= int(self.maximum_turn.get()) and float(self.conversation_dict[conversation_id]['min_pos']) >= float(self.minimum_positive_sentiment.get()) and float(self.conversation_dict[conversation_id]['min_neg']) >= float(self.minimum_negative_sentiment.get())):
                        self.tree_queue.put(self.conversation_dict[conversation_id]['conversation'])

    def checkConditions(self):
        error_message = ""
        if int(self.minimum_part.get()) > int(self.maximum_part.get()):
            error_message += "The minimum number of participants cannot be higher than the maximum number of participants\n"
        if int(self.minimum_turn.get()) > int(self.maximum_turn.get()):
            error_message += "The minimum number of turns cannot be higher than the maximum number of turns\n"
        if int(self.minimum_part.get()) > int(self.minimum_turn.get()):
            error_message += "The minimum amount of participants cannot be higher than the minimum number of turns\n"
        if error_message == "":
            return True
        else:
            tk.messagebox.showerror("Error", error_message)
            return False

    def openFile(self):
        mytextfilename = askopenfilename(
            filetypes=[("All Files", "*.*")]
        )
        if not mytextfilename:
            return
        self.conversation_tree.delete(*self.conversation_tree.get_children())
        self.conversation_dict = pickle.load(open(mytextfilename, 'rb'))
        for conversation_id in self.conversation_dict:
            self.conversation_tree.insert('', tk.END, iid=self.conversation_dict[conversation_id]['conversation'][0][1],
                                          text=self.conversation_dict[conversation_id]['conversation'][0][0].replace('\n', ' '),
                                          open=True)
            for i in range(1, len(self.conversation_dict[conversation_id]['conversation'])):
                self.conversation_tree.insert(conversation_id, tk.END, iid=self.conversation_dict[conversation_id]['conversation'][i][1],
                                              text=self.conversation_dict[conversation_id]['conversation'][i][0].replace('\n', ' '))


def main():
    root = tk.Tk()
    root.state('zoomed')
    frame = MainProgram(root)
    frame.tweet_extractor.startLocationChecker()
    frame.tweet_extractor.startProcessingTweets()
    frame.tweet_extractor.insertConversations()
    frame.sentiment_analysis.insertConversations()
    root.mainloop()


if __name__ == "__main__":
    main()