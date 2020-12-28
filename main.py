#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import json
import logging
import datetime

import requests

log = logging.getLogger("jira")


class Jira(object):
    API_URL = None
    USERNAME = None
    PASSWORD = None
    SESSION = None

    def __init__(self, root_url, username, token):
        self.API_URL = root_url
        self.USERNAME = username
        self.PASSWORD = token
        if self.SESSION is None:
            self.SESSION = requests.Session()

    def _fetch(self, url):
        log.info('Request for url: %s', url)
        res = self.SESSION.get(url)
        try:
            ret = res.json()
            log.debug(f'Response: {ret}')
        except ValueError:
            log.debug('Request for url: %s', url)
            ret = []
        return ret

    def create_sprint(self, name:str, start_date:str, end_date:str, origin_board_id:int, goal:str):
        url = f"{self.API_URL}/rest/agile/1.0/sprint"

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": self._get_auth()
        }

        payload = json.dumps({
            "name": name,
            "startDate": start_date,
            "endDate": end_date,
            "originBoardId": origin_board_id,
            "goal": goal
        })

        response = requests.request(
            "POST",
            url,
            data=payload,
            headers=headers
        )

    def _get_auth(self):
        return base64.b64encode(f"{self.USERNAME}:{self.PASSWORD}".encode('ascii')).decode()

    def get_all_boards(self):
        url = f"{self.API_URL}/rest/agile/1.0/board"

        headers = {
            "Accept": "application/json",
            "Authorization" : f"Basic {self._get_auth()}"
        }

        payload = json.dumps({
            "startAt": 0,
            "maxResults": 1000,
            "type": "scrum"
        })


        response = requests.request(
            "GET",
            url,
            headers=headers,
            data = payload
        )

        print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))

    def get_all_sprints(self, board_id:int):
        url = f"{self.API_URL}/rest/agile/1.0/board/{board_id}/sprint"

        headers = {
            "Accept": "application/json",
            "Authorization" : f"Basic {self._get_auth()}"
        }

        payload = json.dumps({
            "startAt": 0,
            "maxResults": 1000
        })


        response = requests.request(
            "GET",
            url,
            headers=headers,
            data = payload
        )
        print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))

    def get_sprint(self, sprint_id):
        url = f"{self.API_URL}/rest/agile/1.0/sprint/{sprint_id}"

        headers = {
            "Accept": "application/json",
            "Authorization" : f"Basic {self._get_auth()}"
        }

        response = requests.request(
            "GET",
            url,
            headers=headers
        )

        print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))



with open('credentials.json') as fp:
    credentials = json.load(fp)

j = Jira(**credentials)

j.get_all_boards()
j.get_all_sprints(1)

j.get_sprint(1)
j.get_sprint(2)
j.get_sprint(3)

#def create_sprints_for_year(year):
#    pass

#tera = datetime.datetime.now()
#print(tera.isocalendar())

#input("Podaj numer tygodnia:")

