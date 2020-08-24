


############### User input:  stocks MSFT 10-k  (example)





import discord
from html.parser import HTMLParser

# Importing built-in libraries (no need to install these)
import re
import os
from time import gmtime, strftime
import datetime as dt
import unicodedata

# Importing libraries you need to install
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import requests
import bs4 as bs
from lxml import html
from tqdm import tqdm
import pickle
from pysec.edgar import EDGARQuery
from pysec.filing_types import FILING_TYPES
import pprint


#creating discord class
client = discord.Client()


#-----GLOBAL VARIABLES ---#
parsed_info = ''
nonparsed_info = ''
text_number = ''

# ----------------------- Yash Code ----------------------------------#

#--------------- Section 1 -----------------------#
def MapTickerToCik(tickers):
    """
    Tickers: List of one or more tickers
    """
    url = 'http://www.sec.gov/cgi-bin/browse-edgar?CIK={}&Find=Search&owner=exclude&action=getcompany'
    cik_re = re.compile(r'.*CIK=(\d{10}).*')

    cik_dict = {}
    for ticker in tqdm(tickers): # Use tqdm lib for progress bar
        results = cik_re.findall(requests.get(url.format(ticker)).text)
        if len(results):
            cik_dict[str(ticker).lower()] = str(results[0])

    return cik_dict
'''
#--------------- Section 2 -----------------------#
cik_dict = MapTickerToCik(["MSFT"])
# Clean up the ticker-CIK mapping as a DataFrame
ticker_cik_df = pd.DataFrame.from_dict(data=cik_dict, orient='index')
ticker_cik_df.reset_index(inplace=True)
ticker_cik_df.columns = ['ticker', 'cik']
ticker_cik_df['cik'] = [str(cik) for cik in ticker_cik_df['cik']]
#--------------- Section 3 -----------------------#
# Check for duplicated tickers/CIKs
print("Number of ticker-cik pairings:", len(ticker_cik_df))
print("Number of unique tickers:", len(set(ticker_cik_df['ticker'])))
print("Number of unique CIKs:", len(set(ticker_cik_df['cik'])))
'''
#--------------- Section 4 -----------------------#
def tickertoform(cik_list, form_desired):
    """
    Cik_List : Must Be A List

    Cik's : Must Be Strings

    Form_Desired : Must Be A String
    """
    edgar = EDGARQuery()
    cik_to_filing = {}
    for x in cik_list:
        data = edgar.company_filings_by_type(x, form_desired)
        data_url = data[0]["filing_href"]
        print(data_url)
        resp = requests.get(data_url).text
        soup = bs.BeautifulSoup(resp, 'lxml')
        body = soup.find('table')
        rows = body.find_all("td",{"scope" :"row"})
        data_link = rows[7]
        data_link = data_link.find("a")
        data_link = data_link.get("href")
        base_url = "https://www.sec.gov"
        resp1 = requests.get(base_url + data_link).content
        print("This is " + x + " " + form_desired + " " + base_url + data_link)
        cik_to_filing[x] = base_url + data_link
        cik = x
        with open(x + "-" + form_desired +".txt", "wb") as f:
            f.write(resp1)
        f.close()
    return x + "-" + form_desired +".txt", cik_to_filing[x]

#--------------- Section 5 -----------------------#
#tickertoform(ticker_cik_df['cik'], "10-K")



#----------------------------------------- PARSER ------------------------------------------------------#






class MyHTMLParser(HTMLParser):
    def handle_data(self, data):
        global parsed_info
        print("Encountered some data  :", data)
        if data != '' or data != ' ' :
            if data.startswith("  ") or data.startswith('\n'):
                return
            if data.startswith("EX-"):
                return
            if len(data) <= 2:
                return
            parsed_info += data
            parsed_info += '\n'
        return parsed_info






print('#========== | Bot Started | ==========#')

print(parsed_info)
#------------------------------Hello test------------------------------------------#



@client.event
async def on_message(message):
    global parsed_info
    #makes all messages lowercase
    #message.content = message.content.lower()
    #checks if it is responding to itself
    if message.author == client.user:
        return
    #returns hello to user
    if message.content.startswith("hello"):
        if str(message.author) == 'NLC#5746':
            await message.channel.send('Hello' + str(message.author))
        else:
            await message.channel.send("Hello I can see the light")

    #----------Stock application ---------#


    if message.content.startswith('stocks'):
        type_t = message.content.split()[1]
        type_k = message.content.split()[2]

#-----------------Yash code in bot-------------------------------------#
         #--------------- Section 2 -----------------------#
        cik_dict = MapTickerToCik([type_t])
        # Clean up the ticker-CIK mapping as a DataFrame
        print(cik_dict)
        for x in cik_dict:
            cik = cik_dict[x]
        #--------------- Section 3 -----------------------#
        # Check for duplicated tickers/CIKs

        #--------------- Section 5 -----------------------#
        file_path, url_dict = tickertoform([cik], type_k)
        print(file_path)
#----------------------------------------------------------------------#

        #-----------Parsing----------#
        file_object  = open(file_path, "r")
        print(file_path)
        nonparsed_info = file_object.read()

        parser = MyHTMLParser()
        parsed = parser.feed(nonparsed_info)

        #---------Sending-------------#
        await message.channel.send (url_dict)
        print(f'Form: --------({type_k})---------')
        print(f'Company: --------({type_t})---------')


        #--------Errases info to prevent repetance---------------#

#------------runs bot with the bot token------------------------------------------------------------
client.run('NzQ1ODAwNzYyMjA2MDYwNjA0.Xz3DFg.8ZPQzG4au44caVpUS8Qsjy1tjq8')
