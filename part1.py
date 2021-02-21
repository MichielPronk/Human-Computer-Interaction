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

        # Specify number of columns
        self.tree["columns"] = ("1", "2")

        # Only show column headers
        self.tree['show'] = 'headings'

        # Assign name to columns
        self.tree.heading("1", text="Subreddit")
        self.tree.heading("2", text="Title")

        # Configure the tree into the GUI
        self.tree.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)

        # Initialize scrollbar
        self.scrollbar = tk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

        # Initialize pause button
        self.is_paused = False
        self.pause = tk.Button(self, text="Pause", command=self.pause)
        self.pause.pack(side="top")

        # Initialize scale bar
        self.speed = tk.IntVar()
        self.speed.set(0.1)
        self.speedbar = tk.Scale(self, from_=0.1, to=1, resolution=0.1, orient=tk.HORIZONTAL, variable=self.speed)
        self.speedbar.pack(side="top")

        # Initialize queue
        self.queue = queue.Queue()

    def insertIntoTree(self):
        try:
            submission = self.queue.get(block=False)
            if submission is not None and not self.is_paused:
                self.tree.insert("", 0, text='Submission', values=(submission[0], submission[1]))
        except queue.Empty:
            pass
        root.after(int(self.speedbar.get() * 1000), self.insertIntoTree)

    def startStreaming(self):
        threading.Thread(target=self.addSubmissionsToQueue).start()

    def addSubmissionsToQueue(self):
        for submission in reddit.subreddit('all').stream.submissions():
            if not self.is_paused:
                self.queue.put([submission.subreddit, submission.title])
                time.sleep(int(self.speedbar.get()))

    def pause(self):
        if self.is_paused:
            self.is_paused = False
        else:
            self.is_paused = True



root = tk.Tk()
root.geometry('1000x1000')
frame = IncomingSubmissions(root)
frame.startStreaming()
frame.after(100, frame.insertIntoTree)
frame.pack()
root.mainloop()

