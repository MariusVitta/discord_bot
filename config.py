import discord

from discord.ext import commands
# ------------------------------------------------------------------------------------------------------------#
# Gestion des commandes du bot
descriptionBot = "Bot pour le jeu mudae"
prefixBot = '!'
messageStart = 'eventMudae'
usageBot = "Usage: {0}event".format(prefixBot)
usageMorpion = "Usage: {0}morpion @adversaire\nEx: {0}morpion <@935246624433782804>".format(prefixBot)
usagePuissance4 = "Usage: {0}puissance4 @adversaire\nEx: {0}puissance4 <@935246624433782804>".format(prefixBot)
intents = discord.Intents().all()

# CLIENT
client = commands.Bot(command_prefix=prefixBot, description=descriptionBot, intents=intents)

# ------------------------------------------------------------------------------------------------------------#
# Gestion des encheres
# https://emojipedia.org/ pour les différents Emojis
titreJeu = "🔸 Jeu Mudae 🔸"
titreJeuMorpion = "🔸 Morpion By Djamal 🔸"
titreJeuPuissance4 = "🎮 Puissance 4"
# --
sleepTime = 10.0

# --
whiteEmbed = discord.Color.from_rgb(255, 255, 255)

