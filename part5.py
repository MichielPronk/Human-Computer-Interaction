import praw
import tkinter as tk
import tkinter.ttk as ttk
import threading
import queue
import time
from part1 import IncomingSubmissions
from part3 import ResponseCommentTreeDisplay

# Connects to reddit with bot account
reddit = praw.Reddit(
    client_id="kXHM-WcuSy2pDQ",
    client_secret="KsixoG3bUwXCnJw5K8PASkaxumX-EQ",
    user_agent="HCI:JeMiBot:1.0 (by u/JeMiBot)",
    username="JeMiBot",
    password="JesmerMichiel"
)


class IncomingSubmissionsAdvanced(tk.Frame):
    def __init__(self, parent):
        self.screen_width = parent.winfo_screenwidth()
        self.screen_height = parent.winfo_screenheight()
        tk.Frame.__init__(self, parent)

        # Makes sure each menu does not appear as its own window
        self.option_add('*tearOff', False)

        # Create id queue
        self.id_queue = queue.Queue()

        # Create menubar
        self.menubar = tk.Menu(parent)
        parent.config(menu=self.menubar)

        # Create File menu
        self.menu_file = tk.Menu(self.menubar)
        self.menubar.add_cascade(menu=self.menu_file, label='File')

        # Add Exit option to File
        self.menu_file.add_command(label="Exit", command=lambda: self.quitProgram(parent))

        # Initialize incoming submission frame
        self.incoming_submissions = IncomingSubmissions(self)
        self.incoming_submissions.tree.bind("<Double-1>", self.detectClick)

        # Initialize notebook
        self.notebook = ttk.Notebook(self)

        # Initialize response tree 1
        self.response1 = ResponseCommentTreeDisplay(self.notebook)
        self.response1.showComments()
        self.response1.startReceiving()
        self.response1.startProcessing()

        # Initialize response tree 2
        self.response2 = ResponseCommentTreeDisplay(self.notebook)
        self.response2.showComments()
        self.response2.startReceiving()
        self.response2.startProcessing()

        # Initialize response tree 3
        self.response3 = ResponseCommentTreeDisplay(self.notebook)
        self.response3.showComments()
        self.response3.startReceiving()
        self.response3.startProcessing()

        # Add response trees to the notebook
        self.notebook.add(self.response1, text="Submission 1")
        self.notebook.add(self.response2, text="Submission 2")
        self.notebook.add(self.response3, text="Submission 3")

        # Initialize the grid
        self.grid(column=0, row=0, sticky='NESW')
        tk.Grid.rowconfigure(parent, 0, weight=1)
        tk.Grid.columnconfigure(parent, 0, weight=1)
        tk.Grid.rowconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 0, weight=1)
        for rows in range(1):
            tk.Grid.rowconfigure(self, rows, weight=1)
        for columns in range(3):
            tk.Grid.columnconfigure(self, columns, weight=1)

        self.incoming_submissions.grid(column=0, row=0, columnspan=2, rowspan=1)
        self.notebook.grid(column=2, row=0, columnspan=1, rowspan=1, sticky='NESW')

    def detectClick(self, event):
        """Puts id of submission in queue when double-clicked"""
        submission_id = self.incoming_submissions.tree.selection()[0]
        self.id_queue.put(submission_id)

    def startDetecting(self):
        """Start selectSubmission thread"""
        threading.Thread(target=self.selectSubmission).start()

    def selectSubmission(self):
        """Puts comments tree of selected comment on active tab"""
        while True:
            try:
                submission_id = self.id_queue.get(block=False)
                submission = reddit.submission(id=submission_id)
                submission_url = submission.permalink
                active_tab_id = self.notebook.select()
                active_tab = self.notebook.index(active_tab_id)
                if active_tab == 0:
                    self.response1.url_queue.put("https://reddit.com" + submission_url)
                elif active_tab == 1:
                    self.response2.url_queue.put("https://reddit.com" + submission_url)
                elif active_tab == 2:
                    self.response3.url_queue.put("https://reddit.com" + submission_url)
            except queue.Empty:
                pass
            time.sleep(0.5)

    def quitProgram(self, parent):
        """Stops program"""
        parent.destroy()


def main():
    root = tk.Tk()
    root.state('zoomed')
    frame = IncomingSubmissionsAdvanced(root)
    frame.incoming_submissions.insertIntoTree()
    frame.incoming_submissions.startStreaming()
    frame.startDetecting()
    root.mainloop()


if __name__ == "__main__":
    main()
