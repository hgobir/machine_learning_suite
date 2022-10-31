# machine_learning_suite

Welcome to my Machine Learning Suite V1

The aim of this project is to demonstrate the viability of Machine Learning with respect to predicting prices of cryptocurrencies. crypto's focusing on are listed below;

- btc - bitcoin
- ada - cardano
- glmr - moonbeam
- usdt - tether
- eth - ethereum
- usdc - usd coin (for testing)


suite is split into 3 stages that have to run consecutively which is very important;

- stage 1 is run
- stage 2 is run for the next 7 consecutive days
- stage 3 is run after

total suite is meant to take 9 days to complete

decide beforehand what day you want stage 1 to run on then once you have done this update the dates list in regression_script.py and reconciliation_script.py with the next 7 days after planned stage 1 run using 'yyyy-mm-dd' format since this is the format coinapi needs to make requests

for example if you planned to run stage 1 on 2023-05-20 the dates list should be updated to;

dates = ['2023-05-21', '2023-05-22', '2023-05-23', '2023-05-24', '2023-05-25', '2023-05-26', '2023-05-27']

remember to update dates list variable in both regression_script.py and reconciliation_script.py!



Prerequisites

- python 3.8
- pycharm
- internet access



Steps

- clone repository into local pycharm ide
- ensure dependencies have compiled and modules are available
- decide what day stage 1 should run then update dates variable in regression_script.py and reconciliation_script.py accordingly
- enter crypto from list into stage_1/models/main.py - this runs the model method in the regression_script.py
- do this for other cryptos in list above
- after finishing stage 1 wait until next day to run stage 2
- run both twitter_sentiment_analysis_script.py and reddit_sentiment_analysis_script.py in any order - repeat this for next 7 days
- after finishing stage 2 wait until next day to run stage 3
- enter crypto from list into stage_3/analysis/main.py - this runs the analysis method in the reconciliation_script.py
- do this for same cryptos that were run in stage 1












