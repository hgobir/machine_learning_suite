# subjectivity is float between 0-1 where 0 is very objective and 1 is very subjective
# polarity is float between -1 and 1 with -1 being negative sentiment and 1 being positive sentiment
from datetime import date
import time
import pandas as pd
import matplotlib.pyplot as plt
from textblob import TextBlob
import tweepy
import numpy as np
import re
import string
from nltk.sentiment.vader import SentimentIntensityAnalyzer

tweet_limit = 3000

plt.style.use('fivethirtyeight')

start_time = time.time()
today = date.today()

# Authentication
client_id = '2Q4H1OppVBLvIZN8ouaSwHX7C'
client_secret = 'iA2KuGZ0e45karZnhJM7CwoUMdP9WJAJkk4fVDxOPF4xhHoR57'
bearer_token = 'AAAAAAAAAAAAAAAAAAAAAH%2BRggEAAAAA8EJy8OPPNrGBoA9nHx%2FDK%2BuIh2E%3Dpz6Cf3L6S8T00WDQyLcrFwkd3g0My8KN1eOvpeaWH1mfcCzEP8'
access_token = '959309679275814917-7EhjFUUjPNz1IbSTrK7T3VPA4LW8Zhb'
access_token_secret = 'kaNDmQkYR1nqpXmuw8q2dvbbVZQ0u6gPJ4Ky0m2KaKAQa'

positive = 0
negative = 0
neutral = 0
polarity = 0
tweet_list = []
neutral_list = []
negative_list = []
positive_list = []

client = tweepy.Client(bearer_token, client_id, client_secret, access_token, access_token_secret,
                       wait_on_rate_limit=True)

search_terms = ['#bitcoin -is_retweet', '#ethereum -is_retweet', '#moonbeam -is_retweet', '#tether -is_retweet',
                '#cardano -is_retweet']
keywords = ['BTC', 'ETH', 'GLMR', 'USDT', 'ADA']
crypto_colors = ['yellow', 'cyan', 'magenta', 'green', 'blue']


def count_values_in_column(data, feature):
    total = data.loc[:, feature].value_counts(dropna=False)
    percentage = round(data.loc[:, feature].value_counts(dropna=False, normalize=True) * 100, 2)
    return pd.concat([total, percentage], axis=1, keys=['Total', 'Percentage'])


def clean_tweet_function(tweet):
    clean_tweet = re.sub('#bitcoin', 'bitcoin', tweet)  # removes the # from bitcoin
    clean_tweet = re.sub('#Bitcoin', 'Bitcoin', clean_tweet)  # removes the # from Bitcoin

    clean_tweet = re.sub('#ethereum', 'ethereum', clean_tweet)  # removes the # from ethereum
    clean_tweet = re.sub('#Ethereum', 'Ethereum', clean_tweet)  # removes the # from Ethereum

    clean_tweet = re.sub('#moonbeam', 'moonbeam', clean_tweet)  # removes the # from moonbeam
    clean_tweet = re.sub('#Moonbeam', 'Moonbeam', clean_tweet)  # removes the # from Moonbeam

    clean_tweet = re.sub('#tether', 'tether', clean_tweet)  # removes the # from tether
    clean_tweet = re.sub('#Tether', 'Tether', clean_tweet)  # removes the # from Tether

    clean_tweet = re.sub('#cardano', 'cardano', clean_tweet)  # removes the # from cardano
    clean_tweet = re.sub('#Cardano', 'Cardano', clean_tweet)  # removes the # from Cardano

    clean_tweet = re.sub('#[A-Za-z0-9]+', '', clean_tweet)  # removes any strings with a #
    clean_tweet = re.sub('\\n', '', clean_tweet)  # removes the \n string
    clean_tweet = re.sub('https?:\/\/\S+', '', clean_tweet)  # removes hyperlinks
    clean_tweet = re.sub('RT @\w+: ', "", clean_tweet)  # removes RT and @mentions
    final_clean_tweet = clean_tweet.translate(str.maketrans('', '', string.punctuation))  # removes punctuation
    return final_clean_tweet.strip()


# subjectivity ranges from 0 (very subjective) to 1 (very objective)
def get_subjectivity(tweet):
    return TextBlob(tweet).sentiment.subjectivity


# polarity ranges from -1 (very negative) to 1 (very positive)
def get_polarity(tweet):
    return TextBlob(tweet).sentiment.polarity


def get_sentiment(score):
    if score < 0:
        return 'Bearish'
    elif score == 0:
        return 'Neutral'
    else:
        return 'Bullish'


def get_percentage(part, whole):
    return 100 * float(part) / float(whole)


for search_param in search_terms:

    index = search_terms.index(search_param)
    current_color = crypto_colors[index]
    current_keyword = keywords[index]

    # create paginator object and store tweets in variable and get full text
    for tweet in tweepy.Paginator(client.search_recent_tweets,
                                  query=search_param,
                                  tweet_fields=['author_id', 'created_at', 'text', 'source', 'lang', 'geo'],
                                  # max_results=100).flatten(limit=3000):
                                  max_results=100).flatten(limit=tweet_limit):

        # filter only english tweets
        if tweet.lang == 'en':
            cleaned_tweet = clean_tweet_function(tweet.text)
            tweet_list.append(cleaned_tweet)
            analysis = TextBlob(cleaned_tweet)
            score = SentimentIntensityAnalyzer().polarity_scores(cleaned_tweet)
            neg = score['neg']
            neu = score['neu']
            pos = score['pos']
            comp = score['compound']

            polarity += analysis.sentiment.polarity

            if neg > pos:
                negative_list.append(cleaned_tweet)
                negative += 1
            elif pos > neg:
                positive_list.append(cleaned_tweet)
                positive += 1
            elif pos == neg:
                neutral_list.append(cleaned_tweet)
                neutral += 1

    print(f'this is what index is currently: ${search_terms.index(search_param)}')
    positive = get_percentage(positive, len(tweet_list))
    negative = get_percentage(negative, len(tweet_list))
    neutral = get_percentage(neutral, len(tweet_list))
    polarity = get_percentage(polarity, len(tweet_list))
    positive = format(positive, '.1f')
    negative = format(negative, '.1f')
    neutral = format(neutral, '.1f')

    tweet_list = pd.DataFrame({'tweets': tweet_list})
    neutral_list = pd.DataFrame(neutral_list)
    negative_list = pd.DataFrame(negative_list)
    positive_list = pd.DataFrame(positive_list)
    print("total number:", len(tweet_list))
    print("positive number:", len(positive_list))
    print("negative number:", len(negative_list))
    print("neutral number:", len(neutral_list))

    path = "C:/Users/Hamza/PycharmProjects/dissertation_project"

    # Creating PieCart
    labels = ['Positive [' + str(positive) + '%]', 'Neutral [' + str(neutral) + '%]',
              'Negative [' + str(negative) + '%]']
    sizes = [positive, neutral, negative]
    colors = ['yellowgreen', 'blue', 'red']
    patches, texts = plt.pie(sizes, colors=colors, startangle=90)
    plt.style.use('default')
    plt.legend(labels)
    plt.title(f"sentiment analysis on twitter for {current_keyword} - {today}")
    plt.axis('equal')

    plt.savefig(f'{path}/data/stage_2/{today}/twitter/{str.lower(current_keyword)}/sentiment.png')

    plt.show()

    tweet_list.drop_duplicates(inplace=False)

    # Creating new dataframe and new features
    # tweet_list = pd.DataFrame(tweet_list)

    # Calculating Negative, Positive, Neutral and Compound values
    tweet_list['subjectivity'] = tweet_list['tweets'].apply(get_subjectivity)
    tweet_list['polarity'] = tweet_list['tweets'].apply(get_polarity)

    for index, row in tweet_list['tweets'].iteritems():
        score = SentimentIntensityAnalyzer().polarity_scores(row)
        neg = score['neg']
        neu = score['neu']
        pos = score['pos']
        comp = score['compound']

        if neg > pos:
            tweet_list.loc[index, 'sentiment'] = "negative"
            tweet_list.loc[index, 'neg'] = neg
            tweet_list.loc[index, 'neu'] = neu
            tweet_list.loc[index, 'pos'] = pos
            tweet_list.loc[index, 'compound'] = comp
        elif pos > neg:
            tweet_list.loc[index, 'sentiment'] = "positive"
            tweet_list.loc[index, 'neg'] = neg
            tweet_list.loc[index, 'neu'] = neu
            tweet_list.loc[index, 'pos'] = pos
            tweet_list.loc[index, 'compound'] = comp
        else:
            tweet_list.loc[index, 'sentiment'] = "neutral"
            tweet_list.loc[index, 'neg'] = neg
            tweet_list.loc[index, 'neu'] = neu
            tweet_list.loc[index, 'pos'] = pos
            tweet_list.loc[index, 'compound'] = comp

    # Creating new data frames for all sentiments (positive, negative and neutral)
    tweet_list_negative = tweet_list[tweet_list["sentiment"] == "negative"]
    tweet_list_positive = tweet_list[tweet_list["sentiment"] == "positive"]
    tweet_list_neutral = tweet_list[tweet_list["sentiment"] == "neutral"]

    # Count_values for sentiment
    print(count_values_in_column(tweet_list, "sentiment"))
    #
    # create data for Pie Chart
    pc = count_values_in_column(tweet_list, "sentiment")
    names = pc.index
    size = pc["Percentage"]

    # Create a circle for the center of the plot
    # my_circle = plt.Circle((0, 0), 0.7, color='white')
    # plt.pie(size, labels=names, colors=['green', 'blue', 'red'])
    # p = plt.gcf()
    # p.gca().add_artist(my_circle)
    #
    # plt.savefig(f'{path}/data/stage_2/{today}/twitter/{str.lower(current_keyword)}/pie.png')
    #
    # plt.show()

    # create scatter plot to show sentiment and polarity
    plt.figure(figsize=(8, 6))
    for i in range(0, tweet_list.shape[0]):
        plt.scatter(tweet_list['polarity'][i], tweet_list['subjectivity'][i], color=current_color)
    plt.title(f'sentiment analysis on twitter for ${current_keyword} scatter plot - {today}')
    plt.xlabel('Polarity')
    plt.ylabel('Subjectivity')

    plt.savefig(f'{path}/data/stage_2/{today}/twitter/{str.lower(current_keyword)}/polarity_sentiment_scatter.png')

    plt.show()

    # create bar chart to show counts of text sentiment
    tweet_list['sentiment'].value_counts().plot(kind='bar')
    plt.title(f'sentiment analysis on twitter for ${current_keyword} bar chart - {today}')
    plt.xlabel('Sentiment')
    plt.ylabel('Number of Tweets')
    plt.xticks(rotation=0)

    plt.savefig(f'{path}/data/stage_2/{today}/twitter/{str.lower(current_keyword)}/bar.png')

    plt.show()

    positive, negative, neutral, polarity = 0, 0, 0, 0

    tweet_list, neutral_list, negative_list, positive_list = [], [], [], []

#
time = (time.time() - start_time)

print(f"Took {time} seconds")
