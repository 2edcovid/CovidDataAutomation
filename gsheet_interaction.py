import os
import pygsheets
import pandas as pd
import json
import time
import glob

from utilities import file_names

filePath = file_names.authJson

def setupEnvAuth():
  if 'SSHKEY' in os.environ:
    if os.path.exists(filePath):
      os.remove(filePath)
    with open(filePath, 'w') as f:
      privateKey = os.environ['SSHKEY']
      f.write(privateKey)


def readData():
  data = {}
  jsonFile = file_names.dailyJson
  if os.path.exists(jsonFile):
    with open(jsonFile, "r") as read_file:
      summary = json.load(read_file)
      data.update(summary)
    os.remove(jsonFile)
  return data


def postData(sh, data):
  wks = sh[0]
  values = []

  fields = wks.get_values('B1', 'AY1')[0]
  origVals = wks.get_values('B2', 'AY2')[0]
  for i in range(len(fields)):
    if not origVals[i]:
      print('inserting data in {}'.format(fields[i]))
      if fields[i] in data:
        values.append(data[fields[i]])
      else:
        values.append("")
        print('missing {} from data'.format(fields[i]))
    else:
      print('field {} already filled'.format(fields[i]))
      values.append(origVals[i])
  if (len(values)):
    wks.update_row(2, values, col_offset=1)


def prepRedditPost(sh):
  sheetStart = 0

  sheetData = {
    'New Data' : 'N31',
    'Percentages' : 'J31',
    '7 Day Rolling' : 'K31',
    'Rates' : 'H31',
    'Month Summaries' : 'L41',
    'Totals' : 'H31',
    'Testing Totals' : 'M27',
    'Testing Breakdown' : 'Q20',
    'Hospitalization' : 'I31'
  }

  for header in sheetData:
    sheetStart += 1
    wks = sh[sheetStart]
    df = wks.get_as_df(start='A1', end=sheetData[header], index_column=1)
    commentFile = os.path.join(file_names.redditCommentDir, "{}.md".format(header))

    with open(commentFile, 'w') as f:
      print('')
      print('## {}'.format(header))
      print('')
      print(df.to_markdown())
      
      f.write('## {}\n\n'.format(header))
      f.write(df.to_markdown())
     
  wks = sh[1]
  newCases = wks.get_value('D2')
  newDeaths = wks.get_value('I2')

  wks = sh[9]
  currentHospitalized = wks.get_value('B2')
  redditPostTitle = "{} as of 11:00am: {} New Cases, {} New Deaths, {} Currently Hospitalized.".format(time.strftime('%a. %m/%d'), newCases, newDeaths, currentHospitalized)
  print(redditPostTitle)
  with open(file_names.redditTitle, 'w') as f:
    f.write(redditPostTitle)


if __name__ == "__main__":
  setupEnvAuth()

  gc = pygsheets.authorize(service_file=filePath)
  sh = gc.open('Covid19')

  data = readData()
  postData(sh, data)

  prepRedditPost(sh)
