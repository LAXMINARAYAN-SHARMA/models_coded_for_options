# -*- coding: utf-8 -*-
"""MY_LIBRARY.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/10hVGu2_6lE-AWMTQG6uz8m8XH5sEfg4b

##  GET_ACCESS_TOKEN
"""

import requests
import pandas as pd
def  get_access_token(code,apikey,secretkey):
  url = 'https://api.upstox.com/v2/login/authorization/token'
  headers = {
      'accept': 'application/json',
      'Content-Type': 'application/x-www-form-urlencoded',
  }

  data = {
      'code': code,
      'client_id': apikey,
      'client_secret': secretkey,
      'redirect_uri': 'https://127.0.0.1:5000/',
      'grant_type': 'authorization_code',
  }

  response = requests.post(url, headers=headers, data=data)

  # Check the response status
  if response.status_code == 200:
      # Parse the JSON response
      data = response.json()

      # Convert to DataFrame
      df_token = pd.DataFrame(data.items(), columns=['Key', 'Value'])

      # Print the DataFrame
      print(df_token)

  else:
      # Print an error message if the request was not successful
      print(f"Error: {response.status_code} - {response.text}")

  # Alternatively, you can use loc
  access_token_value = df_token.loc[df_token['Key'] == 'access_token', 'Value'].iloc[0]

  # Print the access_token value
  # print("Access Token:", access_token_value)
  return access_token_value

"""## GET LTP"""

import requests
import json

def get_last_traded_price(access_token_value,instrument_key,symbol):
    ltp=-1
    url = f'https://api.upstox.com/v2/market-quote/ltp?instrument_key={instrument_key}'
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token_value}'
    }


    # Make the HTTP GET request
    response = requests.get(url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response
        response_data = response.json()


        for key in response_data['data']:
          ltp = response_data['data'][key]['last_price']


        # Return the LTP

        return ltp
    else:
        # Print an error message if the request was not successful
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return None

from datetime import datetime, timedelta

def weekdays_until_last_thursday():
    # Get the current date
    today = datetime.today()

    # Get the first day of the next month and subtract a day to get the last day of the current month
    first_day_next_month = datetime(today.year, today.month + 1, 1) if today.month < 12 else datetime(today.year + 1, 1, 1)
    last_day_current_month = first_day_next_month - timedelta(days=1)

    # Find the last Thursday
    days_to_last_thursday = (last_day_current_month.weekday() - 3) % 7
    last_thursday = last_day_current_month - timedelta(days=days_to_last_thursday)

    # Calculate the number of weekdays between today and the last Thursday
    weekdays_count = 0
    current_date = today

    while current_date <= last_thursday:
        if current_date.weekday() < 5:  # Monday=0, Sunday=6, so <5 means Mon-Fri
            weekdays_count += 1
        current_date += timedelta(days=1)

    return weekdays_count

"""## IMPORT OPTION CHAIN"""

import requests
def import_option_chain_data(instrument_key,access_token_value):
  url = 'https://api.upstox.com/v2/option/chain'
  params = {
      'instrument_key': instrument_key,
      'expiry_date': '2024-08-29'
  }
  headers = {
      'Accept': 'application/json',
      'Authorization': f'Bearer {access_token_value}'
  }

  response = requests.get(url, params=params, headers=headers)
  # Process the response data as needed
  data=response.json()
  df_call,df_put,df_general=format_option_chain_data_into_dataframe(data)
  # print(response.json())
  return df_call,df_put,df_general

def format_option_chain_data_into_dataframe(data):

  # Extract general data
  general_data = []
  call_data = []
  put_data = []

  for item in data['data']:
      general_info = {
          'expiry': item.get('expiry'),
          'strike_price': item.get('strike_price'),
          'underlying_key': item.get('underlying_key'),
          'underlying_spot_price': item.get('underlying_spot_price'),
          'pcr': item.get('pcr')
      }
      general_data.append(general_info)

      if 'call_options' in item:
          call_option = item['call_options']
          call_data.append({
              'expiry': item['expiry'],
              'strike_price': item['strike_price'],
              'instrument_key': call_option['instrument_key'],
              'ltp': call_option['market_data']['ltp'],
              'volume': call_option['market_data']['volume'],
              'oi': call_option['market_data']['oi'],
              'close_price': call_option['market_data']['close_price'],
              'bid_price': call_option['market_data']['bid_price'],
              'bid_qty': call_option['market_data']['bid_qty'],
              'ask_price': call_option['market_data']['ask_price'],
              'ask_qty': call_option['market_data']['ask_qty'],
              'prev_oi': call_option['market_data']['prev_oi'],
              'vega': call_option['option_greeks']['vega'],
              'theta': call_option['option_greeks']['theta'],
              'gamma': call_option['option_greeks']['gamma'],
              'delta': call_option['option_greeks']['delta'],
              'iv': call_option['option_greeks']['iv']
          })

      if 'put_options' in item:
          put_option = item['put_options']
          put_data.append({
              'expiry': item['expiry'],
              'strike_price': item['strike_price'],
              'instrument_key': put_option['instrument_key'],
              'ltp': put_option['market_data']['ltp'],
              'volume': put_option['market_data']['volume'],
              'oi': put_option['market_data']['oi'],
              'close_price': put_option['market_data']['close_price'],
              'bid_price': put_option['market_data']['bid_price'],
              'bid_qty': put_option['market_data']['bid_qty'],
              'ask_price': put_option['market_data']['ask_price'],
              'ask_qty': put_option['market_data']['ask_qty'],
              'prev_oi': put_option['market_data']['prev_oi'],
              'vega': put_option['option_greeks']['vega'],
              'theta': put_option['option_greeks']['theta'],
              'gamma': put_option['option_greeks']['gamma'],
              'delta': put_option['option_greeks']['delta'],
              'iv': put_option['option_greeks']['iv']
          })

  # Convert lists to DataFrames
  df_general = pd.DataFrame(general_data)
  df_call = pd.DataFrame(call_data)
  df_put = pd.DataFrame(put_data)

  # Display the DataFrames
  # print("General Data DataFrame:")
  # print(df_general)

  # print("\nCall Options DataFrame:")
  # print(df_call)

  # print("\nPut Options DataFrame:")
  # print(df_put)
  return df_call,df_put,df_general

def extrcting_only_ltp_and_strikes(df_call):

  new_data_frame=df_call.iloc[:,[1,3]]
  new_data_frame.drop(index=0,inplace=True)
  new_data_frame.reset_index(drop=True,inplace=True)
  my_strike_list=new_data_frame['strike_price'].tolist()
  # print(new_data_frame)
  return my_strike_list,new_data_frame

def calculate_all_possible_spread_and_max_loss(instrument_key,access_token_value):
  df_call,df_put,df_general=import_option_chain_data(instrument_key,access_token_value)
  my_strike_list,new_data_frame=extrcting_only_ltp_and_strikes(df_call)
  #calculation of all_max_loss_possible (it iis 2d array bw all ltp)
  my_outer_list=[]
  my_outer_list_spread=[]
  for i in range(len(new_data_frame)):
    my_list=[]
    for j in range(len(new_data_frame)):
      my_list.append(new_data_frame.iloc[i,1]-new_data_frame.iloc[j,1])

    my_outer_list.append(my_list)

   #calculate all_possible_spreads (it iis 2d array bw all striikes)

  for i in range(len(new_data_frame)):
    my_list_2=[]
    for j in range(len(new_data_frame)):
      my_list_2.append(new_data_frame.iloc[i,0]-new_data_frame.iloc[j,0])

    my_outer_list_spread.append(my_list_2)

  df_max_loss=pd.DataFrame(my_outer_list)
  df_spread=pd.DataFrame(my_outer_list_spread)



  #calculating risk reward ratio
  df_risk_reward=(-df_spread-df_max_loss)/df_max_loss
  # retaining only unique risk reward ratios


  df_risk_reward=df_risk_reward.unstack().sort_values(ascending=False).dropna()





  #finding max_loss and max_profit corresponding to strikes in df_risk_reward
  my_loss_listt=[]
  my_max_profit_list=[]
  for i in range(len(df_risk_reward)):
    my_loss_listt.append(df_max_loss.iloc[df_risk_reward.index[i][1],df_risk_reward.index[i][0]])
    my_max_profit_list.append(-df_spread.iloc[df_risk_reward.index[i][1],df_risk_reward.index[i][0]]-df_max_loss.iloc[df_risk_reward.index[i][1],df_risk_reward.index[i][0]])

  df_risk_reward=pd.DataFrame(df_risk_reward)
  df_risk_reward['loss']=my_loss_listt
  df_risk_reward['profit']=my_max_profit_list

  #retaining only positive losses and positive risk reward ratios
  df_risk_reward=df_risk_reward[df_risk_reward['loss']>0 ]

  df_risk_reward=df_risk_reward[df_risk_reward[0]>0 ]

  # extracting only those strikes retaind corresponding to df_risk_reward
  strike_1=[]
  strike_2=[]

  for i in range(len(df_risk_reward)):
    strike_1.append(my_strike_list[df_risk_reward.index[i][0]])
    strike_2.append(my_strike_list[df_risk_reward.index[i][1]])
  df_risk_reward['strike_1']=strike_1
  df_risk_reward['strike_2']=strike_2
  df_risk_reward.columns=['reward','loss','profit','strike_1','strike_2']
  df_risk_reward.reset_index(drop=True)
  df_risk_reward.index

  return df_risk_reward
  # my_strike_list

"""## CALCULATE MEAN AND STD"""

def cal_ploting_mean_std_returns(historical_stock_data):
  req_data=pd.DataFrame(historical_stock_data)
  req_data.reset_index(inplace=True)


  per_change=[None]


  for i in range(1,len(req_data)):
    change=((req_data.iloc[i,1]-req_data.iloc[i-1,1])/req_data.iloc[i-1,1])*100
    per_change.append(change)


  req_data['%change']=per_change

  req_data=req_data.drop(index=0)

  req_data
  mean=req_data['%change'].mean()
  std=req_data['%change'].std()
  print(f'mean % chaneg is {mean}, and std dev is{std}')

  # plt.figure(figsize=(10,5))
  # sns.histplot(req_data['%change'],kde=True)
  # plt.axvline(mean,color='r',linestyle='--')
  # plt.axvline(mean+std,color='g',linestyle='--')
  # plt.axvline(mean-std,color='g',linestyle='--')
  # plt.show()
  return mean,std,req_data

import math
def linear_range(current_price,historical_stock_data):


  # data=yf.download(tickers=f'{symbol}.NS',period='max',interval='1d')
  # historical_stock_data=data['Adj Close']
  n=weekdays_until_last_thursday()
  mean,std,req_data=cal_ploting_mean_std_returns(historical_stock_data)


  pos_change_in_next_ndays=n*mean+std*math.sqrt(n)
  neg_change_in_next_ndays=n*mean-std*math.sqrt(n)

  upper_range=current_price*(1+pos_change_in_next_ndays/100)
  lower_range=current_price*(1+neg_change_in_next_ndays/100)

  return pos_change_in_next_ndays,neg_change_in_next_ndays,lower_range,upper_range

def exponential_range(current_price,historical_stock_data):
  # data=yf.download(tickers=f'{symbol}.NS',period='max',interval='1d')
  # historical_stock_data=data['Adj Close']
  mean,std,req_data=cal_ploting_mean_std_returns(historical_stock_data)
  n=weekdays_until_last_thursday()
#linear_range_calculation
  pos_change_in_next_ndays=(n*mean+std*math.sqrt(n))/100
  neg_change_in_next_ndays=(n*mean-std*math.sqrt(n))/100

  upper_range=current_price*math.exp(pos_change_in_next_ndays)
  lower_range=current_price*math.exp(neg_change_in_next_ndays)

  return math.exp(pos_change_in_next_ndays)-1,math.exp(neg_change_in_next_ndays)-1,lower_range,upper_range

"""## VOLATILITY_CONE"""

from datetime import datetime, timedelta

def is_last_thursday(date):
    # Ensure the input date is a datetime object
    if not isinstance(date, datetime):
        date = datetime.strptime(date, '%Y-%m-%d')

    # Get the year and month of the given date
    year = date.year
    month = date.month

    # Find the last day of the month
    if month == 12:
        last_day_of_month = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day_of_month = datetime(year, month + 1, 1) - timedelta(days=1)

    # Calculate the last Thursday of the month
    last_thursday_of_month = last_day_of_month - timedelta(days=(last_day_of_month.weekday() - 3) % 7)

    # Check if the given date is the last Thursday
    return date.date() == last_thursday_of_month.date()

# Example usage
# date_str = '2024-08-29'  # Example date (YYYY-MM-DD)

# date = datetime.strptime(date_str, '%Y-%m-%d')

def plotting_volatility_cone(historical_stock_data):


  mean,std,req_data=cal_ploting_mean_std_returns(historical_stock_data)

  no_days_before_expiry=weekdays_until_last_thursday()
  req_data['vol_next_18_days']=np.nan
  for i in range(0,len(req_data)-n+1):
    req_data.iloc[i,3]=(np.std(req_data.iloc[i:i+n,2]))


  volatility_cone=[]

  for i in range(len(req_data)):
    date=req_data.iloc[i,0]
    if is_last_thursday(date):
      volatility_cone.append(req_data.iloc[i-no_days_before_expiry+1,3])
      # print(req_data.iloc[i-17,0])

  volatility_cone=pd.DataFrame(volatility_cone)
  volatility_cone.columns=['past_volatility']
  n=math.sqrt(252)
  volatility_cone=volatility_cone*n
  # volatility_cone
  # plt.plot(figsize=(10,5))
  # sns.histplot(volatility_cone['past_volatility'],kde=True)
  # plt.show()
  mean_vol = volatility_cone['past_volatility'].mean()
  std_vol = volatility_cone['past_volatility'].std()

  list_range_past_volatility = [
      volatility_cone['past_volatility'].min(),
      mean_vol - 2 * std_vol,
      mean_vol - std_vol,
      mean_vol,
      mean_vol + std_vol,
      mean_vol + 2 * std_vol,
      volatility_cone['past_volatility'].max()
  ]
  return list_range_past_volatility
  # print(f"mean annualised volatility of {no_days_before_expiry} days before expiry  is {volatility_cone['past_volatility'].mean()}and std is {volatility_cone['past_volatility'].std()}")

"""## MONTE CARLO"""

import numpy as np
import matplotlib.pyplot as plt
def monte_carlo_simulation(current_price,historical_stock_data,num_simulations):

  # Define inputs
    mean,std,req_data=cal_ploting_mean_std_returns(historical_stock_data)
    mean_return = mean
    volatility = std
    days = weekdays_until_last_thursday()
       # Adjust this to a higher number if needed

    # Initialize array to store the price paths
    price_paths = np.zeros((days + 1, num_simulations))

    # Set the initial price
    price_paths[0] = current_price

    # Run simulations
    for i in range(num_simulations):
        for t in range(1, days + 1):
            daily_return = np.random.normal(mean_return, volatility)
            price_paths[t, i] = price_paths[t-1, i] * (1 + daily_return/100)

    # Plotting the simulation paths
    # plt.figure(figsize=(10, 6))
    # plt.plot(price_paths)
    # plt.title('Monte Carlo Simulation of Stock Price Over 5 Days')
    # plt.xlabel('Days')
    # plt.ylabel('Stock Price')

    # plt.grid(True)
    # plt.show()

    # Calculate percentiles for the final prices
    final_prices = price_paths[-1]
    lower_bound = np.percentile(final_prices, 5)
    upper_bound = np.percentile(final_prices, 95)

    # print(f"5th Percentile Price: ${lower_bound:.2f}","for ",current_price)
    # print(f"95th Percentile Price: ${upper_bound:.2f}","for",current_price)
    # print("\n")
    return lower_bound,upper_bound

"""## GEOMETRRIC BROWNIAN SIMULATION"""

import numpy as np
import matplotlib.pyplot as plt
def geometric_brownian_motion_simulation(current_price,historical_stock_data,no_of_simulation_to_run):
# Define inputs
    mean,std,req_data=cal_ploting_mean_std_returns(historical_stock_data)
    current_price = current_price
    daily_mean_return = mean/100  # Daily mean return
    daily_volatility = std/100  # Daily volatility
    days = weekdays_until_last_thursday()
    num_simulations = no_of_simulation_to_run
    dt = 1  # time step (1 day)

    # Initialize array to store price paths
    price_paths = np.zeros((days + 1, num_simulations))
    price_paths[0] = current_price

    # Run simulations
    for i in range(num_simulations):
        for t in range(1, days + 1):
            # Simulate random component
            rand = np.random.normal(0, 1)
            # Calculate the price using GBM formula
            price_paths[t, i] = price_paths[t-1, i] * np.exp((daily_mean_return - 0.5 * daily_volatility**2) * dt + daily_volatility * np.sqrt(dt) * rand)

    # Plotting the simulation paths
    # plt.figure(figsize=(10, 6))
    # plt.plot(price_paths)
    # plt.title('Geometric Brownian Motion Simulation of Stock Price Over 5 Days')
    # plt.xlabel('Days')
    # plt.ylabel('Stock Price')
    # plt.grid(True)
    # plt.show()

    # Calculate percentiles for the final prices
    final_prices = price_paths[-1]
    lower_bound = np.percentile(final_prices, 5)
    upper_bound = np.percentile(final_prices, 95)

    # print(f"5th Percentile Price: ${lower_bound:.2f}","for",current_price)
    # print(f"95th Percentile Price: ${upper_bound:.2f}","for",current_price)
    print("\n")
    return lower_bound,upper_bound