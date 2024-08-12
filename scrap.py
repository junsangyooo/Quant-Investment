from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from io import StringIO
import pandas as pd
import time
import os

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
    url = st.getUrl()

    # Set up the directory where the script is running as the download directory
    current_directory = os.getcwd()

    # Selenium Setting
    chrome_options = Options()
    prefs = {
        "download.default_directory": current_directory,  # Set the download directory to current directory
        "download.prompt_for_download": False,
        "directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--headless")  # Run headless since there's no GUI in Codespaces
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize WebDriver with the Chrome options
    driver = webdriver.Chrome(options=chrome_options)
    #driver = webdriver.Chrome()
    driver.get(url)
    
    # Wait for the "Time Period" button to be clickable and click it
    time_period_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "tertiary-btn.fin-size-small.menuBtn.rounded.yf-122t2xs"))
    )
    time_period_button.click()

    # Wait for the menu to appear and the "Max" button to be clickable
    max_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='Max']"))
    )
    max_button.click()

    # Wait for the download button to be clickable and click it
    download_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@data-ylk='elm:download;elmt:link;itc:1;sec:qsp-historical;slk:history-download;subsec:download']"))
    )
    download_button.click()

    # Wait for the file to be downloaded
    time.sleep(10)

    # Close the browser
    driver.quit()


indList = ['Technology']
stocks = getStock(indList)
getHistoricalData(stocks[0])