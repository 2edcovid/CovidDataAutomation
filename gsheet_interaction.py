import os
import pygsheets
import pandas as pd
import json
import time
import glob
import datetime
import math

from utilities import commit_checker
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

  dateVal = wks.get_value('A2')
  current_date = time.strftime("%d-%b")

  if (dateVal != current_date):
    print('no values for todays date yet')
    date_val = time.strftime("%m/%d/%Y")
    
    fields = wks.get_values('B1', 'AY1')[0]
    # origVals = wks.get_values('B2', 'AY2')[0]

    # insertNewRow = True
    # for i in range(len(origVals)):
    #   if not origVals[i]:
    #     insertNewRow = False
    #     break
    
    # if not insertNewRow:
    #   values.append(origVals[0])
    # else:
    print('inserting new row')
    values.append(date_val)
    wks.insert_rows(1, number=1, inherit=False)
    # origVals = wks.get_values('B2', 'AY2')[0]


    for i in range(len(fields)):
      # if not origVals[i]:
      print('inserting data in {}'.format(fields[i]))
      if fields[i] in data:
        values.append(data[fields[i]])
      else:
        values.append("")
        print('missing {} from data'.format(fields[i]))
      # else:
      #   print('field {} already filled'.format(fields[i]))
      #   values.append(origVals[i])

    if (len(values)):
      wks.update_row(2, values)


def prepRedditPost(sh):
  sheetStart = 0

  sheetData = {
    'New Data' : 'M31',
    'Percentages' : 'J31',
    '7 Day Rolling' : 'M27',
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

  wks = sh[0]
  totalVaccinated = wks.get_value('AS2')
  wks = sh[1]
  newCases = wks.get_value('D2')
  newDeaths = wks.get_value('I2')

  wks = sh[9]
  currentHospitalized = wks.get_value('B2')
  redditPostTitle = "{} as of 11:00am: {} New Cases, {} New Deaths, {} Currently Hospitalized, {} Fully Vaccinated.".format(time.strftime('%a. %m/%d'), newCases, newDeaths, currentHospitalized, totalVaccinated)
  print(redditPostTitle)
  with open(file_names.redditTitle, 'w') as f:
    f.write(redditPostTitle)


def prepWeeklyRedditPost(sh):
  today = datetime.datetime.now().strftime('%m/%d')

  if datetime.datetime.now().weekday() == 3:
    header = 'Month Summaries'
    wks = sh[2]
    df = wks.get_as_df(start='A1', end='L41', index_column=1)
    commentFile = os.path.join(file_names.redditCommentDir, "{}.md".format(header))

    with open(commentFile, 'w') as f:
      print('')
      print('## {}'.format(header))
      print('')
      print(df.to_markdown())
      
      f.write('## {}\n\n'.format(header))
      f.write(df.to_markdown())


    # Calculated
    wks = sh[1]
    caseMatrix = wks.range('D2:D8', returnas='matrix')
    newCases = 0
    for i in range(len(caseMatrix)):
      newCases = newCases + int(caseMatrix[i][0].replace(',', ''))

    deathsMatrix = wks.range('I2:I8', returnas='matrix')
    newDeaths = 0
    for i in range(len(deathsMatrix)):
      newDeaths = newDeaths + int(deathsMatrix[i][0].replace(',', ''))

    vaccinesMatrix = wks.range('L2:L8', returnas='matrix')
    vaccinesGiven = 0
    for i in range(len(vaccinesMatrix)):
      vaccinesGiven = vaccinesGiven + int(vaccinesMatrix[i][0].replace(',', ''))

    # Hospitalization Totals
    wks = sh[9]
    avgHospitalized = wks.get_value('B2') #-D8

    hospitalMatrix = wks.range('B2:B8', returnas='matrix')
    avgHospitalized = 0
    for i in range(len(hospitalMatrix)):
      avgHospitalized = avgHospitalized + int(hospitalMatrix[i][0].replace(',', ''))

    avgHospitalized = math.ceil(avgHospitalized/7)

  
    lastDay = (datetime.datetime.now() - datetime.timedelta(days=6)).strftime('%m/%d')
    redditPostTitle = "Covid Weekly Info {}-{}: {:,} New Cases, {:,} New Deaths, {:,} Vaccines Doses Given, {:,} Average Hospitalized per day".format(lastDay, today, newCases, newDeaths, vaccinesGiven, avgHospitalized)
    print(redditPostTitle)
    with open(file_names.redditTitle, 'w') as f:
      f.write(redditPostTitle)
  else:
    print('not posting')


if __name__ == "__main__":
  setupEnvAuth()

  gc = pygsheets.authorize(service_file=filePath)
  sh = gc.open('Covid19')

  data = readData()
  postData(sh, data)

  # prepRedditPost(sh)

  prepWeeklyRedditPost(sh)
