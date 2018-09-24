# coding=utf-8
# https://github.com/sammchardy/python-binance/
# https://github.com/binance-exchange/binance-official-api-docs/

# Max 1200 requests / min. Single 500 candles request = 1 request. Get all tickers = 1 request / ticker = 300.

import requests
import time
from operator import itemgetter
from .helpers import date_to_milliseconds, interval_to_milliseconds
from .exceptions import BinanceAPIException, BinanceRequestException, BinanceWithdrawException

class Client(object):

    API_URL = 'https://api.binance.com/api'
    WEBSITE_URL = 'https://www.binance.com'
    PUBLIC_API_VERSION = 'v1'

    KLINE_INTERVAL_1MINUTE = '1m'
    KLINE_INTERVAL_3MINUTE = '3m'
    KLINE_INTERVAL_5MINUTE = '5m'
    KLINE_INTERVAL_15MINUTE = '15m'
    KLINE_INTERVAL_30MINUTE = '30m'
    KLINE_INTERVAL_1HOUR = '1h'
    KLINE_INTERVAL_2HOUR = '2h'
    KLINE_INTERVAL_4HOUR = '4h'
    KLINE_INTERVAL_6HOUR = '6h'
    KLINE_INTERVAL_8HOUR = '8h'
    KLINE_INTERVAL_12HOUR = '12h'
    KLINE_INTERVAL_1DAY = '1d'
    KLINE_INTERVAL_3DAY = '3d'
    KLINE_INTERVAL_1WEEK = '1w'
    KLINE_INTERVAL_1MONTH = '1M'

    def _create_api_uri(self, path):
        return self.API_URL + '/' + self.PUBLIC_API_VERSION + '/' + path

    def _order_params(self, data):
        """Convert params to list with signature as last element

        :param data:
        :return:

        """
        has_signature = False
        params = []
        for key, value in data.items():
            if key == 'signature':
                has_signature = True
            else:
                params.append((key, value))
        # sort parameters by key
        params.sort(key=itemgetter(0))
        if has_signature:
            params.append(('signature', data['signature']))
        return params

    def _request(self, method, uri, force_params=False, **kwargs):

        # set default requests timeout
        kwargs['timeout'] = 10

        data = kwargs.get('data', None)  # Get some key (data) or default key when is missing (None)

        if data and isinstance(data, dict):
            kwargs['data'] = data

        # sort get and post params to match signature order
        if data:
            # find any requests params passed and apply them
            if 'requests_params' in kwargs['data']:
                # merge requests params into kwargs
                kwargs.update(kwargs['data']['requests_params'])
                del (kwargs['data']['requests_params'])

            # sort post params
            kwargs['data'] = self._order_params(kwargs['data'])

        # if get request assign data array to params value for requests lib
        if data and (method == 'get' or force_params):
            kwargs['params'] = kwargs['data']
            del (kwargs['data'])

        response = requests.request(method, uri, **kwargs)
        return self._handle_response(response)

    def _request_api(self, method, path, **kwargs):
        uri = self._create_api_uri(path)
        return self._request(method, uri, **kwargs)

    def _handle_response(self, response):
        """Internal helper for handling API responses from the Binance server.
        Raises the appropriate exceptions when necessary; otherwise, returns the
        response.
        """
        if not str(response.status_code).startswith('2'):
            raise BinanceAPIException(response)
        try:
            return response.json()
        except ValueError:
            raise BinanceRequestException('Invalid Response: %s' % response.text)

    def _get(self, path, **kwargs):
        return self._request_api('get', path, **kwargs)

    # Exchange Endpoints

    def get_exchange_info(self):
        """Return rate limits and list of symbols
        :returns: list - List of product dictionaries
        :raises: BinanceRequestException, BinanceAPIException
        """
        return self._get('exchangeInfo')

    def get_symbol_info(self, symbol):
        """Return information about a symbol
        :param symbol: required e.g BNBBTC
        :type symbol: str
        :returns: Dict if found, None if not
        """
        res = self._get('exchangeInfo')
        for item in res['symbols']:
            if item['symbol'] == symbol.upper():
                return item

        return None

    # General Endpoints

    def ping(self):
        """Test connectivity to the Rest API.
        :returns: Empty array
        :raises: BinanceRequestException, BinanceAPIException
        """
        return self._get('ping')

    def get_server_time(self):
        """Test connectivity to the Rest API and get the current server time.
        :returns: Current server time
        :raises: BinanceRequestException, BinanceAPIException
        """
        return self._get('time')

    # Market Data Endpoints

    def get_all_tickers(self):
        """Latest price for all symbols.
        :returns: List of market tickers
        :raises: BinanceRequestException, BinanceAPIException
        """
        return self._get('ticker/allPrices')

    def get_klines(self, **params):
        """Kline/candlestick bars for a symbol. Klines are uniquely identified by their open time.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#klinecandlestick-data

        :param symbol: required
        :type symbol: str
        :param interval: -
        :type interval: str
        :param limit: - Default 500; max 500.
        :type limit: int
        :param startTime:
        :type startTime: int
        :param endTime:
        :type endTime: int

        :returns: API response

        .. code-block:: python

            [
                [
                    1499040000000,      # Open time
                    "0.01634790",       # Open
                    "0.80000000",       # High
                    "0.01575800",       # Low
                    "0.01577100",       # Close
                    "148976.11427815",  # Volume
                    1499644799999,      # Close time
                    "2434.19055334",    # Quote asset volume
                    308,                # Number of trades
                    "1756.87402397",    # Taker buy base asset volume
                    "28.46694368",      # Taker buy quote asset volume
                    "17928899.62484339" # Can be ignored
                ]
            ]

        :raises: BinanceRequestException, BinanceAPIException

        """
        return self._get('klines', data = params)


    def _get_earliest_valid_timestamp(self, symbol, interval):
        """Get earliest valid open timestamp from Binance

        :param symbol: Name of symbol pair e.g BNBBTC
        :type symbol: str
        :param interval: Binance Kline interval
        :type interval: str

        :return: first valid timestamp

        """
        kline = self.get_klines(
            symbol=symbol,
            interval=interval,
            limit=1,
            startTime=0,
            endTime=None
        )
        return kline[0][0]

    def get_historical_klines(self, symbol, interval, start_str, end_str=None):
        """Get Historical Klines from Binance

        See dateparser docs for valid start and end string formats http://dateparser.readthedocs.io/en/latest/

        If using offset strings for dates add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"

        :param symbol: Name of symbol pair e.g BNBBTC
        :type symbol: str
        :param interval: Binance Kline interval
        :type interval: str
        :param start_str: Start date string in UTC format
        :type start_str: str
        :param end_str: optional - end date string in UTC format (default will fetch everything up to now)
        :type end_str: str

        :return: list of OHLCV values

        """
        # init our list
        output_data = []
        # setup the max limit
        limit = 500
        # convert interval to useful value in seconds
        timeframe = interval_to_milliseconds(interval)
        # convert our date strings to milliseconds
        start_ts = date_to_milliseconds(start_str)
        # establish first available start timestamp
        first_valid_ts = self._get_earliest_valid_timestamp(symbol, interval)
        start_ts = max(start_ts, first_valid_ts)
        # if an end time was passed convert it
        end_ts = None
        if end_str:
            end_ts = date_to_milliseconds(end_str)

        idx = 0
        while True:
            # fetch the klines from start_ts up to max 500 entries or the end_ts if set
            temp_data = self.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit,
                startTime=start_ts,
                endTime=end_ts
            )

            # handle the case where exactly the limit amount of data was returned last loop
            if not len(temp_data):
                break
            # append this loops data to our output data
            output_data += temp_data
            # set our start timestamp using the last value in the array
            start_ts = temp_data[-1][0]

            idx += 1
            # check if we received less than the required limit and exit the loop
            if len(temp_data) < limit:
                # exit the while loop
                break
            # increment next call by our timeframe
            start_ts += timeframe
            # sleep after every 3rd call to be kind to the API
            if idx % 3 == 0:
                time.sleep(1)

        return output_data

    def get_last_klines(self, symbol, interval, limit):

        return self.get_klines(
            symbol=symbol,
            interval=interval,
            limit=limit)

    def get_ticker(self, **params):
        """24 hour price change statistics.
        :param symbol:
        :type symbol: str
        :returns: API response
        .. code-block:: python
            {
                "priceChange": "-94.99999800",
                "priceChangePercent": "-95.960",
                "weightedAvgPrice": "0.29628482",
                "prevClosePrice": "0.10002000",
                "lastPrice": "4.00000200",
                "bidPrice": "4.00000000",
                "askPrice": "4.00000200",
                "openPrice": "99.00000000",
                "highPrice": "100.00000000",
                "lowPrice": "0.10000000",
                "volume": "8913.30000000",
                "openTime": 1499783499040,
                "closeTime": 1499869899040,
                "fristId": 28385,   # First tradeId
                "lastId": 28460,    # Last tradeId
                "count": 76         # Trade count
            }
        :raises: BinanceRequestException, BinanceAPIException
        """
        return self._get('ticker/24hr', data=params)