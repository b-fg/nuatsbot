# -*- coding: utf-8 -*-
"""
Created on Sat Apr  7 20:47:10 2018
@author: troymcfont
"""

# --- Imports
import json
import requests
import time
from collections import defaultdict


# --- Class
class discordWebhook:
    def __init__(self, urls, **kwargs):
        """
        Initialise a Webhook Embed Object
        """
        self.urls = urls
        self.msg = kwargs.get('msg')
        self.color = kwargs.get('color')
        self.title = kwargs.get('title')
        self.title_url = kwargs.get('title_url')
        self.author = kwargs.get('author')
        self.author_icon = kwargs.get('author_icon')
        self.author_url = kwargs.get('author_url')
        self.desc = kwargs.get('desc')
        self.fields = kwargs.get('fields', [])
        self.image = kwargs.get('image')
        self.thumbnail = kwargs.get('thumbnail')
        self.footer = kwargs.get('footer')
        self.footer_icon = kwargs.get('footer_icon')
        self.ts = kwargs.get('ts')


    def add_field(self,**kwargs):
        '''Adds a field to `self.fields`'''
        name = kwargs.get('name')
        value = kwargs.get('value')
        inline = kwargs.get('inline', True)

        field = {'name' : name,
                 'value' : value,
                 'inline' : inline}
        self.fields.append(field)


    @property
    def json(self,*arg):
        '''
        Formats the data into a payload
        '''
        data = {}

        data["embeds"] = []
        embed = defaultdict(dict)
        if self.msg: data["content"] = self.msg
        if self.author: embed["author"]["name"] = self.author
        if self.author_icon: embed["author"]["icon_url"] = self.author_icon
        if self.author_url: embed["author"]["url"] = self.author_url
        if self.color: embed["color"] = self.color
        if self.desc: embed["description"] = self.desc
        if self.title: embed["title"] = self.title
        if self.title_url: embed["url"] = self.title_url
        if self.image: embed["image"]['url'] = self.image
        if self.thumbnail: embed["thumbnail"]['url'] = self.thumbnail
        if self.footer: embed["footer"]['text'] = self.footer
        if self.footer_icon: embed['footer']['icon_url'] = self.footer_icon
        if self.ts: embed["timestamp"] = self.ts

        if self.fields:
            embed["fields"] = []
            for field in self.fields:
                f = {}
                f["name"] = field['name']
                f["value"] = field['value']
                f["inline"] = field['inline']
                embed["fields"].append(f)

        data["embeds"].append(dict(embed))

        empty = all(not d for d in data["embeds"])

        if empty and 'content' not in data:
            print('You cant post an empty payload.')
        if empty: data['embeds'] = []

        return json.dumps(data, indent=4)

    def broadcast_message(self, message):
        self.msg = message
        for url in self.urls:
            self.post(url)
        return

    def post(self, url):
        """
        Send the JSON formated object to the specified `self.url`.
        """
        if url is not None and url != '':
            headers = {'Content-Type': 'application/json'}
            result = requests.post(url, data=self.json, headers=headers)

            if result.status_code == 400:
                print("Post Failed, Error 400")
            else:
                print("Payload delivered successfuly")
                print("Code : "+str(result.status_code))
                time.sleep(2)
