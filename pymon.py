# -*- coding: utf-8 -*-

import numpy as np
import webreader
import datetime
import json
import time
from PyQt5.QtWidgets import *
import sys

# 동서 : 026960
# 삼성물산 : 028260
# S-oil우 : 010955
# SK가스 : 018670
# 효성 : 004800

kospi_codes = ['026960', '028260', '010955', '018670', '004800']

class PyMon :
  def calculate_estimated_dividend_to_treasury( self, code):
    estimated_dividend_yield = webreader.get_estimated_dividend_yield(code)
    if np.isnan(estimated_dividend_yield):
      estimated_dividend_yield = webreader.get_dividend_yield(code)

    current_3year_treasury = webreader.get_current_3year_treasury()
    estimated_dividend_to_treasury = float(estimated_dividend_yield) / float(current_3year_treasury)
    return estimated_dividend_to_treasury

  def get_min_max_dividend_to_treasury(self, code):
    previous_dividend_yield = webreader.get_previous_dividend_yield(code)
    three_years_treasury = webreader.get_3year_treasury()

    now = datetime.datetime.now()
    cur_year = now.year
    previous_dividend_to_treasury = {}

    for year in range(cur_year - 5, cur_year):
      if year in previous_dividend_yield.keys() and year in three_years_treasury.keys():
        ratio = float(previous_dividend_yield[year]) / float(three_years_treasury[year])
        previous_dividend_to_treasury[year] = ratio

    # print (json.dumps(previous_dividend_to_treasury, sort_keys=True))
    min_ratio = min(previous_dividend_to_treasury.values())
    max_ratio = max(previous_dividend_to_treasury.values())

    return ( min_ratio, max_ratio)

  def buy_check_by_dividend_algorithm(self, code):
    estimated_dividend_to_treasury = self.calculate_estimated_dividend_to_treasury(code)
    (min_ratio, max_ratio) = self.get_min_max_dividend_to_treasury(code)

    if estimated_dividend_to_treasury >= max_ratio and max_ratio != 0 :
      return (1, estimated_dividend_to_treasury)
    elif estimated_dividend_to_treasury <= min_ratio and min_ratio != 0:
      return (-1, estimated_dividend_to_treasury)
    else: return ( 0, estimated_dividend_to_treasury)


  def run_dividend(self) :
    buy_list = []
    sell_list = []

    for code in kospi_codes:
      time.sleep(0.5)
      ret = self.buy_check_by_dividend_algorithm(code)
      if ret[0] == 1:
        buy_list.append((code, ret[1]))
      elif ret[0] == -1:
        sell_list.append((code, ret[1]))

      else: pass

    sorted_buy_list = sorted(buy_list, key=lambda t:t[1], reverse=True)
    sorted_sell_list = sorted(sell_list, key=lambda t:t[1], reverse=True)
    print(sorted_buy_list)
    print(sorted_sell_list)

if __name__ == "__main__":
  app = QApplication(sys.argv)
  pymon = PyMon()
  # print(pymon.calculate_estimated_dividend_to_treasury(code))
  # print(pymon.get_min_max_dividend_to_treasury(code))
  # print (pymon.buy_check_by_dividend_algorithm(code))
  pymon.run_dividend()