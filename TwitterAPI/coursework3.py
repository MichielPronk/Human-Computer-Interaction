import tweepy
import tkinter as tk
import tkinter.ttk as ttk
import threading


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
        parent.destroy()


class TweetExtractor(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.is_paused = True

        credentials = self.getCredentials()
        auth = tweepy.OAuthHandler(credentials[0], credentials[1])
        auth.set_access_token(credentials[2], credentials[3])

        self.api = tweepy.API(auth)

        self.conversation_tree = ttk.Treeview(self)
        self.control_panel = tk.Frame(self)

        self.stream_button = tk.Button(self.control_panel, text='Start/Stop', command=self.start_stop)
        self.filter_bar = tk.Entry(self.control_panel)
        self.filter_bar.config(width=30)
        self.option_list = ['English', 'Spanish', 'Italian', 'French', 'Japanese', 'Russian', 'Tamil']
        options = tk.StringVar(self)
        options.set(self.option_list[0])
        self.language_menu = tk.OptionMenu(self.control_panel, options, *self.option_list)
        self.language_menu.config(width=8)
        self.lang_label = tk.Label(self.control_panel, text='Choose language')
        self.filter_list = ttk.Treeview(self.control_panel, columns=1)
        self.filter_list.heading("1", text="Filters")
        self.filter_list.column("1")
        self.filter_list['show'] = 'headings'

        # Initialize the grid
        self.grid(column=0, row=0, sticky='NESW')
        tk.Grid.rowconfigure(parent, 0, weight=1)
        tk.Grid.columnconfigure(parent, 0, weight=1)
        tk.Grid.rowconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 0, weight=1)
        for columns in range(5):
            tk.Grid.columnconfigure(self, columns, weight=1)

        self.conversation_tree.grid(column=0, row=0, columnspan=4, rowspan=1, sticky='NESW')
        self.control_panel.grid(column=4, row=0, columnspan=1, rowspan=1, sticky='NESW')

        tk.Grid.rowconfigure(self.control_panel, 0, weight=1)
        tk.Grid.columnconfigure(self.control_panel, 0, weight=1)
        for columns in range(30):
            tk.Grid.columnconfigure(self.control_panel, columns, weight=2)
        for rows in range(30):
            tk.Grid.rowconfigure(self.control_panel, rows, weight=2)
        self.filter_list.grid(column=1, row=0, columnspan=28, rowspan=6, sticky='NSEW')
        self.filter_bar.grid(column=2, row=6, columnspan=10, sticky='EW')
        self.language_menu.grid(column=1, row=9, sticky='EW')
        self.stream_button.grid(column=1, row=18, sticky='EW')
        self.lang_label.grid(column=1, row=8)

    def getCredentials(self):
        credentials = []
        with open("credentials", "r") as infile:
            lines = infile.readlines()
        credentials.append(lines[0].strip().split(":")[1])
        credentials.append(lines[1].strip().split(":")[1])
        credentials.append(lines[2].strip().split(":")[1])
        credentials.append(lines[3].strip().split(":")[1])
        return credentials

    def startStream(self):
        threading.Thread(target=self.twitterStream).start()

    def twitterStream(self):
        myStreamListener = MyStreamListener()
        myStream = tweepy.Stream(auth=self.api.auth, listener=myStreamListener)
        while True:
            if myStream.running and self.is_paused:
                myStream.disconnect()
            elif not myStream.running and not self.is_paused:
                print(self.filter_bar.get())
                myStream.filter(is_async=True, track=['python'])

    def start_stop(self):
        if self.is_paused:
            self.is_paused = False
        else:
            self.is_paused = True

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


class MyStreamListener(tweepy.StreamListener):

    def on_status(self, tweet):
        print(tweet.text)


def main():
    root = tk.Tk()
    root.state('zoomed')
    frame = MainProgram(root)
    frame.tweet_extractor.startStream()
    root.mainloop()


if __name__ == "__main__":
    main()
