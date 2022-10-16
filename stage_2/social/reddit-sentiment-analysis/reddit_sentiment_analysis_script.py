'''*****************************************************************************
Purpose: To analyze the sentiments of the reddit
This program uses Vader SentimentIntensityAnalyzer to calculate the ticker compound value.
You can change multiple parameters to suit your needs. See below under "set program parameters."
Implementation:
I am using sets for 'x in s' comparison, sets time complexity for "x in s" is O(1) compare to list: O(n).
Limitations:
It depends mainly on the defined parameters for current implementation:
It completely ignores the heavily downvoted comments, and there can be a time when
the most mentioned ticker is heavily downvoted, but you can change that in upvotes variable.
-------------------------------------------------------------------
****************************************************************************'''
from datetime import date
import praw
import re
import os
from data import *
import time
import pandas as pd
import matplotlib.pyplot as plt
import squarify
from nltk.sentiment.vader import SentimentIntensityAnalyzer

start_time = time.time()
today = date.today()

reddit = praw.Reddit(
    user_agent='Comment Extraction',
    client_id='m-1u4PKqu-quQ1dzglQMfA',
    client_secret='LjmuZFBmd6sM_F066HT2W6jH6ibaoQ'
)

'''############################################################################'''
# set the program parameters
subs = ['CryptoCurrency']  # sub-reddit to search
submission_name = 'UNRELIABLE SOURCE'  # posts title to search
goodAuth = {'AutoModerator'}  # authors whom comments are allowed more than once
uniqueCmt = True  # allow one comment per author per symbol
# ignoreAuthP = {'example'}  # authors to ignore for posts
# ignoreAuthC = {'example'}  # authors to ignore for comment
upvoteRatio = 0.70  # upvote ratio for post to be considered, 0.70 = 70%
ups = 20  # define # of upvotes, post is considered if upvotes exceed this #
limit = 1000  # define the limit, comments 'replace more' limit
upvotes = 2  # define # of upvotes, comment is considered if upvotes exceed this #
path = "C:/Users/Hamza/PycharmProjects/dissertation_project/"
'''############################################################################'''

posts, count, c_analyzed, tickers, titles, a_comments = 0, 0, 0, {}, [], {}
cmt_auth = {}


def replace_with_ticker(selftext):
    # clean bitcoin references
    insensitive_bitcoin = re.compile(re.escape('Bitcoin'), re.IGNORECASE)
    converted_bitcoin = insensitive_bitcoin.sub('BTC', selftext)
    # clean ethereum references
    insensitive_ethereum = re.compile(re.escape('Ethereum'), re.IGNORECASE)
    converted_ethereum = insensitive_ethereum.sub('ETH', converted_bitcoin)
    # clean cardano references
    insensitive_cardano = re.compile(re.escape('Cardano'), re.IGNORECASE)
    converted_cardano = insensitive_cardano.sub('ADA', converted_ethereum)
    # clean moonbeam references
    insensitive_moonbeam = re.compile(re.escape('Moonbeam'), re.IGNORECASE)
    converted_moonbeam = insensitive_moonbeam.sub('GLMR', converted_cardano)
    # clean tether references
    insensitive_tether = re.compile(re.escape('Tether'), re.IGNORECASE)
    converted_tether = insensitive_tether.sub('USDT', converted_moonbeam)
    return converted_tether


for sub in subs:
    subreddit = reddit.subreddit(sub)
    hot_python = subreddit.hot(limit=1500)  # sorting posts by hot
    # Extracting comments, symbols from subreddit
    for submission in hot_python:
        # checking: post upvote ratio # of upvotes, post flair, and author
        # submission.link_flair_text
        if submission.link_flair_text is not None and not submission.link_flair_text.endswith(submission_name):
            new_selftext = replace_with_ticker(submission.selftext)
            submission.selftext = new_selftext
            submission.comment_sort = 'new'
            comments = submission.comments
            titles.append(submission.link_flair_text)
            posts += 1
            submission.comments.replace_more(limit=limit)
            for comment in comments:
                print(comment.body)
                print(comment.score)
                # try except for deleted account?
                try:
                    auth = comment.author.name
                except:
                    pass
                c_analyzed += 1

                # checking: comment upvotes and author
                if comment.score > upvotes:
                    new_comment = replace_with_ticker(comment.body)
                    split = new_comment.split(" ")
                    for word in split:
                        word = word.replace("$", "")
                        # upper = ticker, length of ticker <= 5, excluded words,
                        # print(word)
                        if word.isupper() and len(word) <= 5 and word not in blacklist and word in crypto:
                            # print('here')

                            # unique comments, try/except for key errors
                            if uniqueCmt and auth not in goodAuth:
                                try:
                                    if auth in cmt_auth[word]: break
                                except:
                                    pass

                            # counting tickers
                            if word in tickers:
                                print(f"this is ticker being analysed ${word}")
                                tickers[word] += 1
                                a_comments[word].append(comment.body)
                                cmt_auth[word].append(auth)
                                count += 1
                            else:
                                tickers[word] = 1
                                cmt_auth[word] = [auth]
                                a_comments[word] = [comment.body]
                                count += 1

# sorts the dictionary
symbols = dict(sorted(tickers.items(), key=lambda item: item[1], reverse=True))
top_picks = list(symbols.keys())
time = (time.time() - start_time)

# print top picks
print("It took {t:.2f} seconds to analyze {c} comments in {p} posts in {s} subreddits.\n".format(t=time, c=c_analyzed,
                                                                                                 p=posts, s=len(subs)))
print("Posts analyzed saved in titles")

for i in titles: print(i)  # prints the title of the posts analyzed

# print(f"\n{picks} most mentioned picks: ")
print(top_picks)
times = []
top = []
for i in top_picks:
    print(f"{i}: {symbols[i]}")
    times.append(symbols[i])
    top.append(f"{i}: {symbols[i]}")

# Applying Sentiment Analysis
scores, s = {}, {}

vader = SentimentIntensityAnalyzer()

# adding custom words from data.py
vader.lexicon.update(new_words)

picks_sentiment = list(symbols.keys())
for symbol in picks_sentiment:
    crypto_comments = a_comments[symbol]
    for cmnt in crypto_comments:
        score = vader.polarity_scores(cmnt)
        if symbol in s:
            s[symbol][cmnt] = score
        else:
            s[symbol] = {cmnt: score}
        if symbol in scores:
            for key, _ in score.items():
                scores[symbol][key] += score[key]
        else:
            scores[symbol] = score

    # calculating avg.
    for key in score:
        scores[symbol][key] = scores[symbol][key] / symbols[symbol]
        scores[symbol][key] = "{pol:.3f}".format(pol=scores[symbol][key])

# printing sentiment analysis
print(f"\nSentiment analysis for cryptos:")
df = pd.DataFrame(scores)
df.index = ['Bearish', 'Neutral', 'Bullish', 'Sentiment']
df = df.T
print(df)

# Date Visualization
# most mentioned picks
squarify.plot(sizes=times, label=top, alpha=.7)
plt.axis('off')
plt.title(f"most mentioned crypto on reddit - {today}")
plt.savefig(f'C:/Users/Hamza/PycharmProjects/dissertation_project/data/stage_2/{today}/reddit/most_mentioned.png')
plt.show()

# Sentiment analysis
df = df.astype(float)
colors = ['red', 'blue', 'forestgreen', 'coral']
df.plot(kind='bar', color=colors, title=f"sentiment analysis on reddit - {today}")
# plt.legend(loc=2, prop={'size': 6})
plt.legend(loc='best')
plt.savefig(f'C:/Users/Hamza/PycharmProjects/dissertation_project/data/stage_2/{today}/reddit/sentiment.png')
plt.show()

