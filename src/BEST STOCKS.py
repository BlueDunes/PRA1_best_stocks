# -*- coding: utf-8 -*-

print("\nBEST STOCKS\n")

# Importem les llibreries necessàries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import datetime as dt
from fuzzywuzzy import process

# Definim headers
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,\
    */*;q=0.8",
    "Accept-Encoding": "gzip, deflate, sdch, br",
    "Accept-Language": "en-US,en;q=0.8,es-ES;q=0.5,es;q=0.3",
    "Cache-Control": "no-cache",
    "dnt": "1",
    "Pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:93.0)\
    Gecko/20100101 Firefox/93.0"
}

# Recopilem els identificadors corresponents a cada fons
print("1) Recopilant els identificadors dels fons a Morningstar\n")

index = []

for p in range(1, 9): # max 9 (en teoria 931)
    url = 'https://lt.morningstar.com/api/rest.svc/klr5zyak8x/security/screener?page=' + str(p) + '&pageSize=50&sortOrder=ReturnM120%20desc&outputType=json&version=1&languageId=es-ES&currencyId=EUR&universeIds=FOESP%24%24ALL&securityDataPoints=SecId%7CName%7CPriceCurrency%7CTenforeId%7CLegalName%7CClosePrice%7CYield_M12%7CCategoryName%7CAnalystRatingScale%7CStarRatingM255%7CQuantitativeRating%7CSustainabilityRank%7CReturnD1%7CReturnW1%7CReturnM1%7CReturnM3%7CReturnM6%7CReturnM0%7CReturnM12%7CReturnM36%7CReturnM60%7CReturnM120%7CFeeLevel%7CManagerTenure%7CMaxDeferredLoad%7CInitialPurchase%7CFundTNAV%7CEquityStyleBox%7CBondStyleBox%7CAverageMarketCapital%7CAverageCreditQualityCode%7CEffectiveDuration%7CMorningstarRiskM255%7CAlphaM36%7CBetaM36%7CR2M36%7CStandardDeviationM36%7CSharpeM36%7CTrackRecordExtension&filters=&term=&subUniverseId='
    req = requests.get(url, headers=headers)
    jsonlist = req.json()

    for i in jsonlist['rows']:
        index.append(i['SecId'])


# Fem scraping de la informació de cada fons
print("2) Obtenint la informació de cada fons\n")

n = 200 # quantitat d'index dels que volem fer scraping
index = index[:n]

ten_years_list = []
stocks_list = []

for ind in index:
    url = "https://www.morningstar.es/es/funds/snapshot/snapshot.aspx?id="+ind
 
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    ret = soup.find_all("td", class_="value number")
    returns = []
    for i in ret:
        returns.append(i.text)

    sto = soup.find_all("a", class_="holdingLink")
    stocks = []
    for i in sto:
        stocks.append(i.text)

    if len(returns) > 3 and returns[3] != "-":      
        ten_years_return = float(returns[3].replace(",", "."))
        ten_years_list.append(ten_years_return)
    else:
        ten_years_list.append(np.nan)
    
    if len(stocks) > 0:
        stocks_list.append(stocks)
    else: 
        stocks_list.append(np.nan)
    
# Generem dataframe amb la informació obtinguda
new_df = pd.DataFrame()
new_df["ten years return"] = ten_years_list
new_df["stocks"] = stocks_list

# Càlcul del rendiment anualitzat del Nasdaq als darrers 10 anys
today = datetime.today()
initial = today - dt.timedelta(days=3652)

today = today.strftime('%Y-%m-%d')
initial = initial.strftime('%Y-%m-%d')

ndx = yf.download("NDX", start=initial, end=today, progress=False)

inicial = ndx["Adj Close"][0]
final = ndx["Adj Close"][-1]

nasdaq_return = ((final/inicial)**(1/10)-1)*100

# Filtrem per fons que hagin superat al Nasdaq durant els darrers 10 anys
new_df = new_df[new_df["ten years return"] > nasdaq_return].dropna()

# Generem llista d'accions que apareixen en els fons que superen al Nasdaq
print("3) Generant la llista de les accions que apareixen als fons que superen al Nasdaq\n")

lista_stocks = []
for i in new_df["stocks"]:
    lista_stocks = lista_stocks + i

# Comptem les aparicions de cada acció
unique = np.unique(lista_stocks)

aparicions = []
for i in unique:
    aparicions.append(lista_stocks.count(i))
    
resultat = pd.DataFrame()

resultat["stock"] = unique
resultat["appearances"] = aparicions
resultat = resultat.sort_values("appearances", ascending=False)

# Filtrem les accions que apareixen més de 5 cops
limit = 5

resultat = resultat[resultat["appearances"]>limit]

# Definim una funció per convertir els noms de les accions els tickers que les identifiquen
print("4) Obtenint el ticker que identifica a cada acció\n")

def yf_tickers(x):
    company_ndx = list(pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100')[3]["Company"])
    ticker_ndx = list(pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100')[3]["Ticker"])
    
    company_sp = list(pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]["Security"])
    ticker_sp = list(pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]["Symbol"])
    
    company_unknown = ["Snap Inc Class A", "Snowflake Inc Ordinary Shares - ...", "Square Inc Class A",
                        "Cloudflare Inc", "Laboratory Corp of America Holdings", "Synaptics Inc",
                        "Veeva Systems Inc Class A", "Taiwan Semiconductor Manufacturi...",
                        "Twilio Inc Class A", "HDFC Bank Ltd", "Uber Technologies Inc",
                        "Shopify Inc Registered Shs -A- S..."]
    ticker_unknown = ["SNAP", "SNOW", "SQ", "NET", "LH", "SYNA", "VEEV", "TSM", "TWLO", "HDB", "UBER", "SHOP"]
    
    company = company_ndx + company_sp + company_unknown
    ticker = ticker_ndx + ticker_sp + ticker_unknown

    dic = pd.DataFrame()
    dic["company"] = company
    dic["ticker"] = ticker

    ratio = process.extract(x ,company)
    
    if ratio[0][1] >= 90:
        highest = process.extractOne(x ,company)
        yf_ticker = dic[dic["company"]==highest[0]]["ticker"].tolist()
        return yf_ticker[0]
    else:
        return "-"

# Obtenim el ticker de cada acció
tickers = []

for stock in resultat["stock"]:
    ticker = yf_tickers(stock)
    tickers.append(ticker)

resultat["ticker"] = tickers

# Netejem valors que no són vàlids
delete = resultat['ticker'].str.match(r'-')
resultat = resultat[~delete]

# Obtenim informació a Yahoo Finance de cada acció
print("5) Obtenint informació de cada acció a Yahoo Finance\n")

previous_close= []
fiftytwo_weeks_range = []
volume = []
avg_volume = []

for ticker in resultat["ticker"]:
    url = "https://finance.yahoo.com/quote/" + ticker
    data = requests.get(url).text
    soup = BeautifulSoup(data, 'html.parser')

    table = soup.find_all('table')[0]

    data = table.find_all('tr')

    data_list = []

    for row in data:
        text = row.find_all('td')[1]
        data_list.append(text.text)

    previous_close.append(data_list[0])
    fiftytwo_weeks_range.append(data_list[5])
    volume.append(data_list[6])
    avg_volume.append(data_list[7])

resultat["previous close"] = previous_close
resultat["fiftytwo weeks range"] = fiftytwo_weeks_range
resultat["volume"] = volume
resultat["avg. volume"] = avg_volume

beta = []
per = []
one_year_target = []

for ticker in resultat["ticker"]:
    url = "https://finance.yahoo.com/quote/" + ticker
    data = requests.get(url).text
    soup = BeautifulSoup(data, 'html.parser')

    table = soup.find_all('table')[1]

    data = table.find_all('tr')

    data_list = []

    for row in data:
        text = row.find_all('td')[1]
        data_list.append(text.text)

    beta.append(data_list[1])
    per.append(data_list[2])
    one_year_target.append(data_list[7])
    
resultat["beta"] = beta
resultat["per"] = per
resultat["1y target"] = one_year_target

# Guardem el dataset resultant
print("6) Guardant el dataset resultant\n")

resultat.to_csv("best_stocks.csv", index = False)

print("By Jaume Antolí & Maria Dupla")

