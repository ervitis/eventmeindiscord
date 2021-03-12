# -*- coding: utf-8 -*-

import logging

from discord.ext import commands

from handlers.calendar import Calendar, Event


class EventMeBot(commands.Cog):
    def __init__(self, bot_client):
        self._bot = bot_client
        self._subcommands = ['new']
        self._cal_service = Calendar()
        self.__logger = logging.getLogger(__name__)

    @commands.group(name='ev', help='create a calendar event')
    async def ev(self, ctx):
        await ctx.channel.send(f'Subcommands: {", ".join(self._subcommands)}')

    @ev.command(name='new')
    async def new(self, ctx, name, start, end):
        """create a new event: -ev new <name> <date in format YYYYMMDDHHMM> <end in format XH or XM where H is hour and M is minutes>
        Example: -ev new test 202104222230 1H
        """
        event = None
        try:
            event = Event(name=name, start=start, end=end)
        except ValueError:
            self.__logger.error(f'Exception ocurred with the event: {e}')
            await ctx.channel.send('Unrecognized event')

        if not event:
            return

        try:
            result = self._cal_service.create_event(event)
        except Exception as e:
            self.__logger.error(f'Exception ocurred: {e}')
            await ctx.channel.send('Error creating event in calendar')
        else:
            await ctx.channel.send(f'Event created! see it in your calendar on {result["htmlLink"]}')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        print(error)


def setup(client):
    client.add_cog(EventMeBot(client))
