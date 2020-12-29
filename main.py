#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import json
import logging
import datetime

import requests

log = logging.getLogger("jira")


def weeks_for_year(year):
    last_week = datetime.date(year, 12, 28)
    return last_week.isocalendar()[1]


class Jira(object):
    def __init__(self, root_url, username, token):
        self.API_URL = root_url
        self.USERNAME = username
        self.PASSWORD = token
        self.SESSION = requests.Session()

    def create_sprint(self, name:str, start_date:str, end_date:str, origin_board_id:int, goal:str=None):
        url = f"{self.API_URL}/rest/agile/1.0/sprint"

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization" : self._get_auth()
        }

        data = {
            "name": name,
            "startDate": start_date,
            "endDate": end_date,
            "originBoardId": origin_board_id,
        }
        if goal:
            data["goal"] = goal

        payload = json.dumps(data)

        response = requests.request(
            "POST",
            url,
            data=payload,
            headers=headers
        )
        return json.loads(response.text)

    def _get_auth(self):
        return f"Basic {base64.b64encode(f'{self.USERNAME}:{self.PASSWORD}'.encode('ascii')).decode()}"

    def get_all_boards(self):
        url = f"{self.API_URL}/rest/agile/1.0/board"

        headers = {
            "Accept": "application/json",
            "Authorization" : self._get_auth()
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
        return json.loads(response.text)

    def get_all_sprints(self, board_id:int):
        url = f"{self.API_URL}/rest/agile/1.0/board/{board_id}/sprint"

        headers = {
            "Accept": "application/json",
            "Authorization" : self._get_auth()
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
        return json.loads(response.text)

    def get_sprint(self, sprint_id):
        url = f"{self.API_URL}/rest/agile/1.0/sprint/{sprint_id}"

        headers = {
            "Accept": "application/json",
            "Authorization" : self._get_auth()
        }

        response = requests.request(
            "GET",
            url,
            headers=headers
        )
        return json.loads(response.text)


    def create_sprints_for_year(self, board_id, year, first_week = 1, num_weeks=0):
        begin_weekday = 6
        last_week_in_year = weeks_for_year(year)
        if num_weeks == 0:
            num_weeks = last_week_in_year - first_week + 1
        for week_number in range(first_week, first_week+num_weeks):
            begin_date = datetime.date.fromisocalendar(year,week_number,begin_weekday)
            if begin_date.year != year:
                # due to starting sprints in saturday
                continue
            sprint_name = f"Sprint tydzień {week_number} ({begin_date.isoformat()})"
            sprint_start_date = datetime.datetime.combine(begin_date, datetime.datetime.min.time())
            sprint_end_date = sprint_start_date + datetime.timedelta(days=6, hours=23, minutes=59, seconds=59)
            sprint_start_date_str = sprint_start_date.isoformat()
            sprint_end_date_str = sprint_end_date.isoformat()
            self.create_sprint(sprint_name, start_date=sprint_start_date_str, end_date=sprint_end_date_str, origin_board_id=board_id)

    def create_issue(self, project_name:str, name:str, due_date:str):
        url = f"{self.API_URL}/rest/api/3/issue"

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization" : self._get_auth()
        }

        data = {
            "fields" : {
                "summary": name,
                "duedate": due_date,
                "project": {
                    "key": project_name
                },
                "issuetype":
                    {
                        "id" : "10002"
                    }
            }
        }

        payload = json.dumps(data)

        response = requests.request(
            "POST",
            url,
            data=payload,
            headers=headers
        )
        return json.loads(response.text)



with open('credentials.json') as fp:
    credentials = json.load(fp)

j = Jira(**credentials)


board_id = 1
#j.create_sprints_for_year(board_id, 2021)

content = j.create_issue("DOM", "nazwa", datetime.datetime.now().isoformat())
print(json.dumps(content, sort_keys=False, indent=4, separators=(",", ": ")))


#j.get_all_boards()
#content = j.get_all_sprints(1)
#print(json.dumps(content, sort_keys=False, indent=4, separators=(",", ": ")))


#content = j.get_sprint(1)
#print(json.dumps(content, sort_keys=False, indent=4, separators=(",", ": ")))
#j.get_sprint(2)
#j.get_sprint(3)

#def create_sprints_for_year(year):
#    pass

#tera = datetime.datetime.now()
#print(tera.isocalendar())

#input("Podaj numer tygodnia:")

