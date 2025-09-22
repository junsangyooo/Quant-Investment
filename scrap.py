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

INDUSTRIES = { 'Financials': 'https://stockanalysis.com/stocks/sector/financials/', 
              'Healthcare':'https://stockanalysis.com/stocks/sector/healthcare/', 
              'Technology':'https://stockanalysis.com/stocks/sector/technology/', 
              'Industrials':'https://stockanalysis.com/stocks/sector/industrials/', 
              'Consumer Discretionary':'https://stockanalysis.com/stocks/sector/consumer-discretionary/', 
              'Materials':'https://stockanalysis.com/stocks/sector/materials/', 
              'Real Estate':'https://stockanalysis.com/stocks/sector/real-estate/', 
              'Communication Services':'https://stockanalysis.com/stocks/sector/communication-services/',
              'Energy':'https://stockanalysis.com/stocks/sector/energy/', 
              'Consumer Staples':'https://stockanalysis.com/stocks/sector/consumer-staples/', 
              'Utilities':'https://stockanalysis.com/stocks/sector/utilities/'}

# Change for your environment
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

DEBUG = False

# recieve parameters and web scrap the historical data of it
# getHistoricalData(sym, url) -> save 'sym.csv' file to /cwd/stock_data
def getHistoricalData(sym, url):
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
   driver = webdriver.Chrome(executable_path="./chromedriver", options=chromeOptions)


    # Construct the path to the CSV file
    filePath = os.path.join(downloadDirectory, f'{sym}.csv')

    # Check if the CSV file already exists
    if os.path.exists(filePath):
        print(f"File {sym}.csv already exists. Skipping download.")
        return
    
    if DEBUG:
        print(f'driver.get({url})')
    driver.get(url)
    
    # Wait for the "Time Period" button to be clickable and click it
    periodButton = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "tertiary-btn.fin-size-small.menuBtn.rounded.yf-122t2xs"))
    )
    if DEBUG:
        print(" click a periodButton")
    periodButton.click()

    # Wait for the menu to appear and the "Max" button to be clickable
    maxButton = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='Max']"))
    )
    if DEBUG:
        print("click a maxButton")
    maxButton.click()

    # Wait for the download button to be clickable and click it
    downloadButton = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@data-ylk='elm:download;elmt:link;itc:1;sec:qsp-historical;slk:history-download;subsec:download']"))
    )
    if DEBUG:
        print("click a downloadButton")
    downloadButton.click()
    
    # Wait for the file to be downloaded
    while(True):
        time.sleep(0.5)
        if os.path.exists(filePath): break
    print(f'{sym}.csv file is successfully downloaded.')

    # Close the browser
    driver.quit()

# recieve the list of industries, scrap stock's symbol in the industry, and send symbol and link to getHistoricalData
# getStock([industries]) -> getHistoricalData(stock)
def getStock(indList):
    for industry in indList:
        url = INDUSTRIES[industry]
        response = requests.get(url)
        html = response.text

        soup = BeautifulSoup(html, 'html.parser')
        body = soup.find('tbody')
        elements = body.find_all('tr', class_='svelte-eurwtr')
        for element in elements:
            sym = element.find('td', class_='sym svelte-eurwtr').find('a').text.replace('.','-')
            #name = element.find(class_='slw svelte-eurwtr').text
            link = 'https://finance.yahoo.com/quote/' + sym + '/history/'
            if DEBUG:
                print(f'call getHistoricalData({sym}, {link})')
            getHistoricalData(sym, link)

# update all csv files in the stock_data for most recent datas
def updateDatas():
    currentDir = os.getcwd()
    dataDir = os.path.join(currentDir, 'stock_data')
    
    endDate = datetime.combine(date.today(), datetime.min.time())
    for filename in os.listdir(dataDir):
        df = pd.read_csv(os.path.join(dataDir, filename))
        lastUpdatedDate = datetime.strptime(df.iloc[-1]['Date'],"%Y-%m-%d")
        if lastUpdatedDate >= endDate: continue
        startDate = lastUpdatedDate + timedelta(days=1)
        if DEBUG:
            print(f"Start date is: {startDate}, and its type is {type(startDate)}")
            print(f"End date is: {endDate}, and its type is {type(endDate)}")
        
        startDateEpochTime = int(time.mktime(startDate.timetuple()))
        endDateEpochTime = int(time.mktime(endDate.timetuple()))

        sym = filename.split('.')[0]
        href=f"https://query1.finance.yahoo.com/v7/finance/download/{sym}?period1={startDateEpochTime}&period2={endDateEpochTime}&interval=1d&events=history&includeAdjustedClose=true"
        if DEBUG: print(href)

        # Fetch the CSV data from the URL without saving it to disk
        response = requests.get(href, headers=headers)
        if DEBUG:
            print(filename)
        if response.status_code == 200:
            updateData = StringIO(response.text)
            updateDf = pd.read_csv(updateData)
            
            # Concatenate the new data with the existing DataFrame
            df = pd.concat([df, updateDf], ignore_index=True)

            # Check duplicates
            originLen = len(df)
            df.drop_duplicates(inplace=True)
            afterLen = len(df)
            if originLen != afterLen:
                print(f"Duplicates found and removed in {filename}:  {originLen - afterLen} date duplicates.")

            # Save the updated DataFrame back to the CSV file
            df.to_csv(os.path.join(dataDir, filename), index=False)
            print(f"Updated data for {sym} has been saved to {filename}")
        else:
            print(f"Failed to fetch data for {sym}. HTTP Status Code: {response.status_code}")

def main():
    # If I need to scrap the historical datas of new stocks in specific industry, run below
    # intList = ['Financials', 'Healthcare', 'Technology', 'Industrials', 'Consumer Discretionary', 
    # 'Materials', 'Real Estate', 'Communication Services', 'Energy', 'Consumer Staples', 'Utilities']
    # indList = ['Communication Services'] 
    # getStock(indList)
    
    # Everyday please run below once
    updateDatas()

if __name__ == "__main__": updateDatas()