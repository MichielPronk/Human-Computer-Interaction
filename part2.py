import praw
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import simpledialog
import threading

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

        # Create a menubar and add it to root
        menubar = tk.Menu(parent)
        parent['menu'] = menubar

        # Create File menu
        menu_file = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_file, label='File')

        # Add Exit option to File
        menu_file.add_command(label="Exit")

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

    def askURL(self):
        url = tk.simpledialog.askstring(title="URL", prompt="Type your URL here")
        threading.Thread(target=lambda: self.showComments(url)).start()

    def showComments(self, URL):
        submission = reddit.submission(url=URL)
        submission.comments.replace_more(limit=None)
        n = 1
        for comment in submission.comments:
            comment_id = str(n)
            layer = self.comment_tree.insert('', tk.END, iid=comment_id, text=comment_id, values=comment.body)
            self.parseComments(comment, 1, layer, comment_id)
            n += 1

    def parseComments(self, top_comment, depth, layer, comment_id):
        for comment in top_comment.replies:
            comment_id = comment_id + "." + str(depth)
            sublayer = self.comment_tree.insert(layer, tk.END, iid=comment_id, text=comment_id, values=comment.body)
            self.parseComments(comment, depth + 1, sublayer, comment_id)


root = tk.Tk()
root.state('zoomed')
frame = CommentTreeDisplay(root)
frame.pack(fill="both", expand=1)
root.mainloop()
