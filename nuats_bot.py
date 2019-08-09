# -*- coding: utf-8 -*-
"""
Created on Sat Apr  7 20:47:10 2018
@author: troymcfont
"""

# Imports
from telegram_helper import telegramBot
from discord_helper import discordWebhook
from binance_client.client import Client as BinanceClient
from nuats_ta import Candlestick, NuatsTA
import time
import config
from tqdm import *
from concurrent.futures import ThreadPoolExecutor


# Functions
def request_tickers():
    tickers = []
    bclient = BinanceClient().get_exchange_info()
    for element in bclient['symbols']:
        if element['status'] == 'TRADING':
            tickers.append(element['symbol'])
    return tickers


def broadcast_signals(tickers_TA_list):
    all_notifications_list = list(filter(None.__ne__, tickers_TA_list)) # Filter out tickers with no bull/bear notifications
    all_notifications_list.sort()
    ntb_str = '\nSignals: \n'
    for ticker_notifications in all_notifications_list:
        for notification in ticker_notifications:
            ntb_str += str(notification) + '\n'

    print(ntb_str)

    print('Telegram broadcasting: \n {}'.format(telegram_chat_ids))
    print('Discord broadcasting: \n {}'.format(discord_webhooks))

    telegramBot(token=telegram_token, chat_ids=telegram_chat_ids).broadcast_message(ntb_str)
    discordWebhook(urls=discord_webhooks).broadcast_message(ntb_str)

def TA_task(a):
    ticker, interval = a[0], a[1]
    bclient = BinanceClient()

    if start_time == '':
        klines = bclient.get_last_klines(ticker, interval, n_periods)
    elif start_time != '' and end_time != '':
        klines = bclient.get_historical_klines(ticker, interval, start_time, end_time)
    else:
        raise ValueError('Error on configuration. Check n_periods and/or start_time and end_time. Look at README.md for more details')

    candles = []
    if len(klines) > 0:
        for kline in klines:
            candles.append(Candlestick(kline))
        nta = NuatsTA(ticker, interval, candles)
        # print("{} {}".format(ticker, interval), sep=' ', end='\n', flush=True)
        return nta.analyse()


# Get configuration from config.py
tickers = config.kline['tickers']
intervals = config.kline['intervals']
n_periods = config.kline['n_periods']
start_time = config.kline['start_time']
end_time = config.kline['end_time']
sleep = config.live_bot['sleep']
threading = config.live_bot['threading']
live = config.live_bot['live']
telegram_token = config.live_bot['telegram_token']
telegram_chat_ids = config.live_bot['telegram_chat_id']
discord_webhooks = config.live_bot['discord_web_hook']


def main():
    global tickers, intervals, n_periods, start_time, end_time, sleep, threading, live, telegram_token, telegram_chat_ids, discord_webhooks

    # Get the tickers to analyse
    if tickers is None or not tickers:
        tickers = request_tickers() # This will request tickers from Binance.
    # Generate a list of tuples containing (ticker, interval)
    a = []
    for ticker in tickers:
        for interval in intervals:
            a.append((ticker, interval))

    # Loop over tickers and intervals to get signals (threading or serial)
    tickers_TA_list = []
    if threading and live:
        while True:
            with ThreadPoolExecutor(max_workers=16) as executor:
                notifications_list =  list(tqdm(executor.map(TA_task, a), total=len(a)))
                if len(notifications_list) > 0: broadcast_signals(notifications_list)
            print('Sleeping {} sec now ... \n'.format(sleep))
            time.sleep(sleep)

    elif not threading and live:
        while True:
            with tqdm(total=len(a)) as pbar:
                for tup in a:
                    tickers_TA_list.append(TA_task(tup))
                    pbar.update(1)
            if len(tickers_TA_list) > 0: broadcast_signals(tickers_TA_list)
            print('Sleeping {} sec now ... \n'.format(sleep))
            time.sleep(sleep)

    elif threading and not live:
        with ThreadPoolExecutor(max_workers=16) as executor:
            tickers_TA_list =  list(tqdm(executor.map(TA_task, a), total=len(a)))

    elif not threading and not live:
        with tqdm(total=len(a)) as pbar:
            for tup in a:
                tickers_TA_list.append(TA_task(tup))
                pbar.update(1)

    if len(tickers_TA_list) > 0: broadcast_signals(tickers_TA_list)


if __name__ == '__main__':
    main()
