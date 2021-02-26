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


        self.grid(column=0, row=0, sticky='NESW')
        tk.Grid.rowconfigure(parent, 0, weight=1)
        tk.Grid.columnconfigure(parent, 0, weight=1)
        tk.Grid.rowconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 0, weight=1)
        self.comment_tree.grid(column=0, row=0, columnspan=1, rowspan= 1, sticky='NESW')

    def askURL(self):
        url = tk.simpledialog.askstring(title="URL", prompt="Type your URL here")
        threading.Thread(target=lambda: self.showComments(url)).start()

    def showComments(self, URL):
        submission = reddit.submission(url=URL)
        submission.comments.replace_more(limit=None)
        n = 1
        for comment in submission.comments:
            comment_id = str(n)
            print(comment_id, comment.body)
            layer = self.comment_tree.insert('', tk.END, iid=comment_id, text=comment.body)
            self.parseComments(comment, 1, layer, comment_id)
            n += 1

    def parseComments(self, top_comment, depth, layer, comment_id):
        for comment in top_comment.replies:
            comment_id = comment_id + "." + str(depth)
            print(comment_id, comment.body)
            sublayer = self.comment_tree.insert(layer, tk.END, iid=comment_id, text=comment.body)
            self.parseComments(comment, depth + 1, sublayer, comment_id)


root = tk.Tk()
root.state('zoomed')
frame = CommentTreeDisplay(root)
frame.pack()
root.mainloop()
