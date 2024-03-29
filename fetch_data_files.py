
import os
import time
import requests

from utilities.selenium_utils import *
from utilities import file_names
from utilities import urls
from utilities import commit_checker
import shutil

SLEEP_DURATION = 20
SHORT_SLEEP_DURATION = 10

buttonContainer = 'cd-control-menu_container_2gtJe'
buttonCss = "button[class='db-button small button cd-control-menu_option_wH8G6 cd-control-menu_expand_VcWkC cd-control-menu_button_2VfJA cd-control-menu_db-button_2UMcr cd-control-menu_noTransition_tNu8c ng-scope']"
# buttonCss = "button[class='db-button small button cd-control-menu_option_wH8G6 cd-control-menu_expand_VcWkC cd-control-menu_button_2VfJA cd-control-menu_db-button_2UMcr ng-scope']"

def getPDF(browser, link_text, name_fmt):
    filePath = None

    link = browser.find_element_by_link_text(link_text)
    html = link.get_attribute('outerHTML')
    # print(html)
    htmlList = html.split('"')
    linkURL = htmlList[1]
    # print(linkURL)

    if 'drive.google' in linkURL:
      linkURL = linkURL.replace('https://drive.google.com/file/d/', '')
      fileID = linkURL.replace('/view?usp=sharing', '')

      linkURL = 'https://drive.google.com/uc?export=download&id={}'.format(fileID)
    
    browser.get(linkURL)
    time.sleep(SLEEP_DURATION)

    timeString = time.strftime("%Y-%m-%d %H%M")
    localFilePath = name_fmt.format(timeString)
    if saveDownloadFile(browser, file_names.storageDir, localFilePath):
      filePath = localFilePath
    closeBrowser(browser)

    return filePath


def getVaccineData():
    print('getting vaccination data')
    browser = getBrowser(urls.newVaccinePage, height=6200, zoom=90, timeout=SLEEP_DURATION)
    elements = browser.find_elements_by_class_name(buttonContainer)
    print(len(elements))
    saveScreenshot(browser, file_names.vaccineScreenshot)
    closeBrowser(browser)

    # fileNames = [
    #   None,
    #   None,
    #   None,
    #   None,
    #   None,
    #   None,
    #   os.path.join(file_names.storageDir, "VaccineDosesAdministered{}.csv"),
    #   os.path.join(file_names.storageDir, "VaccineIowanDoses{}.csv"),
    #   os.path.join(file_names.storageDir, "VaccineIndividuals1stDose{}.csv"),
    #   os.path.join(file_names.storageDir, "VaccineIndividuals2ndComplete{}.csv"),
    #   os.path.join(file_names.storageDir, "cvs11{}.csv"),
    #   os.path.join(file_names.storageDir, "cvs12{}.csv"),
    #   os.path.join(file_names.storageDir, "VaccineIndividualsComplete{}.csv"), 
    #   os.path.join(file_names.storageDir, "VaccineIndividualsSingleComplete{}.csv"), 
    #   os.path.join(file_names.storageDir, "cvs15{}.csv"),
    #   os.path.join(file_names.storageDir, "cvs16{}.csv"),
    #   os.path.join(file_names.storageDir, "VaccineManufacturer{}.csv"), 
    #   os.path.join(file_names.storageDir, "VaccineDosesDistinctPersons{}.csv"), 
    #   os.path.join(file_names.storageDir, "VaccinePercentageClarification{}.csv"),
    #   os.path.join(file_names.storageDir, "VaccineDosesByRace{}.csv"), 
    #   os.path.join(file_names.storageDir, "VaccineDosesByAgeGroup{}.csv"), 
    #   os.path.join(file_names.storageDir, "VaccineDosesByEthnicity{}.csv"), 
    #   os.path.join(file_names.storageDir, "VaccineDosesByGender{}.csv"), 
    #   os.path.join(file_names.storageDir, "VaccinePercentClarification{}.csv"), 
    #   os.path.join(file_names.storageDir, "VaccinePercentageByRace{}.csv"), 
    #   os.path.join(file_names.storageDir, "VaccinePercentageByAgeGroup{}.csv"), 
    #   os.path.join(file_names.storageDir, "VaccinePercentageByEthnicity{}.csv"), 
    #   os.path.join(file_names.storageDir, "VaccinePercentageByGender{}.csv"), 
    #   os.path.join(file_names.storageDir, "VaccineDosesByDay{}.csv"), 
    #   os.path.join(file_names.storageDir, "datanotes{}.csv"),
    # ]
  
    timeString = time.strftime("%Y-%m-%d %H%M") 
    # for i in range(len(elements)):
    #   try:
    #     if fileNames[i]:
    #       browser = getBrowser(urls.newVaccinePage, height=1400, zoom=90, timeout=SHORT_SLEEP_DURATION)
    #       localPath = fileNames[i].format(timeString) 
    #       downloadFile(browser, i, localPath)
    #       closeBrowser(browser)
    #   except:
    #     pass

    browser = getBrowser(urls.newVaccineDownload, height=6200, zoom=90, timeout=SLEEP_DURATION)
    elements = browser.find_elements_by_class_name(buttonContainer)
    print(len(elements))
    closeBrowser(browser)

    fileNames = [
      os.path.join(file_names.storageDir, "VaccineDosesToCountyResident{}.csv"),
      os.path.join(file_names.storageDir, "VaccineDosesDoneByCountyProvider{}.csv"),
      os.path.join(file_names.storageDir, "VaccineSeriesCompletedByCountyResident{}.csv"),
      os.path.join(file_names.storageDir, "VaccineSeriesCompletedByCountyProvider{}.csv"),
    ]

    for i in range(len(elements)):
      try:
        if fileNames[i]:
          browser = getBrowser(urls.newVaccineDownload, height=1400, zoom=90, timeout=SHORT_SLEEP_DURATION)
          localPath = fileNames[i].format(timeString) 
          downloadFile(browser, i, localPath)
          closeBrowser(browser)
      except:
        pass

    try:
      src_dir=os.path.join(file_names.storageDir, "VaccineSeriesCompletedByCountyResident{}.csv".format(timeString))
      dst_dir=os.path.join(file_names.storageDir, "VaccineDosesByCounty{}.csv".format(timeString))
      shutil.copy(src_dir,dst_dir)
    except:
      pass

    # # debug dl
    # for i in range(len(elements)):
    #   browser = getBrowser(urls.newVaccineDownload, height=1400, zoom=90, timeout=SHORT_SLEEP_DURATION)
    #   localPath=os.path.join(file_names.storageDir, "newVaccineDownload{}-{}.csv".format(i, timeString))
    #   downloadFile(browser, i, localPath)
    #   closeBrowser(browser)


def getHospitalData():
    print('get hospital pdf')
    browser = getBrowser(urls.mainPage, height=1700, zoom=90, timeout=SHORT_SLEEP_DURATION)
    return getPDF(browser, 'Iowa Hospitalizations by County', file_names.countyHospitalFormat)


def getNewSummaryData():
    print('screenshot of new summary page')
    browser = getBrowser(urls.mainPage, height=2200, timeout=SHORT_SLEEP_DURATION)
    saveScreenshot(browser, file_names.newSummaryScreenshot) 
    closeBrowser(browser)


def downloadFile(browser, index, localPath):
    try:
      elements = browser.find_elements_by_class_name(buttonContainer) 
      button = elements[index].find_element_by_css_selector(buttonCss) 
      browser.execute_script("$(arguments[0].click());", button) 
      time.sleep(SHORT_SLEEP_DURATION) 
      saveDownloadFile(browser, file_names.storageDir, localPath)
    except:
      print('issue downloading', localPath)


def getSummary():
    try:
      print('loading Summary Page')
      browser = getBrowser(urls.summaryPage, height=2400, zoom=90, timeout=SLEEP_DURATION)
      saveScreenshot(browser, file_names.summaryScreenshot) 
      timeString = time.strftime("%Y-%m-%d %H%M") 
      localPath = file_names.storageSummaryFormat.format(timeString) 
      downloadFile(browser, -2, localPath)
      closeBrowser(browser)
    except Exception as e:
      print('issue getting summary data {}'.format(e))


def getCSVs():
    print('attempting csv download')
    timeString = time.strftime("%Y-%m-%d %H%M")

    filenameLists = [
      os.path.join(file_names.storageDir,'IndividualsTested{}.csv'.format(timeString)),
      os.path.join(file_names.storageDir,'IndividualsTestedGraph{}.csv'.format(timeString)),
      os.path.join(file_names.storageDir,'IndividualsPositive{}.csv'.format(timeString)),
      os.path.join(file_names.storageDir,'IndividualsPositiveGraph{}.csv'.format(timeString)),
      os.path.join(file_names.storageDir,'TotalRecovered{}.csv'.format(timeString)),
      os.path.join(file_names.storageDir,'TotalRecoveredGraph{}.csv'.format(timeString)),
      os.path.join(file_names.storageDir,'TotalDeaths{}.csv'.format(timeString)),
      os.path.join(file_names.storageDir,'TotalDeathsGraph{}.csv'.format(timeString)),
      os.path.join(file_names.storageDir,'UnderlyingCauseDeaths{}.csv'.format(timeString)),
      os.path.join(file_names.storageDir,'UnderlyingCauseDeathsGraph{}.csv'.format(timeString)),
      os.path.join(file_names.storageDir,'ContributingFactorsDeaths{}.csv'.format(timeString)),
      os.path.join(file_names.storageDir,'ContributingFactorsDeathsGraph{}.csv'.format(timeString)),
    ]

    for i in range(12):
      browser = getBrowser(urls.summaryPage, timeout=SHORT_SLEEP_DURATION)
      buttons = browser.find_elements_by_css_selector('button[aria-label="Export data"]')
      browser.execute_script("$(arguments[0].click());", buttons[i])
      time.sleep(SLEEP_DURATION)

      localPath = filenameLists[i]
      saveDownloadFile(browser, file_names.storageDir, localPath)

      closeBrowser(browser)


def getAccessVals():
  browser = getBrowser(urls.accessPage, height=3200, timeout=SHORT_SLEEP_DURATION)
  saveScreenshot(browser, file_names.newAccessScreenshot) 
  closeBrowser(browser)


def getGeoJSON():
  r = requests.get(urls.dailyGeoJson, stream=True)
  if r.status_code == 200:
    filePath = file_names.originalGeoJson
    if os.path.exists(filePath):
      os.remove(filePath)
    open(filePath, 'wb').write(r.content)
  return filePath


def getOriginalMap():
  print('screenshot of original map')
  try:
    browser = getBrowser(urls.argisMap, timeout=SLEEP_DURATION)
    time.sleep(40)
    saveScreenshot(browser, file_names.mapScreenshot)
    closeBrowser(browser)
  except:
    print('original map down')



def getCases():
  print('screenshot of case page')
  browser = getBrowser(urls.newCasePage, height=3200, zoom=90, timeout=SLEEP_DURATION)
  saveScreenshot(browser, file_names.caseScreenshot)
  closeBrowser(browser)


def getRecovery():
  browser = getBrowser(urls.recoveredPage, height=2500, timeout=SLEEP_DURATION)
  saveScreenshot(browser, file_names.recoveryScreenshot)
  closeBrowser(browser)


def getDeaths():
  print('screenshot of deaths page')
  browser = getBrowser(urls.newDeathPage, height=2500, timeout=SLEEP_DURATION)
  saveScreenshot(browser, file_names.deathsScreenshot)
  closeBrowser(browser)


def getLTC():
  browser = getBrowser(urls.ltcPage, height=400, timeout=SLEEP_DURATION)
  saveScreenshot(browser, file_names.ltcScreenshot)
  closeBrowser(browser)


def getRMCCData():
  print('screenshot of hospital page')
  browser = getBrowser(urls.newHospitalPage, height=5500, timeout=SLEEP_DURATION)
  saveScreenshot(browser, file_names.rmccScreenshot)
  closeBrowser(browser)


def getSerologyData():
  browser = getBrowser(urls.serologyPage, zoom=80, height=400, timeout=SLEEP_DURATION)
  saveScreenshot(browser, file_names.serologyScreenshot)
  closeBrowser(browser)



if __name__ == "__main__":
  if not os.path.exists(file_names.screenshotDir):
      os.makedirs(file_names.screenshotDir)

  getOriginalMap()
  getRMCCData()
  # try:
  #   getHospitalData()
  # except:
  #   print('no hospital pdf')
  getDeaths()
  getCases()
  getNewSummaryData()
  getAccessVals()
  getVaccineData()

  getSummary()

      
