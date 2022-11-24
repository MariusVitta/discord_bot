import collections
import json
import os
import re

import discord

from config import titreJeuPuissance4

nbJoueurMaxTop = 6

dossierScore = "scores"
fichierScore = "scores.json"  # id/<nombre_victoires>/<nombre_défaites>
path = "/home/minecraft/multicraft/servers/server248791/MudaeGames/"

# 1 2 3 4 5 6
# 7 8 9 10 11 12
# 13 14 15 16 17 18
# 19 20 21 22 23 24
# 25 26 27 28 29 30

async def topEmbed(page: int, guild, channel):
    data: list = getData()
    if data is None:
        await channel.send("Il y a pas encore de leaderboard, aucune partie n'a été encore joué")
    guildActual = guild
    embed = discord.Embed(
        title=titreJeuPuissance4,
        color=discord.Color.from_rgb(115, 150, 255)
    )
    premierJ = nbJoueurMaxTop * (page - 1)
    dernierJ = nbJoueurMaxTop * page
    pseudos, victoires, defaites = await getTextEmbed(guildActual, data, premierJ, dernierJ)

    nbPages = len(data) / nbJoueurMaxTop if (len(data) % nbJoueurMaxTop) == 0 else round(len(data) / nbJoueurMaxTop + 1)

    embed.add_field(name="Joueurs", value=pseudos, inline=True)
    embed.add_field(name="Victoires", value=victoires, inline=True)
    embed.add_field(name="Défaites", value=defaites, inline=True)
    embed.set_footer(text="Page {}/{}".format(page, nbPages))

    return embed


def getData():
    """ Méthode qui crée (si non existance) le chemin de sauvegarde du fichier scores
        ensuite récupere les données du leaderboard, le tri et les renvoie sous forme d'un tableau
        indice 0 :Id du joueur
        indice 1 : nombre de victoires du joueur
        indice 2 : nombre de défaites du joueur

        Returns
        -------
        data : list
             tableau de données ou None s'il n'y a pas encore de données dans le leaderboard

    """
    if not os.path.exists(f"{path}{dossierScore}"):
        os.makedirs(f"{path}{dossierScore}", mode=0o777, exist_ok=False)  # création du dossier s'il n'existe pas encore
    if not os.path.exists(f"{path}{dossierScore}/{fichierScore}"):
        open(f"{path}{dossierScore}/{fichierScore}", "x",
             encoding="utf-8")  # création du fichier s'il n'existe pas encore

    filesize = os.path.getsize(f"{dossierScore}/{fichierScore}")
    if filesize == 0:
        return None
    data = ""

    # récuperation de l'ensemble des scores actuels
    with open(f"{dossierScore}/{fichierScore}", 'r') as json_file:
        data = json.load(json_file)

    # tri du tableau de données selon la méthode passe paramètres
    result = collections.OrderedDict(
        sorted(data.items(), key=lambda t: (t[1]["victoires"], - t[1]['defaites']), reverse=True))

    return list(result.items())


def getNumberPage():
    # récuperation de l'ensemble des scores actuels
    with open(f"{dossierScore}/{fichierScore}", 'r') as json_file:
        data = json.load(json_file)

    nbPages = len(list(data.items())) / nbJoueurMaxTop if (len(list(data.items())) % nbJoueurMaxTop) == 0 else round(len(list(data.items())) / nbJoueurMaxTop + 1)
    return nbPages


async def getTextEmbed(guildActual, data, minIndice, maxIndice):
    pseudos = ""
    victoires = ""
    defaites = ""
    medaille = ""
    for i in range(minIndice, maxIndice):
        print(i)
        if i == 0:
            medaille = "🥇 - "
        elif i == 1:
            medaille = "🥈 - "
        elif i == 2:
            medaille = "🥉 - "
        else:
            medaille = "🔸 - "

        if i < len(data):
            member = await guildActual.fetch_member(data[i][0])

            pseudos += f"{medaille}**{member.display_name}**\n"
            victoires += f"<:Victory:937012638536314951> **{data[i][1]['victoires']}**\n"
            defaites += f"<:Defeat:937012765254615080> **{data[i][1]['defaites']}**\n"
        else:
            pass

    return pseudos, victoires, defaites
