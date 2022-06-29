import yfinance as yf
from dateutil import parser
import pandas


def get_sorted_timestamps_per_crypto(published_per_crypto):
    """
    function get list of published stories per crypto coin
    then parse each (GMT from pyGoogleNews) and sort them
    :param published_per_crypto: list of extracted GMT 'timestamps' from pyGoogleNews object
    :return: sorted list of published times for each crypto coin
    """
    sorted_timestamps_per_crypto = []
    parsed_non_sorted_times = []
    # parsed_sorted_times = []
    idx = 0
    for crypto_timestamps in published_per_crypto:
        if len(crypto_timestamps) == 0:
            idx += 1
            continue
        for time in crypto_timestamps:
            parsed_non_sorted_times.append(parser.parse(time))

        parsed_sorted_times = sorted(parsed_non_sorted_times)

        sorted_timestamps_per_crypto.append(parsed_sorted_times)
        idx += 1
    return sorted_timestamps_per_crypto


def get_dates_between_dates(start_date, end_date):
    """
    function takes start date and end date parameters and create
    a list of dates between the dates with 1 day delta
    :param start_date: 'YYYY-MM-DD'
    :param end_date:   'YYYY-MM-DD'
    :return dates: list of dates between said start and end dates
    """
    s_date = parser.parse(start_date).date()  # start date
    e_date = parser.parse(end_date).date()  # end date
    # dates = pandas.date_range(s_date, e_date - days=1), freq='d').date
    dates = pandas.date_range(s_date, e_date, freq='d').date
    return dates


def get_str_dates_from_dates(dates):
    """
    function takes list of date objects and convert them to string dates
    :param dates: list of date objects
    :return str_dates: list of string dates
    """
    str_dates = []
    for date in dates:
        str_dates.append(str(date))
    return str_dates


def init_all_dates_for_ticker(yf_tickers_name):
    """
    function takes yfinance ticker name, download the ticker history and get the first and last date with data
    then use 'get_dates_between_dates' to get all dates between
    then use get_str_dates_from_dates to return list of string dates
    :param yf_tickers_name: yfinance ticker name -> can be found at (*never trust a link you don't know):
                        https://finance.yahoo.com/cryptocurrencies
    :return: list of string dates
    """
    try:
        initial_data = yf.Ticker(yf_tickers_name)
        hist = initial_data.history(period="max")

        start_date = str(hist.index.min().date())
        end_date = str(hist.index.max().date())

        dates = get_dates_between_dates(start_date, end_date)
    except Exception as ex:
        print(ex)
        return []

    return get_str_dates_from_dates(dates)


def get_total_hours_between_dates(end_date, start_date):
    diff = end_date - start_date
    days, seconds = diff.days, diff.seconds
    days_in_seconds = days * 24 * 60 * 60
    total_hours = ((days_in_seconds + seconds) / 60) / 60
    return total_hours
