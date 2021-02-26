import praw
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import simpledialog, messagebox
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

    def askURL(self):
        url = tk.simpledialog.askstring(title="URL", prompt="Type your URL here")
        threading.Thread(target=lambda: self.showComments(url)).start()

    def showComments(self, URL):
        try:
            submission = reddit.submission(url=URL)
            submission.comments.replace_more(limit=None)
            for comment in submission.comments:
                text = self.filter(comment.body)
                layer = self.comment_tree.insert('', tk.END, iid=comment.id, text=text)
                self.parseComments(comment, layer)
        except:
            tk.messagebox.showerror('Error', 'URL not found')

    def parseComments(self, top_comment, layer):
        for comment in top_comment.replies:
            text = self.filter(comment.body)
            sublayer = self.comment_tree.insert(layer, tk.END, iid=comment.id, text=text)
            self.parseComments(comment, sublayer)

    def filter(self, text):
        new_text = ''
        for char in text:
            if char != '\n':
                new_text = new_text + char
            else:
                new_text = new_text + ' '
        return new_text

root = tk.Tk()
root.state('zoomed')
frame = CommentTreeDisplay(root)
frame.pack(fill="both", expand=1)
root.mainloop()
