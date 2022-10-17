import json
import numpy as np
import pandas as pd
import requests
import time

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

list_of_urls = {
    "glmr": 'https://rest.coinapi.io/v1/ohlcv/KRAKEN_SPOT_GLMR_USD/history?period_id=1DAY&time_start=2022-01-11T00:00:00&limit=500',
    "btc": 'https://rest.coinapi.io/v1/ohlcv/BITSTAMP_SPOT_BTC_USD/history?period_id=1DAY&time_start=2022-01-11T00:00:00&limit=500',
    "eth": 'https://rest.coinapi.io/v1/ohlcv/BITSTAMP_SPOT_ETH_USD/history?period_id=1DAY&time_start=2022-01-11T00:00:00&limit=500',
    "ada": 'https://rest.coinapi.io/v1/ohlcv/BITSTAMP_SPOT_ADA_USD/history?period_id=1DAY&time_start=2022-01-11T00:00:00&limit=500',
    "usdt": 'https://rest.coinapi.io/v1/ohlcv/BITSTAMP_SPOT_USDT_USD/history?period_id=1DAY&time_start=2022-01-11T00:00:00&limit=500'
}

# api_key = 'AE75B183-3C7D-4DD5-81D6-67CD8386395F'
# api_key = 'B6A54D76-BCD6-45AE-9F5E-E87536D4255C'
api_key = 'B7843BD3-39AB-4D68-87EF-4C6D988627E7'

projection = 7

dates = ['2022-10-05', '2022-10-06', '2022-10-07', '2022-10-08', '2022-10-09', '2022-10-10', '2022-10-11']


def model(crypto: str):
    start_time = time.time()

    url = list_of_urls[crypto]

    headers = {
        'X-CoinAPI-Key': api_key
    }

    response = requests.get(url, headers=headers)
    data = json.loads(response.text)

    df_json = response.json()
    df = pd.DataFrame.from_dict(df_json)

    df['symbol'] = crypto.capitalize()
    df['currency'] = 'USD'
    df_converted = df.convert_dtypes()

    df_converted = df_converted.drop(columns=['time_period_end'])
    df_converted = df_converted.rename(columns={"time_period_start": "date"})

    df_converted['date'] = df_converted['date'].str.split('T').str.get(0)
    df_converted['time_open'] = df_converted['time_open'].str.split('T').str.get(1)
    df_converted['time_open'] = df_converted['time_open'].str.replace('Z', '')
    df_converted['time_close'] = df_converted['time_close'].str.split('T').str.get(1)
    df_converted['time_close'] = df_converted['time_close'].str.replace('Z', '')

    df_converted.to_csv(f'C:/Users/Hamza/PycharmProjects/dissertation_project/data/stage_1/datasets/{crypto}_original'
                        f'.csv', encoding='utf-8', index=False)

    df_converted['prediction_7_days'] = df_converted[['price_close']].shift(-projection)

    df_converted.to_csv(f'C:/Users/Hamza/PycharmProjects/dissertation_project/data/stage_1/datasets/{crypto}_prediction.csv', encoding='utf-8', index=False)

    X = np.array(df_converted.iloc[:, [False, False, False, True, True, True, True, True, True, False, False, False]])
    X = X[:-projection]
    y = df_converted['prediction_7_days'].values
    y = y[:-projection]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.25)
    lin_reg = LinearRegression()
    lin_reg.fit(X_train, y_train)
    lin_reg_confidence = lin_reg.score(X_test, y_test)
    x_projection = np.array(
        df_converted.iloc[:, [False, False, False, True, True, True, True, True, True, False, False, False]])[
                   -projection:]
    lin_reg_prediction = lin_reg.predict(x_projection)
    df_pred = pd.DataFrame({'date': dates, 'predicted_price_close': lin_reg_prediction})

    df_pred.to_csv(f'C:/Users/Hamza/PycharmProjects/dissertation_project/data/stage_1/datasets/{crypto}_7_day_model_prediction.csv', encoding='utf-8', index=False)

    end_time = (time.time() - start_time)