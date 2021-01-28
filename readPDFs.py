# pylint: disable=missing-function-docstring, missing-module-docstring, invalid-name
import os
import re
import glob
import fitz
from utilities import file_names


dateRegex = r'(\d+\/\d+\/\d+)'

counties = [
    'Adair',
    'Adams',
    'Allamakee',
    'Appanoose',
    'Audubon',
    'Benton',
    'Black Hawk',
    'Boone',
    'Bremer',
    'Buchanan',
    'Buena Vista',
    'Butler',
    'Calhoun',
    'Carroll',
    'Cass',
    'Cedar',
    'Cerro Gordo',
    'Cherokee',
    'Chickasaw',
    'Clarke',
    'Clay',
    'Clayton',
    'Clinton',
    'Crawford',
    'Dallas',
    'Davis',
    'Decatur',
    'Delaware',
    'Des Moines',
    'Dickinson',
    'Dubuque',
    'Emmet',
    'Fayette',
    'Floyd',
    'Franklin',
    'Fremont',
    'Greene',
    'Grundy',
    'Guthrie',
    'Hamilton',
    'Hancock',
    'Hardin',
    'Harrison',
    'Henry',
    'Howard',
    'Humboldt',
    'Ida',
    'Iowa',
    'Jackson',
    'Jasper',
    'Jefferson',
    'Johnson',
    'Jones',
    'Keokuk',
    'Kossuth',
    'Lee',
    'Linn',
    'Louisa',
    'Lucas',
    'Lyon',
    'Madison',
    'Mahaska',
    'Marion',
    'Marshall',
    'Mills',
    'Mitchell',
    'Monona',
    'Monroe',
    'Montgomery',
    'Muscatine',
    "O'Brien",
    'Osceola',
    'Page',
    'Palo Alto',
    'Plymouth',
    'Pocahontas',
    'Polk',
    'Pottawattamie',
    'Poweshiek',
    'Ringgold',
    'Sac',
    'Scott',
    'Shelby',
    'Sioux',
    'Story',
    'Tama',
    'Taylor',
    'Union',
    'Van Buren',
    'Wapello',
    'Warren',
    'Washington',
    'Wayne',
    'Webster',
    'Winnebago',
    'Winneshiek',
    'Woodbury',
    'Worth',
    'Wright'
]

def readVaccinePDF(pdfFile):
    vaccineData = {}
    pageTitles = ['Summary', 'Doses by County', 'Doses by Provider',
                  'Completed by County', 'Completed by Provider', 'Admin Page']
    doc = fitz.open(pdfFile)

    pageCount = doc.pageCount
    for i in range(pageCount):
        page = doc.loadPage(i)
        pdfText = page.getText('words')
        if i == 0:
            originalText = []
            textToUse = []
            for text in pdfText:
                originalText.append(text[4])
                matches = re.match(dateRegex, text[4])
                noCommaText = text[4].replace(',', '')
                if noCommaText.isnumeric() or matches:
                    textToUse.append(text[4])
            if len(textToUse) > 9:
              vaccineData['Doses Administered in Iowa'] = textToUse[0]
              vaccineData['Doses Administered to Iowans'] = textToUse[1]
              vaccineData['Manufacturer Unknown'] = textToUse[4]
              vaccineData['Manufacturer Pfizer'] = textToUse[5]
              vaccineData['Manufacturer Moderna'] = textToUse[6]
              vaccineData['Vaccine Report Date'] = textToUse[7]
              vaccineData['Series Started'] = textToUse[8]
              vaccineData['Series Completed'] = textToUse[9]
            else:
              vaccineData['Doses Administered in Iowa'] = textToUse[0]
              vaccineData['Doses Administered to Iowans'] = textToUse[1]
              vaccineData['Manufacturer Pfizer'] = textToUse[4]
              vaccineData['Manufacturer Moderna'] = textToUse[5]
              vaccineData['Vaccine Report Date'] = textToUse[6]
              vaccineData['Series Started'] = textToUse[7]
              vaccineData['Series Completed'] = textToUse[8]
        elif i not in [2, 4, 5]:
            print(pageTitles[i])
            vaccineData[pageTitles[i]] = {}
            page = doc.loadPage(i)
            pdfText = page.getText('words')
            countyName = ''
            extraText = ''
            readingCounty = True
            for text in pdfText:
                noCommaText = text[4].replace(',', '')
                if not noCommaText.isnumeric():
                    if readingCounty:
                        if countyName:
                            countyName = countyName + " " + text[4]
                        else:
                            countyName = text[4]
                    else:
                        extraText = extraText + ' ' + text[4]
                else:
                    if countyName:
                        readingCounty = countyName != 'Adair'
                        vaccineData[pageTitles[i]][countyName] = text[4]
                        countyName = ''
                    else:
                        extraText = extraText + ' ' + text[4]

    return vaccineData


def readHospitalPDF(pdfFile):
    countyHospitalData = {}
    countyHospitalData['Hospitalized By County'] = {}

    doc = fitz.open(pdfFile)
    pageCount = doc.pageCount
    page = doc.loadPage(pageCount-1)
    pdfText = page.getText('words')

    countyName = ''
    extraText = ''
    readingCounty = True
    for text in pdfText:
        if not text[4].isnumeric():
            if readingCounty:
                if countyName:
                    countyName = countyName + " " + text[4]
                else:
                    countyName = text[4]
            else:
                extraText = extraText + ' ' + text[4]
        else:
            if countyName:
                readingCounty = countyName != 'Wright'
                countyHospitalData['Hospitalized By County'][countyName] = text[4]
                countyName = ''
            else:
                extraText = extraText + ' ' + text[4]

    textToUse = []
    for text in extraText.split():
        matches = re.match(dateRegex, text)
        noCommaText = text.replace(',', '')
        if noCommaText.isnumeric() or matches:
            textToUse.append(text)
    countyHospitalData['Out of State Hospitalized'] = textToUse[0]
    countyHospitalData['Iowans Hospitalized'] = textToUse[1]
    countyHospitalData['Total Hospitalized'] = textToUse[2]
    countyHospitalData['Hospital Report Date'] = textToUse[3]

    return countyHospitalData


def readHospitalData():
    list_of_pdfs = glob.glob(os.path.join(
        file_names.storageDir, 'countyHospital*.pdf'))
    list_of_pdfs.sort()
    pdfFile = list_of_pdfs[-1]

    hospitalData = None
    hospitalData = readHospitalPDF(pdfFile)
    verifyCounties(hospitalData['Hospitalized By County'])
    print(hospitalData)

    return hospitalData


def readVaccineData():
    list_of_pdfs = glob.glob(os.path.join(
        file_names.storageDir, 'countyVaccine*.pdf'))
    list_of_pdfs.sort()
    pdfFile = list_of_pdfs[-1]

    vaccineData = None
    vaccineData = readVaccinePDF(pdfFile)
    verifyCounties(vaccineData['Doses by County'])
    verifyCounties(vaccineData['Completed by County'])
    print(vaccineData)

    return vaccineData


def verifyCounties(data):
    for county in counties:
        if county not in data:
            data[county] = 0


if __name__ == "__main__":
    hospitalData = readHospitalData()
    vaccineData = readVaccineData()
