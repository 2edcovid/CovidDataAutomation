# pylint: disable=too-many-locals, too-many-statements


import csv
import json
import os
import glob

from utilities import file_names
from utilities import commit_checker
import readPDFs
import readImages


def createGeoJson(localCsvFile, hospitalData, vaccineCSV=None, removePending=False, vaccineData=None):
    countyData = {}
    data = {}
    date = (localCsvFile.split('.csv')[0].split()[0].split('Summary')[1])
    with open(localCsvFile) as csvFile:
        csvReader = csv.DictReader(csvFile)
        for row in csvReader:
          countyHeader = 'County'
          if 'EventResidentCounty' in row:
            countyHeader = 'EventResidentCounty'

          tests = 'Total Tests'
          if 'Individuals Tested' in row:
            tests = 'Individuals Tested'

          positives = 'Total Positive Tests'
          if 'Individuals Positive' in row:
            positives = 'Individuals Positive'
            
          countyData[row[countyHeader]] = {
                'Tested' : row[tests],
                'Positive' : row[positives],
                'Recovered' : row['Total Recovered'],
                'Deaths' : row['Total Deaths'],
            }
          try:
            countyData[row[countyHeader]]['Active'] = int(row[positives]) - (int(row['Total Recovered']) + int(row['Total Deaths']))
          except:
            countyData[row[countyHeader]]['Active'] = row[positives]

    if vaccineCSV:
      with open(vaccineCSV) as csvFiles:
        csvReader = csv.DictReader(csvFiles)
        for row in csvReader:
          try:
            countyHeader = 'County'
            countyName = row[countyHeader]
            if countyName == '.':
              countyName = 'Pending Investigation'
            countyData[countyName]['Vaccine Series Initiated'] = row['Series Initiated']
            countyData[countyName]['Vaccine Series Completed'] = row['Series Completed']
          except:
            print('csv issue')
            print(row)
    elif vaccineData:
      for countyName in countyData:
        try:
          countyData[countyName]['Vaccine Series Completed'] = vaccineData[countyName]
        except:
          countyData[countyName]['Vaccine Series Completed'] = 0
          print(countyName)


    with open(file_names.originalGeoJson, 'r') as read_file:
        data = json.load(read_file)

    removeList = []
    for county in data['features']:
        name = county['properties']['Name']

        if name == 'Pending Investigation' and removePending:
          removeList.append(county)
          continue

        if name == 'Obrien':
            name = 'O\'Brien'
        try:
            props = countyData[name]
            county['properties']['Recovered'] = int(props['Recovered'])
            county['properties']['Active'] = int(props['Active'])
            county['properties']['Deaths'] = int(props['Deaths'])
            county['properties']['Confirmed'] = int(props['Positive'])
            county['properties']['Tested'] = int(props['Tested'])
            try:
              county['properties']['VaccineSeriesInitiated'] = int(props['Vaccine Series Initiated'])
            except:
              county['properties']['VaccineSeriesInitiated'] = 0

            try:
              county['properties']['VaccineSeriesCompleted'] = int(props['Vaccine Series Completed'])
            except:
              county['properties']['VaccineSeriesCompleted'] = 0

            try:
              county['properties']['Hospitalized'] = int(hospitalData[name])
            except:
              county['properties']['Hospitalized'] = 0

            try:
              county['properties']['PercentRecovered'] = round(int(props['Recovered'])/county['properties']['pop_est_2018']*100,2)
              county['properties']['PercentActive'] = round(int(props['Active'])/county['properties']['pop_est_2018']*100,2)
              county['properties']['PercentDeaths'] = round(int(props['Deaths'])/county['properties']['pop_est_2018']*100,2)
              county['properties']['PercentConfirmed'] = round(int(props['Positive'])/county['properties']['pop_est_2018']*100,2)
              county['properties']['PercentTested'] = round(int(props['Tested'])/county['properties']['pop_est_2018']*100,2)
            except:
              county['properties']['PercentRecovered'] = 0
              county['properties']['PercentActive'] = 0
              county['properties']['PercentDeaths'] = 0
              county['properties']['PercentConfirmed'] = 0
              county['properties']['PercentTested'] = 0

            try:
              county['properties']['PercentVaccineSeriesInitiated'] = round(int(props['Vaccine Series Initiated'])/county['properties']['pop_est_2018']*100,2)
            except:
              county['properties']['PercentVaccineSeriesInitiated'] = 0

            try:
              county['properties']['PercentVaccineSeriesCompleted'] = round(int(props['Vaccine Series Completed'])/county['properties']['pop_est_2018']*100,2)
            except:
              county['properties']['PercentVaccineSeriesCompleted'] = 0

            try:
              county['properties']['PercentHospitalized'] = round(int(hospitalData[name])/county['properties']['pop_est_2018']*100,2)
            except:
              county['properties']['PercentHospitalized'] = 0

        except:
            print('issues with {}'.format(name))
            county['properties']['Active'] = 0
            county['properties']['Tested'] = 0
            county['properties']['Hospitalized'] = 0
            county['properties']['PercentRecovered'] = 0
            county['properties']['PercentActive'] = 0
            county['properties']['PercentDeaths'] = 0
            county['properties']['PercentConfirmed'] = 0
            county['properties']['PercentTested'] = 0
            county['properties']['PercentHospitalized'] = 0
            county['properties']['VaccineSeriesInitiated'] = 0
            county['properties']['VaccineSeriesCompleted'] = 0
            county['properties']['PercentVaccineSeriesInitiated'] = 0
            county['properties']['PercentVaccineSeriesCompleted'] = 0

    for county in removeList:
        data['features'].remove(county)

    combinedFile = file_names.storageGeoJsonFormat.format(date)
    write_json(combinedFile, data)

    return combinedFile


def write_json(file_path, data):
    if os.path.exists(file_path):
        os.remove(file_path)
    with open(file_path, 'w') as open_file:
        json.dump(data, open_file, indent="")


def load_image_data():
  data = {}

  data.update(readImages.getSerologyData())
  data.update(readImages.getCaseData())
  data.update(readImages.getRMCCData())

  data.update(readImages.getDeathData())
  data.update(readImages.getLTCData())
  return data


def readRecoveredCSVData():
  list_of_files = glob.glob(os.path.join(file_names.storageDir, 'Summary*.csv'))
  list_of_files.sort()
  summary_csv_file = list_of_files[-1]

  runningTotal = 0

  with open(summary_csv_file) as csvFile:
    csvReader = csv.DictReader(csvFile)
    for row in csvReader:
      runningTotal = runningTotal + int(row['Total Recovered'])

  return runningTotal

def readVaccineCSVData():
  fileNames = [
    os.path.join(file_names.storageDir, "VaccineDosesAdministered{}.csv"),
    os.path.join(file_names.storageDir, "VaccineIndividuals1stDose{}.csv"),
    os.path.join(file_names.storageDir, "VaccineIndividualsComplete{}.csv"),
    os.path.join(file_names.storageDir, "VaccineManufacturer{}.csv")
  ]

  vaccineData = {}

  list_of_files = glob.glob(fileNames[0].format("*"))
  list_of_files.sort()
  localCsvFile = list_of_files[-1]
  with open(localCsvFile) as csvFile:
    csvReader = csv.DictReader(csvFile)
    for row in csvReader:
      for key in row:
        vaccineData['Total Vaccine Doses Given'] = row[key]

  list_of_files = glob.glob(fileNames[1].format("*"))
  list_of_files.sort()
  localCsvFile = list_of_files[-1]
  with open(localCsvFile) as csvFile:
    csvReader = csv.DictReader(csvFile)
    for row in csvReader:
      for key in row:
        vaccineData['Vaccine Series Started'] = row[key]

  list_of_files = glob.glob(fileNames[2].format("*"))
  list_of_files.sort()
  localCsvFile = list_of_files[-1]
  with open(localCsvFile) as csvFile:
    csvReader = csv.DictReader(csvFile)
    for row in csvReader:
      for key in row:
        vaccineData['Vaccine Series Completed'] = row[key]

  list_of_files = glob.glob(fileNames[3].format("*"))
  list_of_files.sort()
  localCsvFile = list_of_files[-1]
  with open(localCsvFile) as csvFile:
    csvReader = csv.DictReader(csvFile)
    for row in csvReader:
      manufacturer = row['Vaccine Manufacturer']
      if manufacturer == 'Moderna':
        vaccineData['Moderna Doses Given'] = row['Doses']
      else:
        vaccineData['Pfizer Doses Given'] = row['Doses']

  return vaccineData


if __name__ == "__main__":
    image_data = load_image_data()
    vaccine_data = readVaccineCSVData()
    image_data['Total Recovered'] = readRecoveredCSVData()
    image_data.update({'Recovered With Preexisting Condition': 0,
            'Recovered With No Preexisting Condition': 0,
            'Recovered Preexisting Condition Unknown': 0,
        })
    print(vaccine_data)

    image_data.update(vaccine_data)
    write_json(file_names.dailyJson, image_data)

    hospital_pdf_data = readPDFs.readHospitalData()

    list_of_files = glob.glob(os.path.join(file_names.storageDir, 'Summary*.csv'))
    list_of_files.sort()
    summary_csv_file = list_of_files[-1]

    countyData = os.path.join(file_names.storageDir, "VaccineDosesByCounty{}.csv")

    list_of_files = glob.glob(os.path.join(file_names.storageDir, "VaccineDosesByCounty*.csv"))
    list_of_files.sort()
    vaccine_csv_file = list_of_files[-1]

    print(vaccine_csv_file)
    print(summary_csv_file)

    createGeoJson(summary_csv_file, hospital_pdf_data['Hospitalized By County'], vaccineCSV=vaccine_csv_file)

    print(image_data)
