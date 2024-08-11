from bs4 import BeautifulSoup
import requests
import pandas as pd

class stock:
    def __init__(self, sym, name, industry):
        self.sym = sym
        self.name = name
        self.link = 'https://finance.yahoo.com/quote/' + sym + '/'
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

def getIndustries():
    response = requests.get(BASEURL + 'stocks/industry/sectors/')
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    elements = soup.find('tbody').find_all('tr', class_='svelte-qmv8b3')
    industries = {}
    for element in elements:
        element = element.find('td', class_='svelte-qmv8b3')
        industry = element.find('a').text
        url = element.find('a', href=True).get('href')
        industries[industry] = url
    return industries

def getStock():
    stocks = []
    industries = getIndustries()
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