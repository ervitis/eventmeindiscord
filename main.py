# -*- coding: utf-8 -*-
import logging

from discord.ext import commands

from infra.manager import SecretManager

EXTENSIONS = [
    'eventme'
]


def get_token() -> str:
    return SecretManager.discord()


def create_client() -> commands.Bot:
    return commands.Bot(command_prefix='-', description='Create an event in your Google Calendar')


def load_extensions(client: commands.Bot) -> commands.Bot:
    path_extensions = 'extensions'
    for extension in EXTENSIONS:
        pe = '.'.join([path_extensions, extension])
        client.load_extension(pe)
    return client


if __name__ == '__main__':
    __logger = logging.getLogger(__name__)
    __logger.info('Starting client')
    client = create_client()
    client = load_extensions(client)
    __logger.info('Extensions loaded')
    client.run(get_token(), bot=True, reconnect=True)
