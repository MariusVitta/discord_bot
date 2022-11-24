import asyncio
import random
import re
import typing
from datetime import datetime
import discord
from discord import Interaction
from typing import List
from unidecode import unidecode

import jeuPVP
import puissance4
from config import client
from morpion import Morpion

global joueurs, precis, somme, labelJ
joueurs = {}
precis = {}
sommes = {}
LOGS = 936404977059000320
COMMANDS = 918255435553841222

tabEmoji = ["<:xcross:936758268448100443>", "<:circle:936758258172063854>"]

em = {
    "couleur": "<:rondcasino:935601205651079299>",
    "douzaine": "<:table:935603960113406003>",
    "nombre": "<:chiffre:935605036296323173>",
    "roulette": "<:roulette:935623739721277575>",
    "fleche": "<:fleche:925077237164806164>",
    "kakera": "<:kake:925052720870752296>",
    "colonne": "<:colonne:935895894413422592>",
    "parite": "<:parite:935897220279054367>",
    "pair": "<:parite:935897220279054367>",
    "impair": "<:parite:935897220279054367>",
    "jeton": "<:Jeton:935878250620661881>",
    "noire": "⚫",
    "rouge": "🔴"
}


async def verifKake(id):
    await asyncio.sleep(0.5)
    logschan = client.get_channel(LOGS)
    pseudo = logschan.guild.get_member(id).name

    def check(m):
        if m.author.id == 591619285663875073 and m.content.startswith("kverif"):
            return pseudo == m.content.split(" ", maxsplit=2)[2]

    await logschan.send(f":pr <@{id}>")
    msg = await client.wait_for("message", check=check)
    return int(msg.content.split(" ")[1])


class BoutonTypeMise(discord.ui.Button):
    def __init__(self, typeMise, index, emote):
        self.typeMise = typeMise
        self.index = index
        self.emote = emote
        super().__init__(style=discord.ButtonStyle.blurple, label=typeMise, row=0, emoji=emote)

    async def callback(self, interaction: Interaction):
        assert self.view is not None
        view: TypeMise = self.view

        joueur = interaction.user
        if joueur.id in joueurs:
            await interaction.response.send_message(
                "Vous avez déjà choisi un type de mise ! Vous ne pouvez pas le changer.", ephemeral=True)
        else:
            await interaction.response.send_message("Vérification de vos kakeras...", ephemeral=True)
            kakeJoueurs = await verifKake(joueur.id)
            if int(kakeJoueurs) >= 50:
                joueurs[joueur.id] = (joueur.display_name, self.typeMise, kakeJoueurs, self.index)
                await interaction.followup.send(
                    f"Vous avez bien été ajouté à la liste des joueurs !\nVous pourrez choisir votre {self.typeMise.lower()} quand les 15 secondes seront écoulées.",
                    ephemeral=True)
                await interaction.channel.send(f"{joueur.display_name} a rejoint la partie !")
            else:
                await interaction.followup.send(
                    "Vous n'avez pas assez de kakeras pour rejoindre la partie ! Il en faut minimum 50", ephemeral=True)


class BoutonTypePrecis(discord.ui.Button):
    def __init__(self, typePrecis, row, emote):
        self.typePrecis = typePrecis
        self.row = row
        self.emote = emote
        super().__init__(style=discord.ButtonStyle.blurple, label=typePrecis, row=row, emoji=emote)

    async def callback(self, interaction: Interaction):
        assert self.view is not None
        view: TypePrecis = self.view

        joueur = interaction.user
        if joueur.id in precis:
            await interaction.response.send_message(
                "Vous avez déjà choisi ce sur quoi vous misez ! Vous ne pouvez pas le changer.", ephemeral=True)
        else:
            if joueur.id in joueurs:
                if joueurs[joueur.id][-1] == self.row:
                    precis[joueur.id] = (joueur.display_name, self.typePrecis)
                    await interaction.response.send_message(
                        f"L'item sur lequel vous misez a bien été pris en compte ! En attente de tous les joueurs...",
                        ephemeral=True)
                    if len(joueurs) == len(precis):
                        view.stop()
                else:
                    await interaction.response.send_message(
                        f"Vous ne pouvez pas choisir \"{self.typePrecis.lower()}\". Vous n'avez pas choisi ce type de mise à la première étape.",
                        ephemeral=True)


class BoutonSomme(discord.ui.Button):
    def __init__(self, somme, ligne):
        self.somme = somme
        self.ligne = ligne
        super().__init__(style=discord.ButtonStyle.blurple, label=somme, row=ligne, emoji="<:kake:925052720870752296>")

    async def callback(self, interaction: Interaction):
        assert self.view is not None
        view: Somme = self.view

        joueur = interaction.user
        if joueur.id in sommes:
            await interaction.response.send_message("Vous avez déjà misé votre somme ! Vous ne pouvez pas la changer.",
                                                    ephemeral=True)
        else:
            if joueur.id in joueurs:
                if int(self.somme) <= int(joueurs[joueur.id][2]):
                    sommes[joueur.id] = (joueur.display_name, self.somme)
                    await interaction.response.send_message(
                        f"Votre mise de {self.somme} <:kake:925052720870752296> a bien été prise en compte ! Vous ne pouvez pas la changer.",
                        ephemeral=True)
                    if len(joueurs) == len(sommes):
                        view.stop()
                else:
                    await interaction.response.send_message(
                        f"Vous n'avez pas assez de sous ! Vous avez {str(joueurs[joueur.id][2])} <:kake:925052720870752296>",
                        ephemeral=True)


class TypeMise(discord.ui.View):
    children: typing.List[BoutonTypeMise]

    def __init__(self):
        super().__init__(timeout=15.0)
        self.mises = ["Douzaine", "Colonne", "Parité", "Couleur", "Nombre"]

        for i in range(len(self.mises)):
            self.add_item(BoutonTypeMise(self.mises[i], i, em[unidecode(self.mises[i]).lower()]))


class MorpionButtonPlayGame(discord.ui.Button):
    def __init__(self, indiceBouton: int, member: discord.Member, emoji, style):
        self.indiceBouton = indiceBouton
        self.member = member
        super().__init__(style=style, label=emoji, row=indiceBouton)

    async def callback(self, interaction: Interaction):
        assert self.view is not None
        view: ViewVerificationP4 = self.view

        interactionJoueur = interaction.user
        if interactionJoueur.id != self.member.id:
            await interaction.response.send_message("Vous n'êtes pas le joueur concerné par cette invitation",
                                                    ephemeral=True)
        else:
            for i in view.children:
                if i == self:
                    i.disabled = True
            if self.style == discord.ButtonStyle.green:
                view.setVeutJouer()
            else:
                await interaction.response.defer()
            view.stop()


class ViewVerificationMorpion(discord.ui.View):
    children: typing.List[MorpionButtonPlayGame]

    def __init__(self, member):
        self.veutJouer = False
        super().__init__(timeout=30.0)
        self.add_item(Puissance4ButtonPlayGame(0, member, "✔️", discord.ButtonStyle.green))
        self.add_item(Puissance4ButtonPlayGame(0, member, "❌", discord.ButtonStyle.red))

    def setVeutJouer(self):
        self.veutJouer = True
        return


class MorpionButton(discord.ui.Button):
    def __init__(self, valJ, indiceLigne, indiceCol, estDesactive, partie):
        self.indiceLigne = indiceLigne
        self.indiceCol = indiceCol
        self.valJ = valJ
        self.estDesactive = estDesactive
        self.partie = partie
        super().__init__(style=self.style(), label="‎", row=indiceLigne, disabled=estDesactive, emoji=self.setEmoji())

    def style(self):
        if not self.estDesactive:
            return discord.ButtonStyle.blurple

        if self.partie.getTableauStateButton()[self.indiceLigne][self.indiceCol][1] == "X":
            return discord.ButtonStyle.green
        else:
            return discord.ButtonStyle.red

    def setEmoji(self):
        if not self.estDesactive:
            return None

        if self.partie.getTableauStateButton()[self.indiceLigne][self.indiceCol][1] == "X":
            return tabEmoji[0]
        else:
            return tabEmoji[1]

    async def callback(self, interaction: Interaction):
        assert self.view is not None
        view: ViewMorpion = self.view

        interactionJoueur = interaction.user
        if interactionJoueur.id != view.getJoueurActuel().id:
            await interaction.response.send_message("Ce n'est pas votre tour de jeu.", ephemeral=True)
        else:
            if view.getValeurJoueurActuel() == 1:
                if view.getPartieMorpion().getTableauJeu()[self.indiceLigne][self.indiceCol] != '-':
                    await interaction.response.send_message("Vous ne pouvez pas jouer sur cette case", ephemeral=True)
                else:
                    for i in view.children:
                        if i == self:
                            i.disabled = True
                            i.style = discord.ButtonStyle.green
                            self.emoji = tabEmoji[0]
                            view.getPartieMorpion().setTableauJeu(self.indiceLigne, self.indiceCol, 'X')
                            view.getPartieMorpion().setTableauStateButton(self.indiceLigne, self.indiceCol, 'X')
                            await interaction.response.edit_message(
                                view=self.view)
                            view.stop()

            else:
                if view.getPartieMorpion().getTableauJeu()[self.indiceLigne][self.indiceCol] != '-':
                    await interaction.response.send_message("Vous ne pouvez pas jouer sur cette case", ephemeral=True)
                else:
                    for i in view.children:
                        if i == self:
                            i.disabled = True
                            i.style = discord.ButtonStyle.red
                            self.emoji = tabEmoji[1]
                            view.getPartieMorpion().setTableauJeu(self.indiceLigne, self.indiceCol, 'O')
                            view.getPartieMorpion().setTableauStateButton(self.indiceLigne, self.indiceCol, 'O')
                            await interaction.response.edit_message(
                                view=self.view)
                            view.stop()


class ViewMorpion(discord.ui.View):
    children: typing.List[MorpionButton]

    def __init__(self, partieMorpion: Morpion):
        # timeout=10.0)
        super().__init__()
        self.partieMorpion = partieMorpion
        val = 0
        for i in range(len(self.partieMorpion.getTableauJeu())):
            self.add_item(
                MorpionButton(self.partieMorpion.getJoueurActuel().getValeur(), i, 0,
                              self.partieMorpion.getTableauStateButton()[i][val + 0][0], self.partieMorpion))
            self.add_item(
                MorpionButton(self.partieMorpion.getJoueurActuel().getValeur(), i, 1,
                              self.partieMorpion.getTableauStateButton()[i][1][0], self.partieMorpion))
            self.add_item(
                MorpionButton(self.partieMorpion.getJoueurActuel().getValeur(), i, 2,
                              self.partieMorpion.getTableauStateButton()[i][2][0], self.partieMorpion))

    def getJoueurActuel(self):
        return self.partieMorpion.getJoueurActuel().getMember()

    def getValeurJoueurActuel(self):
        return self.partieMorpion.getJoueurActuel().getValeur()

    def getPartieMorpion(self):
        return self.partieMorpion


class Puissance4Button(discord.ui.Button):
    def __init__(self, player, label, valJoueur, row, entierLabel, tabHauteurPuissance4, valColonnePuissance4):
        self.player = player
        self.valJoueur = valJoueur
        self.entierLabel = entierLabel
        self.tabHauteurPuissance4 = tabHauteurPuissance4
        self.valColonnePuissance4 = valColonnePuissance4
        super().__init__(style=discord.ButtonStyle.blurple, label=label, row=row)

    async def callback(self, interaction: Interaction):
        assert self.view is not None
        view: ViewPuissance4 = self.view

        interactionJoueur = interaction.user
        if interactionJoueur.id != self.player.id:
            await interaction.response.send_message("Ce n'est pas votre tour de jeu.",
                                                    ephemeral=True)
        else:
            if self.valJoueur == 1:
                if self.tabHauteurPuissance4[self.entierLabel] < 0:
                    await interaction.response.send_message("Vous ne pouvez pas jouer sur cette case", ephemeral=True)
                else:
                    self.tabHauteurPuissance4[self.entierLabel] -= 1
                    view.getPartie().setValColonnePuissance4(self.entierLabel)
                    view.stop()

            else:
                if self.tabHauteurPuissance4[self.entierLabel] < 0:
                    await interaction.response.send_message("Vous ne pouvez pas jouer sur cette case", ephemeral=True)
                else:
                    view.getPartie().setValColonnePuissance4(self.entierLabel)
                    self.tabHauteurPuissance4[self.entierLabel] -= 1
                    view.stop()


class ViewPuissance4(discord.ui.View):
    children: typing.List[Puissance4Button]

    def __init__(self, nbBoutons, joueurPuissance4, valJoueurPuissance4, tabHauteurPuissance4, valColonnePuissance4,
                 partie):
        self.partie = partie
        super().__init__(timeout=10.0)
        for i in range(nbBoutons):
            if i < 5:
                self.add_item(
                    Puissance4Button(joueurPuissance4, str(i + 1), valJoueurPuissance4, 0, i, tabHauteurPuissance4,
                                     valColonnePuissance4))
            if i >= 5:
                self.add_item(
                    Puissance4Button(joueurPuissance4, str(i + 1), valJoueurPuissance4, 1, i, tabHauteurPuissance4,
                                     valColonnePuissance4))

    def getPartie(self):
        return self.partie


class CreatePuissance4Party:

    def __init__(self, nbBoutons, joueur, valColonnePuissance4):
        self.joueurPuissance4 = joueur
        self.tabHauteurPuissance4 = [5, 5, 5, 5, 5, 5, 5]
        self.valColonnePuissance4 = valColonnePuissance4
        self.valJoueurPuissance4 = 1
        self.indiceColPrec = None
        self.indiceLignePrec = None
        self.nbBoutons = nbBoutons
        self.enCours = False
        self.casesPuissance4 = [
            ["<:square:936719107989065799>", "<:square:936719107989065799>", "<:square:936719107989065799>",
             "<:square:936719107989065799>", "<:square:936719107989065799>", "<:square:936719107989065799>",
             "<:square:936719107989065799>"],
            ["<:square:936719107989065799>", "<:square:936719107989065799>", "<:square:936719107989065799>",
             "<:square:936719107989065799>", "<:square:936719107989065799>", "<:square:936719107989065799>",
             "<:square:936719107989065799>"],
            ["<:square:936719107989065799>", "<:square:936719107989065799>", "<:square:936719107989065799>",
             "<:square:936719107989065799>", "<:square:936719107989065799>", "<:square:936719107989065799>",
             "<:square:936719107989065799>"],
            ["<:square:936719107989065799>", "<:square:936719107989065799>", "<:square:936719107989065799>",
             "<:square:936719107989065799>", "<:square:936719107989065799>", "<:square:936719107989065799>",
             "<:square:936719107989065799>"],
            ["<:square:936719107989065799>", "<:square:936719107989065799>", "<:square:936719107989065799>",
             "<:square:936719107989065799>", "<:square:936719107989065799>", "<:square:936719107989065799>",
             "<:square:936719107989065799>"],
            ["<:square:936719107989065799>", "<:square:936719107989065799>", "<:square:936719107989065799>",
             "<:square:936719107989065799>", "<:square:936719107989065799>", "<:square:936719107989065799>",
             "<:square:936719107989065799>"],
        ]

    def __eq__(self, o: object) -> bool:
        return super().__eq__(o)

    def setValColonnePuissance4(self, val):
        self.valColonnePuissance4 = val

    def setTabHauteurPuissance4(self, colonne):
        self.tabHauteurPuissance4[colonne] -= 1

    def verifColonne(self, colonne):
        return self.tabHauteurPuissance4[colonne] < 0

    def createView(self):
        return ViewPuissance4(self.nbBoutons, self.joueurPuissance4, self.valJoueurPuissance4,
                              self.tabHauteurPuissance4, self.valColonnePuissance4, self)


class Puissance4ButtonPlayGame(discord.ui.Button):
    def __init__(self, indiceBouton: int, member: discord.Member, emoji, style):
        self.indiceBouton = indiceBouton
        self.member = member
        super().__init__(style=style, label=emoji, row=indiceBouton)

    async def callback(self, interaction: Interaction):
        assert self.view is not None
        view: ViewVerificationP4 = self.view

        interactionJoueur = interaction.user
        if interactionJoueur.id != self.member.id:
            await interaction.response.send_message("Vous n'êtes pas le joueur concerné par cette invitation",
                                                    ephemeral=True)
        else:
            for i in view.children:
                if i == self:
                    i.disabled = True
            if self.style == discord.ButtonStyle.green:
                view.setVeutJouer()
            view.stop()


class ViewVerificationP4(discord.ui.View):
    children: typing.List[Puissance4ButtonPlayGame]

    def __init__(self, member):
        self.veutJouer = False
        super().__init__(timeout=30.0)
        self.add_item(Puissance4ButtonPlayGame(0, member, "✔️", discord.ButtonStyle.green))
        self.add_item(Puissance4ButtonPlayGame(0, member, "❌", discord.ButtonStyle.red))

    def setVeutJouer(self):
        self.veutJouer = True
        return


class TypePrecis(discord.ui.View):
    children: typing.List[BoutonTypeMise]

    def __init__(self):
        super().__init__(timeout=20.0)
        self.sommes = [
            ["Douzaine 1", "Douzaine 2", "Douzaine 3"],
            ["Colonne 1", "Colonne 2", "Colonne 3"],
            ["Pair", "Impair"],
            ["Rouge", "Noire"]
        ]

        for typeI in range(len(self.sommes)):
            for typeJ in self.sommes[typeI]:
                self.add_item(BoutonTypePrecis(typeJ, typeI, em[typeJ.split(" ")[0].lower()]))

        # joueursNombre = []
        # for item in joueurs:
        #     if joueurs[item][1] == "Nombre":
        #         joueursNombre.append(item)

        # def check(m):
        #     if m.author.id in joueursNombre:
        #         if m.content.isdecimal():
        #             precis[m.author.id] = (m.author.display_name, m.content)
        #             joueursNombre.remove(m.author.id)
        #     return not joueursNombre

        # await client.wait_for("message", check=check)


class Somme(discord.ui.View):
    children: typing.List[BoutonSomme]

    def __init__(self):
        super().__init__(timeout=20.0)
        self.sommes = [
            ["50", "100", "150", "200"],
            ["250", "500", "750", "1000"],
            ["2500", "3500", "5000"]
        ]

        for i in range(len(self.sommes)):
            for j in self.sommes[i]:
                self.add_item(BoutonSomme(j, i))
        # for somme in self.sommes:
        #     self.add_item(BoutonSomme(somme))


class TopButton(discord.ui.Button):
    def __init__(self, cid, emote):
        self.cid = cid
        self.emote = emote

        super().__init__(style=discord.ButtonStyle.secondary, custom_id=self.cid, emoji=self.emote, row=0)

    async def callback(self, interaction: Interaction):
        assert self.view is not None
        view: ViewTop = self.view

        textFooter = r"Page (\d)\/" + str(view.getLastPage())
        print(textFooter)
        currentPage = int(re.search(textFooter, interaction.message.embeds[0].footer.text).group(1))
        newPage = 0
        if self.cid == "cst_next_btn":
            if currentPage == view.getLastPage():
                newPage = 1
            else:
                newPage = currentPage + 1
        if self.cid == "cst_prev_btn":
            if currentPage - 1 == 0:
                newPage = view.getLastPage()
            else:
                newPage = currentPage - 1
        print("new", newPage)
        await interaction.message.edit(
            embed=await puissance4.topEmbed(newPage, interaction.guild, interaction.message.channel), view=view)
        await interaction.response.defer()


def isFirstPage(page):
    return page == 1


class ViewTop(discord.ui.View):
    childen: typing.List[TopButton]

    def __init__(self, dernierpage):
        self.lastPage = dernierpage
        super().__init__()

        tabTop = [
            ["cst_prev_btn", discord.PartialEmoji.from_str("<:reversefleche:936724361740693585>")],
            ["cst_next_btn", discord.PartialEmoji.from_str("<:fleche:925077237164806164>")]
        ]

        for i in range(len(tabTop)):
            self.add_item(TopButton(tabTop[i][0], tabTop[i][1]))

    def isLastPage(self, page):
        return self.lastPage == page

    def getLastPage(self):
        return self.lastPage


coordonnesObstacles = [(337, 337), (337, 253), (421, 337), (253, 673), (925, 169), (841, 505), (757, 505), (841, 589)]
valeurDeplacement = 84  # nombre de pixels entres 2 cases
# valeurs en pixels des limites de la map dans les 4 directions
maxOuest = 85
maxEst = 1093
maxSud = 757
maxNord = 85


def dirigerVersLeBord(direction: str, coordX: int, coordY: int):
    if direction == "ouest":
        return coordX < maxOuest
    elif direction == "est":
        return coordX > maxEst
    elif direction == "nord":
        return coordY < maxNord
    elif direction == "sud":
        return coordY > maxSud


def dirigeVersObstacle(coordX: int, coordY: int):
    return (coordX, coordY) in coordonnesObstacles


class ButtonJeuPVP(discord.ui.Button):
    def __init__(self, cid, emote, ligne, estDesactive):
        self.cid = cid
        self.emote = emote

        super().__init__(style=discord.ButtonStyle.secondary, custom_id=self.cid, emoji=self.emote, row=ligne,
                         disabled=estDesactive)

    async def callback(self, interaction: Interaction):
        assert self.view is not None
        view: ViewJeuPVP = self.view

        if interaction.user.id not in view.getListID():
            await interaction.response.send_message("Vous ne faites pas partie des joueurs de la partie actuelle.",
                                                    ephemeral=True)
            return
        elif interaction.user.id != view.getJoueurActuel().getJoueurID():
            await interaction.response.send_message("Ce n'est pas votre tour de jeu.", ephemeral=True)
            return

        coordX = view.getJoueurActuel().getCoordX()
        coordY = view.getJoueurActuel().getCoordY()
        listJoueurs = view.getJoueurs()
        description = ""
        tourPasse = False
        if view.getJoueurActuel().getPointsAction() == 0 and self.cid in ["attack", "defense", "utility"]:
            await interaction.response.send_message("Vous n'avez plus de points d'action", ephemeral=True)
            return

        if view.getJoueurActuel().getPointsMouvement() == 0 and self.cid in ["arrow_left_btn", "arrow_up_btn",
                                                                             "arrow_right_btn", "arrow_down_btn"]:
            await interaction.response.send_message("Vous n'avez plus de points de mouvement", ephemeral=True)
            return
        # 85
        if self.cid == "arrow_left_btn":
            if view.dirigeVersJoueur(coordX - valeurDeplacement, coordY):
                await interaction.response.send_message("Vous ne pouvez pas être sur la même case que votre adversaire",
                                                        ephemeral=True)
                return
            elif dirigerVersLeBord("ouest", coordX - valeurDeplacement, 0) or dirigeVersObstacle(
                    coordX - valeurDeplacement, coordY):
                await interaction.response.send_message("Vous ne pouvez pas jouer dans cette direction", ephemeral=True)
                return
            else:
                view.getJoueurActuel().setCoordX(view.getJoueurActuel().getCoordX() - valeurDeplacement)
                view.getJoueurActuel().removePointsMouvement(1)
        # 85
        elif self.cid == "arrow_up_btn":
            if view.dirigeVersJoueur(coordX, coordY - valeurDeplacement):
                await interaction.response.send_message("Vous ne pouvez pas être sur la même case que votre adversaire",
                                                        ephemeral=True)
                return
            elif dirigerVersLeBord("nord", 0, coordY - valeurDeplacement) or dirigeVersObstacle(coordX,
                                                                                                coordY - valeurDeplacement):
                await interaction.response.send_message("Vous ne pouvez pas jouer dans cette direction", ephemeral=True)
                return
            else:
                view.getJoueurActuel().setCoordY(view.getJoueurActuel().getCoordY() - valeurDeplacement)
                view.getJoueurActuel().removePointsMouvement(1)
        # 757
        elif self.cid == "arrow_down_btn":
            if view.dirigeVersJoueur(coordX, coordY + valeurDeplacement):
                await interaction.response.send_message("Vous ne pouvez pas être sur la même case que votre adversaire",
                                                        ephemeral=True)
                return
            elif dirigerVersLeBord("sud", 0, coordY + valeurDeplacement) or dirigeVersObstacle(coordX,
                                                                                               coordY + valeurDeplacement):
                await interaction.response.send_message("Vous ne pouvez pas jouer dans cette direction", ephemeral=True)
                return
            else:
                view.getJoueurActuel().setCoordY(view.getJoueurActuel().getCoordY() + valeurDeplacement)
                view.getJoueurActuel().removePointsMouvement(1)
        # 1093
        elif self.cid == "arrow_right_btn":
            if view.dirigeVersJoueur(coordX + valeurDeplacement, coordY):
                await interaction.response.send_message("Vous ne pouvez pas être sur la même case que votre adversaire",
                                                        ephemeral=True)
                return
            elif dirigerVersLeBord("est", coordX + valeurDeplacement, 0) or dirigeVersObstacle(
                    coordX + valeurDeplacement, coordY):
                await interaction.response.send_message("Vous ne pouvez pas jouer dans cette direction", ephemeral=True)
                return
            else:
                view.getJoueurActuel().setCoordX(view.getJoueurActuel().getCoordX() + valeurDeplacement)
                view.getJoueurActuel().removePointsMouvement(1)
        elif self.cid == "skip_the_turn":
            description = f"{view.getJoueurActuel().getObjetMember().display_name} a passé son tour"
            view.getJoueurActuel().setPasseTour(True)

        elif self.cid == "rankyaku":
            if not view.getJoueurActuel().getPointsAction() >= 2:
                await interaction.response.send_message("Vous n'avez pas assez de point d'action",
                                                        ephemeral=True)
                return
            description = f"{view.getJoueurActuel().getObjetMember().display_name} a attaqué"
            view.getJoueurActuel().removePointsAction(2)
            view.getJoueurActuel().setPointsDeVie(100)
            if view.getJoueurActuel().estMort():
                view.removePlayer(view.getJoueurActuel())
            print(view.getJoueurs())
            print("attaque")
        elif self.cid == "tekkai":
            if not view.getJoueurActuel().getPointsAction() >= 2:
                await interaction.response.send_message("Vous n'avez pas assez de point d'action",
                                                        ephemeral=True)
                return
            description = f"{view.getJoueurActuel().getObjetMember().display_name} s'est défendu"
            view.getJoueurActuel().removePointsAction(2)
            print("defense")
        elif self.cid == "geppo":
            if not view.getJoueurActuel().getPointsAction() >= 3:
                await interaction.response.send_message("Vous n'avez pas assez de point d'action",
                                                        ephemeral=True)
                return
            random.seed(datetime.now())
            nbRandom = random.random()
            print("Nombre random", nbRandom)
            nbPM = 0
            # 25% chance de rien gagner
            # 50% chance de gagner 1 PM
            # 15% chance de gagner 2 PM
            # 9% chance de gagner 3 PM
            # 1% chance de gagner 4 PM
            #
            # 0 - 0.25
            # 0.25 - 0.75
            # 0.75 - 0.90
            # 0.90 - 0.99
            # 0.99 - 1.00
            if 0 <= nbRandom <= 0.25:
                nbPM = 0
            elif 0.25 < nbRandom <= 0.75:
                nbPM = 1
            elif 0.75 < nbRandom <= 0.90:
                nbPM = 2
            elif 0.90 < nbRandom <= 0.99:
                nbPM = 3
            elif 0.99 < nbRandom <= 1.00:
                nbPM = 4

            view.getJoueurActuel().addPointsMouvement(nbPM)
            view.getJoueurActuel().removePointsAction(3)
            description = f"{view.getJoueurActuel().getObjetMember().display_name} a gagné des PM: {nbPM}"

        # print(  f"PM de {view.getJoueurActuel().getObjetMember().display_name}: {view.getJoueurActuel().getPointsMouvement()}, PM de {view.getAdversaire().getObjetMember().display_name}: {view.getAdversaire().getPointsMouvement()}")
        if view.getJoueurActuel().estMort() or view.getJoueurActuel().getPasseTour() or view.getJoueurActuel().getPointsMouvement() == 0 and view.getJoueurActuel().getPointsAction() == 0:
            view.getJoueurActuel().resetStat()
            view.changerJoueur()
        ancienne_description = interaction.message.embeds[2].description
        if ancienne_description is None:
            ancienne_description = ""
        await interaction.message.edit(
            embeds=[jeuPVP.embedJeu(view.getJoueurActuel(), view.getJoueurs()), jeuPVP.embedPVJoueurs(view.getJoueurs()), jeuPVP.embedActionJoueurs(ancienne_description, description)], view=view,
            attachments=[discord.File(f"{jeuPVP.pathImage}temp/jeu.png")])

        await interaction.response.defer()


class ViewJeuPVP(discord.ui.View):
    childen: typing.List[ButtonJeuPVP]

    def __init__(self, joueurActuel: jeuPVP.Joueur, joueursPvP: List[jeuPVP.Joueur], team1: List[int],
                 team2: List[int]):
        self.joueurActuel = joueurActuel
        self.joueursPvP = joueursPvP
        self.team1 = team1
        self.team2 = team2
        super().__init__()

        tabTop = [
            [
                ["vide_1", discord.PartialEmoji.from_str("<:space:982675739553976332>"), True],
                ["arrow_up_btn", discord.PartialEmoji.from_str("<:haut:982417211681546341>"), False],
                ["vide_2", discord.PartialEmoji.from_str("<:space:982675739553976332>"), True],
                ["rankyaku", discord.PartialEmoji.from_str("<:Rankyaku:983398785872973975>"), False],
                ["attaqueDiagonale", discord.PartialEmoji.from_str("<:Attaque_Diagonale:983791854044708954>"), False]
            ],
            [
                ["arrow_left_btn", discord.PartialEmoji.from_str("<:gauche:982417254568300584>"), False],
                ["skip_the_turn", discord.PartialEmoji.from_str("⏳"), False],
                ["arrow_right_btn", discord.PartialEmoji.from_str("<:droite:982417243809927168>"), False],
                ["tekkai", discord.PartialEmoji.from_str("<:Tekkai:983400219817426974>"), False],
                ["etourdissement", discord.PartialEmoji.from_str("<:Etourdissement:983498702679335002>"), False]
            ],
            [
                ["vide_4", discord.PartialEmoji.from_str("<:space:982675739553976332>"), True],
                ["arrow_down_btn", discord.PartialEmoji.from_str("<:bas:982417224922988595>"), False],
                ["vide_5", discord.PartialEmoji.from_str("<:space:982675739553976332>"), True],
                ["geppo", discord.PartialEmoji.from_str("<:Geppo:983400196966854667>"), False],
                ["terrainMouvant", discord.PartialEmoji.from_str("<:Terrain_Mouvant:983789197313839158>"), False]
            ],

        ]

        for i in range(len(tabTop)):
            for tab in tabTop[i]:
                self.add_item(ButtonJeuPVP(tab[0], tab[1], i, tab[2]))

    def changerJoueur(self):
        self.joueurActuel = self.getJoueurs().pop(0)
        self.getJoueurs().append(self.joueurActuel)

    def setJoueurActuel(self, val: discord.Member):
        self.joueurActuel = val

    def getJoueurActuel(self) -> jeuPVP.Joueur:
        return self.joueurActuel

    def getJoueurs(self):
        return self.joueursPvP

    def inTeam1(self, joueurID):
        return joueurID in self.team1

    def inTeam2(self, joueurID):
        return joueurID in self.team2

    def dirigeVersJoueur(self, coordX: int, coordY: int):
        tuplesJoueurs = [(j.getCoordX(), j.getCoordY()) for j in self.getJoueurs()]
        return (coordX, coordY) in tuplesJoueurs

    def getListID(self) -> List[int]:
        return [j.getJoueurID() for j in self.getJoueurs()]

    def removePlayer(self, joueur: jeuPVP.Joueur):
        self.joueursPvP.remove(joueur)
        if self.inTeam1(joueur.getJoueurID()):
            self.team1.remove(joueur.getJoueurID())
        elif self.inTeam2(joueur.getJoueurID()):
            self.team2.remove(joueur.getJoueurID())


class DofusButtonPlayGame(discord.ui.Button):
    def __init__(self, cid: str, member: discord.Member, content, style):
        self.cid = cid
        self.member = member
        super().__init__(style=style, label=content, row=0, custom_id=cid)

    async def callback(self, interaction: Interaction):
        assert self.view is not None
        view: ViewVerificationDofus = self.view

        interactionJoueur = interaction.user
        if interactionJoueur.id != self.member.id:
            await interaction.response.send_message("Vous n'êtes pas le joueur concerné par cette demande",
                                                    ephemeral=True)
        else:
            for i in view.children:
                if i == self:
                    i.disabled = True
            if self.custom_id == "two_versus_two":
                view.setVeutJouer()
            if self.custom_id == "cancel_party":
                view.setAnnulerPartie()
            await interaction.response.defer()
            view.stop()


class ViewVerificationDofus(discord.ui.View):
    children: typing.List[DofusButtonPlayGame]

    def __init__(self, member):
        self.veutJouerA2 = False
        self.aAnnuler = False
        super().__init__(timeout=30.0)
        self.add_item(DofusButtonPlayGame("one_versus_one", member, "1v1", discord.ButtonStyle.grey))
        self.add_item(DofusButtonPlayGame("two_versus_two", member, "2v2", discord.ButtonStyle.grey))
        self.add_item(DofusButtonPlayGame("cancel_party", member, "❌", discord.ButtonStyle.red))

    def setVeutJouer(self):
        self.veutJouerA2 = True
        return

    def setAnnulerPartie(self):
        self.aAnnuler = True
        return


class DofusButtonWaitPlayer(discord.ui.Button):
    def __init__(self, cid: str, content, style, ligne: int):
        self.cid = cid
        super().__init__(style=style, label=content, row=ligne, custom_id=cid)

    async def callback(self, interaction: Interaction):
        assert self.view is not None
        view: ViewAttenteJoueurDofus = self.view

        interactionJoueur = interaction.user
        listeA = [joueurID.id for joueurID in view.getJoueursA()]
        listeB = [joueurID.id for joueurID in view.getJoueursB()]
        listeA += listeB

        if self.custom_id == "team_a":
            if interactionJoueur.id not in listeA and not view.estComplet("team_a"):
                view.addJoueur("team_a", interactionJoueur)
                await interaction.response.send_message("Vous avez rejoint l'équipe.",
                                                        ephemeral=True)
                await interaction.message.edit(embed=jeuPVP.embedListeJoueurs(view.getJoueurs()), view=view)
                return
            elif view.estComplet("team_a"):
                await interaction.response.send_message("Cette équipe est complète.", ephemeral=True)
                return
            else:
                await interaction.response.send_message(
                    "Vous êtes déjà dans une équipe, cliquez sur la croix rouge pour quitter votre équipe.",
                    ephemeral=True)
                return

        if self.custom_id == "team_b":
            if interactionJoueur.id not in listeA and not view.estComplet("team_b"):
                view.addJoueur("team_b", interactionJoueur)
                await interaction.response.send_message("Vous avez rejoint l'équipe.", ephemeral=True)
                await interaction.message.edit(embed=jeuPVP.embedListeJoueurs(view.getJoueurs()), view=view)
                return
            elif view.estComplet("team_b"):
                await interaction.response.send_message("Cette équipe est complète.", ephemeral=True)
                return
            else:
                await interaction.response.send_message(
                    "Vous êtes déjà dans une équipe, cliquez sur la croix rouge pour quitter votre équipe.",
                    ephemeral=True)
                return
        if self.custom_id == "cancel_party":
            if interactionJoueur.id in listeA:
                await interaction.response.send_message("Vous avez quitté le jeu", ephemeral=True)
                view.removeJoueur(interactionJoueur)
                await interaction.message.edit(embed=jeuPVP.embedListeJoueurs(view.getJoueurs()), view=view)
            else:
                await interaction.response.send_message("Vous n'êtes parmi les joueurs de la partie.", ephemeral=True)

        if self.custom_id == "start_party":
            if interactionJoueur != view.getHost():
                await interaction.response.send_message("Vous ne pouvez pas lancer la partie.", ephemeral=True)
                return
            elif len(view.getJoueursA()) == 0 or len(view.getJoueursB()) == 0:
                await interaction.response.send_message("Vous ne pouvez pas lancer la partie avec une équipe vide", ephemeral=True)
                return
            else:
                await interaction.response.defer()
                view.stop()
        # await interaction.response.defer()


class ViewAttenteJoueurDofus(discord.ui.View):
    children: typing.List[DofusButtonWaitPlayer]

    def __init__(self, host: discord.Member, member: discord.Member):
        self.joueurs = {"team_a": [host], "team_b": [member]}
        self.host = host
        super().__init__()
        self.add_item(DofusButtonWaitPlayer("team_a", f"Équipe {host.display_name}", discord.ButtonStyle.grey, ligne=0))
        self.add_item(DofusButtonWaitPlayer("team_b", f"Équipe {member.display_name}", discord.ButtonStyle.grey, ligne=0))
        self.add_item(DofusButtonWaitPlayer("start_party", "✔️", discord.ButtonStyle.green, ligne=1))
        self.add_item(DofusButtonWaitPlayer("cancel_party", "❌", discord.ButtonStyle.red, ligne=1))

    def addJoueur(self, strTeam: str, idJoueur: discord.Member):
        self.joueurs[strTeam].append(idJoueur)
        return

    def removeJoueur(self, idJoueur: discord.Member):
        if idJoueur in self.joueurs["team_a"]:
            self.joueurs["team_a"].remove(idJoueur)
        elif idJoueur in self.joueurs["team_b"]:
            self.joueurs["team_b"].remove(idJoueur)

    def getJoueursA(self):
        return self.joueurs["team_a"]

    def getJoueursB(self):
        return self.joueurs["team_b"]

    def getJoueurs(self):
        return self.joueurs

    def getHost(self):
        return self.host

    def estComplet(self, strTeam: str):
        return len(self.joueurs[strTeam]) == 4
