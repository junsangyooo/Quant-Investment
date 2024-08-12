from bs4 import BeautifulSoup
from selenium import webdriver
import requests
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
    def getLink(self):
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
    

