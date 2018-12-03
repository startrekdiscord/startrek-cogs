import discord
from redbot.core import commands
from redbot.core import Config
import datetime
from dateutil.relativedelta import relativedelta

"""
Version 0.6 - Red-DiscordBot version
countdown command to replace nightbot on Star Trek Discord

needs dateutil from pip:
pip install python-dateutil

"""


class Countdown(commands.Cog):
    def __init__(self):
        self.config = Config.get_conf(self, identifier=47477389) # random identifier

    async def save_countdown_config(self):
        await self.config.countdowns.set(self.countdown_config)

    def calculate_until(self, end_time):
        # take a time string formatted as 'yyyy-mm-dd hh:mm:ss' and return how long it is from now
        end_time_formatted = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        # make a relativedelta object for the time between now and end_time_formatted
        time_left = relativedelta(datetime.datetime.now(), end_time_formatted)
        # each relative time field
        relative_time = [
            time_left.years,
            time_left.months,
            time_left.days,
            time_left.hours,
            time_left.minutes,
            time_left.seconds,
        ]
        # strings to represent each relative_time field
        time_string = ["years", "months", "days", "hours", "minutes", "seconds"]
        event_end_string = ""

        for period in relative_time:  # don't show 0 length time periods
            if period != 0:
                # add the number and corresponding time_string to what we'll return
                event_end_string += (
                    str(-period) + " " + time_string[relative_time.index(period)] + " "
                )
        return event_end_string

    def show_countdown(self, countdown_requested):

        # show a named countdown
        # find it in the loaded json file
        countdown_to_show = self.countdown_config[countdown_requested]
        # separate out the time portion and calculate it
        time_remaining = self.calculate_until(countdown_to_show[0])
        return (
            "**"
            + countdown_to_show[1]
            + "** `"
            + time_remaining
            + "`\n```"
            + countdown_to_show[2]
            + "```"
        )

    @commands.command()
    async def countdown(self, ctx, *, arg="next"):
        """ Show next occuring countdown

        countdown list   - retrievs a list of stored countdowns

        countdown all    - displays all current countdowns

        countdown add    - add an item, ex: countdown add christmas 2020-12-25 00:00:00 Christmas|Merry Christmas!

        countdown del    - remove an item, ex: countdown del christmas

        countdown [item] - get the definition for an item, ex: countdown christmas
        """

        self.countdown_config = await self.config.countdowns()
        if self.countdown_config is None:
          self.countdown_config = {}

        if arg.startswith("add"):

            # add new countdown

            try:
                # get the name
                new_countdown_shortname = arg.split()[1]
                # the end time
                new_countdown_time = str(
                    datetime.datetime.strptime(
                        " ".join(arg.split()[2:4]), "%Y-%m-%d %H:%M:%S"
                    )
                )
                # the description and synopsis
                temp_desc = " ".join(arg.split()[4:])
                new_countdown_description, new_countdown_synopsis = temp_desc.split("|")
                # add it to the dictionary and save the json
                self.countdown_config[new_countdown_shortname] = [
                    new_countdown_time,
                    new_countdown_description,
                    new_countdown_synopsis,
                ]
                await self.save_countdown_config()
                await ctx.send("Countdown added: " + new_countdown_shortname)

            except:

                # syntax error

                await ctx.send(
                    "Syntax error! Please check your date format and argument order."
                )

        elif arg.startswith("del"):

            # remove existing countdown

            try:

                countdown_to_remove = arg.split()[1]
                # take out the entire named section and save
                self.countdown_config.pop(countdown_to_remove)
                await self.save_countdown_config()
                await ctx.send("Removed countdown: " + countdown_to_remove)

            except:

                await ctx.send("Countdown not found: " + countdown_to_remove)

        elif arg.startswith("list"):

            # list existing countdowns

            await ctx.send(
                "These are the existing countdowns:\n`"
                + ", ".join(list(self.countdown_config.keys()))
                + "`"
            )

        elif arg.startswith("all"):

            # display all countdowns, properly formatted (todo: put them in date order)
            for each_countdown in list(self.countdown_config.keys()):
                await ctx.send(self.show_countdown(each_countdown))

        elif arg.startswith("next"):

            # show the soonest ending countdown
            # make temporary ordered lists, countdown names and their datetime objects
            temp_tags_list = []
            temp_dates_list = []
            for k, v in self.countdown_config.items():
                temp_tags_list.append(k)
                temp_dates_list.append(
                    datetime.datetime.strptime(v[0], "%Y-%m-%d %H:%M:%S")
                )
            if len(temp_tags_list) < 1:
                await ctx.send("Error, no existing countdowns!")
            else:
                # compare the temp dates to find the list index of the min
                countdown_to_show = temp_tags_list[
                    temp_dates_list.index(
                        min(temp_dates_list)
                    )  # get the name of the corresponding index
                ]
                await ctx.send(self.show_countdown(countdown_to_show))

        else:

            # show a countdown

            try:

                # pass the named countdown to the show_countdown function and send the result
                await ctx.send(self.show_countdown(arg.split()[0]))

            except:
                await ctx.send("Countdown not found: " + arg.split()[0])
