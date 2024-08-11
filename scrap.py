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

baseUrl = 'https://stockanalysis.com/stocks/'

def getIndustries():
    response = requests.get(baseUrl + 'industry/sectors/')
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    elements = soup.find('tbody').find_all('td', class_='svelte-qmv8b3')
    print(len(elements))
    industries = {}
    for element in elements:
        industry = element.find('a').text
        url = element.find('a', href=True)
        industries[industry] = url
    return industries

print(getIndustries())