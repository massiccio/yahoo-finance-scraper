from lxml import html
import requests
from time import sleep
from collections import OrderedDict
import csv
import argparse
import os
import logging

import urllib3
urllib3.disable_warnings()

import pandas as pd
import sys

# File where the tickers downloaded from Wikipedia are stored
TICKERS = 'tickers.csv'

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

def __init_dict(ticker):
    '''
    Cretes a dict object.
    '''

    summary_data = OrderedDict()
    summary_data['ticker'] = ticker

    summary_data['current_price'] = 'NA'
    summary_data['PEG_5y'] = 'NA'
    summary_data['trailing_pe'] = 'NA'
    summary_data['forward_pe'] = 'NA'
    summary_data['beta'] = 'NA'
    summary_data['enterprise_to_ebitda'] = 'NA'

    summary_data['52_week_change_pct'] = 'NA'
    summary_data['SPY_52_week_change_pct'] = 'NA'

    summary_data['short_pct_of_float'] = 'NA'

    summary_data['profit_margins_pct'] = 'NA'
    summary_data['earnings_growth_pct'] = 'NA'
    summary_data['revenue_growth_pct'] = 'NA'

    summary_data['ROA_pct'] = 'NA'
    summary_data['ROE_pct'] = 'NA'

    summary_data['total_cash_bn'] = 'NA'
    summary_data['total_debt_bn'] = 'NA'
    summary_data['total_revenue_bn'] = 'NA'

    summary_data['target_low_price'] = 'NA'
    summary_data['target_mean_price'] = 'NA'
    summary_data['target_median_price'] = 'NA'
    summary_data['target_high_price'] = 'NA'

    return summary_data


def _parse_data(ticker, json_string):
    '''
    Parse the data from JSON.
    '''
    summary_data = __init_dict(ticker)

    try:
        summary_data['current_price'] = float(json_string["quoteSummary"]["result"][0]["financialData"]['currentPrice']['fmt'])
    except:
        pass

    try:
        summary_data['PEG_5y'] = float(json_string["quoteSummary"]["result"][0]["defaultKeyStatistics"]['pegRatio']['fmt'])
    except:
        pass

    try:
        summary_data['trailing_pe'] = round(summary_data['current_price'] / float(json_string["quoteSummary"]["result"][0]["defaultKeyStatistics"]['trailingEps']['fmt']), 2)
    except:
        pass

    try:
        summary_data['forward_pe'] =  float(json_string["quoteSummary"]["result"][0]["defaultKeyStatistics"]['forwardPE']['fmt'])
    except:
        pass
    try:
        summary_data['beta'] =  float(json_string["quoteSummary"]["result"][0]["defaultKeyStatistics"]['beta']['fmt'])
    except:
        pass

    try:
        summary_data['enterprise_to_ebitda'] =  float(json_string["quoteSummary"]["result"][0]["defaultKeyStatistics"]['enterpriseToEbitda']['fmt'])
    except:
        pass

    try:
        summary_data['52_week_change_pct'] =  round(float(json_string["quoteSummary"]["result"][0]["defaultKeyStatistics"]['52WeekChange']['raw']) * 100.0, 2)
    except:
        pass

    try:
        summary_data['SPY_52_week_change_pct'] = round(float(json_string["quoteSummary"]["result"][0]["defaultKeyStatistics"]['SandP52WeekChange']['raw']) * 100.0, 2)
    except:
        pass

    try:
        summary_data['short_pct_of_float'] = round(float(json_string["quoteSummary"]["result"][0]["defaultKeyStatistics"]['shortPercentOfFloat']['raw']) * 100.0, 2)
    except:
        pass

    try:
        summary_data['profit_margins_pct'] = round(float(json_string["quoteSummary"]["result"][0]["defaultKeyStatistics"]['profitMargins']['raw']) * 100.0, 2)
    except:
        pass

    try:
        summary_data['earnings_growth_pct'] =  round(float(json_string["quoteSummary"]["result"][0]["financialData"]['earningsGrowth']['raw']) * 100.0, 2)
    except:
        pass

    try:
        summary_data['revenue_growth_pct'] =  round(float(json_string["quoteSummary"]["result"][0]["financialData"]['revenueGrowth']['raw']) * 100.0, 2)
    except:
        pass

    try:
        summary_data['ROA_pct'] =  round(float(json_string["quoteSummary"]["result"][0]["financialData"]['returnOnAssets']['raw']) * 100.0, 2)
    except:
        pass

    try:
        summary_data['ROE_pct'] =  round(float(json_string["quoteSummary"]["result"][0]["financialData"]['returnOnEquity']['raw']) * 100.0, 2)
    except:
       pass

    try:
        summary_data['total_cash_bn']  = round(float(json_string["quoteSummary"]["result"][0]["financialData"]['totalCash']['raw']) / 10**9, 2)
    except:
        pass

    try:
        summary_data['total_debt_bn']  = round(float(json_string["quoteSummary"]["result"][0]["financialData"]['totalDebt']['raw']) / 10**9, 2)
    except:
        pass

    try:
        summary_data['total_revenue_bn']  = round(float(json_string["quoteSummary"]["result"][0]["financialData"]['totalRevenue']['raw']) / 10**9, 2)
    except:
        pass

    try:
        summary_data['target_low_price'] = round(float(json_string["quoteSummary"]["result"][0]["financialData"]['targetLowPrice']['raw']), 2)
    except:
        pass

    try:
        summary_data['target_mean_price'] = round(float(json_string["quoteSummary"]["result"][0]["financialData"]['targetMeanPrice']['raw']), 2)
    except:
        pass

    try:
        summary_data['target_median_price'] = round(float(json_string["quoteSummary"]["result"][0]["financialData"]['targetMedianPrice']['raw']), 2)
    except:
        pass

    try:
        summary_data['target_high_price'] = round(float(json_string["quoteSummary"]["result"][0]["financialData"]['targetHighPrice']['raw']), 2)
    except:
        pass

    return summary_data


class YahooFinanceScraper():
    '''
    Download data from Yahoo Finance
    '''

    def __init__(self, input, output, pause, timeout):
        '''
        type input: str (path of tickers file)
        type output: str (path of file where results are stored)
        type pause: int (interval between two consecutive requests to yahoo finance, in seconds)
        type timeout: int (timeout for HTTP requets, in seconds)
        '''
        self.input = input
        self.output = output
        self.pause = pause
        self.timeout = timeout

        if not os.access(self.input, os.R_OK):
            logging.warning('Unable to read {0}. Donwloading list of tickers from Wikipedia...'.format(self.input))
            get_tickers_from_wikipedia(self.input)


    def __count_rows(self):
        '''
        Count the number of rows.
        '''
        with open(self.input, 'r') as f:
            # the 1st line is a comment
            return sum(1 for line in f) - 1


    def download_all(self):
        '''
        Download data for all tickers.
        '''
        row_count = self.__count_rows() # count number of rows
        logging.info("Total {0} rows".format(row_count))

        with open(self.input, 'r') as tickers:
            csv_reader = csv.reader(tickers, delimiter=',')
            next(csv_reader, None)  # skip the headers

            counter = 0 # count number of processed tickers
            write_header = True # write header the 1st time only

            for row in csv_reader:
                ticker = row[0]
                if '.' in ticker: # e.g., Berkshire
                    logging.debug('Ticker {0}, replacing . with -'.format(ticker))
                    ticker = ticker.replace('.', '-')

                counter = counter + 1
                logging.info('{0}/{1}: downloading {2}...'.format(counter, row_count, ticker))
                try:
                    summary_data = self.download(ticker)
                    self.write_data_about_ticker(summary_data, write_header)
                    write_header = False
                except Exception, e:
                    logging.error("Error while downloading data for {0}: {1}".format(ticker, e))

                sleep(self.pause)


    def download(self, ticker):
        '''
        Download data about the specified ticker.
        type ticker: str
        '''
        url = "https://finance.yahoo.com/quote/{0}".format(ticker)
        response = requests.get(url, verify=False)

        parser = html.fromstring(response.text)
        summary_table = parser.xpath('//div[contains(@data-test,"summary-table")]//tr')
        summary_data = OrderedDict()

        other_details_json_link = "https://query2.finance.yahoo.com/v10/finance/quoteSummary/{0}?formatted=true&modules=financialData%2CdefaultKeyStatistics".format(ticker)
        json_response = requests.get(other_details_json_link, timeout = self.timeout)
        json_string = json_response.json()

        #parsed_json = json.dumps(json_string, sort_keys=True, indent=4) # print nicely
        return _parse_data(ticker, json_string)


    def write_data_about_ticker(self, summary_data, write_header):
        '''
        Write data to CSV.
        type summary data: dict
        type write_header: bool
        '''
        flag = 'w' if write_header else 'a' # open in write or append mode
        with open(self.output, flag) as f:
            w = csv.DictWriter(f, fieldnames = summary_data.keys())

            if write_header:
                w.writeheader()
            else:
                pass

            w.writerow(summary_data)


def get_tickers_from_wikipedia(save_to):
    '''
    Get list of S&P 500 components from Wikipedia
    '''
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies#S&P_500_Component_Stocks'
    l = pd.read_html (url)
    # store the result in a dataframe - you only need the first element, the table
    output = pd.DataFrame(l[0])

    # keep only columns: Security Symbol and GICS Sector
    output = output.drop(columns=[2, 4, 5, 6, 7, 8], axis=1)
    output = output[[1, 0, 3]] # swap order of ticker and company name
    output.to_csv(save_to, sep=',', encoding='utf-8',index=False, header=None)


# Main
if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Get data about the S&P 500 companies.', usage='%(prog)s [options]')
    parser.add_argument('--all_tickers', action='store_true', required = False, help = 'Download data for all companies [default: true].')
    parser.add_argument('--ticker', type = str, required = False, help = 'Download data for "ticker" only.')
    parser.add_argument('-d', '--download_index', action='store_true', required = False, help = 'Download list of all S&P 500 compononents [default: false].')
    parser.add_argument('-i', '--input', type = str, required = False, default=TICKERS, help = 'File containing the tickers, in CSV format. Tickers are in the 1st column [default: ./tickers.csv].')
    parser.add_argument('-o', '--output', type = str, required = False, default='result.csv', help = 'File where results are stored, in CSV format [default: ./result.csv].')
    parser.add_argument('-a', '--append', action='store_true', required = False, help = 'Do no create header [Default: false].')
    parser.add_argument('-p', '--pause', type = int, required = False, default = 4, help = 'Interval between requests to Yahoo Finance [default: 4 seconds].')
    parser.add_argument('-t', '--request_timeout', type = int, required = False, default = 1, help = 'Timeout for Yahoo Finance requests.')
    args = parser.parse_args()

    if args.all_tickers and args.ticker is not None:
        raise argparse.ArgymentTypeError('Invalid option: all-tickers and ticker cannot be used together.')

    dir_path = os.path.dirname(os.path.realpath(args.output))
    if not os.access(dir_path, os.W_OK):
        raise argparse.ArgumentTypeError('Unable to write to {0}'.format(dir_path))

    if args.download_index:
        logging.info("Downloading tickers from Wikipedia...")
        get_tickers_from_wikipedia(args.input)

    if args.all_tickers:
        logging.info("Downloading all data. It will take approximately 40 minutes...")
        scraper = YahooFinanceScraper(args.input, args.output, args.pause, args.request_timeout)
        scraper.download_all()
    elif args.ticker:
        logging.info("Downloading data for {0}".format(args.ticker))
        scraper = YahooFinanceScraper(args.input, args.output, args.pause, args.request_timeout)
        summary_data = scraper.download(args.ticker)
        scraper.write_data_about_ticker(summary_data, args.append)

    sys.exit(0)
