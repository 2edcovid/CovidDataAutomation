import praw
import os
import glob
import time

from utilities import file_names
from utilities import post_time

secret = os.environ['APIKEY']
clientID = os.environ['APIID']
name = 'IowaCovidDailyPost by 2eD'
userName = '2eD'
pwd = os.environ['APIPWD']

def post(reddit, sub='Iowa'):
  with open(file_names.redditTitle, 'r') as f:
    title = f.read()
  os.remove(file_names.redditTitle)
  url = reddit.subreddit(sub).submit_image(title, file_names.mapScreenshot)
  print('https://www.reddit.com/r/{}/comments/{}'.format(sub, url))
  os.remove(file_names.mapScreenshot)

  submission = reddit.submission(url="https://www.reddit.com/comments/{}".format(url))

  fileList = glob.glob(os.path.join(file_names.redditCommentDir, "*.md"))
  for fileName in fileList:
    if fileName != 'README.md' and fileName != file_names.redditTitle:
      try:
        with open(fileName, 'r') as f:
          comment = f.read()
          submission.reply(comment)
        if (fileName not in [os.path.join(file_names.redditCommentDir, 'Links.md'), os.path.join(file_names.redditCommentDir, 'Maps.md')]):
          os.remove(fileName)
      except:
        print(fileName)


reddit = praw.Reddit(client_id=clientID, client_secret=secret,
                     password=pwd, user_agent=name,
                     username=userName)
reddit.validate_on_submit = True

if __name__ == "__main__":
  if post_time.shouldPost():
    post(reddit)

