# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime
import numpy as np

current_year = datetime.datetime.now().year

def get_dividend_yield(code):
  url =  "http://companyinfo.stock.naver.com/company/c1010001.aspx?cmp_cd=" + code
  html = requests.get(url).text

  soup = BeautifulSoup(html, 'lxml')
  td_data = soup.find_all('td', { 'class': 'cmp-table-cell td0301'})

  if not td_data:
    return ""
  dt_data = td_data[0].find_all('dt')

  dividend_yield = dt_data[5].text
  dividend_yield = dividend_yield.split(' ')[1]
  dividend_yield = dividend_yield[:-1]

  return dividend_yield

def get_current_3year_treasury():
  url =  "http://info.finance.naver.com/marketindex/interestDailyQuote.nhn?marketindexCd=IRR_GOVT03Y&page=1"
  html = requests.get(url).text

  soup = BeautifulSoup(html, 'lxml')
  tbody_data = soup.find_all('tbody')
  tr_data = tbody_data[0].find_all('tr')
  td_data = tr_data[0].find_all('td')
  return td_data[1].text



def get_3year_treasury():
  url = "http://www.index.go.kr/potal/main/EachDtlPageDetail.do?idx_cd=1073"
  html = requests.get(url).text

  soup = BeautifulSoup(html, 'lxml')
  tbody_data = soup.find_all('tbody')
  tr_data = tbody_data[0].find_all('tr')
  td_data = tr_data[0].find_all('td')

  treasury_3year = {}
  start_year = 2010

  for x in td_data:
    if start_year == current_year:
      break
    treasury_3year[start_year] = x.text
    start_year += 1

  return treasury_3year

def get_financial_statements(code):
  url = "http://companyinfo.stock.naver.com/v1/company/ajax/cF1001.aspx?cmp_cd=%s&fin_typ=0&freq_typ=Y" % (code)
  html = requests.get(url).text

  html = html.encode('utf-8').replace('<th class="bg r01c02 endLine line-bottom"colspan="8">연간</th>', "")
  html = html.replace("<span class='span-sub'>(IFRS연결)</span>", "")
  html = html.replace("<span class='span-sub'>(IFRS별도)</span>", "")
  html = html.replace("<span class='span-sub'>(GAAP개별)</span>", "")
  html = html.replace('\t', '')
  html = html.replace('\n', '')
  html = html.replace('\r', '')

  for year in range(2009, current_year+1):
    for month in range(6, 13):
      month = "/%02d" % month
      html = html.replace(str(year).encode('utf-8') + month, str(year).encode('utf-8'))

    for month in range(1, 6):
      month = "/%02d" % month
      html = html.replace(str(year + 1).encode('utf-8') + month, str(year).encode('utf-8'))

  html = html.replace(str(year) + '(E)', str(year))
  df_list = pd.read_html(html, index_col=u'주요재무정보'  )
  df = df_list[0]

  return df

def get_estimated_dividend_yield(code):
  df = get_financial_statements(code)
  dividend_yield = df.ix[u'현금배당수익률']

  now = datetime.datetime.now()
  cur_year = now.year

  if str(cur_year).encode('utf-8') in dividend_yield.index:
    cur_year_dividend_yield = dividend_yield[str(cur_year)]
    if np.isnan(cur_year_dividend_yield):
      return dividend_yield[str(cur_year-1)]
    else:
      return cur_year_dividend_yield

  else:
    return dividend_yield[str(cur_year-1)]

def get_previous_dividend_yield(code):
  df = get_financial_statements(code)
  dividend_yield = df.ix[u'현금배당수익률']

  now = datetime.datetime.now()
  cur_year = now.year

  previous_dividend_yield = {}

  for year in range (cur_year-5, cur_year):
    if str(year) in dividend_yield.index :
      previous_dividend_yield[year] = dividend_yield[str(year)]

  return previous_dividend_yield

if __name__ == "__main__" :
  estimated_dividend_yield = get_estimated_dividend_yield(code)