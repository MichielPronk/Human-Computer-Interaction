import tweepy
import tkinter as tk
import tkinter.ttk as ttk
import threading
import time


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

        credentials = self.getCredentials()
        auth = tweepy.OAuthHandler(credentials[0], credentials[1])
        auth.set_access_token(credentials[2], credentials[3])

        self.api = tweepy.API(auth)

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

    def getCredentials(self):
        credentials = []
        with open("credentials", "r") as infile:
            lines = infile.readlines()
        credentials.append(lines[0].split(":")[1])
        credentials.append(lines[1].split(":")[1])
        credentials.append(lines[2].split(":")[1])
        credentials.append(lines[3].split(":")[1])
        return credentials


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
    root.mainloop()


if __name__ == "__main__":
    main()
