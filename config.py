kline = dict(tickers = [],                      # List of tickers. Leave empty to request all the updated tickers on binance.
             intervals = ['30m'],               # List with multiple intervals if desired: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
             n_periods = 200,                   # Number of periods to analise
             start_time = '14 Sep 2018 UTC+6',  # Start of the period to analise
             end_time = 'now UTC+6')            # End of the period to analise
live_bot = dict(live = False,                   # Make the bot run on an infinite loop and perform the analysis every `sleep` seconds.
                sleep = 20,                     # Sleep time for the live bot to not overload the Binance API.
                threading = True,               # Multithreading boolean. Makes the Bot faster when set to True.
                telegram_token = '',            # Telegram token of the Bot created with BotFather
                telegram_chat_id = [''],        # Telegram channel id
                discord_web_hook = [''])        # Discord server webhook
