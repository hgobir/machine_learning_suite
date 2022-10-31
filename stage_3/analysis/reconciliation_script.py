"""*****************************************************************************
Purpose: Reconciles prediction price values and actual price values
This program uses data from CoinAPI to get actual price data for 7 day prediction window and calculates % error

Important: remember to amend dates variable accordingly

Authentication: Please create own CoinAPI key id and set it to api_key variable below
or use hamza's personal CoinAPI key listed on Chapter 7.1 Personal API Keys section of thesis
-------------------------------------------------------------------
****************************************************************************"""

import json
import pandas as pd
import requests
from matplotlib.ticker import FormatStrFormatter
from matplotlib import pyplot as plt

# Authentication - see documentation top of file
api_key = ''

dates = ['2022-10-05', '2022-10-06', '2022-10-07', '2022-10-08', '2022-10-09', '2022-10-10', '2022-10-11']


def return_url(crypto, date):
    if crypto == 'glmr':
        return f'https://rest.coinapi.io/v1/ohlcv/KRAKEN_SPOT_GLMR_USD/history?period_id=1DAY&time_start={date}T00:00:00&limit=500'
    elif crypto == 'btc':
        return f'https://rest.coinapi.io/v1/ohlcv/BITSTAMP_SPOT_BTC_USD/history?period_id=1DAY&time_start={date}T00:00:00&limit=500'
    elif crypto == 'eth':
        return f'https://rest.coinapi.io/v1/ohlcv/BITSTAMP_SPOT_ETH_USD/history?period_id=1DAY&time_start={date}T00:00:00&limit=500'
    elif crypto == 'ada':
        return f'https://rest.coinapi.io/v1/ohlcv/BITSTAMP_SPOT_ADA_USD/history?period_id=1DAY&time_start={date}T00:00:00&limit=500'
    elif crypto == 'usdt':
        return f'https://rest.coinapi.io/v1/ohlcv/BITSTAMP_SPOT_USDT_USD/history?period_id=1DAY&time_start={date}T00:00:00&limit=500'


def calculate_percent_error(estimated_value, actual_value):
    percent_error = ((estimated_value - actual_value) / actual_value) * 100
    return percent_error


headers = {
    #   'Accepts': 'application/json',
    'X-CoinAPI-Key': api_key
}


def analysis(crypto: str):
    actual_price_list = []
    predictions = pd.read_csv(
        f'C:/Users/Hamza/PycharmProjects/dissertation_project/data/stage_1/datasets/{crypto}/{crypto}_7_day_model_prediction.csv')
    for date in dates:
        url = return_url(crypto, date)
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)
        print(f'for {date} this is the value returned')
        print("\n")
        print(data)
        print("\n")

        df_json = response.json()
        df = pd.DataFrame.from_dict(df_json)

        actual_price = df['price_close'].values[0]

        actual_price_list.append(actual_price)

    predictions['actual_price_close'] = actual_price_list

    predictions.to_csv(
        f'C:/Users/Hamza/PycharmProjects/dissertation_project/data/stage_3/{crypto}/{crypto}_7_day_actual.csv',
        encoding='utf-8', index=False)

    new_count = len(predictions)
    percent_error_list = []
    for i in range(0, new_count):
        print("")
        date = predictions['date'].values[i]
        estimated_value = predictions['predicted_price_close'].values[i]
        actual_value = predictions['actual_price_close'].values[i]
        print("")
        print(f'for {date} the estimated value is {estimated_value} and actual value is {actual_value}')
        print("")
        percent_error = calculate_percent_error(estimated_value, actual_value)
        # percent_error = ((estimated_value - actual_value) / actual_value) * 100
        print(f'error between predicted and actual is {percent_error}%')
        percent_error_list.append(percent_error)

    predictions['percent_error'] = percent_error_list

    predictions.to_csv(
        f'C:/Users/Hamza/PycharmProjects/dissertation_project/data/stage_3/{crypto}/{crypto}_percent_error.csv',
        encoding='utf-8',
        index=False)

    plt.plot(dates, percent_error_list, color="red", label="percent error")
    plt.legend()
    plt.title(f"${crypto} percentage error")
    plt.xticks(fontsize=5)
    plt.xlabel('days')
    plt.ylabel('percent (%)')
    plt.savefig(f'C:/Users/Hamza/PycharmProjects/dissertation_project/data/stage_3/{crypto}/percent_error_line.png')
    plt.show()

    new_prediction_list = predictions['predicted_price_close'].values
    new_actual_list = predictions['actual_price_close'].values

    fig, ax = plt.subplots()
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.4f'))
    plt.plot(dates, new_actual_list, color="orange", label="actual")
    plt.plot(dates, new_prediction_list, color='blue', label="predicted")

    plt.legend()
    plt.title(f"${crypto} predicted vs actual")
    plt.xticks(fontsize=5)
    plt.yticks(fontsize=6)
    plt.xlabel('days')
    plt.ylabel('dollars ($)')
    plt.savefig(f'C:/Users/Hamza/PycharmProjects/dissertation_project/data/stage_3/{crypto}/predicted_vs_actual.png')
    plt.show()
