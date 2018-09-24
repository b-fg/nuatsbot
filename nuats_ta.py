# https://github.com/rpazyaquian/PyTA

import pandas
import numpy as np
from six.moves import range
from sklearn.linear_model import LinearRegression
# import matplotlib
# matplotlib.use('agg')
# import matplotlib.pyplot as plt

class Candlestick(object):

    def __init__(self, kline):
       self.open_time = kline[0]
       self.open = float(kline[1])
       self.high = float(kline[2])
       self.low = float(kline[3])
       self.close = float(kline[4])
       self.volume = float(kline[5])
       self.close_time = kline[6]

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

class Notification(object):
    """
    Types:
        0: RSI bull
        1: RSI bear
        2: Volume increase
        3: RSI-price bull divergence
        4: RSI-price bear divergence
    """

    def __init__(self, code, ticker, interval, value):
        self.code = code
        self.ticker = ticker
        self.interval = interval
        self.value = value

    def __str__(self):
        if self.code == 0:
            return '{} ({}) High RSI: {:.1f}'.format(self.ticker, self.interval, self.value)         # RSI value
        elif self.code == 1:
            return '{} ({}) Low RSI: {:.1f}'.format(self.ticker, self.interval, self.value)        # RSI value
        elif self.code == 2:
            return '{} ({}) Volume increase: {:.1f} %'.format(self.ticker, self.interval, self.value) # % Volume increase
        elif self.code == 3:
            return '{} ({}) Bullish divergence with {} interval confirmations'.format(self.ticker, self.interval, self.value)
        elif self.code == 4:
            return '{} ({}) Bearish divergence with {} interval confirmations'.format(self.ticker, self.interval, self.value)
        else:
            return 'Error (no code present)'

    def __lt__(self, other):
        return self.ticker < other.ticker


class NuatsTA(object) :

    def __init__(self, ticker, interval, candles):
        self.ticker = ticker
        self.interval = interval
        self.candles = candles
        self.prices = np.asarray([candle.close for candle in candles])
        self.n_periods = len(candles)
        self.indicators = {}


    def analyse(self):
        notifications = []

        rsi_bull_threshold = 70
        rsi_bear_threshold = 20
        volume_growth_threshold = 5
        divergence_confirmations = 2
        divergence_degrees = 5

        # Compute indicators
        rsi = self.rsi()

        # RSI analysis
        if rsi[-1] > rsi_bull_threshold:
            notifications.append(Notification(0, self.ticker, self.interval, rsi[-1]))
        elif rsi[-1] < rsi_bear_threshold:
            notifications.append(Notification(1, self.ticker, self.interval, rsi[-1]))

        # Volume analysis
        volumes = [candle.volume for candle in self.candles[-30:]] # Get volumes of last 30 candles
        avg_vol = np.mean(volumes)
        avg_last_volumes = np.mean(volumes[-2:])
        growth = (avg_last_volumes-avg_vol)/avg_vol
        if growth > volume_growth_threshold:
            notifications.append(Notification(2, self.ticker, self.interval, growth*100))

        # RSI-Price divergence analysis
        reg_rsi = LinearRegression()
        reg_price = LinearRegression(normalize=True)

        num_intervals = [10, 20, 30, 40] # At least 3 and then check for other intervals and volume as well.

        intervals_register = []
        for num_int in num_intervals:
            x = list(range(num_int))
            x = np.expand_dims(x, 1)

            y_rsi = self.indicators['rsi'][-num_int:]
            y_price = self.prices[-num_int:]

            reg_rsi.fit(x, y_rsi)
            reg_price.fit(x, y_price)

            m_rsi = reg_rsi.coef_[0]
            m_price = reg_price.coef_[0]
            m_rsi_deg = np.arctan(m_rsi) * 180 / np.pi
            m_price_deg = np.arctan(m_price) * 180 / np.pi

            if m_rsi > 0 and m_price < 0 and m_rsi_deg > divergence_degrees:
            # if m_rsi > 0 and m_price < 0: # Bullish div
                intervals_register.append(('Bull', num_int))
            elif m_rsi < 0 and m_price > 0: # Bearish div
                intervals_register.append(('Bear', num_int))

        all_bull = all(item[0] == "Bull" for item in intervals_register)
        all_bear = all(item[0] == "Bear" for item in intervals_register)

        if all_bull and len(intervals_register) >= 3:
            notifications.append(Notification(3, self.ticker, self.interval, len(intervals_register)))
        if all_bear and len(intervals_register) >= 3:
            notifications.append(Notification(4, self.ticker, self.interval, len(intervals_register)))

        # print(intervals_register)

        # plt.figure()
        # plt.scatter(x, y_rsi, color='blue')  # you can use test_data_X and test_data_Y instead.
        # plt.plot(x, reg_rsi.predict(x), color='k')
        #
        # plt.figure()
        # plt.scatter(x, y_price, color='green')  # you can use test_data_X and test_data_Y instead.
        # plt.plot(x, reg_price.predict(x), color='k')
        #
        # plt.show()

        return notifications


    def sma(self):
        """
        Returns the rolling mean of a given list of stock prices "prices"
        over a period of time "n_periods". Interfaces with Pandas, so the details are
        sort of unknown to me.

        n_periods, for a typical SMA, is equivalent to the "days" it spans.
        So for a 50-day SMA, n_periods is equal to 50.

        Accepts: Array; integer.
        Return type: Array.
        """
        sma = pandas.rolling_mean(self.prices, self.n_periods, min_periods=self.n_periods)
        return sma  # Returns a Numpy array in this case


    def bollinger_upper(self, sma):
        """
        Returns the upper Bollinger band line, for implementing a Bollinger
        band into the plot. Uses the list of stock prices "prices",
        the rolling mean returned by sma() "sma", over a number of periods "n_periods".
        You must use the same number of periods as used in the associated sma() function.
        Accepts: Array; array; integer.
        Return type: Array.
        """
        stdev = pandas.rolling_std(self, self.prices, self.n_periods, min_periods=self.n_periods)
        return sma + (2 * stdev)  # Returns a Numpy Array in this case


    def bollinger_lower(self, sma):
        """
        Returns the lower Bollinger band line, for implementing a Bollinger
        band into the plot. Uses the list of stock prices "prices",
        the rolling mean returned by sma() "sma", over a number of periods "n_periods".
        You must use the same number of periods as used in the associated sma() function.
        Accepts: Array; array; integer.
        Return type: Array.
        """
        stdev = pandas.rolling_std(self, self.prices, self.n_periods, min_periods=self.n_periods)
        return sma - (2 * stdev)  # Returns a Numpy Array in this case


    def stackify(self, x, y):
        """
        Stacks two arrays of data together. Used with Bollinger bands, at least for Bokeh.

        For example, in Bollinger bands, x would be the upper band data (which gets reversed)
        and y would be the lower band data (which has the reversed upper data appended).
        This would supply the y coordinates.

        The function still needs a little more work, since it's not very generalized.
        (Especially since it assumes the input is an array.)
        Accepts: Array 1; Array 2.
        Return type: Array.
        """

        stack = np.append(y, x[::-1])
        return stack


    def rsi(self, timeframe=14):
        """
        Returns the Relative Strength Index for a list of stock prices "prices"
        over a period of time "timeframe".
        Code shamelessly stolen from Sentdex. Sorry!

        Accepts: Array; integer (optional).
        Return type: Array.
        """

        delta = np.diff(self.prices)
        seed = delta[:timeframe + 1]

        up = seed[seed >= 0].sum() / timeframe
        down = -seed[seed < 0].sum() / timeframe

        with np.errstate(divide='ignore', invalid='ignore'):
            rs = up / down

        rsi = np.zeros_like(self.prices)
        rsi[:timeframe] = 100. - (100. / (1. + rs))

        for i in range(timeframe, len(self.prices)):

            i_delta = delta[i - 1]

            if i_delta > 0:
                upval = i_delta
                downval = 0.
            else:
                upval = 0.
                downval = -i_delta

            up = (up * (timeframe - 1) + upval) / timeframe
            down = (down * (timeframe - 1) + downval) / timeframe

            with np.errstate(divide='ignore', invalid='ignore'):
                rs = up / down

            rsi[i] = 100. - (100. / (1. + rs))

        self.indicators['rsi'] = rsi
        return rsi  # Returns a Numpy Array.


    def ema(self):
        """
        Returns the exponentially weighted moving average of a given SMA "sma".

        A MACD requires a 12-day EMA, a 26-day EMA, and a 9-day EMA.
        When writing an EMA, we need to figure out how to say "give me an n-day EMA".
        n_periods is the number of days you want it to span.
        So, a 12-day EMA would have n_periods=12.

        Accepts: Array; float.
        Return type: Array.
        """

        span = self.n_periods

        ema = pandas.ewma(self.prices, span=span)
        return ema


    def macd_line(self):
        """
        Returns the Moving Average Convergence-Divergence (MACD) of a given set of price data.
        This is the main line for plotting on a chart.

        Accepts: Array.
        Return type: Array.
        """

        ema12 = pandas.ewma(self.prices, span=12)
        ema26 = pandas.ewma(self.prices, span=26)

        macd = ema12 - ema26
        return macd


    def macd_signal(self):
        """
        Returns the MACD signal line of a given set of price data.

        Accepts: Array.
        Return type: Array.
        """

        ema9 = pandas.ewma(self.prices, span=9)

        return ema9


    def macd_hist(self):
        """
        Returns the MACD histogram data for a given set of price data.

        Accepts: Array.
        Return type: Array.
        """

        ema9 = pandas.ewma(self.prices, span=9)
        ema12 = pandas.ewma(self.prices, span=12)
        ema26 = pandas.ewma(self.prices, span=26)

        hist = (ema12 - ema26) - ema9
        return hist