# -*- coding: utf-8 -*-
import json
import os
from dataclasses import dataclass
from typing import Type

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


@dataclass
class EventTime(object):
    dateTime: str
    timeZone: str


@dataclass
class Event(object):
    name: str
    start: EventTime
    end: EventTime
    summary: str
    description: str
    status: str = 'confirmed'
    timeZone: str = 'Japan/Tokyo'

    @classmethod
    def to_json(cls):
        return json.dumps(cls.__dict__)

    @classmethod
    def validate_event(cls, args):
        print(args)


class Calendar(object):
    __SCOPES = [
        'https://www.googleapis.com/auth/calendar'
    ]
    __token_file = os.path.join('.', 'secret', 'token.json')
    __secret_file = os.path.join('.', 'secret', 'client-secret.json')
    __default_calendar = 'primary'

    def __init__(self):
        self._creds: Credentials = Type['None']
        self._service = None

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
        if not self._service:
            self._build_service()
        try:
            self._service.events().insert(calendarId=self.__default_calendar, body=event.to_json()).execute()
        except Exception as e:
            raise e
