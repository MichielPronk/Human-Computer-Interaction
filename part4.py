import praw
import threading
import tkinter as tk
import queue
from part3 import ResponseCommentTreeDisplay

reddit = praw.Reddit(
    client_id="kXHM-WcuSy2pDQ",
    client_secret="KsixoG3bUwXCnJw5K8PASkaxumX-EQ",
    user_agent="HCI:JeMiBot:1.0 (by u/JeMiBot)",
    username="JeMiBot",
    password="JesmerMichiel"
)


class UpdatedTreeDisplay(ResponseCommentTreeDisplay):
    def __init__(self, parent):
        ResponseCommentTreeDisplay.__init__(self, parent)




def main():
    root = tk.Tk()
    root.state('zoomed')
    frame = UpdatedTreeDisplay(root)
    threading.Thread(target=frame.processComments).start()
    frame.pack(fill="both", expand=1)
    root.mainloop()


if __name__ == "__main__":
    main()
