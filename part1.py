import praw
import tkinter as tk
import tkinter.ttk as ttk
import time


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
        tree = ttk.Treeview(parent)
        tree.insert('', 'end', 'widgets', text='Test')


root = tk.Tk()
frame = IncomingSubmissions(root)
frame.pack()
root.mainloop()

