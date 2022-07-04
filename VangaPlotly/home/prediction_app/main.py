from home.prediction_app.vanga_me_core import get_coins_predictions_for_last_x_hours_or_days, get_coin_predictions_history_accuracy
from home.prediction_app.utils.files_util import get_search_term_google_and_yf_ticker_names_from_file, create_vanga_me_db_file
from datetime import datetime, timedelta
import home.prediction_app.vanga_configs as cfg

# __DETAILED_PRINTING__ = False

def init_db():
    status, msg = create_vanga_me_db_file()
    if not status:
        print('DB CONNECTION ERROR')
        return False, msg

global_term_and_tickers = cfg.basic_search_term_google_and_yf_ticker_name


def get_future_predictions(term_and_tickers, days_to_subtract=None, check_x_last_hours=None):
    try:
        coin_names = []
        for term in term_and_tickers:
            coin_names.append(term[0])

        predictions = get_coins_predictions_for_last_x_hours_or_days(coin_names, days_to_subtract, check_x_last_hours)

        for prediction in predictions:
            print(prediction)

        return True, predictions
    except Exception as ex:
        print(f"{ex}")
        return False, f"{ex}"


def get_predictions_accuracy(term_and_tickers, days_to_subtract=2):
    status, msg = create_vanga_me_db_file()
    if not status:
        return status, msg
        
    try:
        today = datetime.now()
        start_date = today - timedelta(days=days_to_subtract)

        prediction_accuracy = get_coin_predictions_history_accuracy(term_and_tickers,
                                                                    start_date=start_date.strftime("%Y-%m-%d"),
                                                                    end_date=today.strftime("%Y-%m-%d"),
                                                                    multiprocess_enabled=True)
        for prediction in prediction_accuracy.items():
            print(prediction)
        return True, prediction_accuracy
    except Exception as ex:
        print(f"{ex}")
        return False, f"{ex}"


def export_for_tables():
    
    status, predictions = get_future_predictions(global_term_and_tickers, check_x_last_hours=50)
    print(status, predictions)

    return status,predictions

    status, predictions = get_predictions_accuracy(global_term_and_tickers, days_to_subtract=7)
    print(status, predictions)


# if __name__ == '__main__':
#     main()
