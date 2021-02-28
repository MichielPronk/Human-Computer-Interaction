import praw
from prawcore import NotFound
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

        # Initialize scrollbar
        self.scrollbar = tk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Initialize pause button
        self.is_paused = False
        self.pause = tk.Button(self, text="Pause", command=self.pause)

        # Initialize scale bar
        self.speed = tk.IntVar()
        self.speed.set(int(1))
        self.speedbar = tk.Scale(self, from_=1, to=10, resolution=1, orient=tk.HORIZONTAL, variable=self.speed)

        # Initialize queue
        self.queue = queue.Queue()

        self.after(100, self.insertIntoTree)

        # Initialize whitelist and blacklist list
        self.white_list = []
        self.black_list = []

        # Initialize whitelist
        self.whitelist = ttk.Treeview(self, columns='1')
        self.whitelist.heading("1", text="Whitelist")
        self.whitelist.column("1")
        self.whitelist['show'] = 'headings'

        # Initialize blacklist
        self.blacklist = ttk.Treeview(self, columns='1')
        self.blacklist.heading("1", text="Blacklist")
        self.blacklist.column("1")
        self.blacklist['show'] = 'headings'

        # Initialize input whitelist
        self.list_frame = tk.Frame(self)
        self.w_text = tk.Entry(self.list_frame)
        self.w_submit = tk.Button(self.list_frame, text='Submit', command=lambda: self.submit('W'))
        self.w_delete = tk.Button(self.list_frame, text='Delete', command=lambda: self.delete('W'))
        self.b_text = tk.Entry(self.list_frame)
        self.b_submit = tk.Button(self.list_frame, text='Submit', command=lambda: self.submit('B'))
        self.b_delete = tk.Button(self.list_frame, text='Delete', command=lambda: self.delete('B'))

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
                self.tree.insert("", 0, text='Submission', iid=submission.id, values=(submission.subreddit, submission.title))
        except queue.Empty:
            pass
        self.after(int(self.speedbar.get() * 100), self.insertIntoTree)

    def startStreaming(self):
        threading.Thread(target=self.addSubmissionsToQueue).start()

    def addSubmissionsToQueue(self):
        for submission in reddit.subreddit('all').stream.submissions():
            if not self.is_paused:
                if self.white_list and not self.black_list:
                    if submission.subreddit in self.white_list:
                        self.queue.put(submission)
                elif self.black_list and not self.white_list:
                    if submission.subreddit not in self.black_list:
                        self.queue.put(submission)
                elif not self.black_list and not self.white_list:
                    self.queue.put(submission)
                time.sleep(int(self.speedbar.get())/10)

    def pause(self):
        if self.is_paused:
            self.is_paused = False
        else:
            self.is_paused = True

    def subExists(self, sub):
        try:
            reddit.subreddits.search_by_name(sub, exact=True)
        except NotFound:
            return False
        return True

    def submit(self, color):
        if color == 'W':
            subreddit = self.w_text.get()
            self.w_text.delete(0, tk.END)
            if self.subExists(subreddit):
                self.white_list.append(subreddit)
                self.whitelist.insert("", tk.END, text=subreddit, values=subreddit)
        elif color == 'B':
            subreddit = self.b_text.get()
            self.b_text.delete(0, tk.END)
            if self.subExists(subreddit):
                self.black_list.append(subreddit)
                self.blacklist.insert("", tk.END, text=subreddit, values=subreddit)

    def delete(self, color):
        if color == 'W':
            row_id = self.whitelist.focus()
            node_name = self.whitelist.item(row_id)['text']
            try:
                self.whitelist.delete(row_id)
                self.white_list.remove(node_name)
            except:
                pass

        elif color == 'B':
            row_id = self.blacklist.focus()
            node_name = self.blacklist.item(row_id)['text']
            try:
                self.blacklist.delete(row_id)
                self.black_list.remove(node_name)
            except:
                pass


def main():
    root = tk.Tk()
    root.state('zoomed')
    frame = IncomingSubmissions(root)
    frame.startStreaming()
    root.mainloop()


if __name__ == "__main__":
    main()
