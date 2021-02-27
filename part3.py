import praw
import tkinter as tk

from praw.exceptions import RedditAPIException

from part2 import CommentTreeDisplay
from tkinter import simpledialog, messagebox
import queue
import threading

reddit = praw.Reddit(
    client_id="kXHM-WcuSy2pDQ",
    client_secret="KsixoG3bUwXCnJw5K8PASkaxumX-EQ",
    user_agent="HCI:JeMiBot:1.0 (by u/JeMiBot)",
    username="JeMiBot",
    password="JesmerMichiel"
)


class ResponseCommentTreeDisplay(CommentTreeDisplay):
    def __init__(self, parent):
        CommentTreeDisplay.__init__(self, parent)
        self.comment_tree.bind("<Double-1>", self.doubleClick)
        self.reply_queue = queue.Queue()

    def doubleClick(self, event):
        comment_id = self.comment_tree.selection()[0]
        reply = tk.simpledialog.askstring(title="Reply", prompt="Type your reply here")
        if reply == "":
            tk.messagebox.showerror('Error', 'Reply is empty')
        else:
            self.reply_queue.put([comment_id, reply])

    def processComments(self):
        try:
            item = self.reply_queue.get(block=False)
            comment = reddit.comment(id=item[0])
            comment.reply(item[1])
        except queue.Empty:
            self.after(1, self.processComments)
        except RedditAPIException as e:
            tk.messagebox.showerror('Error', e)


def main():
    root = tk.Tk()
    root.state('zoomed')
    frame = ResponseCommentTreeDisplay(root)
    threading.Thread(target=frame.processComments).start()
    frame.pack(fill="both", expand=1)
    root.mainloop()


if __name__ == "__main__":
    main()
