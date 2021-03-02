import praw
import tkinter as tk
import threading
import time
from praw.exceptions import InvalidURL
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
        self.comment_set = set()
        self.old_comment_set = set()

        # Initialize scale bar
        self.speed = tk.IntVar()
        self.speed.set(int(5))
        self.speedbar = tk.Scale(self, from_=5, to=50, resolution=1, orient=tk.HORIZONTAL, variable=self.speed)
        self.speedbar.pack(side="top")

    def startComparing(self):
        threading.Thread(target=self.compareComments).start()

    def compareComments(self):
        while True:
            self.old_comment_set = self.comment_set
            self.comment_set = set()
            try:
                submission = reddit.submission(url=self.submission_url)
                submission.comments.replace_more(limit=None)
                for comment in submission.comments:
                    self.comment_set.add(comment.id)
                    self.parseCommentsCheck(comment)
                if self.comment_set != self.old_comment_set:
                    self.url_queue.put(self.submission_url)
            except InvalidURL:
                pass
            except ValueError:
                pass
            time.sleep(self.speed.get())

    def parseCommentsCheck(self, top_comment):
        for comment in top_comment.replies:
            self.comment_set.add(comment.id)
            self.parseCommentsCheck(comment)


def main():
    root = tk.Tk()
    root.state('zoomed')
    frame = UpdatedTreeDisplay(root)
    frame.showComments()
    frame.startReceiving()
    frame.startProcessing()
    frame.startComparing()
    frame.pack(fill="both", expand=1)
    root.mainloop()


if __name__ == "__main__":
    main()
