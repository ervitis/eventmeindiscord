# -*- coding: utf-8 -*-

import os
import re
from datetime import datetime, timedelta

from pytz import timezone
from typing import Type

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from infra.manager import SecretManager


class EventTime(object):

    def __init__(self, date_time, time_zone):
        self.date_time: datetime = date_time
        self.time_zone: timezone = time_zone


class Event(object):
    __default_format_datetime = '%Y%m%d%H%M'
    __c = re.compile
    __ptime = datetime.strptime

    __fields = {
        '__required': ['name', 'start', 'end'],
        'name': {
            'empty': False,
            'format': __c(r'\w+')
        },
        'start': {
            'empty': False,
            'format': __c(r'^(\d{4})(\d{2})(\d{2})\d{2}\d{2}$'),
            'dateformat': __ptime
        },
        'end': {
            'empty': False,
            'format': __c(r'\d{1,2}[H|M]')
        }
    }
    _args = None

    def __init__(self, **kwargs):
        self._args = kwargs

        if not self._validate_event():
            raise ValueError('arguments not valid')

        self.name = kwargs.get('name')
        self.time_zone = kwargs.get('time_zone', 'Asia/Tokyo')
        self.start = EventTime(
            self.__ptime(kwargs.get('start'), self.__default_format_datetime),
            timezone(self.time_zone)
        )
        self.end = kwargs.get('end')
        self.status = kwargs.get('status', 'confirmed')

    def to_json(self):
        if self.end.find('H') > 0:
            delta = timedelta(hours=int(self.end[:-1]))
        else:
            delta = timedelta(minutes=int(self.end[:-1]))
        end_date = self.start.date_time + delta
        return dict(
            start=dict(
                dateTime=f'{self.start.date_time:%Y-%m-%dT%H:%M:00}',
                timeZone=f'{self.start.time_zone}'
            ),
            end=dict(
                dateTime=f'{end_date:%Y-%m-%dT%H:%M:00}',
                timeZone=f'{self.start.time_zone}'
            ),
            summary=self.name,
            status=self.status,
        )

    def _validate_event(self) -> bool:
        args = self._args
        if len(args) != 3:
            return False

        c = 0
        for k, v in args.items():
            if k in self.__fields['__required']:
                c += 1
            if k not in self.__fields:
                return False
            dv = self.__fields[k]
            if dv['empty'] and v.strip().lower() == '':
                return False
            if 'format' not in dv:
                continue
            if not dv['format'].match(v):
                return False
            if 'dateformat' not in dv:
                continue
            try:
                dv['dateformat'](v, self.__default_format_datetime)
            except ValueError:
                return False
        if c != len(self.__fields['__required']):
            return False
        del self._args
        return True


class Calendar(object):
    __SCOPES = [
        'https://www.googleapis.com/auth/calendar'
    ]
    __token_file = os.path.join('.', 'secret', 'token.json')
    __secret_file = os.path.join('.', 'secret', 'client-secret.json')
    __default_calendar = 'primary'

    def __init__(self, smanager: SecretManager):
        self._creds: Credentials = Type['None']
        self._service = None
        self._smanager = smanager

    def _load_credentials(self) -> None:
        if os.path.exists(self.__token_file):
            self._creds = Credentials.from_authorized_user_file(self.__token_file)
        if not self._creds or not self._creds.valid:
            if self._creds and self._creds.expired and self._creds.refresh_token:
                self._creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.__secret_file,
                    self.__SCOPES
                )
                self._creds = flow.run_local_server()
            with open(self.__token_file, 'w') as ft:
                ft.write(self._creds.to_json())

    def _build_service(self) -> None:
        try:
            self._smanager.save()
        except Exception as e:
            raise e

        self._load_credentials()
        self._service = build('calendar', 'v3', credentials=self._creds)

    def list_events(self) -> None:
        if not self._service:
            self._build_service()
        result = self._service.events().list(calendarId=self.__default_calendar, maxResults=10).execute()
        events = result.get('items', [])

        for event in events:
            print(event)

    def create_event(self, event: Event):
        try:
            if not self._service:
                self._build_service()

            body = event.to_json()
            return self._service.events().insert(calendarId=self.__default_calendar, body=body).execute()
        except Exception as e:
            raise e
