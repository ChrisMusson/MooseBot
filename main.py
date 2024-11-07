import logging
import os
import subprocess

import discord
from discord.commands import Option
from dotenv import load_dotenv

from bonus import bonus

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_IDS = [1140257494732656730]

logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
logging_format = "%(asctime)s:%(levelname)s:%(name)s: %(message)s"
handler.setFormatter(logging.Formatter(logging_format))
logger.addHandler(handler)

bot = discord.Bot()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.slash_command(guild_ids=GUILD_IDS, description="Connect to a VPN")
async def connect(ctx):
    subprocess.Popen("nordvpn connect", shell=True).wait()
    await ctx.respond("Connected to VPN")


@bot.slash_command(guild_ids=GUILD_IDS, description="Disconnect from a VPN")
async def disconnect(ctx):
    subprocess.Popen("nordvpn disconnect", shell=True).wait()
    await ctx.respond("Disonnected from VPN")


@bot.slash_command(guild_ids=GUILD_IDS, description="Show the bps of specified games")
async def bps(
    ctx,
    team: Option(
        str, "3 letter abbreviation of the team you want", required=False, default=""
    ),
    gameweek: Option(
        str,
        "Gameweek to look at (defaults to current or most recent gw)",
        required=False,
        default="",
    ),
    only_live_matches: Option(
        bool,
        "Choose whether to only look at live matches (defaults to True)",
        required=False,
        default=True,
    ),
):
    try:
        if gameweek:
            only_live_matches = False
        resp = bonus(gameweek=gameweek, team=team, only_live_matches=only_live_matches)
        if resp:
            await ctx.respond(resp)
        else:
            if only_live_matches:
                await ctx.respond(
                    "There are no live matches. Either specify a gameweek, or set only_live_matches to False"
                )
            else:
                await ctx.respond("There are no matches that fit your criteria")
    except Exception as e:
        await ctx.respond(f"Sorry, that failed. Error:\n{e}")


bot.run(TOKEN)