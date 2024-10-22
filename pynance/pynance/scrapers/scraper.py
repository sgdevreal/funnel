# your_library/scrapers/nyse_scraper.py
import requests
from bs4 import BeautifulSoup
from ..ticker import Ticker

def scrape_nyse_tickers(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    tickers = []
    
    # Scraping logic for NYSE
    ticker_elements = soup.find_all('div', class_='nyse-ticker-row')
    
    for ticker_element in ticker_elements:
        symbol = ticker_element.find('span', class_='symbol').text
        name = ticker_element.find('span', class_='name').text
        price = float(ticker_element.find('span', class_='price').text)
        tickers.append(Ticker(symbol, name, price))
    
    return tickers