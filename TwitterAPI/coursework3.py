import tweepy
import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk
import threading
import queue
from geopy.geocoders import Nominatim


class MainProgram(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        # Initialize notebook
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

        # Add Exit option to File
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


class TweetExtractor(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        # Initial state of the stream
        self.is_paused = True

        # Get the credentials
        credentials = self.getCredentials()

        # Login to twitter
        auth = tweepy.OAuthHandler(credentials[0], credentials[1])
        auth.set_access_token(credentials[2], credentials[3])
        self.api = tweepy.API(auth)

        # Initialize stream listener
        self.myStreamListener = MyStreamListener()
        self.myStream = tweepy.Stream(auth=self.api.auth, listener=self.myStreamListener)

        # Initialize conversation queue
        self.convo_queue = queue.Queue()


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
        self.option_list = ['English', 'Spanish', 'Italian', 'French', 'Japanese', 'Russian', 'Tamil', 'Dutch']
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
        self.conversation_tree.grid(column=0, row=0, columnspan=4, rowspan=1, sticky='NESW')

        # Insert control panel into main frame
        self.control_panel.grid(column=4, row=0, columnspan=1, rowspan=1, sticky='NESW')

        # Initialize weights for control panel frame
        tk.Grid.rowconfigure(self.control_panel, 0, weight=1)
        tk.Grid.columnconfigure(self.control_panel, 0, weight=1)
        for columns in range(7):
            tk.Grid.columnconfigure(self.control_panel, columns, weight=1)
        for rows in range(50):
            tk.Grid.rowconfigure(self.control_panel, rows, weight=1)

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
        credentials = []
        with open("credentials3", "r") as infile:
            lines = infile.readlines()
        credentials.append(lines[0].strip().split(":")[1])
        credentials.append(lines[1].strip().split(":")[1])
        credentials.append(lines[2].strip().split(":")[1])
        credentials.append(lines[3].strip().split(":")[1])
        return credentials

    def startStream(self):
        threading.Thread(target=self.twitterStream).start()

    def twitterStream(self):
        while True:
            if self.myStream.running and self.is_paused:
                self.myStream.disconnect()
            elif not self.myStream.running and not self.is_paused:
                language = self.getLanguage()
                location = self.getLocation()
                if location is None:
                    self.myStream.filter(is_async=True, track=self.filter_list_internal, languages=[language])
                else:
                    print('locatie aan')
                    self.myStream.filter(is_async=True, track=self.filter_list_internal, languages=[language],
                                         locations=location)

    def start_stop(self):
        if self.is_paused:
            if not self.filter_list_internal:
                tk.messagebox.showerror("Error", "Please specify at least one filter in the filter list")
            else:
                self.is_paused = False
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
            self.conversation_tree.delete(*self.conversation_tree.get_children())
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
                pass

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
                 'Tamil': 'ta', 'Dutch': 'nl'}
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
            tweet = self.myStreamListener.getfromQueue()
            if tweet is not None:
                conversation = [(tweet.text, tweet.id)]
                while tweet.in_reply_to_status_id is not None:
                    try:
                        tweet = self.api.get_status(tweet.in_reply_to_status_id)
                        conversation.insert(0, (tweet.text, tweet.id))
                    except tweepy.error.TweepError:
                        break
                if 2 < len(conversation) < 11:

                    self.convo_queue.put(conversation)

    def insertConversations(self):
        try:
            conversation = self.convo_queue.get(block=False)
            if conversation is not None:
                self.conversation_tree.insert('', tk.END, iid=conversation[0][1], text=conversation[0][0].replace('\n', ' '), open=True)
                parent_id = conversation[0][1]
                for i in range(1, len(conversation)):
                    self.conversation_tree.insert(parent_id, tk.END, iid=conversation[i][1], text=conversation[i][0].replace('\n', ' '))
        except queue.Empty:
            pass
        self.after(100, self.insertConversations)


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

        self.conversation_tree = ttk.Treeview(self)
        self.control_panel = tk.Frame(self)

        # Initialize the grid
        self.grid(column=0, row=0, sticky='NESW')
        tk.Grid.rowconfigure(parent, 0, weight=1)
        tk.Grid.columnconfigure(parent, 0, weight=1)
        tk.Grid.rowconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 0, weight=1)
        for columns in range(3):
            tk.Grid.columnconfigure(self, columns, weight=1)

        self.conversation_tree.grid(column=0, row=0, columnspan=2, rowspan=1, sticky='NESW')
        self.control_panel.grid(column=2, row=0, columnspan=1, rowspan=1, sticky='NESW')

    def openFile(self):
        print("Open file")


def main():
    root = tk.Tk()
    root.state('zoomed')
    frame = MainProgram(root)
    frame.tweet_extractor.startStream()
    #frame.tweet_extractor.startLocationChecker()
    frame.tweet_extractor.startProcessingTweets()
    frame.tweet_extractor.insertConversations()
    root.mainloop()


if __name__ == "__main__":
    main()
