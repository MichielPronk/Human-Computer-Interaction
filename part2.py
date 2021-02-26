import praw
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import simpledialog, messagebox
import threading
import queue

reddit = praw.Reddit(
    client_id="kXHM-WcuSy2pDQ",
    client_secret="KsixoG3bUwXCnJw5K8PASkaxumX-EQ",
    user_agent="HCI:JeMiBot:1.0 (by u/JeMiBot)",
    username="JeMiBot",
    password="JesmerMichiel"
)


class CommentTreeDisplay(tk.Frame):
    def __init__(self, parent):
        self.screen_width = parent.winfo_screenwidth()
        self.screen_height = parent.winfo_screenheight()
        tk.Frame.__init__(self, parent)

        # Makes sure each menu does not appear as its own window
        self.option_add('*tearOff', False)

        # Create queue
        self.queue = queue.Queue()
        self.after(1, self.showComments())

        # Create a menubar and add it to root
        menubar = tk.Menu(parent)
        parent['menu'] = menubar

        # Create File menu
        menu_file = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_file, label='File')

        # Add Exit option to File
        menu_file.add_command(label="Exit", command=quit)

        # Create Processing menu
        menu_processing = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_processing, label='Processing')

        # Add Load comments option to Processing
        menu_processing.add_command(label="Load comments", command=self.askURL)

        # Initialize Treeview
        self.comment_tree = ttk.Treeview(self)
        self.comment_tree.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)

        # Initialize scrollbar
        self.scrollbar = tk.Scrollbar(self.comment_tree, orient="vertical", command=self.comment_tree.yview)
        self.comment_tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

    def showComments(self):
        try:
            item = self.queue.get(block=False)
            if item is not None:
                comment = item[0]
                text = comment.body.replace("\n", " ")
                if item[1]:
                    self.comment_tree.insert('',  tk.END, iid=comment.id, text=text, open=True)
                    self.after(1, self.showComments)
                else:
                    self.comment_tree.insert(comment.parent_id[3:], tk.END, iid=comment.id, text=text, open=True)
                    self.after(1, self.showComments)
        except queue.Empty:
            self.after(1, self.showComments)

    def askURL(self):
        url = tk.simpledialog.askstring(title="URL", prompt="Type your URL here")
        self.comment_tree.delete(*self.comment_tree.get_children())
        threading.Thread(target=lambda: self.getComments(url)).start()

    def getComments(self, URL):
        try:
            submission = reddit.submission(url=URL)
            submission.comments.replace_more(limit=None)
            for comment in submission.comments:
                self.queue.put([comment, True])
                self.parseComments(comment)
        except:
            tk.messagebox.showerror('Error', 'URL not found')

    def parseComments(self, top_comment):
        for comment in top_comment.replies:
            self.queue.put([comment, False])
            self.parseComments(comment)


root = tk.Tk()
root.state('zoomed')
frame = CommentTreeDisplay(root)
frame.pack(fill="both", expand=1)
root.mainloop()
