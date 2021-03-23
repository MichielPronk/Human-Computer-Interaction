import praw
import tkinter as tk
import time
from RedditAPI.part2 import CommentTreeDisplay
from tkinter import simpledialog, messagebox
import queue
import threading

# Connects to reddit with bot account
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

        # Binds double click event to treeview
        self.comment_tree.bind("<Double-1>", self.doubleClick)

        # Initializes queue for replies
        self.reply_queue = queue.Queue()

    def doubleClick(self, event):
        """Prompts user for reply to selected comment and puts them in the reply queue"""
        print(self.comment_tree.selection())
        comment_id = self.comment_tree.selection()[0]
        reply = tk.simpledialog.askstring(title="Reply", prompt="Type your reply here")
        if reply != "" and reply is not None:
            self.reply_queue.put([comment_id, reply])
        else:
            tk.messagebox.showerror('Error', 'Something went wrong')

    def startProcessing(self):
        """Start processComments thread"""
        threading.Thread(target=self.processComments).start()

    def processComments(self):
        """Takes replies from queue and posts them to the right comment"""
        while True:
            try:
                item = self.reply_queue.get(block=False)
                comment = reddit.comment(id=item[0])
                comment.reply(item[1])
            except queue.Empty:
                pass
            time.sleep(1)


def main():
    root = tk.Tk()
    root.state('zoomed')
    frame = ResponseCommentTreeDisplay(root)
    frame.showComments()
    frame.startReceiving()
    frame.startProcessing()
    frame.pack(fill="both", expand=1)
    root.mainloop()


if __name__ == "__main__":
    main()
