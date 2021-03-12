# -*- coding: utf-8 -*-

from discord.ext import commands

from handlers.calendar import Calendar, Event


class EventMeBot(commands.Cog):
    def __init__(self, bot_client):
        self._bot = bot_client
        self._subcommands = ['new']
        self._cal_service = Calendar()

    @commands.group(name='ev', help='create a calendar event')
    async def ev(self, ctx):
        await ctx.channel.send(f'Subcommands: {", ".join(self._subcommands)}')

    @ev.command()
    async def new(self, ctx, *, event_data):
        if not Event.validate_event(event_data):
            await ctx.channel.send('Unrecognized event')
            return
        await ctx.channel.send('Creating')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        print(error)


def setup(client):
    client.add_cog(EventMeBot(client))
