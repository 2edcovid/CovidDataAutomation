# 07-01 - 08-05
# 
import os
import sys
rootPath = os.path.dirname(os.path.dirname(__file__))
sys.path.append(rootPath)
import csv
import json
import strip_data
import readPDFs
import glob
import re
import fetch_data_files


months = [7, 8]
days = [1,5]

csvHeaders = ["EventResidentCounty","Individuals Tested","Individuals Positive","Total Recovered","Total Deaths"]
jsonHeaders = ["Name","Tested","Confirmed","Recovered","Deaths"]

def genCSV():
  for file in os.listdir("historical"):
    if file.endswith(".geojson"):
      date = file.split("_")[2]
      date = date.split(".")[0]
      dates = date.split("-")

      if int(dates[1]) == months[0] or (int(dates[1]) == months[1] and int(dates[2]) <= days[1]):
        summaryFile = "Summary{} 1608.csv".format(date)
        rows = []
        with open (os.path.join('historical', file), 'r') as f:
          data = json.load(f)
          
          for county in data['features']:
            name = county['properties']['Name']
            if name == 'Obrien':
              name = 'O\'Brien'
            rows.append( {"EventResidentCounty" : name,
              "Individuals Tested" : county['properties']['Tested'],
              "Individuals Positive" : county['properties']['Confirmed'],
              "Total Recovered" : county['properties']['Recovered'],
              "Total Deaths" : county['properties']['Deaths']}
            )

        with open(summaryFile, 'w',encoding='utf-8',newline='',) as f:
          writer = csv.DictWriter(f, csvHeaders)
          writer.writeheader()
          writer.writerows(rows)

def genGeoJson():

  list_of_files = glob.glob(os.path.join(rootPath, 'historical', '*.csv'))
  for csv_file in list_of_files:
    hospitalData = None
    vaccineData = None
    dateRegex = r".+Summary(2020\-\d\d\-\d\d)\ \d\d\d\d\.csv"
    result = re.match(dateRegex, csv_file)
    print(result.group(1))
    
    list_of_hospital_pdfs = glob.glob(os.path.join(rootPath, 'historical', 'countyHospital{} *.pdf').format(result.group(1)))
    list_of_vaccine_pdfs = glob.glob(os.path.join(rootPath, 'historical', 'countyVaccine{} *.pdf').format(result.group(1)))
    if len(list_of_hospital_pdfs):
      hospitalData = readPDFs.readHospitalPDF(list_of_hospital_pdfs[0])
    if len(list_of_vaccine_pdfs):
      vaccineData = readPDFs.readVaccinePDF(list_of_vaccine_pdfs[0])
    strip_data.createGeoJson(csv_file, hospitalData, vaccine_data=vaccineData)
def cleanGeoJson():
  removeList = [
    'individuals_tested',
    'CreationDate',
    'Creator',
    'EditDate',
    'Editor'
  ]

  for geoFile in os.listdir("historical"):
    if geoFile.endswith(".geojson"):
      date = geoFile.split("_")[2]
      date = date.split(".")[0]
      print(date)

      data = {}
      with open(os.path.join("historical", geoFile), 'r') as read_file:
        data = json.load(read_file)

      for county in data['features']:
        name = county['properties']['Name']
        county['properties']['last_updated'] = date
        for prop in removeList:
          try:
            county['properties'].pop(prop)
          except:
            pass

      with open(os.path.join("historical", geoFile), "w") as write_file:
            json.dump(data, write_file)


def readableDataFromGeoJson():

  removeList = [
    'individuals_tested',
    'CreationDate',
    'Creator',
    'EditDate',
    'Editor',
    'OBJECTID',
    'IACountyID',
    'FIPS',
    'Country',
    'last_updated',
    'GlobalID',
    'SHAPE_Length',
    'SHAPE_Area',
    'pop_est_2018',
    'State'
  ]

  for geoFile in os.listdir("historical"):
    if geoFile.endswith(".geojson"):
      date = geoFile.split("_")[2]
      date = date.split(".")[0]
      print(date)

      data = {}
      with open(os.path.join("historical", geoFile), 'r') as read_file:
        data = json.load(read_file)

      for county in data['features']:
        county.pop('geometry')
        county.pop('type')
        name = county['properties']['Name']
        for prop in removeList:
          try:
            county['properties'].pop(prop)
          except:
            pass

      with open(os.path.join("historical", 'ReadableGeoFileP{}.json'.format(date)), "w") as write_file:
        json.dump(data, write_file)


# readableDataFromGeoJson()
genGeoJson()