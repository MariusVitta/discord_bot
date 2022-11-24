import discord
from discord import Colour
from tinydb import TinyDB

path = "Data"
fichierData = "json_data.json"
database = TinyDB(f"{path}/{fichierData}", sort_keys=True, indent=4, separators=(',', ': '))
db = database.table("dessinateurs")


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def afficher_top(page: int, guild, affichageMobile: bool = False):
    page = page - 1
    sortedData = list(sorted(db.all(), key=lambda k: (k["victoires"], -k["defaites"]), reverse=True))
    sortedDessinateur = []
    for sortedMsg in sortedData:
        membre = guild.get_member(sortedMsg["id"])
        if membre is not None:
            if not membre.bot:
                sortedDessinateur.append([membre.display_name, sortedMsg["victoires"], sortedMsg["defaites"]])
    sortedTop = list(chunks(sortedDessinateur, 10))

    embed = discord.Embed(title="Top dessinateurs 🎨", colour=Colour.from_str("#0095FF"))
    pseudos, victoires, defaites = "", "", ""

    if not affichageMobile:
        for ind, joueur in enumerate(sortedTop[page]):
            if page == 0:
                if ind == 0:
                    pseudos += f"🥇- **{joueur[0]}**\n"
                elif ind == 1:
                    pseudos += f"🥈- **{joueur[0]}**\n"
                elif ind == 2:
                    pseudos += f"🥉- **{joueur[0]}**\n"
                else:
                    pseudos += f"🔸- **{joueur[0]}**\n"
            else:
                pseudos += f"🔸- **{joueur[0]}**\n"
            victoires += f"<:Victory:937012638536314951> **{joueur[1]}**\n"
            defaites += f"<:Defeat:937012765254615080> **{joueur[2]}**\n"

        # embed.set_thumbnail(url="https://f.angiva.re/XaSyB.gif")
        embed.add_field(name="Dessinateurs", value=pseudos, inline=True)
        embed.add_field(name="Victoires", value=victoires, inline=True)
        embed.add_field(name="Défaites", value=defaites, inline=True)

        embed.set_footer(text=f"Page {page + 1}/{len(sortedTop)}")
        return embed
    else:
        chaine = f"**Dessinateurs** - **Victoires** - **Défaites**‏\n\n"
        for ind, joueur in enumerate(sortedTop[page]):
            if page == 0:
                if ind == 0:
                    chaine += f"🥇- **{joueur[0]}** - <:Victory:937012638536314951> **{joueur[1]}** - <:Defeat:937012765254615080> **{joueur[2]}**\n"
                elif ind == 1:
                    chaine += f"🥈- **{joueur[0]}** - <:Victory:937012638536314951> **{joueur[1]}** - <:Defeat:937012765254615080> **{joueur[2]}**\n"
                elif ind == 2:
                    chaine += f"🥉- **{joueur[0]}** - <:Victory:937012638536314951> **{joueur[1]}** - <:Defeat:937012765254615080> **{joueur[2]}**\n"
                else:
                    chaine += f"🔸- **{joueur[0]}** - <:Victory:937012638536314951> **{joueur[1]}** - <:Defeat:937012765254615080> **{joueur[2]}**\n"
            else:
                chaine += f"🔸- **{joueur[0]}** - <:Victory:937012638536314951> **{joueur[1]}** - <:Defeat:937012765254615080> **{joueur[2]}**\n"

        embed = discord.Embed(title="Top dessinateurs 🎨", description=chaine, colour=Colour.from_str("#0095FF"))
        embed.set_footer(text=f"Page {page + 1}/{len(sortedTop)}")

        return embed


def afficher_top_coin(page: int, guild, affichageMobile: bool = False):
    page = page - 1
    sortedData = list(sorted(db.all(), key=lambda k: k["coins"] if "coins" in k.keys() else 0, reverse=True))
    sortedDessinateur = []
    for sortedMsg in sortedData:
        membre = guild.get_member(sortedMsg["id"])
        if membre is not None:
            if not membre.bot:
                coins = 0
                if "coins" in sortedMsg.keys():
                    coins = sortedMsg["coins"]
                sortedDessinateur.append([membre.display_name, coins])
    sortedTop = list(chunks(sortedDessinateur, 10))

    if not affichageMobile:
        embed = discord.Embed(title="Top dessinateurs 🎨", colour=Colour.from_str("#0095FF"))
        pseudos, coins = "", ""
        for ind, joueur in enumerate(sortedTop[page]):
            if page == 0:
                if ind == 0:
                    pseudos += f"🥇- **{joueur[0]}**\n"
                elif ind == 1:
                    pseudos += f"🥈- **{joueur[0]}**\n"
                elif ind == 2:
                    pseudos += f"🥉- **{joueur[0]}**\n"
                else:
                    pseudos += f"🔸- **{joueur[0]}**\n"
            else:
                pseudos += f"🔸- **{joueur[0]}**\n"
            coins += f"<:Coins:1013067321251737650> **{joueur[1]}**\n"

        # embed.set_thumbnail(url="https://f.angiva.re/XaSyB.gif")
        embed.add_field(name="Dessinateurs", value=pseudos, inline=True)
        embed.add_field(name="Coins", value=coins, inline=True)
        embed.set_footer(text=f"Page {page + 1}/{len(sortedTop)}")
        return embed
    else:
        chaine = f"**Dessinateurs** - **Coins**‏\n\n"
        for ind, joueur in enumerate(sortedTop[page]):
            if page == 0:
                if ind == 0:
                    chaine += f"🥇- **{joueur[0]}** - <:Coins:1013067321251737650> **{joueur[1]}**\n"
                elif ind == 1:
                    chaine += f"🥈- **{joueur[0]}** - <:Coins:1013067321251737650> **{joueur[1]}**\n"
                elif ind == 2:
                    chaine += f"🥉- **{joueur[0]}** - <:Coins:1013067321251737650> **{joueur[1]}**\n"
                else:
                    chaine += f"🔸- **{joueur[0]}** - <:Coins:1013067321251737650> **{joueur[1]}**\n"
            else:
                chaine += f"🔸- **{joueur[0]}** - <:Coins:1013067321251737650> **{joueur[1]}**\n"
        embed = discord.Embed(title="Top dessinateurs 🎨", description=chaine, colour=Colour.from_str("#0095FF"))
        embed.set_footer(text=f"Page {page + 1}/{len(sortedTop)}")
        return embed
