
import os
from typing import List
from bs4 import BeautifulSoup

import requests
import random
import string

def generate_random_placeholder (s: str):
    while True:
        f = f"PLACEHOLDER{''.join([random.choice(string.ascii_letters) for _ in range(16)])}"
        if f not in s:
            return f

class PrinterEntry:
    __url    : str
    __team   : str
    __content: str

    def __init__ (self, team: str, url: str, content: str):
        self.__team = team
        self.__url  = url
        self.__content = content
    @property
    def url (self):
        return self.__url
    @property
    def team (self):
        return self.__team
    @property
    def content (self):
        return self.__content

class PrinterAPI:
    def __init__ (self, token: str):
        self.__token = token
    @property
    def print_url (self):
        return f"http://printer.codeforces.com/printEntry/query/{self.__token}"
    def read_entry (self) -> "PrinterEntry | None":
        response = requests.get( self.print_url ).json()
        if response['ready'] == 'false': return None
        team: str = response['teamName']
        link: str = response['printedLink']

        view_content: str = requests.get(link).content.decode("utf-8")
        placeholder_br    = generate_random_placeholder( view_content )
        
        view_content = view_content.replace("<br />", placeholder_br)
        text_content = BeautifulSoup( view_content ).get_text()
        
        text_content = text_content.replace(placeholder_br, "\n").strip()
        team_slug = team.split("=")[-1]
        return PrinterEntry(team_slug, link, text_content)
