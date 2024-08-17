from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime, timedelta, date
import os
from io import StringIO
import pandas as pd

class stock:
    def __init__(self, sym, name, industry):
        self.sym = sym
        self.name = name
        self.link = 'https://finance.yahoo.com/quote/' + sym + '/history/'
        self.industry = industry
    def getSym(self):
        return self.sym
    def getName(self):
        return self.name
    def getUrl(self):
        return self.link
    def getIndustry(self):
        return self.industry

BASEURL = 'https://stockanalysis.com/'
yahooURL = 'https://finance.yahoo.com/quote/'

DEBUG = False

def getIndustries(indList = None):
    industries = {}
    response = requests.get(BASEURL + 'stocks/industry/sectors/')
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    elements = soup.find('tbody').find_all('tr', class_='svelte-qmv8b3')
    for element in elements:
        element = element.find('td', class_='svelte-qmv8b3')
        industry = element.find('a').text
        if indList == None or industry in indList:
            industries[industry] = element.find('a', href=True).get('href')
    return industries

def getStock(indList = None):
    stocks = []
    industries = getIndustries(indList)
    for industry, url in industries.items():
        response = requests.get(BASEURL + url)
        html = response.text

        soup = BeautifulSoup(html, 'html.parser')
        body = soup.find('tbody')
        elements = body.find_all('tr', class_='svelte-eurwtr')
        for element in elements:
            sym = element.find('td', class_='sym svelte-eurwtr').find('a').text.replace('.','-')
            name = element.find(class_='slw svelte-eurwtr').text
            stocks.append(stock(sym,name,industry))
    return stocks

def getHistoricalData(st):
    # Set up the directory where the script is running as the download directory
    currentDirectory = os.getcwd()
    downloadDirectory = os.path.join(currentDirectory, 'stock_data')

    # Create the download directory if it doesn't exist
    if not os.path.exists(downloadDirectory):
        os.makedirs(downloadDirectory)

    # Selenium Setting
    chromeOptions = Options()
    prefs = {
        "download.default_directory": downloadDirectory,  # Set the download directory to current directory
        "download.prompt_for_download": False,
        "directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chromeOptions.add_experimental_option("prefs", prefs)
    chromeOptions.add_argument("--headless")  # Run headless since there's no GUI in Codespaces
    chromeOptions.add_argument("--no-sandbox")
    chromeOptions.add_argument("--disable-dev-shm-usage")

    # Initialize WebDriver with the Chrome options
    driver = webdriver.Chrome(options=chromeOptions)

    url = st.getUrl()
    sym = st.getSym()

    # Construct the path to the CSV file
    filePath = os.path.join(downloadDirectory, f'{sym}.csv')

    # Check if the CSV file already exists
    if os.path.exists(filePath):
        print(f"File {sym}.csv already exists. Skipping download.")
        return
    
    #driver = webdriver.Chrome()
    driver.get(url)
    
    # Wait for the "Time Period" button to be clickable and click it
    periodButton = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "tertiary-btn.fin-size-small.menuBtn.rounded.yf-122t2xs"))
    )
    periodButton.click()

    # Wait for the menu to appear and the "Max" button to be clickable
    maxButton = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='Max']"))
    )
    maxButton.click()

    # Wait for the download button to be clickable and click it
    downloadButton = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@data-ylk='elm:download;elmt:link;itc:1;sec:qsp-historical;slk:history-download;subsec:download']"))
    )
    downloadButton.click()
    
    # Wait for the file to be downloaded
    while(True):
        time.sleep(0.5)
        if os.path.exists(filePath): break
    print(f'{sym}.csv file is successfully downloaded.')

    # Close the browser
    driver.quit()

# indList = ['Technology']
# stocks = getStock(indList)
# for st in stocks:
#     getHistoricalData(st)

# Change for your environment
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def updateDatas():
    currentDir = os.getcwd()
    dataDir = os.path.join(currentDir, 'stock_data')
    
    endDate = datetime.combine(date.today(), datetime.min.time())
    for filename in os.listdir(dataDir):
        df = pd.read_csv(os.path.join(dataDir, filename))
        startDate = datetime.strptime(df.iloc[-1]['Date'],"%Y-%m-%d") + timedelta(days=1)
        if DEBUG:
            print(f"Start date is: {startDate}, and its type is {type(startDate)}")
            print(f"End date is: {endDate}, and its type is {type(endDate)}")

        if startDate >= endDate: continue
        startDateEpochTime = int(time.mktime(startDate.timetuple()))
        endDateEpochTime = int(time.mktime(endDate.timetuple()))

        sym = filename.split('.')[0]
        href=f"https://query1.finance.yahoo.com/v7/finance/download/{sym}?period1={startDateEpochTime}&period2={endDateEpochTime}&interval=1d&events=history&includeAdjustedClose=true"
        if DEBUG: print(href)

        # Fetch the CSV data from the URL without saving it to disk
        response = requests.get(href, headers=headers)
        print(filename)
        if response.status_code == 200:
            updateData = StringIO(response.text)
            updateDf = pd.read_csv(updateData)
            
            # Concatenate the new data with the existing DataFrame
            df = pd.concat([df, updateDf], ignore_index=True)
            # Save the updated DataFrame back to the CSV file
            with open(os.path.join(dataDir, filename), 'w', newline='') as csvfile:
                df.to_csv(csvfile, index=False)
            
            if DEBUG:
                print(f"Updated data for {sym} has been saved to {filename}")
        else:
            if DEBUG:
                print(f"Failed to fetch data for {sym}. HTTP Status Code: {response.status_code}")



updateDatas()