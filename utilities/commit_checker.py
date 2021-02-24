from git import Repo
import os
import time
import sys

def onMaster():
  repo = Repo(os.getcwd())
  branch = repo.active_branch
  return branch.name == 'master'

def stillNeedTodaysData():
  needIt = True
  repo = Repo(os.getcwd())

  current_time = time.strftime("%Y-%m-%d")

  three_first_commits = list(repo.iter_commits('data', max_count=3))
  for commit in three_first_commits:
    if current_time in commit.message:
      needIt = False
      break

  return needIt


def commitAndMerge(commit_message):
    repo = Repo(os.getcwd())
    origin = repo.remotes.origin
    origin.fetch()

    repo.index.add(repo.untracked_files)
    repo.git.add(update=True)
    repo.index.commit(commit_message)
    data = repo.heads.data 
    data.checkout() 

    os.system('git merge --strategy-option theirs master -m "Merge branch \'master\' into data"') 

if __name__ == "__main__":
  if len(sys.argv) > 1:
    commitAndMerge('data {}'.format(time.strftime("%Y-%m-%d")))
  else:
    commitAndMerge(time.strftime("%Y-%m-%d"))
