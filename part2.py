import praw
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import simpledialog, messagebox
import threading
import queue
import time

from praw.exceptions import InvalidURL

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

        # Create variables
        self.submission_url = ""

        # Create queue
        self.c_queue = queue.Queue()
        self.url_queue = queue.Queue()

        # Create a menubar and add it to root
        if not isinstance(parent, ttk.Notebook):
            self.menubar = tk.Menu(parent)
            parent.config(menu=self.menubar)

            # Create File menu
            self.menu_file = tk.Menu(self.menubar)
            self.menubar.add_cascade(menu=self.menu_file, label='File')

            # Add Exit option to File
            self.menu_file.add_command(label="Exit", command=lambda: self.quitProgram(parent))

            # Create Processing menu
            self.menu_processing = tk.Menu(self.menubar)
            self.menubar.add_cascade(menu=self.menu_processing, label='Processing')

            # Add Load comments option to Processing
            self.menu_processing.add_command(label="Load comments", command=self.askURL)

        # Initialize Treeview
        self.comment_tree = ttk.Treeview(self)
        self.comment_tree.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)

        # Initialize scrollbar
        self.scrollbar = tk.Scrollbar(self.comment_tree, orient="vertical", command=self.comment_tree.yview)
        self.comment_tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

    def showComments(self):
        try:
            item = self.c_queue.get(block=False)
            if item is not None:
                comment = item[0]
                text = comment.body.replace("\n", " ")
                if item[1]:
                    self.comment_tree.insert('', tk.END, iid=comment.id, text=text, open=True)
                else:
                    self.comment_tree.insert(comment.parent_id[3:], tk.END, iid=comment.id, text=text, open=True)
                self.after(50, self.showComments)
        except queue.Empty:
            self.after(50, self.showComments)

    def startReceiving(self):
        threading.Thread(target=self.getComments).start()

    def askURL(self):
        try:
            user_input = tk.simpledialog.askstring(title="URL", prompt="Type your URL here")
            if user_input != "":
                reddit.submission(url=user_input)
                self.submission_url = user_input
                self.url_queue.put(self.submission_url)
        except InvalidURL:
            tk.messagebox.showerror('Error', "URL does not exist")
        except TypeError:
            pass

    def getComments(self):
        while True:
            try:
                submission_url = self.url_queue.get(block=False)
                submission = reddit.submission(url=submission_url)
                self.c_queue.queue.clear()
                self.comment_tree.delete(*self.comment_tree.get_children())
                submission.comments.replace_more(limit=None)
                for comment in submission.comments:
                    self.c_queue.put([comment, True])
                    self.parseComments(comment)
            except queue.Empty:
                pass
            except InvalidURL:
                pass
            time.sleep(1)

    def parseComments(self, top_comment):
        for comment in top_comment.replies:
            self.c_queue.put([comment, False])
            self.parseComments(comment)

    def quitProgram(self, parent):
        parent.destroy()


def main():
    root = tk.Tk()
    root.state('zoomed')
    frame = CommentTreeDisplay(root)
    frame.showComments()
    frame.startReceiving()
    frame.pack(fill="both", expand=1)
    root.mainloop()


if __name__ == "__main__":
    main()
