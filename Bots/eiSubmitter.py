# from selenium import webdriver
from base64 import b64decode
import json
from selenium.common.exceptions import TimeoutException
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from notify_run import Notify 
import csv
import time
import undetected_chromedriver as uc
from fake_headers import Headers
import os
import sys
#Custom class from custom py code in same directory
from sendGmail import gmailObject
from readGmail import readLastGmail
from uDecrypter import uDecrypter

EIDates = []
newDates= []
SSFilenames = []
count = 0
pathScreenshots = os.path.dirname(__file__)+'\\screenshots'

#Android notifier object variable
notify = Notify()

#readGmail variables
folder = 'Special'
PKey = os.environ.get('PKEY')

#Opens csv file to get EI payment date history to date. 
file = '\\EISubmissions.csv'
pathEDates = os.path.dirname(__file__)+file

with open(pathEDates) as csvfile:
    EIFile = csv.reader(csvfile)  
    for row in EIFile:
        EIDates.append(row[0])

#Declare browser driver and navigate to the website. Set headless options so that sites will show in a standard fashion in headless and not break code.
chromeOptions = uc.ChromeOptions()
chromeOptions.add_argument('–headless')
chromeOptions.add_argument("--window-size=1920,1080")
chromeOptions.add_argument('--ignore-certificate-errors')
chromeOptions.add_argument('--allow-running-insecure-content')
chromeOptions.add_argument('--no-sandbox')
#This portion generates fake headers and user agent for use with headless chrome. Bank bot detection will block headless chrome otherwise.
header = Headers(
    browser="chrome",  # Generate only Chrome UA
    os="win",  # Generate only Windows platform
    headers=False # generate misc headers
)
customUserAgent = header.generate()['User-Agent']
chromeOptions.add_argument(f'--user-agent={customUserAgent}')

driver = uc.Chrome(options=chromeOptions)

driver.get('https://www.canada.ca/en/employment-social-development/services/my-account.html')
assert 'Service Canada' in driver.title

def findElem(ByMode, searchString, wait = 5, multi = False):
    '''Wrapper for combination of WebDriverWait until Element(s) are visible and find Element By.'''
    try:
        if multi:
            elem = WebDriverWait(driver, wait).until(
            EC.visibility_of_all_elements_located((ByMode, searchString))
            )
        else:
            elem = WebDriverWait(driver, wait).until(
            EC.presence_of_element_located((ByMode, searchString))
            )
        return elem
    except TimeoutException as timeError:
        print(f'{searchString} element was not found')
        return None

try:
    #Interac Sign-In Button
    findElem(By.PARTIAL_LINK_TEXT, 'bank Sign-In').click()
    #TD Button
    findElem(By.ID, 'TD').click()
    #TD User/Pass Fields
    userElem = findElem(By.ID, 'username')
    passElem = findElem(By.ID, 'uapPassword')
    userElem.send_keys(os.environ.get('BU'))
    passElem.send_keys(os.environ.get('BP'))
    
    '''Had to use undetected chrome driver to get beyond login button. Current version of UC needed modification to not double invoke process.kill twice by moving
    quit() invocation inside except block as opposed to be invoked every time after try in __init__.py for the UC'''
    #TD Login Button
    findElem(By.CSS_SELECTOR, 'button.td-button-secondary').click()
    
    '''This if statement is here because it's possible TD has already validated your SMS code on their end so they don't send another two factor auth.
    If you don't need to go through the two factor auth from TD, then you'll be sent directly to two factor auth for Service Canada.'''
    #TD Two Factor Auth Send SMS Button
    TDAuthElem = findElem(By.XPATH, '//button[text()="Text me "]')
    #If the TD send SMS button is found then continue with TD authentication. If not, then continue to Service Canada. 
    if TDAuthElem:
        TDAuthElem.click()
        #Wait for email to arrive, Print SMS code countdown to console on one line. 15 second default.
        for i in range(6,0,-1):
            sys.stdout.write(str(i)+' ')
            sys.stdout.flush()
            time.sleep(1)
        codeTD = uDecrypter(readLastGmail(os.environ.get('GU'),os.environ.get('GP'),folder, delLast=True),PKey)
        codeFieldTD = findElem(By.ID, 'code')
        codeFieldTD.send_keys(codeTD)
        #Submit TD SMS Code Button, waits 1 second just in case the field being filled out lags.
        time.sleep(1)
        findElem(By.XPATH, '//*[@id="mat-dialog-1"]/core-otp-challenge-modal/span/div[2]/form/button').click()
    else: 
        print(f'TD did not request two factor auth or possibly blocked bot. Continuing to Service Canada portion.')
    
    #Service Canada Two Factor Auth Send SMS Button
    findElem(By.NAME, 'ctl00$ctl00$MainContent$ContentPlaceHolder$btnSendOTP').click()
    #Wait for email to arrive and read it. Print SMS code countdown to console on one line. 15 second default.
    for i in range(6,0,-1):
        sys.stdout.write(str(i)+' ')
        sys.stdout.flush()
        time.sleep(1)
    codeSC = uDecrypter(readLastGmail(os.environ.get('GU'),os.environ.get('GP'),folder, delLast=True),PKey)
    codeFieldSC = findElem(By.ID, 'txtMFASMSCode')
    codeFieldSC.send_keys(codeSC) 
    #Submit SMS Code Button, waits 1 second just in case the field being filled out lags.
    time.sleep(1)
    findElem(By.ID, 'MainContent_ContentPlaceHolder_btnSubmitSMSCode').click()
    #Employment Insurance Page Button
    findElem(By.ID, 'employment-insurancetest-card-button-').click()
    #Payment Info Button
    # findElem(By.XPATH, '/html/body/main/section[2]/div/div[2]/div[2]/div/ul/li[5]/a').click()
    findElem(By.PARTIAL_LINK_TEXT, 'payments').click()
    #Find all Service Canada row text elements that are in tableID 'CurrentData' under header 'Report Covering Period. Returns a list.'
    tableElems = findElem(By.XPATH, '//table[@id="CurrentData"]/tbody/tr/td[count(//table/tbody/tr/th[.=" Report Covering Period "]/preceding-sibling::th)+1]', multi = True)   
    #Compare each date in Service Canada table list to set containing all dates in EISubmissions.csv. This set was originally extracted at beginning of program from same file.
    for row in tableElems:
        #print(f'Row Count: {count}')            
        if row.text not in set(EIDates):
            # print(f'EIDates: {EIDates[count]} \nDate Added: {row.text}')
            newDates.append(row.text)
            EIDates.insert(count,row.text)
        count += 1
    #Write new dates to csv file.
    if newDates:
        with open('C:\\Users\\shent\\OneDrive\\Desktop\\Coding Stuff\\Python Stuff\\Projects\\Bots\\EISubmissions.csv','w',newline="" ) as csvfile:
            print('Writing Dates to File')
            EIFile = csv.writer(csvfile)
            for row in EIDates:
                EIFile.writerow([row])
        #Click new date link in Service Canada table, save screenshot and go back to repeat with next new date.
        for row in newDates:
            findElem(By.PARTIAL_LINK_TEXT, row).click()
            print(f'Saved pdf: {row}.pdf')

            #Get b64 code for print to pdf of current page
            a = driver.execute_cdp_cmd(
                "Page.printToPDF", {"path": 'html-page.pdf', "format": 'A4'})
            # Define the Base64 string of the PDF file
            b64 = a['data']

            # Decode the Base64 string, making sure that it contains only valid characters
            bytes = b64decode(b64, validate=True)
            # Perform a basic validation to make sure that the result is a valid PDF file
            # Be aware! The magic number (file signature) is not 100% reliable solution to validate PDF files
            # Moreover, if you get Base64 from an untrusted source, you must sanitize the PDF contents
            if bytes[0:4] != b'%PDF':
                raise ValueError('Missing the PDF file signature')

            # Write the PDF contents to a local file
            with open(f'{pathScreenshots}//{row}.pdf', 'wb') as f:
                f.write(bytes)

            SSFilenames.append(f'{pathScreenshots}\\{row}.pdf')
            driver.execute_script("window.history.go(-1)")

        #Send email with EI payment information if new dates exist.
        subject = f'PREGNANCY & PARENTAL TOP UPS {os.environ.get('COTName')} {os.environ.get('COTENum')}'
        body = 'Hi there please see below statements for processing\n\nThanks,\n\nTim.'
        email =  gmailObject(os.environ.get('GU'), os.environ.get('GP'), os.environ.get('GU'), os.environ.get('COTSubE'), subject, body, files = SSFilenames) 
        email.send()
        notify.send(f'EI Submission Email: Sent {len(newDates)} new dates')
    else:
        print('No email sent because there are no new dates.')
        notify.send('EI Submission Email: No new dates')

except Exception as e:
    print(e)
    #Save a screenshot of the page when an error occurs to inspect when using headless chrome. It's saved in same screenshots folder as EI statements. 
    driver.save_screenshot(f'{pathScreenshots}\\error.png')
    notify.send('EI Submitter Broke')

finally:
    driver.quit()
    #pass