# pylint: disable=too-many-locals, too-many-statements


import csv
import json
import os
import glob

from utilities import file_names
from utilities import commit_checker
import readPDFs
import readImages


def createGeoJson(localCsvFile, hospitalData, removePending=False):
    countyData = {}
    data = {}
    date = (localCsvFile.split('.csv')[0].split()[0].split('Summary')[1])
    with open(localCsvFile) as csvFile:
        csvReader = csv.DictReader(csvFile)
        for row in csvReader:
          countyHeader = 'County'
          if 'EventResidentCounty' in row:
            countyHeader = 'EventResidentCounty'
            
          countyData[row[countyHeader]] = {
                'Tested' : row['Individuals Tested'],
                'Positive' : row['Individuals Positive'],
                'Recovered' : row['Total Recovered'],
                'Deaths' : row['Total Deaths'],
            }
          try:
            countyData[row[countyHeader]]['Active'] = int(row['Individuals Positive']) - (int(row['Total Recovered']) + int(row['Total Deaths']))
          except:
            countyData[row[countyHeader]]['Active'] = row['Individuals Positive']

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
              county['properties']['Hospitalized'] = int(hospitalData[name])
            except:
              county['properties']['Hospitalized'] = 0
            county['properties']['PercentRecovered'] = round(int(props['Recovered'])/county['properties']['pop_est_2018']*100,2)
            county['properties']['PercentActive'] = round(int(props['Active'])/county['properties']['pop_est_2018']*100,2)
            county['properties']['PercentDeaths'] = round(int(props['Deaths'])/county['properties']['pop_est_2018']*100,2)
            county['properties']['PercentConfirmed'] = round(int(props['Positive'])/county['properties']['pop_est_2018']*100,2)
            county['properties']['PercentTested'] = round(int(props['Tested'])/county['properties']['pop_est_2018']*100,2)
            try:
              county['properties']['PercentHospitalized'] = round(int(hospitalData[name])/county['properties']['pop_est_2018']*100,2)
            except:
              county['properties']['PercentHospitalized'] = 0
        except:
            county['properties']['Active'] = 0
            county['properties']['Tested'] = 0
            county['properties']['Hospitalized'] = 0
            county['properties']['PercentRecovered'] = 0
            county['properties']['PercentActive'] = 0
            county['properties']['PercentDeaths'] = 0
            county['properties']['PercentConfirmed'] = 0
            county['properties']['PercentTested'] = 0
            county['properties']['PercentHospitalized'] = 0

    for county in removeList:
        data['features'].remove(county)

    combinedFile = file_names.storageGeoJsonFormat.format(date)
    with open(combinedFile, "w") as write_file:
        json.dump(data, write_file)

    with open(file_names.webGeoJson, "w") as write_file:
        json.dump(data, write_file)
    return combinedFile


def write_json(file_path, data):
    if os.path.exists(file_path):
        os.remove(file_path)
    with open(file_path, 'w') as open_file:
        json.dump(data, open_file)


def load_image_data():
  data = {}

  data.update(readImages.getSerologyData())
  data.update(readImages.getCaseData())
  data.update(readImages.getRMCCData())

  data.update(readImages.getDeathData())
  data.update(readImages.getRecoveryData())
  data.update(readImages.getLTCData())
  # data.update(readImages.getSummaryData())
  return data


if __name__ == "__main__":
    image_data = load_image_data()
    write_json(file_names.dailyJson, image_data)

    hospital_pdf_data = readPDFs.readHospitalData()
    try:
      vaccine_pdf_data = readPDFs.readVaccineData()
    except:
      print('issue reading vaccine data')

    list_of_files = glob.glob(os.path.join(file_names.storageDir, 'Summary*.csv'))
    list_of_files.sort()
    csvFile = list_of_files[-1]

    createGeoJson(csvFile, hospital_pdf_data['Hospitalized By County'])

    print(image_data)
