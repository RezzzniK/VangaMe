from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import vanga_configs as cfg
# Create A Sentiment Analyzer Object
sentimentAnalyzer = SentimentIntensityAnalyzer()


def get_crypto_coins_evaluations(stories_per_crypto, coin_name):
    """
    function get a list of stories per crypto coin and coin name
    (TBD - support only one coin: remove outer loop and stick with only summation for one coin.
                                  yet, still return list coin_and_eval)
    use sentimentAnalyzer.polarity_scores to get sentiment for story title and add up the total evaluation
    add coin name, overall sentiment and compound sentiment POS/NEG/NEU to list
    :param stories_per_crypto: list of stories per crypto coin
    :param coin_name: crypto coin name
    :return: list of coin and evaluations
    """
    coin_and_eval = []
    idx = 0
    for crypto_coin_stories in stories_per_crypto:
        if len(crypto_coin_stories) == 0:
            idx += 1
            continue
        coin_evaluation = 0
        for story in crypto_coin_stories:
            sentiment_dict = sentimentAnalyzer.polarity_scores(story['title'])
            coin_evaluation += sentiment_dict['compound']

        overall = coin_evaluation / len(crypto_coin_stories)
        coin_and_eval.append([coin_name, overall, get_sentiment_compound(overall)])
        idx += 1

    return coin_and_eval


def get_sentiment_compound(value):
    """
    function get value and return whether it's Positive, Negative or Neutral
    :param value: floating number
    :return: whether value is Positive, Negative or Neutral
    """
    # decide sentiment as positive, negative and neutral
    sentiment_compound = "Positive"

    if value >= cfg.compound_sentiment_threshold:
        sentiment_compound = "Positive"
    elif value < cfg.compound_sentiment_threshold:
        sentiment_compound = "Negative"
    # else:
    #     sentiment_compound = "Neutral"

    return sentiment_compound
