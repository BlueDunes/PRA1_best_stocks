# PRA1_best_stocks

## Description
This project was created as part of the course "Tipologia i cicle de vida de les dades" (Master's Degree in Data Science - Universitat Oberta de Catalunya).
The objective is to figure out which are the bests stocks according to the best fund managers. 
In order to achieve that objective, we extracted first a list of the funds with the highest 10-year returns. Then, we selected the ones that had a higher return than the NASDAQ and collected a list of the main stocks they invest in. We oredered the stocks according to the amount of appearances and collected some of the main parameters related to each of them.  Finally, we generated a dataframe with the information.

## Team members
- Jaume Antolí
- Maria Dupla

## Files included in the repository
- Memoria_PRA1_jantolip_mduplag.pdf: Details about the process followed and the content of the project.
- BEST STOCKS.py: code that executes the different web scraping procedures and generates the final dataset with the selected stocks.
- LICENSE: document with the license.
- best_stocks.csv: dataset with the selected stocks.

## The final dataset can be found here
https://doi.org/10.5281/zenodo.5648614

## Libraries needed in order to run the code
- requests
- BeautifulSoup
- pandas
- numpy
- yfinance
- datetime
- fuzzywuzzy

## Resources
- Subirats, L., Calvo, M. (2018). Web Scraping. Editorial UOC.
- Morningstar https://www.morningstar.es/es/
- Yahoo Finance https://finance.yahoo.com/
- Wikipedia  
    https://en.wikipedia.org/wiki/List_of_S%26P_500_companies  
    https://en.wikipedia.org/wiki/Nasdaq-100
