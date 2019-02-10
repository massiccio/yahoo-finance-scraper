# yahoo-finance-scraper
Python 2.7 utility that scrapes data of stocks belonging to the S&amp;P 500 index from Yahoo Finance.

# Background
Tools such as [Finviz](https://finviz.com/) let you create screeners to identify certain stocks, e.g., potentially undervalued ones. Unfortunately those tools do not let you download data. With that in mind I have written this program that downloads the following data from Yahoo Finance:
1. Ticker
2. Current Price
3. 5-year PEG ratio
4. Trailing P/E ratio
5. Forward P/E ratio
6. Beta
7. Enterprise Value/EBITDA
8. 52-week Change
9. 52-week Change Compared to S&P 500
10. Short % of Float
11. Profit Margin %
12. Quarterly Earnings Growth (yoy)
13. Quarterly Revenue Growth (yoy)
14. Return on Assets (ttm)
15. Return on Equity (ttm)
16. Total Cash
17. Total Debt
18. Target price estimate (low)
19. Target price estimate (average)
20. Target price estimate (median)
21. Target price estimate (high)



# Usage
```
python yahoo-finance-scraper.py --help
usage: yahoo-finance-scraper.py [options]

Get data about the S&P 500 companies.

optional arguments:
  -h, --help            show this help message and exit
  --all_tickers         Download data for all companies whose ticker is specified in the -i option [default: true].
  --ticker TICKER       Download data for "ticker" only.
  -d, --download_index  Download list of all S&P 500 compononents from Wikipedia [default: false].
  -i INPUT, --input INPUT
                        File containing the tickers, in CSV format. Tickers are in the 1st column [default: ./tickers.csv].                         You can have any ticker available in Yahoo finance here, not only those of companies belonging to                           the S&P 500 index.
  -o OUTPUT, --output OUTPUT
                        File where results are stored, in CSV format [default: ./result.csv].
  -a, --append          Do no create header [Default: false].
  -p PAUSE, --pause PAUSE
                        Interval between requests to Yahoo Finance [default: 4 seconds]. Without a pause between requests,                           Yahoo Finance will bounce queries.
  -t REQUEST_TIMEOUT, --request_timeout REQUEST_TIMEOUT
                        Timeout for Yahoo Finance requests [default: 1 second]. The timeout value will be applied to both                           the connect and the read timeouts.
                        Please refer to http://docs.python-requests.org/en/master/user/advanced/#timeouts for more details.
```

# Prerequisites
The following libraries are used:
1. [Requests](http://docs.python-requests.org/en/master/)
2. [Pandas](https://pandas.pydata.org/)
3. [lxml](https://lxml.de/)
