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
        self.screen_width = parent.winfo_screenwidth()
        self.screen_height = parent.winfo_screenheight()
        tk.Frame.__init__(self, parent)

        # Initialize Treeview
        self.tree = ttk.Treeview(self, columns=('1', '2'))

        # Specify number of columns
        self.tree.heading("1", text="Subreddit")
        self.tree.column("1")
        self.tree.heading("2", text="Title")
        self.tree.column("2")

        # Only show column headers
        self.tree['show'] = 'headings'

        # Configure the tree into the GUI
        # self.tree.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)

        # Initialize scrollbar
        self.scrollbar = tk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        # self.scrollbar.pack(side="right", fill="y")

        # Initialize pause button
        self.is_paused = False
        self.pause = tk.Button(self, text="Pause", command=self.pause)
        # self.pause.pack(side="top")

        # Initialize scale bar
        self.speed = tk.IntVar()
        self.speed.set(0.1)
        self.speedbar = tk.Scale(self, from_=0.1, to=1, resolution=0.1, orient=tk.HORIZONTAL, variable=self.speed)
        # self.speedbar.pack(side="top")

        # Initialize queue
        self.queue = queue.Queue()

        # Initialize whitelist
        self.whitelist = ttk.Treeview(self, columns=('1'))
        self.whitelist.heading("1", text="Whitelist")
        self.whitelist.column("1")
        self.whitelist['show'] = 'headings'

        # Initialize blacklist
        self.blacklist = ttk.Treeview(self, columns=('1'))
        self.blacklist.heading("1", text="Blacklist")
        self.blacklist.column("1")
        self.blacklist['show'] = 'headings'

        # Initialize input whitelist
        self.list_frame = tk.Frame(self)
        self.w_text = tk.Entry(self.list_frame)
        self.w_submit = tk.Button(self.list_frame, text='Submit')
        self.w_delete = tk.Button(self.list_frame, text='Delete')
        self.b_text = tk.Entry(self.list_frame)
        self.b_submit = tk.Button(self.list_frame, text='Submit')
        self.b_delete = tk.Button(self.list_frame, text='Delete')

        # Grid layout
        self.grid(column=0, row=0, sticky='NESW')
        tk.Grid.rowconfigure(parent, 0, weight=1)
        tk.Grid.columnconfigure(parent, 0, weight=1)
        for rows in range(12):
            tk.Grid.rowconfigure(self, rows, weight=1)
        for columns in range(6):
            tk.Grid.columnconfigure(self, columns, weight=1)

        self.tree.grid(column=0, row=0, columnspan=4, rowspan=12, sticky='NESW')
        self.pause.grid(column=4, row=0, columnspan=1, rowspan=1)
        self.speedbar.grid(column=5, row=0, columnspan=1, rowspan=1)
        self.whitelist.grid(column=4, row=1, columnspan=1, rowspan=9, sticky='NESW')
        self.blacklist.grid(column=5, row=1, columnspan=1, rowspan=9, sticky='NESW')
        self.list_frame.grid(column=4, row=11, columnspan=2, rowspan=1, sticky='NESW')

        tk.Grid.rowconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 0, weight=1)
        for rows in range(2):
            tk.Grid.rowconfigure(self.list_frame, rows, weight=1)
        for columns in range(12):
            tk.Grid.columnconfigure(self.list_frame, columns, weight=1)
        self.w_text.grid(column=3, row=0, columnspan=1, rowspan=1)
        self.w_submit.grid(column=2, row=1, columnspan=1, rowspan=1, sticky='E')
        self.w_delete.grid(column=4, row=1, columnspan=1, rowspan=1, sticky='W')
        self.b_text.grid(column=9, row=0, columnspan=1, rowspan=1)
        self.b_submit.grid(column=8, row=1, columnspan=1, rowspan=1, sticky='E')
        self.b_delete.grid(column=10, row=1, columnspan=1, rowspan=1, sticky='W')


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
root.state('zoomed')
frame = IncomingSubmissions(root)
frame.startStreaming()
frame.after(100, frame.insertIntoTree)
# frame.pack()
root.mainloop()
