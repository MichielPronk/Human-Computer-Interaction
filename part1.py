import praw
import tkinter as tk
import tkinter.ttk as ttk
import time
import queue
import threading


reddit = praw.Reddit(
    client_id="kXHM-WcuSy2pDQ",
    client_secret="KsixoG3bUwXCnJw5K8PASkaxumX-EQ",
    user_agent="HCI:JeMiBot:1.0 (by u/JeMiBot)",
    username="JeMiBot",
    password="JesmerMichiel"
)


class IncomingSubmissions(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        # Initialize Treeview
        self.tree = ttk.Treeview(parent)

        # Initialize queue
        self.queue = queue.Queue()

        # Specify number of columns
        self.tree["columns"] = ("1", "2")

        # Only show column headers
        self.tree['show'] = 'headings'

        # Assign name to columns
        self.tree.heading("1", text="Subreddit")
        self.tree.heading("2", text="Title")

        self.scrollbar = tk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

        # Configure the tree into the GUI
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    def insideMainLoopCheckQueue(self):
        try:
            submission = self.queue.get(block=False)
            if submission is not None:
                self.tree.insert("", 0, text='Submission', values=(submission[0], submission[1]))
        except queue.Empty:
            pass
        root.after(10, self.insideMainLoopCheckQueue)

    def startTask(self):
        threading.Thread(target=self.otherThreadGeneratingOutput).start()

    def otherThreadGeneratingOutput(self):
        for submission in reddit.subreddit('all').stream.submissions():
            self.queue.put([submission.subreddit, submission.title])


root = tk.Tk()
frame = IncomingSubmissions(root)
frame.startTask()
frame.after(0, frame.insideMainLoopCheckQueue)
frame.pack()
root.mainloop()

