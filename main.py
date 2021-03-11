# -*- coding: utf-8 -*-
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv


EXTENSIONS = [
    'eventme'
]


def get_token() -> str:
    load_dotenv()
    return os.getenv('DISCORD_TOKEN')


def create_client() -> commands.Bot:
    return commands.Bot(command_prefix='-', description='Create an event in your Google Calendar')


def load_extensions(client: commands.Bot) -> commands.Bot:
    path_extensions = 'extensions'
    for extension in EXTENSIONS:
        pe = '.'.join([path_extensions, extension])
        client.load_extension(pe)
    return client


if __name__ == '__main__':
    client = create_client()
    client = load_extensions(client)
    client.run(get_token(), bot=True, reconnect=True)
