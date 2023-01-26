import praw
import pprint



url = 'https://www.reddit.com/r/thenetherlands/comments/kieo5k/hoe_spaart_rthenetherlands/'
# subreddit = reddit.subreddit(url)
submission = reddit.submission(url=url)
submission.comment_sort = 'top'
submission.comments.replace_more(limit=None)
comment_queue = submission.comments[:]
# print(comment_queue)
# while comment_queue:
#     comment = comment_queue.pop(0)
#     print(comment.body)
#     print('#')

for submission in reddit.subreddit('all').stream.submissions():
    print(submission.subreddit, submission.title)
