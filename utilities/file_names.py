import os

storageDir = 'historical'
screenshotDir = 'screenshots'
redditCommentDir = 'RedditComments'

originalGeoJson = 'IA_COVID19_Cases.geojson'

storageGeoJsonFormat = os.path.join(storageDir, "data_file_{}.geojson")
storageSummaryFormat = os.path.join(storageDir, 'Summary{}.csv')
storageVaccineCountyFormat = os.path.join(storageDir, 'VaccineCounty{}.csv')
storageVaccineManufactuerFormat = os.path.join(storageDir, 'VaccineManufacturer{}.csv')
countyHospitalFormat = os.path.join(storageDir, 'countyHospital{}.pdf')
countyVaccineFormat = os.path.join(storageDir, 'countyVaccine{}.pdf')

mapScreenshot = os.path.join(screenshotDir, "Screenshot_ArgisMap.png")
rmccScreenshot = os.path.join(screenshotDir, "Screenshot_RMCC.png")
serologyScreenshot = os.path.join(screenshotDir, "Screenshot_Serology.png")
summaryScreenshot = os.path.join(screenshotDir, "Screenshot_Summary.png")
caseScreenshot = os.path.join(screenshotDir, "Screenshot_Cases.png")
recoveryScreenshot = os.path.join(screenshotDir, "Screenshot_Recovery.png")
deathsScreenshot = os.path.join(screenshotDir, "Screenshot_Deaths.png")
ltcScreenshot = os.path.join(screenshotDir, "Screenshot_LTC.png")
vaccineScreenshot = os.path.join(screenshotDir, "Screenshot_Vaccine.png")

accessJson = 'accessVals.json'

authJson = 'gsheetAuth.json'

dailyJson = 'dailyData.json'

imgurComment = 'imgurComment.md'
redditTitle = os.path.join(redditCommentDir, 'title.md')
