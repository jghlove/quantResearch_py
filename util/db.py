#coding:utf-8
import tushare as ts
import MySQLdb as mdb
import datetime
import time
import numpy as np
import pandas as pd
import sys
import pandas as pd
import pandas_datareader.data as web




#从tushare中获取hs300的股票
def save_hs300_into_db():
	db_host = 'localhost'
	db_user = 'root'
	db_password = ''
	db_name = 'ticker_master'
	con = mdb.connect(host=db_host, user=db_user, passwd=db_password, db=db_name)
	now = datetime.datetime.utcnow()
	hs300 = ts.get_hs300s()
	column_str = """ticker, instrument, name, sector, currency, created_date, last_updated_date"""
	insert_str = ("%s, " * 7)[:-2]
	final_str = "INSERT INTO symbol (%s) VALUES (%s)" % (column_str, insert_str)
	symbols = []

	for i in range(len(hs300)):
		t = hs300.ix[i]
		symbols.append(
			(
				t['code'],
				'stock',
				t['name'],
				'',
				'RMB',
				now,
				now,
				)
			)
	cur = con.cursor()
	with con:
		cur = con.cursor()
		cur.executemany(final_str, symbols)
	print 'success insert hs300 into symbol!'

def save_us_into_db(symbols):
	db_host = 'localhost'
	db_user = 'root'
	db_password = ''
	db_name = 'us_ticker_master'
	con = mdb.connect(host=db_host, user=db_user, passwd=db_password, db=db_name)
	now = datetime.datetime.utcnow()
	column_str = """ticker, instrument, name, sector, currency, created_date, last_updated_date"""
	insert_str = ("%s, " * 7)[:-2]
	final_str = "INSERT INTO symbol (%s) VALUES (%s)" % (column_str, insert_str)
	symbols_content = []

	for i in range(len(symbols)):
		t = symbols.ix[i]
		symbols_content.append(
			(
				t['Symbol'],
				'stock',
				t['Name'],
				t['Sector'],
				'USD',
				now,
				now,
				)
			)
	cur = con.cursor()
	with con:
		cur = con.cursor()
		cur.executemany(final_str, symbols_content)
	print 'success insert us_ticker into symbol!'

#获取事先储存过的300支股票
def get_hs300_tickers():
	db_host = 'localhost'
	db_user = 'root'
	db_password = ''
	db_name = 'ticker_master'
	con = mdb.connect(host=db_host, user=db_user, passwd=db_password, db=db_name)
	with con:
		cur = con.cursor();
		cur.execute('SELECT id,ticker,name FROM symbol')
		data = cur.fetchall();
		return [(d[0],d[1],d[2]) for d in data]

#获取美股id用于遍历获取信息以及存储
def get_us_tickers():
	db_host = 'localhost'
	db_user = 'root'
	db_password = ''
	db_name = 'us_ticker_master'
	con = mdb.connect(host=db_host, user=db_user, passwd=db_password, db=db_name)
	with con:
		cur = con.cursor();
		cur.execute('SELECT id,ticker,name FROM symbol')
		data = cur.fetchall();
		return [(d[0],d[1],d[2]) for d in data]

#根据id获取ticker
def get_ticker_info_by_id(ticker_id,start_date,end_date=str(datetime.date.today())):
	#如果没传，则默认为该支股票开始的位置
	if start_date == '':
		df = ts.get_stock_basics()
		start_date = df.ix[ticker_id]['timeToMarket'] #上市日期YYYYMMDD
		start_date = str(start_date)
		start_date_year = start_date[0:4]
		start_date_month = start_date[4:6]
		start_date_day = start_date[6:8]
		start_date = start_date_year + '-' + start_date_month + '-' + start_date_day

	print ('======= loading：%s to %s , %s ========' % (start_date,end_date,ticker_id))
	ticker_data = ts.get_h_data(ticker_id,start=start_date,end=end_date,retry_count=50,pause=1)
	print ('======= loading success =======')
	return ticker_data

#获取美股数据
def get_us_ticker_by_id(ticker_id,start_date,end_date=datetime.date.today()):
	start = datetime.datetime(2010, 1, 1)
	end = datetime.datetime(2013, 1, 27)
	print(start,end,ticker_id,'-----')
	data = web.DataReader(ticker_id, 'yahoo', start_date, end_date)
	return data

#下载失败则在symbol中删除
def delete_symbol_from_db_by_id(id):
	db_host = 'localhost'
	db_user = 'root'
	db_password = ''
	db_name = 'us_ticker_master'
	con = mdb.connect(host=db_host, user=db_user, passwd=db_password, db=db_name)
	with con:
		cur = con.cursor()
		print "DELETE FROM symbol where ticker='%s'" % id
		cur.execute("DELETE FROM symbol where ticker='%s'" % id)


#读取symbol表里的最新的日期
def get_last_date(ticker_id):
	db_host = 'localhost'
	db_user = 'root'
	db_password = ''
	db_name = 'ticker_master'
	con = mdb.connect(host=db_host, user=db_user, passwd=db_password, db=db_name)
	with con:
		cur = con.cursor()
		cur.execute("SELECT price_date FROM daily_price WHERE symbol_id=%s ORDER BY price_date DESC" % ticker_id)
		date = cur.fetchall()
		return date

#读取us美股最老日期
def get_us_oldest_date(ticker_id):
	db_host = 'localhost'
	db_user = 'root'
	db_password = ''
	db_name = 'us_ticker_master'
	con = mdb.connect(host=db_host, user=db_user, passwd=db_password, db=db_name)
	with con:
		cur = con.cursor()
		cur.execute("SELECT price_date FROM daily_price WHERE symbol_id=%s ORDER BY price_date" % ticker_id)
		date = cur.fetchall()
		return date

#读取美股最新日期
def get_us_last_date(ticker_id):
	db_host = 'localhost'
	db_user = 'root'
	db_password = ''
	db_name = 'us_ticker_master'
	con = mdb.connect(host=db_host, user=db_user, passwd=db_password, db=db_name)
	with con:
		cur = con.cursor()
		cur.execute("SELECT price_date FROM daily_price WHERE symbol_id='%s' ORDER BY price_date DESC" % ticker_id)
		date = cur.fetchall()
		return date

#储存到数据库
def save_ticker_into_db(ticker_id,ticker,vendor_id):
	db_host = 'localhost'
	db_user = 'root'
	db_password = ''
	db_name = 'ticker_master'
	con = mdb.connect(host=db_host, user=db_user, passwd=db_password, db=db_name)
	# Create the time now
	now = datetime.datetime.utcnow()
	 # Create the insert strings
	column_str = """data_vendor_id, symbol_id, price_date, created_date,
	              last_updated_date, open_price, high_price, low_price,
	              close_price, volume, amount"""
	insert_str = ("%s, " * 11)[:-2]
	final_str = "INSERT INTO daily_price (%s) VALUES (%s)" % (column_str, insert_str)
	daily_data = []

	for i in range(len(ticker.index)):
		t_date = ticker.index[i]
		t_data = ticker.ix[t_date]
		daily_data.append(
			(vendor_id, ticker_id, t_date, now, now,t_data['open'], t_data['high']
				, t_data['low'], t_data['close'], t_data['volume'], t_data['amount'])
		)

	with con:
		cur = con.cursor()
		cur.executemany(final_str, daily_data)

#储存到美股数据库
def save_us_ticker_into_db(ticker_id,ticker,vendor_id):
	db_host = 'localhost'
	db_user = 'root'
	db_password = ''
	db_name = 'us_ticker_master'
	con = mdb.connect(host=db_host, user=db_user, passwd=db_password, db=db_name)
	# Create the time now
	now = datetime.datetime.utcnow()
	 # Create the insert strings
	column_str = """data_vendor_id, symbol_id, price_date, created_date,
	             last_updated_date, open_price, high_price, low_price,
	             close_price, volume, adj_close_price"""
	insert_str = ("%s, " * 11)[:-2]
	final_str = "INSERT INTO daily_price (%s) VALUES (%s)" % (column_str, insert_str)
	daily_data = []

	for i in range(len(ticker.index)):
		t_date = ticker.index[i]
		t_data = ticker.ix[t_date]
		daily_data.append(
			(vendor_id, ticker_id, t_date, now, now,t_data['Open'], t_data['High']
				, t_data['Low'], t_data['Close'], t_data['Volume'], t_data['Adj Close'])
		)

	with con:
		cur = con.cursor()
		cur.executemany(final_str, daily_data)
		print 'success insert new into db!'

		


#从数据中获取数据
def get_ticker_from_db_by_id(ticker_id):
	db_host = 'localhost'
	db_user = 'root'
	db_password = ''
	db_name = 'ticker_master'
	con = mdb.connect(host=db_host,user=db_user,passwd=db_password,db=db_name)
	with con:
		cur = con.cursor()
		cur.execute('SELECT price_date,open_price,high_price,low_price,close_price,volume from daily_price where symbol_id = %s ORDER BY price_date DESC' % ticker_id )
		daily_data = cur.fetchall()
		daily_data_np = np.array(daily_data)
		daily_data_df = pd.DataFrame(daily_data_np,columns=['index','open','high','low','close','volume'])

		return daily_data_df


#从数据中获取美股us数据
def get_us_ticker_from_db_by_id(ticker_id,start_date,end_date=datetime.date.today()):
	db_host = 'localhost'
	db_user = 'root'
	db_password = ''
	db_name = 'us_ticker_master'
	con = mdb.connect(host=db_host,user=db_user,passwd=db_password,db=db_name)

	start_date = str(start_date)[:10]
	end_date = str(end_date)[:10]

	with con:
		cur = con.cursor()
		cur.execute('SELECT price_date,open_price,high_price,low_price,adj_close_price,volume FROM daily_price WHERE (price_date BETWEEN "%s" and "%s") AND (symbol_id="%s") ORDER BY price_date DESC' % ( start_date,end_date,ticker_id ))
		daily_data = cur.fetchall()
		daily_data_np = np.array(daily_data)
		daily_data_df = pd.DataFrame(daily_data_np,columns=['index','open','high','low','close','volume'])		
		return daily_data_df

#从csv中获取美股的名称
def get_us_ticker_name_from_csv(filename):
	data = pd.read_csv(filename)[['Symbol','Name','Sector','MarketCap']]
	# print (data)
	return data;


#获取us日均交易量在中间33%的股票,从当日计算, 股票值在10到30之间
def get_us_middle33_volume(delay_days,low_price,high_price):
	tickers = get_us_tickers()
	cal_volume_list = pd.DataFrame([],columns=['id','volume'])
	df = pd.DataFrame([],columns=['id','volume'])
	length = len(tickers)
	print '================ is calculating ================='
	# print tickers
	for i in range(length):
		ticker = tickers[i]
		ticker_id = ticker[1]
		
		#处理时间
		end_date = get_us_last_date(ticker_id)[0][0]
		start_date = end_date + datetime.timedelta(days = delay_days * -1)
		ticker_data = get_us_ticker_from_db_by_id(ticker_id,start_date,end_date)
		days_mean_volume = ticker_data['volume'].mean()
		days_mean_daily_price = ticker_data['close'].mean()
		print '========== %s of %s , %s , %s==========' % (i,length,ticker_id,days_mean_volume)		
		#判断是否符合10到30取值区间
		if int(days_mean_daily_price) in range(int(low_price),int(high_price)):
			days_mean_volume_df = pd.DataFrame([[ticker_id,days_mean_volume,days_mean_daily_price]],columns=['id','volume','price'])
			df = df.append(days_mean_volume_df)	

		# if i > 1000:
		# 	break

	df = df.sort(columns="volume")	
	df_len = len(df)
	df = df[int(df_len * 0.33) : int(df_len * 0.66)]
	df.index = range(len(df))


	return df


#得出平均值与方差
def get_average_days_price_by_id(ticker_id,average_days = 7 * 30):
	db_host = 'localhost'
	db_user = 'root'
	db_password = ''
	db_name = 'us_ticker_master'
	con = mdb.connect(host=db_host,user=db_user,passwd=db_password,db=db_name)

	end_date=datetime.date.today()
	start_date = end_date + datetime.timedelta(days = int(average_days) * -1)
	start_date = str(start_date)[:10]
	end_date = str(end_date)[:10]
	with con:
		cur = con.cursor()
		cur.execute('SELECT adj_close_price FROM daily_price WHERE (price_date BETWEEN "%s" and "%s") AND (symbol_id="%s") ORDER BY price_date DESC' % ( start_date,end_date,ticker_id ))
		daily_data = cur.fetchall()
		daily_data_np = np.array(daily_data)
		daily_data_df = pd.DataFrame(daily_data_np,columns=['close']).fillna(method="pad").fillna(method="bfill")
		if len(daily_data_df) == 0 :
			mean = 0;
			std = 0
		else:
			mean = daily_data_df['close'].mean()
			std = daily_data_df['close'].astype('float').std()

		return mean,std


#获取一只股票的currt数据，均值方差数据
def get_current_mean_std_df(ticker_id,days_range=200,cal_range=60,end_date=datetime.date.today()):
	db_host = 'localhost'
	db_user = 'root'
	db_password = ''
	db_name = 'us_ticker_master'
	con = mdb.connect(host=db_host,user=db_user,passwd=db_password,db=db_name)
	
	end_date=datetime.date.today()
	start_date = end_date + datetime.timedelta(days = int(days_range + cal_range) * -1)
	start_date = str(start_date)[:10]
	end_date = str(end_date)[:10]

	with con:
		cur = con.cursor()
		cur.execute('SELECT adj_close_price FROM daily_price WHERE (price_date BETWEEN "%s" and "%s") AND (symbol_id="%s") ORDER BY price_date DESC' % ( start_date,end_date,ticker_id ))
		daily_data = cur.fetchall()
		daily_data_np = np.array(daily_data)
		daily_data_df = pd.DataFrame(daily_data_np,columns=['close'])
		daily_data_df['ma_60'] = pd.rolling_mean(daily_data_df['close'],cal_range)
		daily_data_df['ewma_60'] = pd.ewma(daily_data_df['close'],cal_range)
		daily_data_df['std_60'] = pd.rolling_std(daily_data_df['close'],cal_range)

		return daily_data_df[60:]
