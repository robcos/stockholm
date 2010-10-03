import ystockquote
import time
import datetime
from datetime import date
import MySQLdb
import re

class Base:
  def __init__(self, dict_):
    self.__dict__ = dict_
 
  def __str__(self):
    s = self.__class__.__name__
    for k,v in self.__dict__.items():
      s += " %s:%s" % (k,v)
    return s

  def save(self):
    Query.save(self.__class__, self.__dict__)
 
class Query:
  db=MySQLdb.connect(host="localhost", user="robcos",
                      passwd="robcos", db="stocks")
  def __init__(self, query, params):
    self.query = query
    self.params = params

  @staticmethod
  def get_cols(cols):
    return ", ".join(cols)

  def execute(self):
    self.cursor = self.db.cursor()
    self.cursor.execute(self.query, self.params)
    #print "######## DEBUG ########\n" if debug
    #print self.query % self.params
    #print "\n######## DEBUG ########" if debug
    return self

  def keys_(self):
    keys = re.split(' *, *', re.search('SELECT (.*) FROM', self.query, flags=re.IGNORECASE).group(1))
    for i, key in enumerate(keys):
      keys[i] = key.strip()
    return keys

  def fetchone_(self):
    return self.cursor.fetchone()

  def fillall(self, aclass):
    self.execute()
    all = []
    while(True):
      values = self.fetchone_()
      if values == None:
        break
      all.append(self.fillone_(aclass, values))
    return all

  def fillone(self, aclass):
    self.execute()
    values = self.fetchone_()
    return self.fillone_(aclass, values)

  def fillone_(self, aclass, values):
    if not values:
      return None
    d = dict()
    for i, k in enumerate(self.keys_()):
      d[k] = values[i]
    return aclass(d)
 
  @staticmethod 
  def save(claz, dictionary):
    table = claz.__name__
    keys = dictionary.keys()
    cols = ", ".join(keys)
    values = []
    value_places = []
    for k in keys:
      value_places.append("%s")
      values.append(dictionary.get(k))
    insert = "INSERT INTO %s (%s) values (%s)" % (table, cols, ", ".join(value_places))
    cursor = Query.db.cursor()
    cursor.execute(insert, values)

  @staticmethod 
  def find(claz, where, where_args):
    table = claz.__name__
    cols = ", ".join(claz.__cols__)
    select = "SELECT %s FROM %s where (%s)" % (cols, table, where)
    return Query(select, where_args).fillone(claz)

class Position(Base):
  __cols__ = ["symbol", "currency", "currency_rate", "enter_date", "exit_date,"
      "enter_price", "exit_price", "enter_commission", "exit_commission",
      "shares", "stop", "portfolio_id"]

  @staticmethod
  def get_position(symbol, date):
    return Query.find(Position, 'symbol = %s and enter_date = %s', (symbol, date))
    pass

  @staticmethod
  def open(symbol, currency, currency_rate, enter_date, enter_price,
       enter_commission, shares, stop):
    position = Position({'symbol': symbol, 'currency': currency, 
        'currency_rate': currency_rate, 'enter_date': enter_date, 
        'enter_price': enter_price, 'enter_commission': enter_commission,
        'shares': shares, 'portfolio_id': 1, 'stop': stop})
    position.save();
  
class Quote(Base):
  start_date = "2010-01-01"
  
  def has_met_stop(self, position):
    if position.is_long:
      return self.close >= position.stop
    else:
      return self.close <= position.stop

  def is_over_sma50_7(self):
    indicators = self.get_trailing_indicators(7)
    for i in indicators:
      if self.close < i.sma_50:
        return False
    return True
 
  @staticmethod
  def set_tr(symbol, date, value):
    c = Query("UPDATE quote SET tr = %s WHERE symbol = %s and date = %s", (value, symbol, date)).execute()
  
  @staticmethod
  def get_quotes(symbol):
    c = Query("SELECT symbol, date, open, high, low, close, tr from quote where symbol = %s and date > %s order by date asc", (symbol, Quote.start_date))
    return c.fillall(Quote)

  @staticmethod
  def get_quote(symbol, date):
    c = Query("SELECT symbol, date, open, high, low, close, tr from quote where symbol = %s and date = %s", (symbol, date))
    return c.fillone(Quote)

  def previous(self):
    c = Query("SELECT symbol, date, open, high, low, close from quote where symbol = %s and date < %s order by date desc limit 1", (self.symbol, self.date))
    return c.fillone(Quote)
  
  def get_trailing_indicators(self, days):
    return Indicator.get_trailing_indicators(self.symbol, self.date, days)

  def get_indicator(self):
    return Indicator.get_indicator(self.symbol, self.date)
    
class Indicator(Base):
  atr_stop = 3
  def calculate_stop(self, quote):
    return float(quote.close) - float(self.atr_14) * float(self.atr_stop);

  @staticmethod
  def get_indicator(symbol, date):
    query = Query('SELECT symbol, date, sma_20, sma_50, atr_14 FROM indicator i WHERE i.symbol = %s AND i.date = %s', (symbol, date))
    return query.fillone(Indicator)

  @staticmethod
  def get_trailing_indicators(symbol, date, days):
    """
      Returns the indicators for the last x days.
    """
    c = Query('SELECT symbol, date, sma_20, sma_50, atr_14 FROM indicator i WHERE i.symbol = %s AND i.date <=%s ORDER BY i.date desc LIMIT %s', (symbol, date, days))
    return c.fillall(Indicator)
