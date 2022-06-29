from os import mkdir
from datetime import datetime
from vanga_configs import *

import sqlite3
from vanga_configs import *
from vanga_configs import __DETAILED_PRINTING__
# use for debug printing
# __DETAILED_PRINTING__ = False


# CREATE table for coin_name, ticker_name
def create_vanga_me_db_file():
    try:
        conn = sqlite3.connect(db_filename, timeout=20)
        cursor = conn.cursor()

        create_prediction_table_command = f""" CREATE TABLE IF NOT EXISTS {prediction_accuracy_table_name} (
                                                    coin_name text NOT NULL,
                                                    prediction_date text NOT NULL,
                                                    real_evaluation real,
                                                    real_sentiment text,
                                                    prediction_evaluation real,
                                                    prediction_sentiment text,
                                                    correct_wrong_prediction integer NOT NULL,
                                                    UNIQUE(coin_name, prediction_date)
                                                ); """
        cursor.execute(create_prediction_table_command)

        create_yfinance_table_command = f""" CREATE TABLE IF NOT EXISTS {yfinance_table_name} (
                                                    coin_name text NOT NULL,
                                                    evaluation_date text NOT NULL,
                                                    open_rate real,
                                                    close_rate real,
                                                    UNIQUE(coin_name, evaluation_date)
                                                ); """
        cursor.execute(create_yfinance_table_command)

        create_stories_data_table_command = f""" CREATE TABLE IF NOT EXISTS {stories_data_table_name} (
                                                            coin_name text NOT NULL,
                                                            story_id text NOT NULL,
                                                            title text NOT NULL,
                                                            link text NOT NULL,
                                                            published text NOT NULL,
                                                            UNIQUE(coin_name, story_id)
                                                        ); """
        cursor.execute(create_stories_data_table_command)

        conn.commit()
        conn.close()

    except sqlite3.Error as err:
        print('Sql error: %s' % (' '.join(err.args)))
        print("Exception class is: ", err.__class__)

        return False, str(err)

    return True, "OK"


def get_search_term_google_and_yf_ticker_names_from_file(coin_names_file):
    """
    function takes file name and retrieve coin names and ticker names
    file should specify ticker name and coin name in each row, divided by ', '
    example:
    BTC-USD, Bitcoin
    ETH-USD, Ethereum
    BNB-USD, BinanceCoin

    :return: if succeeded return list of names and tickers.
             if not, return empty list
    """

    names_and_tickers = []
    try:
        with open(coin_names_file, 'r') as f:
            for line in f:
                if line == "\n":
                    continue

                splitted = line.strip().split(', ')
                try:
                    names_and_tickers.append([splitted[1], splitted[0]])
                except Exception as ex:
                    print(f'error appending line: "{line}"')
                    print(f'{ex}')
                    continue

    except Exception as ex:
        print(f"Coin names file error: {ex}\nProceeding with basic terms\n")

    if len(names_and_tickers) > 0:
        return names_and_tickers
    else:
        return []


def write_prediction_to_sql(coin_name, str_date, prediction_evaluation, prediction_sentiment,
                            real_evaluation, real_sentiment):
    correct_prediction = 0
    if prediction_sentiment == real_sentiment:
        correct_prediction = 1

    # CHANGE TO ?, ?, ?, ?, ?
    insert_date_to_sql_table_command = f"INSERT INTO {prediction_accuracy_table_name} VALUES(?, ?, ?, ?, ?, ?, ?);"

    try:
        conn = sqlite3.connect(db_filename, timeout=20)
        cur = conn.cursor()

        cur.execute(insert_date_to_sql_table_command, (coin_name, str_date, real_evaluation, real_sentiment,
                    prediction_evaluation, prediction_sentiment, correct_prediction))
        conn.commit()
        conn.close()
        if __DETAILED_PRINTING__:
            print(f'INSERTED => {coin_name} | {str_date} | {"Correct" if correct_prediction else "Incorrect"}')

    except sqlite3.Error as err:
        print('Sql error: %s' % (' '.join(err.args)))
        print("Exception class is: ", err.__class__)


def output_temporary_data_to_coin_file(coin_filename, dates_str, dates_idx, coins_sentiment_evaluation,
                                       actual_evaluation, total_compound_accuracy_correlation,
                                       actual_evaluation_sentiment, amount_of_correct_prediction,
                                       amount_of_dates_with_data):
    """
    function output temporary data to file:
    example:
    "
    SUMMARY: Real evaluation 'Positive' => Prediction 'Positive' was CORRECT!
    Temp (Actual Evaluation / Compound Prediction) = 4.13
    Temporary Accuracy = 35.7%
    "

    :param coin_filename:                       file name for coin
    :param dates_str:                           list of string dates
    :param dates_idx:                           current index to look at in dates_str
    :param coins_sentiment_evaluation:          list of coin evaluation properties
    :param actual_evaluation:                   real evaluation according to
    :param total_compound_accuracy_correlation: global compound accuracy correlation (currently way off)
    :param actual_evaluation_sentiment:         real evaluation sentiment according to
    :param amount_of_correct_prediction:        number of correct prediction
    :param amount_of_dates_with_data:           number of dates of data collected
    :return: amount_of_dates_with_data, amount_of_correct_prediction, total_compound_accuracy_correlation
    """
    amount_of_dates_with_data += 1
    compound_accuracy_correlation = 0
    with open(coin_filename, "a") as crypto_coin_file:
        try:
            crypto_coin_file.write(dates_str[dates_idx] + ' ' + dates_str[dates_idx + 1] + '\n')
            # print(f'{coins_sentiment_evaluation[0]}')

            if coins_sentiment_evaluation[0][1]:
                compound_accuracy_correlation += (coins_sentiment_evaluation[0][1] / actual_evaluation)
                total_compound_accuracy_correlation += compound_accuracy_correlation

            if coins_sentiment_evaluation[0][2] == actual_evaluation_sentiment:
                if __DETAILED_PRINTING__:
                    print(
                        f'SUMMARY:Real evaluation {actual_evaluation_sentiment} => Prediction {coins_sentiment_evaluation[0][2]} was CORRECT!')
                    print(
                        f'Temp (Actual Evaluation / Compound Prediction) = {compound_accuracy_correlation}')

                crypto_coin_file.write(
                    f'SUMMARY: Real evaluation {actual_evaluation_sentiment} => Prediction {coins_sentiment_evaluation[0][2]} was CORRECT!\n')
                crypto_coin_file.write(
                    f'Temp (Actual Evaluation / Compound Prediction) = {compound_accuracy_correlation}\n')
                amount_of_correct_prediction += 1
            else:
                if __DETAILED_PRINTING__:
                    print(
                        f'SUMMARY: Real evaluation {actual_evaluation_sentiment} => prediction {coins_sentiment_evaluation[0][2]} was WRONG!')
                    print(
                        f'Temp (Actual Evaluation / Compound Prediction) = {compound_accuracy_correlation}')

                crypto_coin_file.write(
                    f'SUMMARY: Real evaluation {actual_evaluation_sentiment} => prediction {coins_sentiment_evaluation[0][2]} was WRONG!\n')
                crypto_coin_file.write(
                    f'Temp (Actual Evaluation / Compound Prediction) = {compound_accuracy_correlation}\n')

        except Exception as ex:
            crypto_coin_file.write(dates_str[dates_idx] + ' ' + dates_str[dates_idx + 1] + '\n')
            amount_of_dates_with_data -= 1
            print(f"An exception occurred: {ex}")
            crypto_coin_file.write(f"An exception occurred: {ex}\n")

    with open(coin_filename, "a") as crypto_coin_file:
        # amount_of_dates_with_data+=1
        if amount_of_dates_with_data:
            # print(f'Temporary Accuracy = {(amount_of_correct_prediction / amount_of_dates_with_data) * 100}%')
            # print('-------------------------------------------\n')
            crypto_coin_file.write(
                f'Temporary Accuracy = {(amount_of_correct_prediction / amount_of_dates_with_data) * 100}%\n')
            crypto_coin_file.write('-------------------------------------------\n\n')
        else:
            # print(f'Temporary length is zero')
            #  print('-------------------------------------------\n')
            crypto_coin_file.write(f'Temporary length is zero\n')
            crypto_coin_file.write('-------------------------------------------\n\n')

    return amount_of_dates_with_data, amount_of_correct_prediction, total_compound_accuracy_correlation


def output_final_data_to_coin_file(coin_filename, amount_of_dates_with_data, time_delta, coin_name,
                                   amount_of_correct_prediction,
                                   total_compound_accuracy_correlation, amount_of_stories_per_crypto):
    """
    function output final data to file:
    example:
    "
    SUMMARY: Real evaluation 'Positive' => Prediction 'Positive' was CORRECT!
    Temp (Actual Evaluation / Compound Prediction) = 4.13
    Temporary Accuracy = 35.7%

    :param coin_filename:                       file name for coin
    :param amount_of_dates_with_data:           number of dates of data collected
    :param time_delta:                          time delta for code running time calculation
    :param coin_name:                           crypto coin name
    :param amount_of_correct_prediction:        number of correct prediction
    :param total_compound_accuracy_correlation: global compound accuracy correlation (currently way off)
    :param amount_of_stories_per_crypto:        number of stories collected for coin
    :return:
    """

    with open(coin_filename, "a") as crypto_coin_file:
        if amount_of_dates_with_data:
            print("Done!")
            print(f'Code ran for: {time_delta / 60} minutes')
            print(f"Amount of evaluation data collected: {amount_of_dates_with_data}")
            print(
                f'Final Accuracy for {coin_name} coin = {(amount_of_correct_prediction / amount_of_dates_with_data) * 100}%')
            print(f'Final Compound Accuracy Correlation For {coin_name} coin = {total_compound_accuracy_correlation}')

            crypto_coin_file.write("Done!\n")
            crypto_coin_file.write(f'Code ran for: {time_delta / 60} minutes\n')
            crypto_coin_file.write(f"Amount of evaluation dates with data collected: {amount_of_dates_with_data}\n")
            crypto_coin_file.write(
                f"Total amount of stories collected for {coin_name}: {amount_of_stories_per_crypto}\n")
            crypto_coin_file.write(
                f'Final Accuracy for {coin_name} coin = {(amount_of_correct_prediction / amount_of_dates_with_data) * 100}%\n')
            crypto_coin_file.write(
                f'Final Compound Accuracy Correlation For {coin_name} coin = {total_compound_accuracy_correlation}\n')
        else:
            print("Done!")
            print("no data found at all")
            crypto_coin_file.write("Done!\n")
            crypto_coin_file.write("No data found at all!\n")


def output_final_data_to_summary_file(directory_name, return_dict):
    """
    function output final data for each coin to summary file

    :param directory_name: directory name to create and append data to
    :param return_dict:    dictionary of data for each coin
    :return:
    """
    summary_filename = directory_name + '\\' + "_Prediction_Summary " + datetime.now().strftime(
        "%y-%m-%d_%H-%M-%S") + ".txt"

    with open(summary_filename, "a") as summary_file:
        for item in return_dict.items():
            if item[1][2]:
                write_data = f'Coin: {item[0]}\n' + \
                             f'Code Running Time: {item[1][0]} minutes\n' + \
                             f'Dates of data Collected: {item[1][1]}\n' + \
                             f'Amount Of Stories Collected: {item[1][2]}\n' + \
                             f'Prediction Accuracy: {item[1][3]}%\n' + \
                             f'Compound Accuracy Correlation: {item[1][4]}\n' + \
                             f'-------------------------------------------------\n\n'
                summary_file.write(f"{write_data}")


def create_data_collecting_directory(directory_name):
    """
    function get directory name and create directory for data collection

    :param directory_name:
    :return: True if success, False if fail
    """
    try:
        mkdir(directory_name)
    except FileExistsError:
        print(f'Folder {directory_name} already exists!')
        return False
    except Exception as ex:
        print(f'error: {ex}')
        return False

    return True


def output_predictions(predictions_dict, collected_time, throwback_collected_time):
    summary_filename = 'Future_Predictions' + '\\' + "_Prediction_Summary " + collected_time + ".txt"

    with open(summary_filename, "a") as summary_file:
        write_data = f"Collected data for last: {throwback_collected_time}\n" + \
                     f"Collected at: {collected_time}\n" + \
                     f'-------------------------------------------------\n\n'
        summary_file.write(f"{write_data}")

        for prediction in predictions_dict.items():
            # if __DETAILED_PRINTING__:
            # print(f'{prediction[0]}: {prediction[1][0]} shift prediction')

            if prediction[1][0]:
                write_data = f'Coin: {prediction[0]}\n' + \
                             f'Shift Prediction: {prediction[1][0]}\n' + \
                             f'Prediction Strength: {prediction[1][1]}\n' + \
                             f'-------------------------------------------------\n\n'
                summary_file.write(f"{write_data}")
