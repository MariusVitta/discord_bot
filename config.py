import discord
from discord import Embed
from discord.ext import tasks
from discord.utils import get
from discord.ext import commands
# ------------------------------------------------------------------------------------------------------------#
# Gestion des commandes du bot
descriptionBot = "Bot DDJ"
prefixBot = '!'
usageBot = "Usage: {0}add".format(prefixBot)
intents = discord.Intents().all()

# CLIENT
client = commands.Bot(command_prefix=prefixBot, description=descriptionBot, intents=intents, help_command=None)