import multiprocessing as mlpcs
from multiprocessing import current_process
import yfinance as yf
import pandas as pd
from dateutil import parser
from datetime import datetime, timedelta, timezone
from time import perf_counter
from pygooglenews import GoogleNews

from vanga_configs import *
from vanga_configs import __DETAILED_PRINTING__
from core.pygooglenews_core import get_stories, get_entries
from core.vaderSentiment_core import get_sentiment_compound, get_crypto_coins_evaluations
from utils.dates_util import init_all_dates_for_ticker, get_dates_between_dates, get_str_dates_from_dates
from utils.files_util import output_temporary_data_to_coin_file, output_predictions, \
    create_data_collecting_directory, output_final_data_to_summary_file, write_prediction_to_sql

import sqlite3


# __DETAILED_PRINTING__ = False


# db_filename = "vanga_me.db"
# yfinance_table_name = 'vanga_me_yfinance_data'
# prediction_accuracy_table_name = "vanga_prediction_accuracy"

# Change dfObj to_sql function to try except for each row

def collect_data_for_coins_history(coin_name, yf_tickers_name, start_date, end_date):
    try:
        data = yf.download(tickers=yf_tickers_name, start=start_date, end=end_date)
    except Exception as e:
        print(f'Error downloading data from yfinance: {e}')

    if data.empty:
        return data

    indexNamesArr = data.index.values
    listOfRowIndexLabels = list(indexNamesArr)
    dates = []

    for date in listOfRowIndexLabels:
        t = pd.to_datetime(str(date))
        dates.append(t.strftime('%Y-%m-%d'))

    Open = data['Open']
    close = data['Close']

    # columns_names = ["coin_name", "evaluation_date", "open_rate", "close_rate"]

    # date_open_close = []

    coin = coin_name.replace('"', "")
    try:
        con = sqlite3.connect(db_filename)
        cur = con.cursor()
        for idx in range(len(dates)):
            insert_yfinance_data_sql_command = f"INSERT OR IGNORE INTO {yfinance_table_name} VALUES(?, ?, ?, ?);"
            cur.execute(insert_yfinance_data_sql_command, (coin, str(dates[idx]), float(Open[idx]), float(close[idx])))

        con.commit()
        con.close()

        print(
            f'============================================================COLLECTED YFINANCE DATA FOR {coin_name}============================================================')
    except sqlite3.Error as err:
        print('Sql error: %s' % (' '.join(err.args)))
        print("Exception class is: ", err.__class__)

    return data
    # return dfObj
    # date_open_close.append((str(coin_name), str(dates[idx]), float(Open[idx]), float(close[idx])))

    # table_name = yfinance_table_name
    # conn = sqlite3.connect(db_filename, timeout=20)

    # dfObj = pd.DataFrame(date_open_close, columns=columns_names, index=dates)

    # try:
    #    dfObj.to_sql(table_name, conn, if_exists='append', index=False)
    # except sqlite3.Error as err:
    #    print('Sql error: %s' % (' '.join(err.args)))
    #    print("Exception class is: ", err.__class__)

    # con.close()

    # return dfObj


def write_predictions_accuracy_to_sql_for_each_date(coin_name, yf_tickers_name, start_date, end_date, return_dict):
    data_history = collect_data_for_coins_history(coin_name, yf_tickers_name, start_date, end_date)
    if data_history.empty:
        return

    try:
        conn = sqlite3.connect(db_filename, timeout=20)
        cur = conn.cursor()

        coin = coin_name.replace('"', "")
        get_yfinance_data_sql_command = f"""SELECT evaluation_date, close_rate-open_rate 
                                            FROM {yfinance_table_name} 
                                            WHERE coin_name = '{coin}'"""
        cur.execute(get_yfinance_data_sql_command)
        yfinance_data = cur.fetchall()

        get_prediction_accuracy_data_sql_command = f"""SELECT coin_name, prediction_date 
                                                        FROM {prediction_accuracy_table_name} 
                                                        WHERE coin_name = '{coin}'"""
        cur.execute(get_prediction_accuracy_data_sql_command)
        prediction_accuracy_data = cur.fetchall()
        conn.close()
    except sqlite3.Error as err:
        print('Sql error: %s' % (' '.join(err.args)))
        print("Exception class is: ", err.__class__)

    loop_dates = []
    coin_real_evaluations_per_date = []
    # get list of dates
    # get real sentiment for each date
    for row in yfinance_data:
        loop_dates.append(row[0])
        coin_real_evaluations_per_date.append(row[1])

    print(f"start scraping {coin_name}")
    gn = GoogleNews()
    for dates_idx in range(0, len(loop_dates) - 2):
        if (coin_name, loop_dates[dates_idx + 2]) in prediction_accuracy_data:
            if __DETAILED_PRINTING__:
                print(f"Already found data for '{coin_name}' on date '{loop_dates[dates_idx + 2]}'")
            continue

        if __DETAILED_PRINTING__:
            print(f"{coin_name} => DATES: {loop_dates[dates_idx]} - {loop_dates[dates_idx + 1]}")
        entries_per_crypto = [get_entries(gn, coin_name, start=loop_dates[dates_idx], end=loop_dates[dates_idx + 1])]

        if not entries_per_crypto[0]:
            continue

        coin_stories = []
        for entries in entries_per_crypto:
            stories = get_stories(entries)
            coin_stories.append(stories)

        if not coin_stories[0]:
            continue

        try:
            conn = sqlite3.connect(db_filename)
            cur = conn.cursor()

            for story in coin_stories[0]:
                insert_story_data_sql_command = f"""INSERT OR IGNORE INTO {stories_data_table_name} VALUES(\"{coin_name}\", 
                \"{story['id']}\", \"{story['title']}\", \"{story['link']}\", \"{story['published']}\");"""

                insert_story_data_sql_command = f"INSERT OR IGNORE INTO {stories_data_table_name} VALUES(?, ?, ?, ?, ?);"
                cur.execute(insert_story_data_sql_command,
                            (coin_name, story['id'], story['title'], story['link'], story['published']))

            conn.commit()
            conn.close()

        except sqlite3.Error as err:
            print('Sql error: %s' % (' '.join(err.args)))
            print("Exception class is: ", err.__class__)

        coins_sentiment_evaluation = get_crypto_coins_evaluations(coin_stories, coin_name)

        prediction_evaluation = coins_sentiment_evaluation[0][1]
        prediction_sentiment = coins_sentiment_evaluation[0][2]
        real_evaluation = coin_real_evaluations_per_date[dates_idx + 2]
        real_sentiment = get_sentiment_compound(real_evaluation)

        write_prediction_to_sql(coin_name, loop_dates[dates_idx + 2], prediction_evaluation, prediction_sentiment,
                                real_evaluation, real_sentiment)

        try:
            conn = sqlite3.connect(db_filename, timeout=20)
            cur = conn.cursor()

            get_prediction_accuracy_data_sql_command = f"SELECT * FROM {prediction_accuracy_table_name} where coin_name = '{coin_name}'"
            cur.execute(get_prediction_accuracy_data_sql_command)
            rows = cur.fetchall()
            conn.close()

            return_dict[coin_name] = rows

        except sqlite3.Error as err:
            print('Sql error: %s' % (' '.join(err.args)))
            print("Exception class is: ", err.__class__)


def output_crypto_prediction_accuracy_to_file_between_dates(coin_name, coin_filename, yf_tickers_name, return_dict=None,
                                                            dates_str=None):
    amount_of_correct_prediction = 0
    amount_of_dates_with_data = 0
    amount_of_stories_per_crypto = 0
    total_compound_accuracy_correlation = 0
    start_seconds_time = perf_counter()
    gn = GoogleNews()

    print(f"starting {coin_name}")

    if dates_str is None or not len(dates_str):
        dates_str = init_all_dates_for_ticker(yf_tickers_name)

        if dates_str is None or not len(dates_str):
            print(f'{coin_name}: problem getting dates_str')
            return

    for dates_idx in range(0, len(dates_str) - 1):
        if __DETAILED_PRINTING__:
            print(f'{current_process().name}: {dates_str[dates_idx]} - {dates_str[dates_idx + 1]}')
            print('-------------------------------------------')
        try:
            data = yf.download(tickers=yf_tickers_name, start=dates_str[dates_idx],
                               end=dates_str[dates_idx + 1])  # , period = '2h', interval = '1h')
        except Exception as e:
            print(f'Error downloading data from yfinance: {e}')
            continue

        if not len(data):
            continue

        actual_evaluation_sum, actual_evaluation_avg = 0, 0
        for idx in range(len(data)):
            actual_evaluation_sum += float(data.iloc[idx]['Close']) - float(data.iloc[idx]['Open'])

        try:
            actual_evaluation = actual_evaluation_sum / len(data)
        except ZeroDivisionError as ex:
            print(f'error: {ex}')
            continue

        actual_evaluation_sentiment = get_sentiment_compound(actual_evaluation)

        entries_per_crypto = [get_entries(gn, coin_name, start=dates_str[dates_idx], end=dates_str[dates_idx + 1])]
        if not entries_per_crypto[0]:
            continue

        stories_per_crypto = []
        for entries in entries_per_crypto:
            stories = get_stories(entries)
            stories_per_crypto.append(stories)
            amount_of_stories_per_crypto += len(stories)
        if not stories_per_crypto[0]:
            continue

        coins_sentiment_evaluation = get_crypto_coins_evaluations(stories_per_crypto, coin_name)

        amount_of_dates_with_data, amount_of_correct_prediction, total_compound_accuracy_correlation = output_temporary_data_to_coin_file(
            coin_filename,
            dates_str, dates_idx,
            coins_sentiment_evaluation,
            actual_evaluation,
            total_compound_accuracy_correlation,
            actual_evaluation_sentiment,
            amount_of_correct_prediction, amount_of_dates_with_data)

        try:
            prediction_sentiment = coins_sentiment_evaluation[0][2]
            prediction_compound_evaluation = coins_sentiment_evaluation[0][1]
            correct_prediction = int(actual_evaluation_sentiment == prediction_sentiment)
            conn = sqlite3.connect('vanga_me_v1.db')
            cursor = conn.cursor()
            sql_command = f"INSERT INTO google_news_coins_daily_predictions_and_accuracy VALUES('{coin_name}', '{dates_str[dates_idx]}', " \
                          f"'{dates_str[dates_idx + 1]}', '{prediction_sentiment}', '{actual_evaluation_sentiment}', " \
                          f"{prediction_compound_evaluation}, {correct_prediction})"
            cursor.execute(sql_command)
            conn.commit()
            conn.close()

        except sqlite3.Error as err:
            print('Sql error: %s' % (' '.join(err.args)))
            print("Exception class is: ", err.__class__)

    end_seconds_time = perf_counter()
    time_delta = end_seconds_time - start_seconds_time

    if not amount_of_dates_with_data:
        prediction_accuracy = 0
    else:
        prediction_accuracy = (amount_of_correct_prediction / amount_of_dates_with_data)

    return_dict[coin_name] = [time_delta / 60, amount_of_dates_with_data, amount_of_stories_per_crypto,
                              prediction_accuracy * 100, total_compound_accuracy_correlation]


def filter_stories_in_hours_range(temp_stories, now, check_x_last_hours):
    stories = []

    for story in temp_stories[0]:
        # then = parser.parse(story['published']).replace(tzinfo=None)
        # total_hours = get_total_hours_between_dates(now, then)

        story_date = parser.parse(story["published"]).replace(tzinfo=timezone.utc)
        date_diff = (now - story_date)
        date_diff_in_hours = date_diff.seconds // 3600

        if date_diff_in_hours <= check_x_last_hours:
            stories.append(story)

    stories = [stories]
    return stories


def get_coin_prediction_for_last_x_hours(coin_name, check_x_last_hours=12):
    gn = GoogleNews()
    if check_x_last_hours is None:
        check_x_last_hours = 12

    dates = get_dates_between_dates((datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                                    datetime.now().strftime("%Y-%m-%d"))
    dates_str = get_str_dates_from_dates(dates)

    all_stories = []

    entries = [get_entries(gn, coin_name, start=dates_str[0], end=dates_str[1])]
    if not entries[0]:
        return
    # get stories for 2 dates
    stories = [get_stories(entries[0])]
    if not stories:
        return
    # add data to global stories list
    all_stories.append(stories[0])

    # combine list of lists to one list
    temp_stories_to_predict = [[inner for outer in all_stories for inner in outer]]

    # now = datetime.now()
    # use both now and then with utc zone to filter correctly
    now = datetime.now(timezone.utc)

    stories_to_predict = filter_stories_in_hours_range(temp_stories_to_predict, now, check_x_last_hours)

    if not stories_to_predict[0]:
        return

    coin_prediction = get_crypto_coins_evaluations(stories_to_predict, coin_name)[0]

    if not coin_prediction:
        return

    return coin_prediction


def get_coin_prediction_for_last_x_days(coin_name, days_to_subtract=7):
    gn = GoogleNews()
    if days_to_subtract is None:
        days_to_subtract = 7

    dates = get_dates_between_dates((datetime.now() - timedelta(days=days_to_subtract)).strftime("%Y-%m-%d"),
                                    datetime.now().strftime("%Y-%m-%d"))
    dates_str = get_str_dates_from_dates(dates)

    all_stories = []

    for idx in range(len(dates_str) - 1):
        # get data for 2 days
        entries = [get_entries(gn, coin_name, start=dates_str[idx], end=dates_str[idx + 1])]
        if not entries[0]:
            return
        # get stories for 2 dates
        stories = [get_stories(entries[0])]
        if not stories:
            return
        # add data to global stories list
        all_stories.append(stories[0])

    # combine list of lists to one list
    stories_to_predict = [[inner for outer in all_stories for inner in outer]]

    if not stories_to_predict[0]:
        return

    coin_prediction = get_crypto_coins_evaluations(stories_to_predict, coin_name)[0]

    if not coin_prediction:
        return

    return coin_prediction


def get_search_terms_predictions(google_terms, days_to_subtract, check_x_last_hours):
    if check_x_last_hours or (not check_x_last_hours and not days_to_subtract):
        use_hours = True
    else:
        use_hours = False

    coins_predictions = dict()

    for term in google_terms:
        if __DETAILED_PRINTING__:
            print(f"\nScraping the web for {term}")

        # prediction = get_coin_prediction(term, days_to_subtract, check_x_last_hours)
        if use_hours:
            prediction = get_coin_prediction_for_last_x_hours(term, check_x_last_hours)
        else:
            # change function name to get_coin_prediction for last x days
            prediction = get_coin_prediction_for_last_x_days(term, days_to_subtract)

        if prediction:
            coins_predictions[prediction[0]] = [prediction[2], abs(prediction[1] * 100)]

    return coins_predictions


def get_coins_predictions_for_last_x_hours_or_days(coin_names, _days_to_subtract=None, _check_x_last_hours=None):
    collected_time = datetime.now().strftime("%y-%m-%d_%H-%M-%S")

    predictions = get_search_terms_predictions(coin_names, days_to_subtract=_days_to_subtract,
                                               check_x_last_hours=_check_x_last_hours)

    if _check_x_last_hours:
        throwback_collected_time = f'{str(_check_x_last_hours)} hours'
    else:
        throwback_collected_time = f'{str(_days_to_subtract)} days'

    output_predictions(predictions, collected_time, throwback_collected_time)

    predictions_arr = []
    for prediction in predictions.items():
        predictions_arr.append([prediction[0], prediction[1][0], prediction[1][1]])

    return predictions_arr


def get_coin_predictions_history_accuracy(terms_and_tickers=basic_search_term_google_and_yf_ticker_name,
                                          start_date="2014-01-01",
                                          end_date=datetime.now().strftime("%Y-%m-%d"),
                                          multiprocess_enabled=True):
    proc, jobs = None, None
    if multiprocess_enabled:
        jobs = []
        manager = mlpcs.Manager()
        return_dict = manager.dict()
    else:
        return_dict = dict()

    if multiprocess_enabled:
        for coin_name in terms_and_tickers:
            proc = mlpcs.Process(target=write_predictions_accuracy_to_sql_for_each_date,
                                 args=tuple([coin_name[0], coin_name[1], start_date, end_date, return_dict]))

            proc.name = coin_name[0]
            proc.start()
            if __DETAILED_PRINTING__:
                print(f'{proc.name} has started')
            jobs.append(proc)

        for proc in jobs:
            proc.join()
            if __DETAILED_PRINTING__:
                print(f'{proc.name} has joined')

    else:
        for coin_name in terms_and_tickers:
            write_predictions_accuracy_to_sql_for_each_date(coin_name[0], coin_name[1], start_date, end_date,
                                                            return_dict)

    print("\nAll Set And Done!\n")

    return return_dict


def get_coin_predictions_history_accuracy_1(terms_and_tickers, dates=None, multiprocess_enabled=True):
    proc, jobs = None, None
    if multiprocess_enabled:
        jobs = []
        manager = mlpcs.Manager()
        return_dict = manager.dict()
    else:
        return_dict = dict()

    directory_name = datetime.now().strftime("%Y-%m-%d_(%H-%M-%S)")

    directory_name = "Collected_Data\\" + directory_name
    if not create_data_collecting_directory(directory_name):
        return

    if __DETAILED_PRINTING__:
        print(f'\nnumber of coins to search: {len(terms_and_tickers)}\n')

    if dates is None:
        dates_str = []
    else:
        dates_str = get_str_dates_from_dates(dates)

    for coin_name in terms_and_tickers:
        coin_filename = directory_name + '\\' + coin_name[0].strip('"') + "_prediction_accuracy_" + \
                        datetime.now().strftime("%y-%m-%d_%H-%M-%S") + ".txt"

        if multiprocess_enabled:
            proc = mlpcs.Process(target=output_crypto_prediction_accuracy_to_file_between_dates,
                                 args=tuple([coin_name[0], coin_filename, coin_name[1], return_dict, dates_str]))
        else:
            output_crypto_prediction_accuracy_to_file_between_dates(coin_name[0], coin_filename, coin_name[1],
                                                                    return_dict, dates_str)

        if multiprocess_enabled:
            proc.name = coin_name[0]
            proc.start()
            if __DETAILED_PRINTING__:
                print(f'{proc.name} has started')
            jobs.append(proc)

    if multiprocess_enabled:
        for proc in jobs:
            proc.join()
            if __DETAILED_PRINTING__:
                print(f'{proc.name} has joined')

    output_final_data_to_summary_file(directory_name, return_dict)

    print("\nAll Set And Done!\n")

    return return_dict

# def get_coin_predictions_history_accuracy(terms_and_tickers):
#     jobs = []
#     manager = mlpcs.Manager()
#
#     directory_name = datetime.now().strftime("%Y-%m-%d_(%H-%M-%S)")
#
#     directory_name = "Collected_Data\\" + directory_name
#     if not create_data_collecting_directory(directory_name):
#         return
#
#     return_dict = manager.dict()
#     if __DETAILED_PRINTING__:
#         print(f'\nnumber of coins to search: {len(terms_and_tickers)}\n')
#
#     for coin_name in terms_and_tickers:
#         coin_filename = directory_name + '\\' + coin_name[0].strip('"') + "_prediction_accuracy_" + \
#                         datetime.now().strftime("%y-%m-%d_%H-%M-%S") + ".txt"
#
#         # dates_str = []
#         # dates = get_dates_between_dates('2021-12-04', datetime.now().strftime("%Y-%m-%d"))
#         dates = get_dates_between_dates('2021-01-01', '2021-01-03')
#         dates_str = get_str_dates_from_dates(dates)
#
#         proc = mlpcs.Process(target=output_crypto_prediction_accuracy_to_file_between_dates,
#                              args=tuple([coin_name[0], coin_filename, coin_name[1], return_dict, dates_str]))
#
#         proc.name = coin_name[0]
#         proc.start()
#         if __DETAILED_PRINTING__:
#             print(f'{proc.name} has started')
#         jobs.append(proc)
#
#     for proc in jobs:
#         proc.join()
#         if __DETAILED_PRINTING__:
#             print(f'{proc.name} has joined')
#
#     output_final_data_to_summary_file(directory_name, return_dict)
#
#     print("\nAll Set And Done!\n")
