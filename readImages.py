# pylint: disable=missing-function-docstring, missing-module-docstring, invalid-name, no-member, broad-except, too-many-statements
import os
import cv2
import pytesseract

from utilities import file_names


def convertVals(vals):
    newVals = []
    for val in vals:
        newVal = val
        if 'K' in val:
            newVal = int(float(val[:-1])*1000)
        newVals.append(newVal)
    return newVals


def sanitizeText(text):
    textList = text.split('\n')
    realList = []
    for string in textList:
        if string:
            string = string.replace(',', '')
            string = string.replace('=', '')
            string = string.replace(':', '')
            string = string.replace('/', '7')
            string = string.replace('?', '2')
            string = string.replace('“', '')
            string = string.strip()
            if string:
                realList.append(string)
    return realList


def getRMCCData():
    print('RMCC Data')
    data = {}

    try:
        fileName = file_names.rmccScreenshot
        img = cv2.imread(fileName)

        crop_img = img[1160:-30, 150:-100]
        cv2.imwrite(os.path.join(file_names.screenshotDir,
                                 'RMCC_crop.png'), crop_img)

        try:
            hosp_img = crop_img[0:90, 0:320]
            cv2.imwrite(os.path.join(file_names.screenshotDir,
                                     'RMCC_hospital.png'), hosp_img)
            text = pytesseract.image_to_string(hosp_img)
            sanitizedText = sanitizeText(text)
            sanitizedText = convertVals(sanitizedText)
            data['Currently Hospitalized'] = sanitizedText[1]
        except Exception as e:
            print('issue reading currently hospitalized value {}'.format(e))

        try:
            icu_img = crop_img[0:90, 650:950]
            cv2.imwrite(os.path.join(
                file_names.screenshotDir, 'RMCC_icu.png'), icu_img)
            text = pytesseract.image_to_string(icu_img)
            sanitizedText = sanitizeText(text)
            sanitizedText = convertVals(sanitizedText)
            data['In ICU'] = sanitizedText[1]
        except Exception as e:
            print('issue reading icu value {}'.format(e))

        try:
            admit_img = crop_img[0:90, 1250:1625]
            cv2.imwrite(os.path.join(file_names.screenshotDir,
                                     'RMCC_admit.png'), admit_img)
            text = pytesseract.image_to_string(admit_img)
            sanitizedText = sanitizeText(text)
            sanitizedText = convertVals(sanitizedText)
            data['Newly Admitted'] = sanitizedText[1]
        except Exception as e:
            print('issue reading admit value {}'.format(e))

        try:
            bed_img = crop_img[800:1200, 50:550]
            cv2.imwrite(os.path.join(
                file_names.screenshotDir, 'RMCC_bed.png'), bed_img)
            text = pytesseract.image_to_string(bed_img)
            sanitizedText = sanitizeText(text)
            sanitizedText = convertVals(sanitizedText)
            data['Beds Available'] = sanitizedText[1]
            data['ICU Beds Available'] = sanitizedText[3]
        except Exception as e:
            print('issue reading bed values {}'.format(e))

        try:
            vent_img = crop_img[1450:1880, 50:550]
            cv2.imwrite(os.path.join(file_names.screenshotDir,
                                     'RMCC_vent.png'), vent_img)
            text = pytesseract.image_to_string(vent_img)
            sanitizedText = sanitizeText(text)
            sanitizedText = convertVals(sanitizedText)
            vents = sanitizedText[1]
            if vents == 7715:
                vents = 775
            data['Vents Available'] = vents
            data['On Vent'] = sanitizedText[3]
        except Exception as e:
            print('issue reading vent values {}'.format(e))

    except Exception as e:
        print('issue reading RMCC {}'.format(e))

    print(data)
    return data


def getSummaryData():
    print('Summary Data')
    data = {}
    try:
        fileName = file_names.summaryScreenshot
        img = cv2.imread(fileName)
        crop_img = img[200:-100, 200:-1400]
        cv2.imwrite(os.path.join(file_names.screenshotDir,
                                 'Summary_totals.png'), crop_img)
        text = pytesseract.image_to_string(crop_img)
        textList = sanitizeText(text)
        data.update({
            'Total Tested' : textList[1].replace(' ', ''),
            'Total Cases' : textList[3].replace(' ', ''),
            'Total Recovered' : textList[5].replace(' ', ''),
            'Total Deaths' : textList[7].replace(' ', ''),
        })
    except Exception as e:
        print('issue reading summary data {}'.format(e))

    print(data)
    return data


def getSerologyData():
    print('Serology Data')
    data = {}
    try:
        fileName = file_names.serologyScreenshot
        img = cv2.imread(fileName)
        crop_img = img[100:-20, 200:-600]
        cv2.imwrite(os.path.join(file_names.screenshotDir,
                                 'Serology_totals.png'), crop_img)
        text = pytesseract.image_to_string(crop_img)
        textList = sanitizeText(text)
        vals = convertVals(textList[1].split())

        data.update({
            'Individual Serologic Tests': vals[0],
            'Individual Serologic Negatives': vals[1],
            'Individual Serologic Positives': vals[2],
        })
    except Exception as e:
        print('issue reading serology data {}'.format(e))

    print(data)
    return data


def getPCRData(crop_img):
    print('PCR Test Data')
    data = {}
    pcrImg = crop_img[100:420, 10:-10]
    cv2.imwrite(os.path.join(file_names.screenshotDir, 'Cases_pcr.png'), pcrImg)

    try:
        totalPCR = crop_img[100:420, 10:500]
        cv2.imwrite(os.path.join(file_names.screenshotDir,
                                 'Cases_total_pcr.png'), totalPCR)
        text = pytesseract.image_to_string(totalPCR)
        sanitizedText = sanitizeText(text)
        pcrText = []
        for text in sanitizedText:
            newText = text.replace(' ', '')
            if newText.isnumeric():
                pcrText.append(newText)
        pcrText = convertVals(pcrText)
        data['Total PCR Tests'] = pcrText[0]
        data['Individual PCR Tests'] = pcrText[1]
    except Exception as e:
        print('issue reading total pcr values {}'.format(e))

    try:
        negativePCR = crop_img[100:420, 600:1100]
        cv2.imwrite(os.path.join(file_names.screenshotDir,
                                 'Cases_negative_pcr.png'), negativePCR)
        text = pytesseract.image_to_string(negativePCR)
        sanitizedText = sanitizeText(text)
        pcrText = []
        for text in sanitizedText:
            newText = text.replace(' ', '')
            if newText.isnumeric():
                pcrText.append(newText)
        pcrText = convertVals(pcrText)
        data['Total PCR Negatives'] = pcrText[0]
        data['Individual PCR Negatives'] = pcrText[1]
    except Exception as e:
        print('issue reading negative pcr values {}'.format(e))

    try:
        positivePCR = crop_img[100:420, 1200:1700]
        cv2.imwrite(os.path.join(file_names.screenshotDir,
                                 'Cases_positive_pcr.png'), positivePCR)
        text = pytesseract.image_to_string(positivePCR)
        sanitizedText = sanitizeText(text)
        pcrText = []
        for text in sanitizedText:
            newText = text.replace(' ', '')
            if newText.isnumeric():
                pcrText.append(newText)
        pcrText = convertVals(pcrText)
        data['Total PCR Positives'] = pcrText[0]
        data['Individual PCR Positives'] = pcrText[1]
    except Exception as e:
        print('issue reading positive pcr values {}'.format(e))

    print(data)
    return data


def getAntigenData(crop_img):
    print('Antigen Test Data')
    data = {}
    antigenImg = crop_img[550:900, 10:-10]
    cv2.imwrite(os.path.join(file_names.screenshotDir,
                             'Cases_antigen.png'), antigenImg)

    try:
        text = pytesseract.image_to_string(antigenImg)
        totalAntigen = crop_img[550:900, 10:500]
        text = pytesseract.image_to_string(totalAntigen)
        sanitizedText = sanitizeText(text)
        antigenText = []
        for text in sanitizedText:
            newText = text.replace(' ', '')
            if newText.isnumeric():
                antigenText.append(newText)
        antigenText = convertVals(antigenText)
        data['Total Antigen Tests'] = antigenText[0]
        data['Individual Antigen Tests'] = antigenText[1]
    except Exception as e:
        print('issue reading total antigen values {}'.format(e))

    try:
        negativeAntigen = crop_img[550:900, 600:1100]
        text = pytesseract.image_to_string(negativeAntigen)
        sanitizedText = sanitizeText(text)
        antigenText = []
        for text in sanitizedText:
            newText = text.replace(' ', '')
            if newText.isnumeric():
                antigenText.append(newText)
        antigenText = convertVals(antigenText)
        data['Total Antigen Negatives'] = antigenText[0]
        data['Individual Antigen Negatives'] = antigenText[1]
    except Exception as e:
        print('issue reading negative antigen values {}'.format(e))

    try:
        positiveAntigen = crop_img[550:900, 1200:1700]
        text = pytesseract.image_to_string(positiveAntigen)
        sanitizedText = sanitizeText(text)
        antigenText = []
        for text in sanitizedText:
            newText = text.replace(' ', '')
            if newText.isnumeric():
                antigenText.append(newText)
        antigenText = convertVals(antigenText)
        data['Total Antigen Positives'] = antigenText[0]
        data['Individual Antigen Positives'] = antigenText[1]
    except Exception as e:
        print('issue reading positive antigen values {}'.format(e))

    print(data)
    return data


def getTestTotalsData(crop_img):
    print('Total Test Data')
    data = {}

    try:
        totalsImg = crop_img[1000:1150, 10:-500]
        cv2.imwrite(os.path.join(file_names.screenshotDir,
                                 'Cases_totals.png'), totalsImg)
        text = pytesseract.image_to_string(totalsImg)
        sanitizedText = sanitizeText(text)[1].split()
        sanitizedText = convertVals(sanitizedText)
        data.update({
            'Total Tests': sanitizedText[0],
            'Total Negative': sanitizedText[1],
            'Total Positive': sanitizedText[2],
        })
    except Exception as e:
        print('issue reading total test values {}'.format(e))

    try:
        individualsImg = crop_img[1450:1600, 10:-500]
        cv2.imwrite(os.path.join(file_names.screenshotDir,
                                 'Cases_individuals.png'), individualsImg)
        text = pytesseract.image_to_string(individualsImg)
        sanitizedText = sanitizeText(text)[1].split()
        sanitizedText = convertVals(sanitizedText)
        data.update({
            'Total Individual Tests': sanitizedText[0],
            'Total Individuals Negative': sanitizedText[1],
            'Total Individuals Positive': sanitizedText[2],
        })
    except Exception as e:
        print('issue reading individual test values {}'.format(e))

    print(data)
    return data


def getCaseData():
    print('Case Data')
    data = {}
    fileName = file_names.caseScreenshot
    img = cv2.imread(fileName)
    crop_img = img[100:-80, 100:-100]
    cv2.imwrite(os.path.join(file_names.screenshotDir,
                             'Cases_crop.png'), crop_img)

    data.update(getPCRData(crop_img))
    data.update(getAntigenData(crop_img))
    data.update(getTestTotalsData(crop_img))

    try:
        breakDownImg = crop_img[-200:-10, 10:-10]
        cv2.imwrite(os.path.join(file_names.screenshotDir,
                                 'Cases_breakdown.png'), breakDownImg)
        text = pytesseract.image_to_string(breakDownImg)
        sanitizedText = sanitizeText(text)[1].split()
        sanitizedText = convertVals(sanitizedText)
        data.update({
            'Cases With Preexisting Condition': sanitizedText[0],
            'Cases With No Preexisting Condition': sanitizedText[1],
            'Cases Preexisting Condition Unknown': sanitizedText[2],
        })
    except Exception as e:
        print('issue reading case breakdown data {}'.format(e))

    print(data)
    return data


def getDeathData():
    print('Death Data')
    data = {}
    fileName = file_names.deathsScreenshot
    img = cv2.imread(fileName)

    try:
        crop_img = img[100:200, 100:-100]
        cv2.imwrite(os.path.join(file_names.screenshotDir,
                                 'Deaths_total.png'), crop_img)
        text = pytesseract.image_to_string(crop_img)
        textList = sanitizeText(text)
        vals = convertVals(textList[1].split())
        data['Total Deaths'] = vals[0]
        data['Underlying Cause Deaths'] = vals[1]
        data['Contributing Factor Deaths'] = vals[2]
    except Exception as e:
        print('issue reading total deaths {}'.format(e))

    try:
        crop_img = img[-150:-10, 100:-100]
        cv2.imwrite(os.path.join(file_names.screenshotDir,
                                 'Deaths_breakdown.png'), crop_img)
        text = pytesseract.image_to_string(crop_img)
        textList = sanitizeText(text)
        vals = convertVals(textList[1].split())

        data.update({
            'Deaths With Preexisting Condition': vals[0],
            'Deaths With No Preexisting Condition': vals[1],
            'Deaths Preexisting Condition Unknown': '0'
        })
    except Exception as e:
        print('issue reading death breakdown {}'.format(e))

    print(data)
    return data


def getRecoveryData():
    print('Reovery Data')
    data = {}
    fileName = file_names.recoveryScreenshot
    img = cv2.imread(fileName)

    try:
        crop_img = img[100:200, 100:500]
        cv2.imwrite(os.path.join(file_names.screenshotDir,
                                 'Recovery_total.png'), crop_img)
        text = pytesseract.image_to_string(crop_img)
        textList = sanitizeText(text)
        vals = convertVals(textList[0].split())
        data['Total Recovered'] = vals[1]
    except Exception as e:
        print('issue reading total recovered {}'.format(e))

    try:
        crop_img = img[2000:-200, 100:-100]
        cv2.imwrite(os.path.join(file_names.screenshotDir,
                                 'Recovery_breakdown.png'), crop_img)
        text = pytesseract.image_to_string(crop_img)
        textList = sanitizeText(text)

        vals = convertVals(textList[1].split())

        data.update({
            'Recovered With Preexisting Condition': vals[0],
            'Recovered With No Preexisting Condition': vals[1],
            'Recovered Preexisting Condition Unknown': vals[2],
        })
    except Exception as e:
        print('issue reading recovery breakdown {}'.format(e))

    print(data)
    return data


def getLTCData():
    print('LTC Data')
    data = {}

    try:
        fileName = file_names.ltcScreenshot
        img = cv2.imread(fileName)
        crop_img = img[150:-10, 100:-100]
        cv2.imwrite(os.path.join(file_names.screenshotDir,
                                 'LTC_totals.png'), crop_img)
        text = pytesseract.image_to_string(crop_img)
        textList = sanitizeText(text)

        vals = convertVals(textList[1].split())

        data = {
            'Current LTC Outbreaks': vals[0],
            'LTC Positives': vals[1],
            'LTC Recovered': vals[2],
            'LTC Deaths': vals[3],
        }
    except Exception as e:
        print('issue reading LTC data {}'.format(e))

    print(data)
    return data
