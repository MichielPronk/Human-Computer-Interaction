import praw
import pprint

reddit = praw.Reddit(
    client_id="kXHM-WcuSy2pDQ",
    client_secret="KsixoG3bUwXCnJw5K8PASkaxumX-EQ",
    user_agent="HCI:JeMiBot:1.0 (by u/JeMiBot)",
    username="JeMiBot",
    password="JesmerMichiel"
)

url = 'https://www.reddit.com/r/thenetherlands/comments/kieo5k/hoe_spaart_rthenetherlands/'
# subreddit = reddit.subreddit(url)
submission = reddit.submission(url=url)
submission.comment_sort = 'top'
submission.comments.replace_more(limit=None)
comment_queue = submission.comments[:]
print(comment_queue)
while comment_queue:
    comment = comment_queue.pop(0)
    print(comment.body)
    print('#')


