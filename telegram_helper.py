# -*- coding: utf-8 -*-
"""
Created on Sat Apr  7 20:47:10 2018

@author: troymcfont
"""

# --- Imports
import requests

# --- Class 
class telegramBot(object):
    def __init__(self, token, chat_ids):
        self.token = token
        self.chat_ids = chat_ids
        self.base_url = "https://api.telegram.org/bot{}/".format(token)


    def send_message(self, message, chat_id):
            url = self.base_url + "sendMessage?text={}&chat_id={}".format(message, chat_id)
            response = requests.get(url)
            content = response.content.decode("utf8")
            return content


    def broadcast_message(self, message):
        for chat_id in self.chat_ids:
            self.send_message(message, chat_id)
        return
