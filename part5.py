import praw
import threading
import praw
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import simpledialog, messagebox
import threading
import queue
import time
from praw.exceptions import InvalidURL

from part1 import IncomingSubmissions
from part3 import ResponseCommentTreeDisplay

reddit = praw.Reddit(
    client_id="kXHM-WcuSy2pDQ",
    client_secret="KsixoG3bUwXCnJw5K8PASkaxumX-EQ",
    user_agent="HCI:JeMiBot:1.0 (by u/JeMiBot)",
    username="JeMiBot",
    password="JesmerMichiel"
)


class IncomingSubmissionsAdvanced(tk.Frame):
    def __init__(self, parent):
        self.screen_width = parent.winfo_screenwidth()
        self.screen_height = parent.winfo_screenheight()
        tk.Frame.__init__(self, parent)

        # Initialize incoming submission frame and notebook
        self.incoming_submissions = IncomingSubmissions(self)
        self.incoming_submissions.startStreaming()
        self.notebook = ttk.Notebook(self)

        # Create 2 reponse comment tree frames within the notebook
        self.response1 = ResponseCommentTreeDisplay(self.notebook)
        self.notebook.add(self.response1, text="Comments 1")
        self.response2 = ResponseCommentTreeDisplay(self.notebook)
        self.notebook.add(self.response2, text="Comments 2")

        # Initialize the grid
        self.grid(column=0, row=0, sticky='NESW')
        tk.Grid.rowconfigure(parent, 0, weight=1)
        tk.Grid.columnconfigure(parent, 0, weight=1)
        tk.Grid.rowconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 0, weight=1)
        for rows in range(1):
            tk.Grid.rowconfigure(self, rows, weight=1)
        for columns in range(3):
            tk.Grid.columnconfigure(self, columns, weight=1)

        self.incoming_submissions.grid(column=0, row=0, columnspan=2, rowspan=1)
        self.notebook.grid(column=2, row=0, columnspan=1, rowspan=1, sticky='NESW')

def main():
    root = tk.Tk()
    root.state('zoomed')
    frame = IncomingSubmissionsAdvanced(root)
    root.mainloop()


if __name__ == "__main__":
    main()