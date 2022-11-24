import json
import os
import subprocess
import sys
from typing import Optional

import discord
from dotenv import load_dotenv
import boutons
from config import *
from discord.ext.commands import CommandNotFound, MissingPermissions
from tinydb import TinyDB, where, Query
from tinydb.operations import add, subtract
from affichage import afficher_top, afficher_top_coin

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
path = "Data"
fichierData = "json_data.json"
database = TinyDB(f"{path}/{fichierData}", sort_keys=True, indent=4, separators=(',', ': '))
db = database.table("dessinateurs")


@client.event
async def on_ready():
    # creer_fichier()
    print('Connecte en tant que {0}!'.format(client.user))
    game = discord.Game("dessine 🎨")
    await client.change_presence(status=discord.Status.online, activity=game)


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.channel.send("Cette commande n'existe pas !", delete_after=15.0)
        return
    if isinstance(error, MissingPermissions):
        await ctx.channel.send(
            "Vous n'avez pas la permission de lancer cette commande, seul un administrateur peut la lancer !",
            delete_after=15.0)
        return
    raise error


@client.command(name="help", aliases=["aide"], extras={"type": "hidden"}, brief="Afficher ce message d'aide")
async def help(ctx, args=None):
    embed = discord.Embed(title="Commandes")
    liste_commandes = [x.name for x in client.commands]
    if not args:
        embed.add_field(
            name="Admin",
            value="\n".join([f"`!{x.name}` - {x.brief}" for x in client.commands if x.extras["type"] == "admin"]),
            inline=False
        )
        embed.add_field(
            name="Global",
            value="\n".join([f"`!{x.name}` - {x.brief}" for x in client.commands if x.extras["type"] == "user"]),
            inline=False
        )
        embed.add_field(
            name="Détails",
            value="Pour en savoir plus sur une commande, tapez `!help <commande>`",
            inline=False
        )
    elif args.replace("!", "") in liste_commandes:
        aliases = '|'.join([x.aliases for x in client.commands if x.name == args.replace("!", "")][0])
        embed.title = f"Commande {args.replace('!', '')}"
        embed.description = f"Utilisation : !{'[' if aliases else ''}{args.replace('!', '')}{'|' if aliases else ''}{aliases}{']' if aliases else ''} {client.get_command(args.replace('!', '')).signature}"
    else:
        await ctx.reply("Cette commande n'existe pas !")
        return False

    await ctx.send(embed=embed)


"""def creer_fichier():
    if not os.path.exists(f"{path}{dossierScore}"):
        os.makedirs(f"{path}{dossierScore}", mode=0o777, exist_ok=False)  # création du dossier s'il n'existe pas encore
    if not os.path.exists(f"{path}{dossierScore}/{fichierScore}"):
        open(f"{path}{dossierScore}/{fichierScore}", "x",
             encoding="utf-8")  # création du fichier s'il n'existe pas encore
    if not os.path.exists(f"{path}"):
        os.makedirs(f"{path}", mode=0o777, exist_ok=False)  # création du dossier s'il n'existe pas encore
    if not os.path.exists(f"{path}/{fichierData}"):
        open(f"{path}/{fichierData}", "x",
             encoding="utf-8")  # création du fichier s'il n'existe pas encore"""


async def ajouter_joueur(context, joueur: discord.Member):
    if db.count(where("id") == joueur.id) == 0:
        db.insert({"id": joueur.id, "victoires": 0, "defaites": 0, "coins": 0})
    else:
        await context.message.reply("Ce joueur existe déjà !", delete_after=15.0)
        return


async def supprimer_joueur(context, joueur: discord.Member):
    if db.count(where("id") == joueur.id) > 0:
        db.remove(where("id") == joueur.id)
    else:
        await context.message.reply("Ce joueur n'existe pas ! Pensez à l'ajouter avant de le supprimer",
                                    delete_after=15.0)
        return


async def add_victory(context, joueur: discord.Member, points: int):
    if db.count(where("id") == joueur.id) > 0:
        db.update({"victoires": points}, where("id") == joueur.id)
    else:
        await context.message.reply("Ce joueur n'existe pas ! Pensez à l'ajouter avant de lui attribuer des victoires",
                                    delete_after=15.0)
        return


async def add_defeat(context, joueur: discord.Member, points: int):
    if db.count(where("id") == joueur.id) > 0:
        db.update({"defaites": points}, where("id") == joueur.id)
    else:
        await context.message.reply("Ce joueur n'existe pas ! Pensez à l'ajouter avant de lui attribuer des défaites",
                                    delete_after=15.0)
        return


def former_chaine(guild: discord.Guild):
    data = list(db.all())
    string_array = []
    chaine_joueurs = "{0: <20}{1: ^15}{2: >15}\n".format('Joueurs', 'Victoires', 'Defaites')
    chaine_joueurs += "--------------------------------------------------\n"
    for dessinateur in data:
        membre = guild.get_member(dessinateur["id"])
        if membre is not None:
            if not membre.bot:
                chaine_joueur = f"{membre.display_name : <20}{dessinateur['victoires'] : ^15}{dessinateur['defaites'] : >15}\n"  # .format(, ,)
                print(len(chaine_joueurs))
                if len(chaine_joueurs) + len(chaine_joueur) > 2000:
                    string_array.append(chaine_joueurs)
                    chaine_joueurs = "{{0: <20}{1: ^15}{2: >15}\n".format('Joueurs', 'Victoires', 'Defaites')
                    chaine_joueurs += "------------------------------------------------------------\n"
                    chaine_joueurs += chaine_joueur
                chaine_joueurs += chaine_joueur
    string_array.append(chaine_joueurs)

    return string_array


async def add_coins_all(context, valeur: int):
    User = Query()
    dict_joueurs_have_coins = db.search((User.coins.exists()))
    dict_joueurs_no_coins = db.search(~(User.coins.exists()))

    # print(dict_joueurs_have_coins)
    # print("dictionnaire 2:", dict_joueurs_no_coins)

    for joueur in dict_joueurs_have_coins:
        db.upsert(add("coins", valeur), where("id") == joueur["id"])

    for joueur in dict_joueurs_no_coins:
        db.upsert({"coins": valeur}, where("id") == joueur["id"])

    await context.message.reply(f"Tous les joueurs ont bien reçus {valeur} coins",
                                delete_after=15.0)


async def add_coins_user(context, joueur: discord.Member, valeur: int):
    if db.count(where("id") == joueur.id) > 0:
        User = Query()
        dict_joueur = db.search((User.coins.exists()) & (User.id == joueur.id))
        if len(dict_joueur) == 1:
            db.upsert(add("coins", valeur), where("id") == joueur.id)
        else:
            db.upsert({"coins": valeur}, where("id") == joueur.id)

    else:
        await context.message.reply("Ce joueur n'existe pas ! Pensez à l'ajouter avant de lui ajouter des points",
                                    delete_after=15.0)
        return


async def remove_coins_user(context, joueur: discord.Member, valeur: int):
    if db.count(where("id") == joueur.id) > 0:
        User = Query()
        dict_joueur = db.search((User.coins.exists()) & (User.id == joueur.id))
        if len(dict_joueur) == 1:
            if dict_joueur[0]["coins"] - valeur > 0:
                db.upsert(subtract("coins", valeur), where("id") == joueur.id)
            else:
                await context.message.reply(
                    f"Vous ne pouvez pas attribuer des points négatifs à ce joueur, points actuels: {dict_joueur[0]['coins']}",
                    delete_after=15.0)
        else:
            await context.message.reply(
                f"Vous ne pouvez pas attribuer des points négatifs à ce joueur, points actuels: 0",
                delete_after=15.0)

    else:
        await context.message.reply("Ce joueur n'existe pas ! Pensez à l'ajouter avant de lui retirer des points",
                                    delete_after=15.0)
        return


@client.command(name='ajouter_victoire', aliases=["victoire", "addv", "addvictory"], extras={"type": "admin"},
                brief="Définir les victoires d'un joueur")
async def addVictory(self, joueur: discord.Member, valeur: int):
    await add_victory(self, joueur, valeur)


@client.command(name='ajouter_defaite', aliases=["defaite", "addd", "adddefeat"], extras={"type": "admin"},
                brief="Définir les défaites d'un joueur")
async def addDefeat(self, joueur: discord.Member, valeur: int):
    await add_defeat(self, joueur, valeur)


@client.command(name='ajouter_joueur', aliases=["addP", "addp", "ajout_j", "new_j"], extras={"type": "admin"},
                brief="Ajouter un nouveau participant")
async def addPlayer(self, joueur: discord.Member):
    await ajouter_joueur(self, joueur)


@client.command(name='supprimer_joueur', aliases=["removeP", "removep", "remove_j", "rm_j"], extras={"type": "admin"},
                brief="Retirer un participant")
async def removePlayer(self, joueur: discord.Member):
    await supprimer_joueur(self, joueur)


@client.command(name="top", aliases=["classement", "top10", "leaderboard", "topdessinateur", "t", "Top"], extras={"type": "user"},
                brief="Afficher les dessinateurs par victoires et ensuite par défaites")
async def printTop(self, affichageMobile: Optional[bool] = False):
    embed = afficher_top(1, self.guild)
    await self.channel.send(embed=embed, view=boutons.ViewTop(False))


@client.command(name="topcoin", aliases=["classementcoin", "top10coin", "leaderboardcoin", "topC", "topc", "coins", "coin", "points", "money", "topcoins"],
                extras={"type": "user"},
                brief="Afficher les coins des dessinateurs")
async def printTopCoin(self, affichageMobile: Optional[bool] = False):
    embed = afficher_top_coin(1, self.guild)
    await self.channel.send(embed=embed, view=boutons.ViewTop(True))


@client.command(name="topmobile", aliases=["classementmobile", "top10mobile", "leaderboardmobile", "topm", "topM", "mobile", "tmobile"], extras={"type": "user"},
                brief="Afficher les dessinateurs par victoires et ensuite par défaites")
async def printTopMobile(self, affichageMobile: Optional[bool] = True):
    embed = afficher_top(1, self.guild, affichageMobile)
    await self.channel.send(embed=embed, view=boutons.ViewTop(False, affichageMobile))


#  aliases=["classementcoin", "top10coin", "leaderboardcoin", "topC", "topc"]
@client.command(name="topcoinmobile", aliases=["classementcoinmobile", "top10coinmobile", "leaderboardcoinmobile", "topCmobile", "topcmobile", "coinsmobile", "coinmobile", "pointsmobile", "moneymobile", "tcm", "tcmobile"], extras={"type": "user"},
                brief="Afficher les coins des dessinateurs")
async def printTopCoinMobile(self, affichageMobile: Optional[bool] = True):
    embed = afficher_top_coin(1, self.guild, affichageMobile)
    await self.channel.send(embed=embed, view=boutons.ViewTop(True, affichageMobile))


@client.command(name="etatbase", aliases=["etat"], extras={"type": "admin"}, brief="Afficher la base en brut")
# @commands.has_permissions(administrator=True)
async def etatbase(self):
    tabString = former_chaine(self.guild)
    print(tabString)
    for chaine in tabString:
        await self.channel.send(chaine)


@client.command(name="addCoinsAll", aliases=["addcoinsall", "aca", "addCAll", "addcall"], extras={"type": "admin"},
                brief="Ajouter à tous les utilisateurs de la base la valeur passée")
async def addCoinsAll(self, valeur: int):
    if valeur <= 0:
        await self.message.reply("Vous pouvez ajouter seulement une valeur supérieur à 0", delete_after=15.0)
        return
    await add_coins_all(self, valeur)


@client.command(name="addCoinsUser", aliases=["addcoinsuser", "acu", "addCUser", "addcuser"], extras={"type": "admin"},
                brief="Ajouter à l'utilisateur choisi (joueur) la valeur passée (valeur)")
async def addCoinsUser(self, joueur: discord.Member, valeur: int):
    if valeur <= 0:
        await self.message.reply("Vous pouvez ajouter seulement une valeur supérieur à 0", delete_after=15.0)
        return
    await add_coins_user(self, joueur, valeur)


@client.command(name="removeCoinsUser", aliases=["removecoinsuser", "rcu", "removeCUser", "removecuser"],
                extras={"type": "admin"},
                brief="Retirer à l'utilisateur choisi (joueur) la valeur passée (valeur)")
async def removeCoinsUser(self, joueur: discord.Member, valeur: int):
    if valeur <= 0:
        await self.message.reply("Vous pouvez retirer seulement une valeur supérieur à 0", delete_after=15.0)
        return
    await remove_coins_user(self, joueur, valeur)


@client.command(name="restartDDJ", aliases=['stopDDJ', 'reDDJ', 'startDDJ', 'reloadDDJ'], extras={"type": "hidden"})
@commands.has_any_role(917873134743478293, 874054405484326962)
# @commands.has_permissions(administrator=True)
async def stop(ctx):
    """ Commande d'arret du jeu.
        On vérifie si une partie est en cours ou non
        si oui on redémarre le bot
        si non on annonce qu'aucune partie n'est en cours

    """
    embed = discord.Embed(
        title="[DDJ] Redemarrage du bot !",
        color=discord.Color.from_rgb(19, 19, 19)
    )
    await ctx.channel.send(embed=embed)
    try:
        await client.close()
    except:
        pass
    finally:
        name = "/home/minecraft/multicraft/servers/server248791/MudaeGames/main.py"
        print("[Loader]Opening file " + name)
        # working_dir = "/".join(name.split("/")[:-1]);
        subprocess.call([sys.executable, '-u', name])
        print("[Loader]File " + name + " stopped")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    client.run(TOKEN)
