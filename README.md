## **NuatsBot**
How about a Technical Analysis Crypto Bot that runs on specified tickers/intervals and sends buy/sell signals on your Telegram or Discord channels?!
#### Meet NuatsBot, a Technical Analysis Bot for Binance

This library includes a set of tools with an easy setup to automatically perform Technical Analysis (TA) on selected cryptocurrencies which are tradable on the Binance Exchange.
Furthermore, the bull/bear signals are broadcast to the specified Telegram/Discord channels.

### TA signals

Currently the implemented signals are:
- Change in volume
- Oversold/Overbought RSI
- RSI/price divergence

In order to modify the trigger values for each indicator check `nuats_ta.py`, the `analyse` function. In the future I will include the trigger values in the `config.py` file as well as the selected strategies for generating the desired signals.

Additionally, I would really appreciate it if someone wants to include more TA strategies to generate the buy/sell signals.

### Usage

In the `config.py` file the user can set the following parameters:

TA related parameters:
- ``tickers``: List of tickers to analyse. If empty, all the available tickers in Binance are selected by default. E.g.: `['BTCUSDT', 'ETHBTC']`
- ``intervals``: List of intervals to analyse. E.g.: `['30min','1h','1d']`.
- ``n_periods``: Number of periods (bars or klines) for the selected intervals for which the TA will be performed. If blank, default is 500.
- ``start_time``: Start of the period to analyse. It will retrieve as many periods as necessary up to right now if `end_time` is not provided. If blank, only the last `n_periods` will be retrieved.
- ``end_time``: End of the period to analyse. Parameter only accepted when `start_time` is provided.

Bot related parameters:
- ``live``: Boolean to indicate if an infinite loop (execution of the bot) is desired. If false, the analysis will be only done once.
- ``sleep``: Sleep value for `live` executions. Indicates the time between analysis. Check Binance API restrictions for more info.
- ``threading``: Boolean to indicate a multithread execution or serial execution. The bot runs much faster multithreading of course!
- ``telegram_token``: Token of the Telegram Bot used to broadcast signals in Telegram channels. More info below.
- ``telegram_chat_ids``: List of the chat ids where the Telegram Bot is admin and can send messages. More info below.
- ``discord_webhooks``: List of discord webhooks. More info below.

When the desired configuration is set, just run `nuats_bot.py` to perform the TA on the tickers selected and automatically broadcast the signals to Telegram/Discord. Make sure to meet the `requirements.txt`.

### Set up Telegram / Discord hooks
##### Telegram
In order to broadcast a message in the Telegram platform you will need to create a Bot with [BotFather](https://core.telegram.org/bots#3-how-do-i-create-a-bot).  Then add the Bot in one of your channels and set it as an admin. You will have received the bot token, which is the  `telegram_token` parameter you need to fill in the `config.py` file.

Finally, get your channel id as explained [here](https://stackoverflow.com/questions/33858927/how-to-obtain-the-chat-id-of-a-private-telegram-channel) and include it in the `telegram_chat_ids` list.
##### Discord
You can create a webhook to your own server as explained [here](https://support.discordapp.com/hc/en-us/articles/228383668-Intro-to-Webhooks). Then copy the webhook link and include it in the `discord_webhooks` list of the `config.py` file. Easy peasy!


### Useful links
Check `useful_links.txt` for interesting GitHub repositories I have looked at to develop this Bot.

### License
Distributed under the MIT License.
  
Author: Bernat Font Garcia  
Email: bernatfontgarcia@gmail.com
