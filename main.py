import asyncio
import json
import os
import re

import discord
from PIL import Image
from discord import Embed
from discord.ext import tasks
from discord.utils import get
from dotenv import load_dotenv
from config import *
from discord.ext.commands import CommandNotFound, ArgumentParsingError, MissingRequiredArgument, BadArgument
import boutons
import random
import unidecode
from datetime import datetime
from jeuPVP import *
from logs import Traces
from morpion import *
from boutons import *

from puissance4 import getData, topEmbed, getNumberPage

global lanceurPartie, tabJoueur, guild, tabIDChannel, enCours, tabReponse, rouletteEnCours, banqueEnCours

fichierMessages = "messages.txt"
tabEmoji = ["✅", "🎴"]
indiceEmojiCheck = 0
indiceEmojiFlower = 1

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
IDCHANNEL = int(os.getenv('IDCHANNEL'))
IDCHANNELMORPION = int(os.getenv('IDCHANNELMORPION'))
LOGS = 936404977059000320
# IDCHANNELROULETTE = int(os.getenv("CHANNEL_ROULETTE"))

# Tableaux avec les cases de la roulette et leur couleur
cases = [
    [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36],
    [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35],
    [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34]
]

douzaines = [
    [i for i in range(1, 13)],
    [i for i in range(13, 25)],
    [i for i in range(25, 37)]
]

rouge = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
noir = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]

# Emojis personnalisés utilisés
em = {
    "couleur": "<:rondcasino:935601205651079299>",
    "douzaine": "<:table:935603960113406003>",
    "chiffre": "<:chiffre:935605036296323173>",
    "nombre": "<:chiffre:935605036296323173>",
    "roulette": "<:roulette:935623739721277575>",
    "fleche": "<:fleche:925077237164806164>",
    "kakera": "<:kake:925052720870752296>",
    "colonne": "<:colonne:935895894413422592>",
    "parite": "<:parite:935897220279054367>",
    "jeton": "<:Jeton:935878250620661881>"
}
fichierRoulette = "dataRoulette.txt"
indiceNbParties = 1
indiceGains = 2
indicePertes = 3

# puissance 4
hauteurPuissance4 = 6
nombreColonne = 7
stringChiffre = ":one::two::three::four::five::six::seven:"
lineBlackSquare = "<:square:936719107989065799><:square:936719107989065799><:square:936719107989065799><:square:936719107989065799><:square:936719107989065799><:square:936719107989065799><:square:936719107989065799>"
stringRedSquare = "<:pionrouge:936719839198842990>"
stringYellowSquare = "<:pionjaune:936720442218147940>"
stringBlackSquare = "<:square:936719107989065799>"
stringYellowSquarePrev = "<:pionjaune2:937121602011799622>"
stringRedSquarePrev = "<:pionrouge2:937121592037761024>"
pointJaune = "<:yellowpoint:937066625390227476>"
pointRouge = "<:redpoint:937066613658771506>"
fichierScore = "scores.json"  # id/<nombre_victoires>/<nombre_défaites>
fichierScoreMorpion = "scores_morpion.json"
dossierScore = "scores"
tabEmojiFleche = ["<:Defeat:937012765254615080>",
                  "<:Lancien:910835421305524224>"]  # ["<:reversefleche:936724361740693585>", "<:fleche:925077237164806164>"]
tabIDFleche = [937012765254615080, 910835421305524224]  # [936724361740693585, 925077237164806164]

indiceID = 0
indiceNbVictoires = 1
indiceNbDefaites = 2
indiceEmbed = 0

path = "/home/minecraft/multicraft/servers/server248791/MudaeGames/"


def getCouleur(case: int):
    """
    Fonction pour récupérer la couleur d'une case

    Paramètres :
        case (int) : Le numéro de la case
    Retourne :
        couleur (str) : La couleur (rouge ou noire)
    """
    couleur = None
    if case in rouge:
        couleur = "Rouge"
    else:
        couleur = "Noire"
    return couleur


def gagnants(joueurs, infos):
    """
    Fonction pour récupérer les gagnants et la somme gagnée

    Paramètres :
        joueurs (dict) : Dictionnaire contenant les infos de tous les joueurs
        infos (tuple) : Dictionnaire contenant les infos de la case gagnante
    Retourne :
        gagnantsMises (list) : Liste contenant des tuples joueurs + somme gagnée
    """
    gagnantsMises = []
    optionsGagnantes = [f"Colonne {infos[0]}", f"{'Pair' if infos[1] is True else 'Impair'}", infos[2],
                        f"Douzaine {infos[3]}", str(infos[4])]
    for joueur in joueurs:
        if joueurs[joueur][2] in optionsGagnantes:
            coeff = 0.
            if optionsGagnantes.index(joueurs[joueur][2]) == 2 or optionsGagnantes.index(joueurs[joueur][2]) == 1:
                coeff = 1.5
            elif optionsGagnantes.index(joueurs[joueur][2]) == 0 or optionsGagnantes.index(joueurs[joueur][2]) == 3:
                coeff = 2
            else:
                coeff = 11
            gagnantsMises.append((joueur, joueurs[joueur][0], int(joueurs[joueur][1]) * coeff))
    return gagnantsMises


def getCaseInfo(case: int):
    """
    Fonction pour récupérer des infos sur une case

    Paramètres :
        case (int) : Le numéro de la case
    Retourne :
        tuple :
        - La colonne de la case (int : 1 à 3)
        - Si le numéro est pair ou non (bool : True ou False)
        - Sa couleur (str : "rouge" ou "noir")
        - Sa douzaine (int : 1 à 3)
        - Le numéro de la case
        - Coordonnées du point haut gauche de la case dans le rectangle (Tuple : (int, int))
    """
    colonne = 0
    colonneTemp = 0
    pair = None
    douzaine = 0
    """for i in range(len(cases)):
        if case in cases[i - 1]:
            colonne = i + 1
            break
    for i in range(len(cases)):
        if case in cases[i]:
            colonneTemp = i + 1
            break"""
    if case % 2 == 0:
        pair = True
    else:
        pair = None

        # cases = [
        #     [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36],
        #     [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35],
        #     [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34]
        # ]

    if case in cases[0]:
        colonne = 3
    elif case in cases[1]:
        colonne = 2
    elif case in cases[2]:
        colonne = 1

    if case in douzaines[0]:
        douzaine = 1
    elif case in douzaines[1]:
        douzaine = 2
    elif case in douzaines[2]:
        douzaine = 3

    return colonne, pair, getCouleur(case), douzaine, case


def phraseTypePrecis(typeP):
    """
    Fonction pour récupérer la phrase utilisée dans les récaps (embed)

    Paramètres :
        typeP (str) : Le type de mise
    Retourne :
        str : la phrase correspondante
    """
    if typeP == "Pair":
        return "la parité du résultat"
    elif typeP == "Impair":
        return "la non-parité du résultat"
    elif typeP == "Noire":
        return "une case noire"
    elif typeP == "Rouge":
        return "une case rouge"
    elif typeP == "Douzaine 1":
        return "la première douzaine (1 à 12)"
    elif typeP == "Douzaine 2":
        return "la seconde douzaine (13 à 24)"
    elif typeP == "Douzaine 3":
        return "la troisième douzaine (25 à 36)"
    elif typeP.isdecimal() and int(typeP) < 10:
        return f"le chiffre {typeP}"
    elif typeP.isdecimal() and int(typeP) > 9:
        return f"le nombre {typeP}"
    else:
        return f"la {typeP.lower()}"


@client.event
async def on_ready():
    init()
    print('Connecte en tant que {0}!'.format(client.user))


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error


def init():
    global lanceurPartie, tabJoueur, guild, tabIDChannel, enCours, tabReponse, rouletteEnCours, banqueEnCours
    tabJoueur = {}
    tabIDChannel = {}
    lanceurPartie = ""
    guild = ""
    enCours = False
    tabReponse = []
    rouletteEnCours = False
    banqueEnCours = False


# @client.command(name='test')
# async def test1(self):
#     await self.channel.send("ahhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh")
#     files = os.listdir("dossier")
#     if os.path.exists("{}".format("dossier")):
#         for file in files:
#             await self.channel.send(file=file)

@client.command()
async def testS(self):
    await boutons.verifKake(128281251596599297)


@client.command()
async def testM(self):
    await boutons.verifKake(401115745670660116)


@client.command(name="si")
async def testS(self):
    await self.channel.send("oui")


@client.command(name="ajoutVerif")
async def ajout_verif(self):
    thisGuild = self.guild
    members = thisGuild.members

    for member in members:
        listRole = member.roles
        if len(listRole) == 1:
            role1 = get(member.guild.roles, id=899978401094443078)
            role2 = get(member.guild.roles, id=874051545006759936)
            await member.add_roles(role2, role1)
            await self.channel.send(member.name + " a bien eu ses roles " + thisGuild.get_role(
                899978401094443078).name + " et " + thisGuild.get_role(874051545006759936).name)


@client.command(name='event')
@commands.has_permissions(administrator=True)
async def event(self):
    global lanceurPartie, guild
    init()
    guild = self.guild
    channel = self.channel
    lanceurPartie = self.message.author

    """if IDCHANNEL != channel.id:
        await channel.send(
            f"Je ne peux pas me lancer dans ce salon là \n ➡️ {client.get_channel(IDCHANNEL).mention}",
            delete_after=15.0)
        return"""
    if self.author.bot:
        return

    embed = discord.Embed(
        title=titreJeu,
        description="{0}\n\n{1}‏\n\n{2}‏".format("Debut du jeu...", "Réagissez (🎴) pour participer au jeu",
                                                 f"la partie se lancera une fois que **{self.message.author.display_name}** cliquera sur ✅"),
        color=discord.Color.from_rgb(255, 255, 255)
    )
    embed.set_footer(text="Session lancée par {}".format(self.message.author.display_name),
                     icon_url=self.message.author.avatar)

    choix = await channel.send(embed=embed)

    for emoji in tabEmoji:
        await choix.add_reaction(emoji)


@client.command(name="topMorpionx", aliases=["morpionTopx", "topMx"])
async def topMorpion(self):
    with open(f"{dossierScore}/{fichierScoreMorpion}") as json_file:
        data = json.load(json_file)

    print(data)
    data = sorted(data, key=lambda k: (k[2], k[0]), reverse=True)
    print(data)
    await self.channel.send(data)


@event.error
async def event_error(ctx, error):
    """ Gestion d'erreur sur la commande vente
        on vérifie que l'erreur `error` est bien une instance de `MissingRequiredArgument`
        on retourne dans le salon d'utilisation un exemple d'usage de la commande

        Parameters
        ----------
        ctx :
            contexte d'execution
        error : erreur
            instance de Error
    """
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send(usageBot, delete_after=15.0)
    if isinstance(error, discord.ext.commands.errors.BadArgument):
        await ctx.send(usageBot, delete_after=15.0)
    return


@client.event
async def on_raw_reaction_add(payload):
    global lanceurPartie, tabJoueur, enCours
    member = payload.member

    if member.bot:
        return

    if payload.channel_id == IDCHANNEL:
        if enCours:
            return
        channel = client.get_channel(IDCHANNEL)
        message = await channel.fetch_message(payload.message_id)

        messageID = payload.message_id
        memberID = member.id
        reaction1 = get(message.reactions, emoji=tabEmoji[indiceEmojiCheck])
        reaction2 = get(message.reactions, emoji=tabEmoji[indiceEmojiFlower])
        if payload.emoji.name == tabEmoji[indiceEmojiFlower] and memberID == lanceurPartie.id:
            await reaction2.remove(member)
        if payload.emoji.name == tabEmoji[indiceEmojiCheck] and memberID != lanceurPartie.id:
            await reaction1.remove(member)
        if memberID == lanceurPartie.id:
            if reaction1 is not None:
                async for user in reaction1.users():
                    if user == lanceurPartie:
                        await lancerJeu()
                        enCours = True

        else:
            if reaction2 is not None:
                tabJoueur[f"{member.id}"] = 0

        if payload.emoji.name != tabEmoji[indiceEmojiFlower] and payload.emoji.name != tabEmoji[indiceEmojiCheck]:
            reactionIndesirable = get(message.reactions, emoji=payload.emoji)
            await reactionIndesirable.clear()


@client.event
async def lancerJeu():
    global lanceurPartie, tabJoueur, guild, tabIDChannel
    category = discord.utils.get(guild.categories, id=917819030277075045)
    channelCorrection = "Corrections"

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True)
    }
    channelCorrection = await guild.create_text_channel(channelCorrection, overwrites=overwrites, category=category)
    tabIDChannel[channelCorrection] = channelCorrection.id

    for key in tabJoueur:
        member = await guild.fetch_member(key)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=False),
        }
        channel = await guild.create_text_channel(f"Salon de {member.name}", overwrites=overwrites, category=category)
        tabJoueur[key] = channel.id
        await channel.send(f"Voici ton salon de jeu <@{key}>")


async def openChannel():
    global tabJoueur
    for key in tabJoueur:
        member = await guild.fetch_member(key)
        channel = client.get_channel(tabJoueur[key])
        await channel.set_permissions(member, send_messages=True, read_messages=True)
        await channel.send(f"Il est temps de taper ta réponse <@{key}>")


async def closeChannel():
    global tabJoueur
    for key in tabJoueur:
        member = await guild.fetch_member(key)
        channel = client.get_channel(tabJoueur[key])
        await channel.set_permissions(member, send_messages=False, read_messages=True)


async def alertAll():
    global tabJoueur
    for key in tabJoueur:
        channel = client.get_channel(tabJoueur[key])
        await channel.send(f"Il reste 5s <@{key}>")


async def getAllAnswer():
    global tabReponse
    reponse = ""
    for key in tabJoueur:
        channel = client.get_channel(tabJoueur[key])
        member = await guild.fetch_member(key)
        message = await channel.fetch_message(channel.last_message_id)
        reponse = "[{}]: {}\n\n".format(member.name, message.content)
    tabReponse.append(reponse)


@client.command(name='reponses')
@commands.has_permissions(administrator=True)
async def reponses(ctx):
    global tabReponse
    for indice in range(len(tabReponse)):
        embed = discord.Embed(
            title="Image N°{}".format(indice),
            description="{0}\n\n{1}‏\n\n".format("Réponses: ", tabReponse[indice]),
            color=discord.Color.from_rgb(109, 7, 26)
        )
        channel = client.get_channel(IDCHANNEL)
        await channel.send(embed=embed)
        await asyncio.sleep(15)
        embed = discord.Embed(
            title="Prochaines Réponses",
            color=discord.Color.from_rgb(109, 7, 26)
        )
        await channel.send(embed=embed)


@client.command(name='openCorrection')
@commands.has_permissions(administrator=True)
async def openCorrection(ctx):
    global tabJoueur, tabIDChannel
    channel = tabIDChannel["Corrections"]
    for key in tabJoueur:
        member = await guild.fetch_member(key)
        await channel.set_permissions(member, send_messages=False, read_messages=True)


@client.command(name='picture')
@commands.has_permissions(administrator=True)
async def picture(self):
    await self.message.attachments[0].save("image.png")
    for key in tabJoueur:
        channel = client.get_channel(tabJoueur[key])
        await channel.send(file=discord.File("image.png"))
    await openChannel()
    await asyncio.sleep(20)
    await alertAll()
    await asyncio.sleep(5)
    await closeChannel()
    await getAllAnswer()
    os.remove("image.png")


@client.command(name='deleteChannels')
@commands.has_permissions(administrator=True)
async def deleteChannels(self):
    global tabJoueur, tabIDChannel
    channel = tabIDChannel["Corrections"]
    if channel is not None:
        await channel.delete()
    for key in tabJoueur:
        channel = client.get_channel(tabJoueur[key])
        # if the channel exists
        if channel is not None:
            await channel.delete()
        # if the channel does not exist, inform the user
        # else:
        #   await self.send(f"Aucun channel nommé, n'a été trouvé"
    await self.delete()


@client.command(name='morpionX')
async def morpion(self, member: discord.Member):
    channel = self.channel
    if IDCHANNELMORPION != channel.id:
        await channel.send(
            f"Je ne peux pas me lancer dans ce salon là \n ➡️ {client.get_channel(IDCHANNELMORPION).mention}",
            delete_after=15.0)
        return
    if self.author.bot:
        return
    if member.bot:
        await self.message.reply("Tu ne peux pas jouer contre un bot, pauvre idiot")
        return
    if member.id == self.message.author.id:
        await self.message.reply("Tu ne peux pas jouer contre toi même -_- !")
        return

    attente = await self.message.reply(
        f"{member.display_name} voulez-vous jouer au morpion contre {self.message.author.display_name} ?")
    viewVeutJouer = boutons.ViewVerificationMorpion(member)
    await attente.edit(view=viewVeutJouer)
    decision = await viewVeutJouer.wait()
    if decision:
        await attente.reply(f"Partie annulée, **{member.display_name}** n'a pas accepté l'invitation à temps.")
        return
    elif not viewVeutJouer.veutJouer:
        await attente.reply(f"Partie annulée, **{member.display_name}** n'a pas accepté l'invitation.")
        return

    embed = discord.Embed(
        title=titreJeuMorpion,
        description="{0}\n\n{1}‏\n\n{2}‏‏".format("Debut du jeu...",
                                                  f"▫️ Le joueur {self.message.author.display_name}: <:xcross:936758268448100443>\n▫️ Le joueur {member.display_name}: <:circle:936758258172063854> ",
                                                  f"Le joueur {self.message.author.display_name} jouera en premier"),
        color=discord.Color.from_rgb(255, 255, 255)
    )
    embed.set_footer(text="Session lancée par {}".format(self.message.author.display_name),
                     icon_url=self.message.author.avatar)

    await channel.send(embed=embed)
    embedPartie = discord.Embed(
        title=titreJeuMorpion,
        description="{0}\n\n".format(
            f"▫️ Le joueur {self.message.author.display_name}: <:xcross:936758268448100443>\n▫️ Le joueur {member.display_name}: <:circle:936758258172063854>"),
        color=discord.Color.from_rgb(255, 255, 255)
    )
    embedComplet = discord.Embed(
        title=titreJeuMorpion,
        description="{0}\n\n".format(
            f"▫️ La grille est complète, fin de partie !"),
        color=discord.Color.from_rgb(255, 255, 255)
    )

    joueur1 = JoueurMorpion(1, self.message.author)
    joueur2 = JoueurMorpion(2, member)

    partieMorpion = Morpion(joueur1, joueur2)

    premierMessage = True
    msg = ""
    messageJoueur = ""
    while partieMorpion.getPartieEnCours():
        viewMorpion = boutons.ViewMorpion(partieMorpion)
        if premierMessage:
            msg = await channel.send(embed=embedPartie, view=viewMorpion)
            messageJoueur = await channel.send(
                f"{partieMorpion.getJoueurActuel().getMember().mention} c'est à ton tour de jouer")
            premierMessage = False
        else:
            await msg.edit(view=viewMorpion)
            await messageJoueur.edit(
                content=f"{partieMorpion.getJoueurActuel().getMember().mention} c'est à ton tour de jouer")
        await viewMorpion.wait()

        verifGrille(partieMorpion)
        if partieMorpion.getEstGagnant():
            viewMorpion = boutons.ViewMorpion(partieMorpion)
            await msg.edit(view=viewMorpion)
            embedGagnant = discord.Embed(
                title=titreJeuMorpion,
                description="{0}\n\n".format(
                    f"▫️ Le gagnant est {partieMorpion.getJoueurActuel().getMember().display_name} ! \n"),
                color=discord.Color.from_rgb(255, 255, 255)
            )
            await channel.send(embed=embedGagnant)
            sauvegardeScoreMorpion(
                [partieMorpion.getJoueurActuel().getMember().id, partieMorpion.getAdversaire().getMember().id],
                [1, 0, 0])
            return
        if partieMorpion.getEstComplet():
            viewMorpion = boutons.ViewMorpion(partieMorpion)
            await msg.edit(view=viewMorpion)
            await channel.send(embed=embedComplet)
            sauvegardeScoreMorpion(
                [partieMorpion.getJoueurActuel().getMember().id, partieMorpion.getAdversaire().getMember().id],
                [0, 0, 1])
            return

        partieMorpion.changerJoueur()


def verifGrille(partieMorpion: Morpion):
    signe = "X" if partieMorpion.getJoueurActuel().getValeur() == 1 else "O"
    tableau = partieMorpion.getTableauJeu()

    # lignes
    for i in range(len(tableau)):
        if tableau[i][0] == signe and tableau[i][1] == signe and tableau[i][2] == signe:
            partieMorpion.setEstGagnant(True)
            return
    # colonne
    for i in range(len(tableau)):
        if tableau[0][i] == signe and tableau[1][i] == signe and tableau[2][i] == signe:
            partieMorpion.setEstGagnant(True)
            return
    # diagonales
    if tableau[0][0] == signe and tableau[1][1] == signe and tableau[2][2] == signe:
        partieMorpion.setEstGagnant(True)
        return
    if tableau[0][2] == signe and tableau[1][1] == signe and tableau[2][0] == signe:
        partieMorpion.setEstGagnant(True)
        return

    tableauFlat = [item for sublist in tableau for item in sublist]
    if "-" not in tableauFlat:
        partieMorpion.setEstComplet(True)
    else:
        return


@morpion.error
async def morpion_error(ctx, error):
    """ Gestion d'erreur sur la commande vente
        on vérifie que l'erreur `error` est bien une instance de `MissingRequiredArgument`
        on retourne dans le salon d'utilisation un exemple d'usage de la commande

        Parameters
        ----------
        ctx :
            contexte d'execution
        error : erreur
            instance de Error
    """
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send(usageMorpion, delete_after=15.0)
    if isinstance(error, discord.ext.commands.errors.BadArgument):
        await ctx.send(usageMorpion, delete_after=15.0)
    return


def sauvegardeScoreMorpion(listJoueurs: list, scoresJoueurs: list):
    """ Methode de sauvegarde du score des joueurs.
        Données réprésentées sous la forme : un_ancian#8649/<nombre_victoires>/<nombre_défaites>

        Parameters
        ----------
        listJoueurs : list
            tableau de string contenant le nom de l'ensemble des joueurs avec leurs discriminants
        scoresJoueurs : list
            tableau de string contenant les scores de l'ensemble des joueurs aux mêmes indices que dans le tableau listJoueurs
    """
    if not os.path.exists(f"{path}{dossierScore}"):
        os.makedirs(f"{path}{dossierScore}", mode=0o777, exist_ok=False)  # création du dossier s'il n'existe pas encore
    if not os.path.exists(f"{path}{dossierScore}/{fichierScoreMorpion}"):
        open(f"{path}{dossierScore}/{fichierScoreMorpion}", "x",
             encoding="utf-8")  # création du fichier s'il n'existe pas encore

    data = []
    # récuperation de l'ensemble des scores actuels
    with open(f"{path}{dossierScore}/{fichierScoreMorpion}", 'r') as json_file:
        data = json.load(json_file)

    i = 0
    val1 = scoresJoueurs.index(1)
    if val1 == 0:
        if str(listJoueurs[val1]) in data.keys():
            data[str(listJoueurs[val1])]["victoires"] += 1
        else:
            data[str(listJoueurs[val1])] = {"victoires": 1, "defaites": 0, "nuls": 0}

        if str(listJoueurs[1]) in data.keys():
            data[str(listJoueurs[1])]["defaites"] += 1
        else:
            data[str(listJoueurs[1])] = {"victoires": 0, "defaites": 1, "nuls": 0}
    else:
        if str(listJoueurs[0]) in data.keys():
            data[str(listJoueurs[0])]["nuls"] += 1
        else:
            data[str(listJoueurs[0])] = {"victoires": 0, "defaites": 0, "nuls": 1}

        if str(listJoueurs[1]) in data.keys():
            data[str(listJoueurs[1])]["nuls"] += 1
        else:
            data[str(listJoueurs[1])] = {"victoires": 0, "defaites": 0, "nuls": 1}

    with open(f"{path}{dossierScore}/{fichierScoreMorpion}", 'w') as json_file:
        json.dump(data, json_file, sort_keys=True, indent=4)
    # joueurDiscriminator = messageAuthor.name + "#" + messageAuthor.discriminator
    # on parcourt le tableau des resultats pour modifier le score des joueurs déjà existant
    pass


@client.command(name='puissance4X')
async def puissance4(self, member: discord.Member):
    channel = self.channel
    """if IDCHANNELMORPION != channel.id:
        await channel.send(
            f"Je ne peux pas me lancer dans ce salon là \n ➡️ {client.get_channel(IDCHANNELMORPION).mention}",
            delete_after=15.0)
        return"""
    if self.author.bot:
        return
    if member.bot:
        await self.message.reply("Tu ne peux pas jouer contre un bot, pauvre idiot")
        return
    if member.id == self.message.author.id:
        await self.message.reply("Tu ne peux pas jouer contre toi même -_- !")
        return
    attente = await self.message.reply(
        f"{member.display_name} voulez-vous jouer au puissance 4 contre {self.message.author.display_name} ?")
    viewVeutJouer = boutons.ViewVerificationP4(member)
    await attente.edit(view=viewVeutJouer)
    decision = await viewVeutJouer.wait()
    if decision:
        await attente.reply(f"Partie annulée, **{member.display_name}** n'a pas accepté l'invitation à temps.")
        return
    elif not viewVeutJouer.veutJouer:
        await attente.reply(f"Partie annulée, **{member.display_name}** n'a pas accepté l'invitation.")
        return

    embed = discord.Embed(
        title=titreJeuPuissance4,
        description="{0:<250}\n\n{1:<250}‏\n\n{2:<250}‏‏\n\n{3:<250}".format("🔹 **Joueurs:**",
                                                                             f"<:redpoint:937066613658771506> **{self.message.author.display_name}** <:reversefleche:936724361740693585>",
                                                                             f"<:yellowpoint:937066625390227476> **{member.display_name}**",
                                                                             initGrill()),
        color=discord.Color.from_rgb(71, 95, 145)
    )
    embed.set_footer(text="Session lancée par {:<200}".format(self.message.author.display_name),
                     icon_url=self.message.author.avatar)

    # await channel.send(embed=embed)

    embedComplet = discord.Embed(
        title=titreJeuMorpion,
        description="{0}\n\n".format(
            f"▫️ La grille est complète, fin de partie !"),
        color=discord.Color.from_rgb(255, 255, 255)
    )
    partie = boutons.CreatePuissance4Party(nombreColonne, self.message.author, 1)
    partie.enCours = True
    premierMessage = True
    msg = ""
    grille = None
    joueur1 = ""
    joueur2 = ""
    timeout = True
    mentionJ = None
    while partie.enCours:
        viewPuissance = partie.createView()
        if premierMessage:
            msg = await channel.send(embed=embed, view=viewPuissance)
            premierMessage = False
        else:
            if partie.valJoueurPuissance4 == 1:
                joueur1 = f"<:redpoint:937066613658771506> ️ **{self.message.author.display_name}** <:reversefleche:936724361740693585>"
                joueur2 = f"<:yellowpoint:937066625390227476>️ **{member.display_name}**"
                mentionJ = member.mention
            else:
                joueur1 = f"<:redpoint:937066613658771506> ️ **{self.message.author.display_name}**"
                joueur2 = f"<:yellowpoint:937066625390227476> **{member.display_name}** <:reversefleche:936724361740693585>"
                mentionJ = self.message.author.mention
            colonne = partie.valColonnePuissance4
            embed = discord.Embed(
                title=titreJeuPuissance4,
                description="{0:<250}\n\n{1:<250}‏\n\n{2:<250}‏‏\n\n{3:^250}".format("🔹 **Joueurs:**",
                                                                                     joueur1,
                                                                                     joueur2,
                                                                                     grille),
                color=discord.Color.from_rgb(71, 95, 145)
            )
            if not timeout:
                await msg.edit(content="", embed=embed, view=viewPuissance)
            else:
                await msg.edit(content=f"[AFK] J'ai joué à la place de {mentionJ} ", embed=embed, view=viewPuissance)

        timeout = await viewPuissance.wait()
        if timeout:
            timeoutPlay(partie)
            "traitement ici"
        grille = updateGrill(partie)
        estGagnant, estComplet = verifGrillePuissance4(partie)
        if estGagnant:
            if partie.valJoueurPuissance4 == 1:
                sauvegardeScore([self.message.author.id, member.id], [1, 0])
                # partie.casesPuissance4[partie.indiceLignePrec][partie.indiceColPrec] = stringRedSquare

            else:
                sauvegardeScore([self.message.author.id, member.id], [0, 1])
                # partie.casesPuissance4[partie.indiceLignePrec][partie.indiceColPrec] = stringYellowSquare
            grille = updateGrillEnd(partie)
            embed = discord.Embed(
                title=titreJeuPuissance4,
                description="{0}\n\n{1}‏\n\n{2}‏‏\n\n{3}".format("🔹 **Joueurs:**", joueur1, joueur2, grille),
                color=discord.Color.from_rgb(0, 0, 255)
            )
            await msg.edit(embed=embed)
            embedGagnant = discord.Embed(
                title=titreJeuPuissance4,
                description="{0}\n\n".format(
                    f"▫️ Le gagnant est {partie.joueurPuissance4.display_name} ! \n"),
                color=discord.Color.from_rgb(255, 255, 255)
            )
            await channel.send(embed=embedGagnant)
            return
            # resetPuissance4()

        if estComplet:
            if partie.valJoueurPuissance4 == 1:
                partie.casesPuissance4[partie.indiceLignePrec][partie.indiceColPrec] = stringRedSquare
            else:
                partie.casesPuissance4[partie.indiceLignePrec][partie.indiceColPrec] = stringYellowSquare
            embed = discord.Embed(
                title=titreJeuPuissance4,
                description="{0}\n\n{1}‏\n\n{2}‏‏\n\n{3}".format("🔹 **Joueurs:**", joueur1, joueur2, grille),
                color=discord.Color.from_rgb(0, 0, 255)
            )
            await msg.edit(embed=embed)
            # resetPuissance4()
            await channel.send(embed=embedComplet)
            return
        partie.valJoueurPuissance4 = 1 if partie.valJoueurPuissance4 == 2 else 2
        partie.joueurPuissance4 = self.message.author if partie.valJoueurPuissance4 == 1 else member


def verifGrillePuissance4(partie: boutons.CreatePuissance4Party):
    solution1 = stringRedSquarePrev + stringRedSquare + stringRedSquare + stringRedSquare if partie.valJoueurPuissance4 == 1 else stringYellowSquarePrev + stringYellowSquare + stringYellowSquare + stringYellowSquare
    solution2 = stringRedSquare + stringRedSquarePrev + stringRedSquare + stringRedSquare if partie.valJoueurPuissance4 == 1 else stringYellowSquare + stringYellowSquarePrev + stringYellowSquare + stringYellowSquare
    solution3 = stringRedSquare + stringRedSquare + stringRedSquarePrev + stringRedSquare if partie.valJoueurPuissance4 == 1 else stringYellowSquare + stringYellowSquare + stringYellowSquarePrev + stringYellowSquare
    solution4 = stringRedSquare + stringRedSquare + stringRedSquare + stringRedSquarePrev if partie.valJoueurPuissance4 == 1 else stringYellowSquare + stringYellowSquare + stringYellowSquare + stringYellowSquarePrev
    case = stringRedSquarePrev if partie.valJoueurPuissance4 == 1 else stringYellowSquarePrev
    caseNonEdit = stringRedSquare if partie.valJoueurPuissance4 == 1 else stringRedSquare
    tableau = partie.casesPuissance4

    # lignes
    for i in range(hauteurPuissance4):
        ligne = "".join(tableau[i])
        if solution1 in ligne or solution2 in ligne or solution3 in ligne or solution4 in ligne:
            indiceColDerniereCase = partie.indiceColPrec
            if indiceColDerniereCase + 3 <= 6:
                if tableau[i][indiceColDerniereCase + 1] == tableau[i][indiceColDerniereCase + 2] == tableau[i][
                    indiceColDerniereCase + 3] == caseNonEdit:
                    tableau[i][indiceColDerniereCase] = case
                    tableau[i][indiceColDerniereCase + 1] = case
                    tableau[i][indiceColDerniereCase + 2] = case
                    tableau[i][indiceColDerniereCase + 3] = case
            if indiceColDerniereCase - 3 >= 0:
                if tableau[i][indiceColDerniereCase - 1] == tableau[i][indiceColDerniereCase - 2] == tableau[i][
                    indiceColDerniereCase - 3] == caseNonEdit:
                    tableau[i][indiceColDerniereCase] = case
                    tableau[i][indiceColDerniereCase - 1] = case
                    tableau[i][indiceColDerniereCase - 2] = case
                    tableau[i][indiceColDerniereCase - 3] = case
            if indiceColDerniereCase + 2 <= 6:
                if tableau[i][indiceColDerniereCase + 1] == tableau[i][indiceColDerniereCase + 2] == caseNonEdit:
                    tableau[i][indiceColDerniereCase - 1] = case
                    tableau[i][indiceColDerniereCase] = case
                    tableau[i][indiceColDerniereCase + 1] = case
                    tableau[i][indiceColDerniereCase + 2] = case
            elif indiceColDerniereCase - 2 >= 0:
                if tableau[i][indiceColDerniereCase - 1] == tableau[i][indiceColDerniereCase - 2] == caseNonEdit:
                    tableau[i][indiceColDerniereCase + 1] = case
                    tableau[i][indiceColDerniereCase] = case
                    tableau[i][indiceColDerniereCase - 1] = case
                    tableau[i][indiceColDerniereCase - 2] = case
            if indiceColDerniereCase + 1 <= 6:
                if tableau[i][indiceColDerniereCase + 1] == caseNonEdit:
                    tableau[i][indiceColDerniereCase - 2] = case
                    tableau[i][indiceColDerniereCase - 1] = case
                    tableau[i][indiceColDerniereCase] = case
                    tableau[i][indiceColDerniereCase + 1] = case
            elif indiceColDerniereCase - 1 >= 0:
                if tableau[i][indiceColDerniereCase - 1] == caseNonEdit:
                    tableau[i][indiceColDerniereCase + 2] = case
                    tableau[i][indiceColDerniereCase + 1] = case
                    tableau[i][indiceColDerniereCase] = case
                    tableau[i][indiceColDerniereCase - 1] = case
            return True, False

    # colonnes
    for i in range(nombreColonne):
        colonne = ""
        indiceDerniereCase = 0
        for j in range(hauteurPuissance4):
            colonne += tableau[j][i]
            if tableau[j][i] == case:
                indiceDerniereCase = j
        if solution1 in colonne:
            tableau[indiceDerniereCase + 1][i] = case
            tableau[indiceDerniereCase + 2][i] = case
            tableau[indiceDerniereCase + 3][i] = case
            return True, False

    # diagonales négatives
    for colonne in range(4):
        for ligne in range(3):
            diagonaleN = "".join(
                [tableau[ligne][colonne], tableau[ligne + 1][colonne + 1],
                 tableau[ligne + 2][colonne + 2],
                 tableau[ligne + 3][colonne + 3]])
            if solution1 in diagonaleN or solution2 in diagonaleN or solution3 in diagonaleN or solution4 in diagonaleN:
                tableau[ligne][colonne] = case
                tableau[ligne + 1][colonne + 1] = case
                tableau[ligne + 2][colonne + 2] = case
                tableau[ligne + 3][colonne + 3] = case
                return True, False

    # diagonales positives
    for ligne in range(5, 2, -1):
        for colonne in range(4):
            diagonaleP = "".join(
                [tableau[ligne][colonne], tableau[ligne - 1][colonne + 1],
                 tableau[ligne - 2][colonne + 2],
                 tableau[ligne - 3][colonne + 3]])
            if solution1 in diagonaleP or solution2 in diagonaleP or solution3 in diagonaleP or solution4 in diagonaleP:
                tableau[ligne][colonne] = case
                tableau[ligne - 1][colonne + 1] = case
                tableau[ligne - 2][colonne + 2] = case
                tableau[ligne - 3][colonne + 3] = case
                return True, False

    # tableau complet
    tableauFlat = [item for sublist in tableau for item in sublist]
    if stringBlackSquare not in tableauFlat:
        return False, True
    else:
        return False, False


def timeoutPlay(partie: boutons.CreatePuissance4Party):
    random.seed(int(datetime.now().strftime("%Y%m%d%H%M%S")))
    colonne = random.randint(0, 5)
    tableau = partie.casesPuissance4
    while partie.verifColonne(colonne):
        colonne = random.randint(0, 5)
        # tableau complet
        tableauFlat = [item for sublist in tableau for item in sublist]
        if stringBlackSquare not in tableauFlat:
            return
        print(colonne)
    partie.setTabHauteurPuissance4(colonne)
    partie.setValColonnePuissance4(colonne)


@puissance4.error
async def puissance4_error(ctx, error):
    """ Gestion d'erreur sur la commande vente
        on vérifie que l'erreur `error` est bien une instance de `MissingRequiredArgument`
        on retourne dans le salon d'utilisation un exemple d'usage de la commande

        Parameters
        ----------
        ctx :
            contexte d'execution
        error : erreur
            instance de Error
    """
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send(usagePuissance4, delete_after=15.0)
    if isinstance(error, discord.ext.commands.errors.BadArgument):
        await ctx.send(usagePuissance4, delete_after=15.0)
    return


def initGrill():
    chaine = "{}\n".format(stringChiffre)
    for i in range(hauteurPuissance4):
        chaine += "{}\n".format(lineBlackSquare)
    return chaine


def updateGrill(partie: boutons.CreatePuissance4Party):
    chaine = "{}\n".format(stringChiffre)
    col = partie.valColonnePuissance4
    ligne = partie.tabHauteurPuissance4[col] + 1
    if partie.valJoueurPuissance4 == 1:
        partie.casesPuissance4[ligne][col] = stringRedSquarePrev
        if partie.indiceLignePrec is not None and partie.indiceColPrec is not None:
            partie.casesPuissance4[partie.indiceLignePrec][partie.indiceColPrec] = stringYellowSquare
    else:
        partie.casesPuissance4[ligne][col] = stringYellowSquarePrev
        if partie.indiceLignePrec is not None and partie.indiceColPrec is not None:
            partie.casesPuissance4[partie.indiceLignePrec][partie.indiceColPrec] = stringRedSquare
    partie.indiceLignePrec = ligne
    partie.indiceColPrec = col
    for i in range(hauteurPuissance4):
        chaine += "{}\n".format("".join(partie.casesPuissance4[i]))
    return chaine


def updateGrillEnd(partie: boutons.CreatePuissance4Party):
    chaine = "{}\n".format(stringChiffre)
    col = partie.valColonnePuissance4
    ligne = partie.tabHauteurPuissance4[col] + 1
    if partie.valJoueurPuissance4 == 1:
        partie.casesPuissance4[ligne][col] = stringRedSquarePrev
        if partie.indiceLignePrec is not None and partie.indiceColPrec is not None:
            partie.casesPuissance4[partie.indiceLignePrec][partie.indiceColPrec] = stringRedSquarePrev
    else:
        partie.casesPuissance4[ligne][col] = stringYellowSquarePrev
        if partie.indiceLignePrec is not None and partie.indiceColPrec is not None:
            partie.casesPuissance4[partie.indiceLignePrec][partie.indiceColPrec] = stringYellowSquarePrev
    partie.indiceLignePrec = ligne
    partie.indiceColPrec = col
    for i in range(hauteurPuissance4):
        chaine += "{}\n".format("".join(partie.casesPuissance4[i]))
    return chaine


def sauvegardeScore(listJoueurs: list, scoresJoueurs: list):
    """ Methode de sauvegarde du score des joueurs.
        Données réprésentées sous la forme : un_ancian#8649/<nombre_victoires>/<nombre_défaites>

        Parameters
        ----------
        listJoueurs : list
            tableau de string contenant le nom de l'ensemble des joueurs avec leurs discriminants
        scoresJoueurs : list
            tableau de string contenant les scores de l'ensemble des joueurs aux mêmes indices que dans le tableau listJoueurs
    """
    if not os.path.exists(f"{path}{dossierScore}"):
        os.makedirs(f"{path}{dossierScore}", mode=0o777, exist_ok=False)  # création du dossier s'il n'existe pas encore
    if not os.path.exists(f"{path}{dossierScore}/{fichierScore}"):
        open(f"{path}{dossierScore}/{fichierScore}", "x",
             encoding="utf-8")  # création du fichier s'il n'existe pas encore

    data = []
    # récuperation de l'ensemble des scores actuels
    with open(f"{dossierScore}/{fichierScore}", 'r') as json_file:
        data = json.load(json_file)

    i = 0
    for idJ in listJoueurs:
        if str(idJ) in data.keys():
            if scoresJoueurs[i] == 1:
                data[str(idJ)]["victoires"] += 1
            else:
                data[str(idJ)]["defaites"] += 1
        else:
            if scoresJoueurs[i] == 1:
                data[str(idJ)] = {"victoires": 1, "defaites": 0}
            else:
                data[str(idJ)] = {"victoires": 0, "defaites": 1}

        i += 1

    with open(f"{dossierScore}/{fichierScore}", 'w') as json_file:
        json.dump(data, json_file, sort_keys=True, indent=4)
    # joueurDiscriminator = messageAuthor.name + "#" + messageAuthor.discriminator
    # on parcourt le tableau des resultats pour modifier le score des joueurs déjà existant
    pass


@client.command(name='top4X')
async def leaderboard(self):
    embed = await topEmbed(1, self.guild, self.channel)

    await self.channel.send(embed=embed, view=boutons.ViewTop(getNumberPage()))


"""@client.command(name='stop')
@commands.has_permissions(administrator=True)
async def stop(ctx):
    \""" Commande d'arret du jeu.
        On vérifie si une partie est en cours ou non
        si oui on redémarre le bot
        si non on annonce qu'aucune partie n'est en cours

    \"""
    global enchereEnCours
    if enchereEnCours:
        embed = discord.Embed(
            title="Fin de l'enchère !",
            color=discord.Color.from_rgb(19, 19, 19)
        )
        await ctx.channel.send(embed=embed, delete_after=15.0)
        enchereEnCours = False
        try:
            await client.close()
        except:
            pass
        finally:
            os.system("py -u main.py")
    else:
        embed = discord.Embed(
            title="Aucune enchère n'est en cours !",
            color=discord.Color.from_rgb(19, 19, 19)
        )
        await ctx.channel.send(embed=embed, delete_after=15.0)"""


@client.command(name='regles')
async def regles(self):
    embed = discord.Embed(
        title="🎴 Casino Mudae",
        description=f"‏‏‎\n{em['couleur']} **Couleur** 🔹 {em['parite']} **Parité**\n{em['fleche']} _Miser sur une de ces options multiplie vos gains par **x0.5**_\n\n{em['colonne']} **Colonne** 🔹 {em['douzaine']} **Douzaine**\n{em['fleche']} _Miser sur une de ces options multiplie vos gains par **x1**_\n\n{em['chiffre']} **Nombre**\n{em['fleche']} _Miser sur un nombre multiplie vos gains par **x10**_",
        color=discord.Color.from_rgb(115, 150, 255)
    )
    embed.set_image(
        url="https://media.discordapp.net/attachments/918255435553841222/935925018263683082/ezgif.com-gif-maker_50.gif")
    await self.channel.send(embed=embed)


@client.command(name='scrap')
async def scrap(ctx):
    chan = client.get_channel(935927250606489660)
    await chan.send("$givescrap <@128281251596599297> 1")


@client.command(name='roulette')
async def roulette(self):
    # On renvoie une erreur et on return s'il y a déjà une partie en cours ou que les kakeras sont en cours de distribution
    global rouletteEnCours
    global banqueEnCours
    channelCommands = 918255435553841222
    channelCasino = 936317865156571296
    if self.channel.id not in [channelCommands, channelCasino]:
        return
    if banqueEnCours:
        await self.channel.send(
            "Les kakeras sont en train d'être récupérés et distribués ! Réessayez dans quelques secondes.")
        return
    if rouletteEnCours:
        await self.channel.send("Il y a déjà une partie en cours ! Réessayez à la fin de celle-ci.")
        return
    rouletteEnCours = True

    # On réinitialise les dictionnaires de joueurs etc. utilisés dans boutons.py
    boutons.joueurs = {}
    boutons.precis = {}
    boutons.sommes = {}
    embedIntro = discord.Embed(
        title="🎴 Casino Mudae",
        description=f"‏‏‎\n{em['couleur']} **Couleur** 🔹 {em['parite']} **Parité**\n{em['fleche']} _Miser sur une de ces options vous fait gagner **1 fois** votre mise_\n\n{em['colonne']} **Colonne** 🔹 {em['douzaine']} **Douzaine**\n{em['fleche']} _Miser sur une de ces vous fait gagner **2 fois** votre mise_\n\n{em['chiffre']} **Nombre**\n{em['fleche']} _Miser sur un nombre vous fait gagner **36 fois** votre mise_\n\n**Vous avez 15 secondes pour rejoindre la partie en cliquant sur le type de mise voulu !**",
        color=discord.Color.from_rgb(115, 150, 255)
    )
    embedIntro.set_footer(text=f"Partie lancée par {self.author.display_name}", icon_url=self.author.avatar)
    embedIntro.set_image(url="attachment://intro.png")
    viewIntro = boutons.TypeMise()

    # Etape 1 : Type de mise
    await self.channel.send(embed=embedIntro, view=viewIntro,
                            file=discord.File(f"{path}fond.png",
                                              filename="intro.png"))
    await viewIntro.wait()
    # S'il n'y a pas de joueurs dans la partie, on l'arrête
    if len(boutons.joueurs) == 0:
        await self.channel.send("Aucun joueur n'a rejoint la partie ! Annulation...")
        rouletteEnCours = False
        return

    embedMiseurs = discord.Embed(
        title="🎴 Casino Mudae",
        description=f"▫ **Choisissez l'option sur laquelle vous misez !**\n⚠️ Pour parier sur un nombre, entrez le **numéro** de la case.",
        color=discord.Color.from_rgb(115, 150, 255)
    )
    viewMiseurs = boutons.TypePrecis()

    # Etape 2 : Type de mise précis
    await self.channel.send(embed=embedMiseurs, view=viewMiseurs)
    joueursNombre = []
    for item in boutons.joueurs:
        if boutons.joueurs[item][1] == "Nombre":
            joueursNombre.append(item)

    # Fonction pour vérifier qu'un joueur entre bien un nombre entre 1 et 36 s'il a choisi "Nombre" à l'étape 1
    def check(m):
        if m.author.id in joueursNombre:
            if m.content.isdecimal():
                if 0 < int(m.content) < 37:
                    boutons.precis[m.author.id] = (m.author.display_name, m.content)
                    joueursNombre.remove(m.author.id)
        return not joueursNombre

    await client.wait_for("message", check=check)
    if len(boutons.joueurs) == len(boutons.precis):
        viewMiseurs.stop()
    await viewMiseurs.wait()
    if len(boutons.precis) == 0:
        await self.channel.send("Fin de la partie ! Il n'y a plus de joueurs dans cette partie.")
        rouletteEnCours = False
        return
    embedPrecis = discord.Embed(
        title="🎴 Casino Mudae",
        description=f"▫ **Choisissez la somme que vous misez !**\n⚠️ Vous ne pouvez pas changer la somme après l'avoir choisie.",
        color=discord.Color.from_rgb(115, 150, 255)
    )
    viewSommes = boutons.Somme()
    await self.channel.send(embed=embedPrecis, view=viewSommes)
    await viewSommes.wait()
    if len(boutons.sommes) == 0:
        await self.channel.send("Fin de la partie ! Il n'y a plus de joueurs dans cette partie.")
        rouletteEnCours = False
        return
    recapStr = ""
    for joueur in boutons.sommes:
        if joueur in boutons.joueurs and joueur in boutons.precis:
            recapStr += f"\n{em[unidecode.unidecode(boutons.joueurs[joueur][1]).lower()]} - **{boutons.sommes[joueur][0]}** a misé **{boutons.sommes[joueur][1]}** {em['kakera']} sur {phraseTypePrecis(boutons.precis[joueur][1])}"
    embedSommes = discord.Embed(
        title="🎴 Casino Mudae",
        description=f"{em['jeton']} **Récapitulatif des mises :**\n{recapStr}",
        color=discord.Color.from_rgb(115, 150, 255)
    )
    await self.channel.send(embed=embedSommes)
    await asyncio.sleep(5)
    embedLancer = discord.Embed(
        title="🎴 Casino Mudae",
        description=f"{em['roulette']} La **roulette** a été lancée !",
        color=discord.Color.from_rgb(115, 150, 255)
    )
    await self.channel.send(embed=embedLancer)
    await asyncio.sleep(5)
    random.seed(int(datetime.now().strftime("%Y%m%d%H%M%S")))
    resultat = random.randint(1, 36)
    # image = Image.new("RGBA", (41, 41), (255, 177, 0, 255))
    # wI, hI = image.size
    # draw = ImageDraw.Draw(image)
    # wT, hT = draw.textsize(str(resultat), font=police)
    # draw.text(((wI-wT)/2, (hI-hT)/2-3), str(resultat), font=police)
    # rectangleCases.paste(image, (cases[i].index(case)*44, i*44), image)
    # fond.paste(rectangleCases, getCaseInfo(resultat)[-1], rectangleCases)
    # fond.save("result.png")
    recap = {}
    for item in boutons.sommes:
        if item in boutons.precis:
            recap[item] = (boutons.sommes[item][0], boutons.sommes[item][1], boutons.precis[item][1])
    winnerz = gagnants(recap, getCaseInfo(resultat))
    gagnantsStr = ""
    if winnerz:
        for gagnant in winnerz:
            gagnantsStr += f"\n- {em['jeton']} **{gagnant[1]}** remporte **{int(gagnant[2])}** {em['kakera']} !"
    else:
        gagnantsStr = f"\n- {em['jeton']} Personne n'a gagné !"
    embedResultat = discord.Embed(
        title="🎴 Casino Mudae",
        description=f"‏‏‎\n{em['roulette']} La **bille** s'est arrêtée sur le **{resultat}** !\n\n🏆 - **Les gagnants :**\n{gagnantsStr}",
        color=discord.Color.from_rgb(115, 150, 255)
    )
    if winnerz:
        embedResultat.set_footer(text="Les gagnants recevront leur récompense sous quelques minutes...")
    embedResultat.set_image(url="attachment://result.png")
    await self.channel.send(embed=embedResultat, file=discord.File(
        f"{path}result/{str(resultat)}.png",
        filename="result.png"))
    banqueEnCours = True
    timingEstim = (7 * len(boutons.sommes) + 5 * len(winnerz)) - 1
    await asyncio.sleep(1)
    await self.channel.send(f"Estimation du temps d'attente avant la prochaine partie : {str(timingEstim)} secondes.")
    for joueur in boutons.sommes:
        await asyncio.sleep(1)
        await client.get_channel(LOGS).send(f":pr <@{joueur}>")
        await asyncio.sleep(1.5)
        await client.get_channel(LOGS).send(f":kakeraremove <@{joueur}> {boutons.sommes[joueur][1]}")
        await asyncio.sleep(2.5)
        await client.get_channel(LOGS).send(f":pr <@{joueur}>")
        await asyncio.sleep(1.5)
        jr = self.guild.get_member(joueur)
        notifRole = self.guild.get_role(937055967751839795)
        if notifRole in jr.roles and joueur not in [i[0] for i in winnerz]:
            await jr.send(embed=discord.Embed.from_dict({
                "color": 14957885,
                "title": "🔸 Historique Casino",
                "description": f" ‏‏‎ \n🔹 Compte : **{str(boutons.joueurs[jr.id][2])}** <:fleche:925077237164806164> **{str(boutons.joueurs[jr.id][2] - int(boutons.sommes[jr.id][1]))}** <:kake:925052720870752296>\n\n<:redarrow:937879614745882664> Perte : **-{boutons.sommes[jr.id][1]}** <:kake:925052720870752296>\n ‏‏‎ ",
                "footer": {
                    "text": f"Date : {datetime.now().strftime('%d/%m/%Y')}"
                }
            }))
    for gagnant in winnerz:
        jr = self.guild.get_member(gagnant[0])
        notifRole = self.guild.get_role(937055967751839795)
        if notifRole in jr.roles:
            await jr.send(embed=discord.Embed.from_dict({
                "color": 7271026,
                "title": "🔸 Historique Casino",
                "description": f" ‏‏‎ \n🔹 Compte : **{str(boutons.joueurs[jr.id][2])}** <:fleche:925077237164806164> **{str(int(boutons.joueurs[jr.id][2] - int(boutons.sommes[jr.id][1]) + int(gagnant[2])))}** <:kake:925052720870752296>\n\n<:greenarrow:937879603777773661> Gain : **+{str(int(int(gagnant[2]) - int(boutons.sommes[jr.id][1])))}** <:kake:925052720870752296>\n ‏‏‎ ",
                "footer": {
                    "text": f"Date : {datetime.now().strftime('%d/%m/%Y')}"
                }
            }))
        await asyncio.sleep(1)
        await client.get_channel(LOGS).send(f":givescrap <@{gagnant[0]}> {str(gagnant[2])}")
        await asyncio.sleep(2.5)
        await client.get_channel(LOGS).send(f":pr <@{gagnant[0]}>")
        await asyncio.sleep(1.5)
    banqueEnCours = False
    rouletteEnCours = False
    await self.channel.send("La roulette est prête pour une nouvelle partie !")


@client.command(name='cpt')
async def les_tests(self):
    # 872920477558009926
    tabChannel = [961316487409315880, 874061634837024800, 874053044524974141,
                  914568302926376980, 914570457578082375, 914571254823002132, 975505814536196196,
                  946908576650252298, 953763749272096928, 969365218134196294, 872920760803545209,
                  917807179627651152, 897576146454056963, 921806083301998622]

    print("[Debut du traitement]")  # await channel.history(limit=100, oldest_first=True)

    frequenceNumeros = {}
    for idChan in tabChannel:
        channel = client.get_channel(idChan)
        print("[Debut channel]" + channel.name)
        async for message in channel.history(limit=None, oldest_first=True):
            if message.author.id not in frequenceNumeros.keys() and not message.author.bot:
                frequenceNumeros[message.author.id] = 1
                print("[un boug]" + message.author.name)
            elif not message.author.bot:
                frequenceNumeros[message.author.id] += 1
        print("[Fin channel]" + channel.name)

    with open('json_data.json', 'w') as outfile:
        json.dump(frequenceNumeros, outfile, sort_keys=True, indent=4)
    print("[Fin du traitement]")

    channel = client.get_channel(872920477558009926)
    frequenceNumeros2 = {}
    print("[Debut channel]" + channel.name)
    async for message in channel.history(limit=None, oldest_first=True):
        if message.author.id not in frequenceNumeros2.keys() and not message.author.bot:
            frequenceNumeros2[message.author.id] = 1
            print("[un boug]" + message.author.name)
        elif not message.author.bot:
            frequenceNumeros2[message.author.id] += 1
    print("[Fin channel]" + channel.name)

    with open('json_data.json', "r") as json_file:
        data = json.load(json_file)
        for key in frequenceNumeros2.keys():
            if key not in data.keys():
                data[str(key)] = frequenceNumeros2[key]
            else:
                data[str(key)] += frequenceNumeros2[key]

    with open('json_data.json', 'w') as json_file:
        json.dump(data, json_file, sort_keys=True, indent=4)

    print("[Fin du traitement]")


def test():
    # Directly from dictionary
    with open('json_data.json', 'w') as outfile:
        json.dump({'4': 5, '6': 7}, outfile, sort_keys=True, indent=4)

    with open('json_data.json', "r") as json_file:

        data = json.load(json_file)
        if '5' not in data.keys():
            print("pas de 5")
            data[str(5)] = 0
            print(type(data['4']))
        else:
            print("un 5")
            print(data)

    with open('json_data.json', 'w') as json_file:
        json.dump(data, json_file, sort_keys=True, indent=4)


@client.command(name='tests')
async def compte_mises(self):
    channel = client.get_channel(936317865156571296)
    print("salut")  # await channel.history(limit=100, oldest_first=True)

    nbPartiesJoueesGlobal = 0  # await channel.history(limit=100, oldest_first=True).flatten()
    dictPartiesJoueurs = {}
    dictGainsJoueurs = {}
    dictPertesJoueurs = {}
    gainBanque = 0
    perteBanque = 0
    gainPotentiel = 0
    joueursPartie = None
    mises = 0
    frequenceNumeros = {}
    async for message in channel.history(limit=None,
                                         oldest_first=True):  # limit=None => c'est lent, mettre une valeur ou supprimer le "limit=" pour limiter les tests à un petit jeu de données
        if message.embeds:
            if message.embeds[indiceEmbed].description != Embed.Empty:
                description = message.embeds[indiceEmbed].description
                if "La **bille** s'est arrêtée" in description:  # vérification des gains
                    nbPartiesJoueesGlobal += 1
                    numero = re.findall(u'arrêtée sur le \*\*(.*)\*\*', description)
                    if numero[0] not in frequenceNumeros.keys():
                        frequenceNumeros[numero[0]] = 1
                    else:
                        frequenceNumeros[numero[0]] += 1

                    joueursGagnants = re.findall(u'\*\*(.*)\*\* remporte', description)  # [a-zA-Z0-9_]
                    gains = re.findall(u'remporte \*\*(.*)\*\*', description)
                    personne = re.findall(u"(\w*) n'a gagné", description)
                    if "Personne" in personne:
                        gainBanque += gainPotentiel
                        gainPotentiel = 0
                        for i in range(len(joueursPartie)):
                            dictPertesJoueurs[joueursPartie[i]] += int(mises[i])
                    else:
                        print("tous les joueurs {}".format(joueursPartie))
                        # ajouts des gains des vainqueurs
                        for i in range(len(joueursGagnants)):
                            # on retire d'abord les vainqueurs de la liste des joueurs de la partie afin de recuperer les perdants
                            # et ainsi ajouter toutes les mises comme gain à la banque
                            indice = joueursPartie.index(joueursGagnants[i])
                            miseJ = mises.pop(indice)
                            joueursPartie.remove(joueursGagnants[i])  # les perdants

                            dictGainsJoueurs[joueursGagnants[i]] += int(gains[i]) - int(miseJ)
                            perteBanque += int(gains[i]) - int(miseJ)
                            gainPotentiel = 0
                        # ajout des gains à la banque et ajout des pertes des perdants dictPertesJoueurs
                        print("les perdants {}".format(joueursPartie))
                        for i in range(len(joueursPartie)):
                            dictPertesJoueurs[joueursPartie[i]] += int(mises[i])
                            gainBanque += int(mises[i])

                elif "Récapitulatif des mises" in description:  # nombre de parties joué par personne
                    joueursPartie = re.findall(u'\*\*(.*)\*\* a misé', description)
                    mises = re.findall(u'a misé \*\*(.*)\*\*', description)
                    # print(mises)
                    for joueur in joueursPartie:
                        if joueur not in dictPartiesJoueurs.keys():
                            dictPartiesJoueurs[joueur] = 1
                            dictGainsJoueurs[joueur] = 0
                            dictPertesJoueurs[joueur] = 0
                        else:
                            dictPartiesJoueurs[joueur] += 1
                    for mise in mises:
                        gainPotentiel += int(mise)
                    # print("gain potentiel:" + str(gainPotentiel))

    print("--")
    values = dictPartiesJoueurs.keys()
    valuesKeys = list(values)
    values = dictPartiesJoueurs.values()
    valuesParties = list(values)
    values = dictGainsJoueurs.values()
    valuesGains = list(values)
    values = dictPertesJoueurs.values()
    valuesPertes = list(values)
    for i in range(len(dictPartiesJoueurs)):
        print("Joueur: {}/ Partie: {}/Gains: {}/Pertes: {}".format(valuesKeys[i], valuesParties[i], valuesGains[i],
                                                                   valuesPertes[i]))
    print("--")
    # print(dictPartiesJoueurs)
    print("Nombre de parties jouées (global): {}".format(nbPartiesJoueesGlobal))
    sorted_tuples = sorted(dictPartiesJoueurs.items(), key=lambda item: item[1], reverse=True)
    dictPartiesJoueurs = {k: v for k, v in sorted_tuples}
    print("Nombre de parties des joueurs: {}".format(dictPartiesJoueurs))
    print("Gain de la banque: {}".format(gainBanque))
    print("Perte de la banque: {}".format(perteBanque))
    sorted_tuples = sorted(dictGainsJoueurs.items(), key=lambda item: item[1], reverse=True)
    dictGainsJoueurs = {k: v for k, v in sorted_tuples}
    print("Gain des joueurs: {}".format(dictGainsJoueurs))
    sorted_tuples = sorted(dictPertesJoueurs.items(), key=lambda item: item[1], reverse=True)
    dictPertesJoueurs = {k: v for k, v in sorted_tuples}
    print("Pertes des joueurs: {}".format(dictPertesJoueurs))

    sorted_tuples = sorted(frequenceNumeros.items(), key=lambda item: item[1], reverse=True)
    frequenceNumeros = {k: v for k, v in sorted_tuples}
    print("Fréquence de sortie des numéros gagnants: {}".format(frequenceNumeros))
    print("au revoir")
    return


@client.command(name="topR")
async def leaderboardCasino(self):
    # nbPartiesGlobal
    # gainBanque
    # perteBanque
    # id/nombreParties/gainsJoueurs/pertesJoueurs

    guildActual = self.guild
    gains = ""
    pertes = ""
    pseudos = ""
    nbParties = ""
    message = ""
    count = 0
    data, dataBanque = getRouletteData()
    nombrePartieGlobal = 0
    gainBanque = 0
    perteBanque = 0
    if data is None:
        await self.channel.send("Il y a pas encore de leaderboard, aucune partie n'a été encore joué")

    for i in range(len(dataBanque)):
        if i == 0:
            nombrePartieGlobal = dataBanque[i]
        elif i == 1:
            gainBanque = dataBanque[i]
        else:
            perteBanque = dataBanque[i]
    for line in data:
        member = await guildActual.fetch_member(line[indiceID])

        pseudos += f"- **{member.display_name}**\n"
        nbParties += f"- 🎮 **{line[indiceNbParties]}**\n"
        gains += f"<:greenarrow:937879603777773661> **{line[indiceGains]}**\n"
        pertes += f"<:redarrow:937879614745882664> **{line[indicePertes]}**\n"
        # message += f"- **{member.display_name}**\t🎮 **{line[indiceNbParties]}**\t<:greenarrow:937879603777773661> **{line[indiceGains]}**\t<:redarrow:937879614745882664> **{line[indicePertes]}**\n"

    embed = discord.Embed(
        title="🎴 Casino Mudae",
        description="Nombre de parties jouées (global): **{}**\nGain de la banque: **{}**\nPerte de la banque: **{}**".format(
            nombrePartieGlobal, gainBanque, perteBanque),
        color=discord.Color.from_rgb(115, 150, 255)
    )
    embed.add_field(name="Joueurs", value=pseudos, inline=True)
    # embed.add_field(name="Nombre de parties", value=nbParties, inline=True)
    embed.add_field(name="Gains", value=gains, inline=True)
    embed.add_field(name="Pertes", value=pertes, inline=True)

    embed2 = discord.Embed(
        title="🎴 Casino Mudae",
        description="Nombre de parties jouées (global): **{}**\nGain de la banque: **{}**\nPerte de la banque: **{}**".format(
            nombrePartieGlobal, gainBanque, perteBanque),
        color=discord.Color.from_rgb(115, 150, 255)
    )
    embed2.add_field(name="Joueurs", value=pseudos, inline=True)
    embed2.add_field(name="Nombre de parties", value=nbParties, inline=True)

    msg = await self.channel.send(embeds=[embed, embed2])

    return


def getRouletteData():
    """ Méthode qui crée (si non existance) le chemin de sauvegarde du fichier scores
        ensuite récupere les données du leaderboard, le tri et les renvoie sous forme d'un tableau
        indice 0 :Id du joueur
        indice 1 : gains du joueur
        indice 2 : pertes du joueur

        Returns
        -------
        data : list
             tableau de données ou None s'il n'y a pas encore de données dans le leaderboard

    """
    """
    if not os.path.exists(f"{path}/{fichierRoulette}"):
        open(f"{path}/{fichierRoulette}", "x",encoding="utf-8")  # création du fichier s'il n'existe pas encore"""

    # filesize = os.path.getsize(f"{path}/{fichierRoulette}")
    filesize = os.path.getsize(f"{fichierRoulette}")
    if filesize == 0:
        return None
    data = []
    dataBanque = []
    count = 0

    # récuperation de l'ensemble des scores actuels
    # with open(f"{path}/{fichierRoulette}", 'r', encoding="utf-8") as source:
    with open(f"{fichierRoulette}", 'r', encoding="utf-8") as source:
        for line in source:
            if line != "\n":
                count += 1
                if count <= 3:
                    line = line.rstrip("\n")
                    dataBanque.append(line)
                else:
                    line = line.rstrip("\n")
                    line = line.split("/")
                    data.append([int(line[indiceID]), int(line[indiceNbParties]), int(line[indiceGains]),
                                 int(line[indicePertes])])

    # take the second element for sort
    def take_second(elem):
        return elem[2]

    data = sorted(data, reverse=True, key=take_second)  # tri du tableau de données selon la méthode passe paramètres
    return data, dataBanque


import sys


def restart_bot():
    os.execv(sys.executable, ['python'] + sys.argv)


@client.command(name='re')
async def restart(ctx):
    try:
        client.clear()
    except EnvironmentError as e:
        print(e)
        ctx.bot.clear()
    finally:
        await client.connect()


@client.command(name='game', aliases=["jouer", "g"], brief="Saha la description")
async def dofus(ctx, member: discord.Member):
    message = ctx.message
    channel = ctx.channel
    authorID = ctx.author.id
    memberID = member.id

    if ctx.author.bot:
        return
    if member.bot:
        await ctx.message.reply("Tu ne peux pas jouer contre un bot, pauvre idiot")
        return
    if member.id == ctx.message.author.id:
        await ctx.message.reply("Tu ne peux pas jouer contre toi même -_- !")
        return

    attente = await ctx.message.reply(
        f"**__{ctx.message.author.display_name}__** voulez-vous jouer au jeu en __1v1__ ou __2v2__ ?")
    attenteJoueur = ""
    viewVeutJouerA2 = ViewVerificationDofus(ctx.message.author)
    await attente.edit(view=viewVeutJouerA2)
    decision = await viewVeutJouerA2.wait()
    if decision:
        await attente.reply(f"Partie annulée, **{ctx.message.author.display_name}** n'avez pas décidé à temps.")
        return
    elif viewVeutJouerA2.aAnnuler:
        await attente.reply(f"Partie annulée, **{ctx.message.author.display_name}** a arrêté la partie.")
        return
    elif viewVeutJouerA2.veutJouerA2:
        attenteJoueur = await attente.reply(
            f"Cette partie sera du 2 contre 2.")
    elif not viewVeutJouerA2.veutJouerA2:
        attenteJoueur = await attente.reply(
            f"Cette partie sera du 1 contre 1.")

    embed = discord.Embed(
        title="Composition des Équipes",
        description=f"Équipe de {ctx.message.author.display_name}:\n- {ctx.message.author.display_name}\n\nÉquipe de {member.display_name}:\n- {member.display_name}",
        color=discord.Colour(0xDB3A3A)
        # tour du rouge DB3A3A
        # tour du bleu 0080FF
    )
    viewAttenteJoueurs = ViewAttenteJoueurDofus(ctx.message.author, member)
    await attenteJoueur.edit(embed=embed, view=viewAttenteJoueurs)
    decision = await viewAttenteJoueurs.wait()

    rankyakuEpee = Sort("rankyaku", 2, "ligne", 2, 0, {"1": (12, 16), "2": (8, 12)})
    rankyakuArc = Sort("rankyaku", 4, "ligne", 2, 0, {"1": (12, 16), "2": (8, 12), "3": (4, 8), "4": (2, 4)})
    # tekkaiEpee = Sort("tekkai", )
    # tekkaiArc = Sort("tekkai")
    geppo = Sort("geppo", 0, "aucune", 3, 0, {})
    attaqueDiagonaleEpee = Sort("attaqueDiagonale", 1, "diagonale", 2, 0, {"1": (8, 12)})
    attaqueDiagonaleArc = Sort("attaqueDiagonale", 2, "diagonale", 2, 0, {"1": (8, 12), "2": (4, 8)})
    etourdissement = Sort("etourdissement", 1, "ligne", 3, 0, {"1": (4, 8)})
    terrainMouvant = Sort("terrainMouvant", 3, "ligne", 2, 0, {"1": (6, 8), "2": (4, 6), "3": (2, 4)})

    sortEpee = [rankyakuEpee, geppo, attaqueDiagonaleEpee, etourdissement, terrainMouvant]
    sortArc = [rankyakuArc, geppo, attaqueDiagonaleArc, etourdissement, terrainMouvant]

    tabJ1 = [(169, 421), (421, 421), (253, 253), (169, 673), (421, 589)]
    tabJ2 = [(1009, 421), (1009, 169), (925, 589), (757, 421), (757, 253)]
    listCouleur = [("rouge", discord.Colour(0xDB3A3A)), ("bleu", discord.Colour(0x0080FF)),
                   ("marron", discord.Colour(0x562E22)),
                   ("orange", discord.Colour(0xDB6F3A)), ("violet", discord.Colour(0x973ADB)),
                   ("rose", discord.Colour(0xDB3A7E)),
                   ("jaune", discord.Colour(0xDBCD3A)), ("vert", discord.Colour(0x70DB3A))]

    listJoueurs = []
    listIDTeam1 = []
    listIDTeam2 = []

    for joueurA in viewAttenteJoueurs.getJoueursA():
        random.seed(datetime.now())
        coord1 = random.choice(tabJ1)
        couleurChoisie = random.choice(listCouleur)
        listJoueurs.append(
            Joueur(coord1[0], coord1[1], couleurChoisie[0], joueurA, couleurChoisie[1], randint(10, 700)))
        listIDTeam1.append(joueurA.id)
        tabJ1.remove(coord1)
        listCouleur.remove(couleurChoisie)

    for joueurB in viewAttenteJoueurs.getJoueursB():
        random.seed(datetime.now())
        coord2 = random.choice(tabJ2)
        couleurChoisie = random.choice(listCouleur)
        listJoueurs.append(
            Joueur(coord2[0], coord2[1], couleurChoisie[0], joueurB, couleurChoisie[1], randint(10, 700)))
        listIDTeam2.append(joueurB.id)
        tabJ2.remove(coord2)
        listCouleur.remove(couleurChoisie)

    newList = sorted(listJoueurs, reverse=True)
    premierJoueur = newList.pop(0)
    newList.append(premierJoueur)

    # création des logs
    trace = Traces()
    trace.createFile(ctx.author.name)
    trace.writePlayers("\n".join([str(j) for j in newList]))
    embed = embedJeu(premierJoueur, newList)
    embed2 = embedPVJoueurs(newList)
    embed3 = embedActionJoueurs("", "")
    view = ViewJeuPVP(premierJoueur, newList, listIDTeam1, listIDTeam2)
    await channel.send(file=discord.File(f"{pathImage}temp/jeu.png"), embeds=[embed, embed2, embed3], view=view)
    finView = await view.wait()
    # os.remove(f"{pathImage}temp/jeu.png")


@dofus.error
async def dofus_error(ctx, error):
    """ Gestion d'erreur sur la commande vente
        on vérifie que l'erreur `error` est bien une instance de `MissingRequiredArgument`
        on retourne dans le salon d'utilisation un exemple d'usage de la commande

        Parameters
        ----------
        ctx :
            contexte d'execution
        error : erreur
            instance de Error
    """
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.message.reply("Utilisation : !game @adversaire", delete_after=15.0)
        raise
    if isinstance(error, discord.ext.commands.errors.BadArgument):
        await ctx.message.reply("Utilisation : !game @adversaire", delete_after=15.0)
        raise
    return


if __name__ == '__main__':
    client.run(TOKEN)

# Colonne, Parité, Couleur, Numéro, Douzaine
# (2, True, 'rouge', 3, 21, (441, 45))
# {128281251596599297: ('Saïd', '250', 'Douzaine 1')}
