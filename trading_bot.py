from kiteconnect import KiteConnect
import pandas as pd
from datetime import datetime, timedelta
import logging
import json


def sma(df, n):
    """Calculate the moving average for the given data.

    :param df: pandas.DataFrame
    :param n: 
    :return: pandas.DataFrame
    """
    MA = pd.Series(df['close'].rolling(
        n, min_periods=n).mean(), name='MA_' + str(n))
    df = df.join(MA)
    return df


def find_order_details(list_order, order_id):
    for order in list_order:
        if order["order_id"] == order_id:
            return order


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)

    api_key = open("api_key.txt").read()
    access_token = open("access_token.txt").read()

    kite = KiteConnect(api_key=api_key)

    from_date = datetime.strftime(datetime.now() - timedelta(1), "%Y-%m-%d")

    to_date = datetime.today().strftime("%Y-%m-%d")

    interval = "1minute"

    token_data = json.load(open("token.json"))

    token_symbol = token_data["symbol"]
    quantity = token_data["quantity"]
    ticker = token_data["ticker"]

    isLong, isShort = False, False

    current_position_details = {}
    while True:

        if datetime.now().seconds == 0:
            token_data = kite.historical_data(
                ticker, from_date=from_date, to_date=to_date, interval=interval)
            df_token_data = pd.Dataframe(token_data)
            df_token_data.drop(df_token_data.tail(1).index, inplace=True)

            token_sma_5 = sma(df_token_data, 5)
            token_sma_15 = sma(df_token_data, 15)

            if token_sma_5.iloc(-2) <= token_sma_15.iloc(-2) and token_sma_5.iloc(-1) > token_sma_15.iloc(-1):
                if isShort:
                    try:
                        order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                                    tradingsymbol=token_symbol,
                                                    exchange=kite.EXCHANGE_NSE,
                                                    transaction_type=kite.TRANSACTION_TYPE_BUY,
                                                    quantity=quantity,
                                                    order_type=kite.ORDER_TYPE_MARKET,
                                                    product=kite.PRODUCT_MIS)

                        order_details = find_order_details(
                            kite.orders(), order_id)

                        PNL = (order_details["average_price"] - current_position_details["average_price"]
                               ) / current_position_details["average_price"] * 100

                        logging.info("Stock Ticker - {}, Number of Stocks -{}, Market Value Bought - {}, Market Value Sold - {}, Buy Time - {}, Sell Time - {}, Trend Indicator - {}. PNL - {}".format(ticker, order_details['filled_quantity'], order_details[
                                     "average_price"], current_position_details["average_price"], current_position_details["order_timestamp"].strftime("%dd-%mm-%YYYY %H:%M:%S"), order_details["order_timestamp"].strftime("%dd-%mm-%YYYY %H:%M:%S"), current_position_details["trend_indicator"], PNL))

                    except Exception as e:
                        logging.info(
                            "Order placement failed: {}".format(str(e)))
                    else:
                        isShort = False
                        current_position_details = {}

                elif not isLong:
                    try:
                        order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                                    tradingsymbol=token_symbol,
                                                    exchange=kite.EXCHANGE_NSE,
                                                    transaction_type=kite.TRANSACTION_TYPE_BUY,
                                                    quantity=quantity,
                                                    order_type=kite.ORDER_TYPE_MARKET,
                                                    product=kite.PRODUCT_MIS)

                        order_details = find_order_details(
                            kite.orders(), order_id)

                        current_position_details["order_timestamp"] = order_details["order_timestamp"]
                        current_position_details["average_price"] = order_details["average_price"]
                        current_position_details["trend_indicator"] = "up"

                    except Exception as e:
                        logging.info(
                            "Order placement failed: {}".format(str(e)))
                    else:
                        isLong = True

            elif token_sma_5.iloc(-2) >= token_sma_15.iloc(-2) and token_sma_5.iloc(-1) < token_sma_15.iloc(-1):
                if not isShort:
                    try:
                        order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                                    tradingsymbol=token_symbol,
                                                    exchange=kite.EXCHANGE_NSE,
                                                    transaction_type=kite.TRANSACTION_TYPE_SELL,
                                                    quantity=quantity,
                                                    order_type=kite.ORDER_TYPE_MARKET,
                                                    product=kite.PRODUCT_MIS)

                        order_details = find_order_details(
                            kite.orders(), order_id)

                        current_position_details["order_timestamp"] = order_details["order_timestamp"]
                        current_position_details["average_price"] = order_details["average_price"]
                        current_position_details["trend_indicator"] = "down"

                    except Exception as e:
                        logging.info(
                            "Order placement failed: {}".format(str(e)))
                    else:
                        isShort = True

                elif isLong:
                    try:
                        order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                                    tradingsymbol=token_symbol,
                                                    exchange=kite.EXCHANGE_NSE,
                                                    transaction_type=kite.TRANSACTION_TYPE_SELL,
                                                    quantity=quantity,
                                                    order_type=kite.ORDER_TYPE_MARKET,
                                                    product=kite.PRODUCT_MIS)

                        order_details = find_order_details(
                            kite.orders(), order_id)

                        PNL = (order_details["average_price"] - current_position_details["average_price"]
                               ) / current_position_details["average_price"] * 100

                        logging.info("Stock Ticker - {}, Number of Stocks -{}, Market Value Bought - {}, Market Value Sold - {}, Buy Time - {}, Sell Time - {}, Trend Indicator - {}. PNL - {}".format(ticker, order_details['filled_quantity'], current_position_details[
                                     "average_price"], order_details["average_price"], order_details["order_timestamp"].strftime("%dd-%mm-%YYYY %H:%M:%S"), current_position_details["order_timestamp"].strftime("%dd-%mm-%YYYY %H:%M:%S"), current_position_details["trend_indicator"], PNL))

                    except Exception as e:
                        logging.info(
                            "Order placement failed: {}".format(str(e)))
                    else:
                        isLong = False
                        current_position_details = {}
