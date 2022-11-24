import asyncio
import os
from random import randint

import discord
import emoji
from PIL import Image, ImageFont, ImageDraw
from typing import List

pathImage = "imagesDofus/"


class Sort:
    def __init__(self, nom: str, portee: int, ligneDeVue: str, coupPA: int, dureeChargement: int, degat: dict):
        self.nom = nom
        self.portee = portee
        self.ligneDeVue = ligneDeVue  # valeurs possibles: ligne, diagnole, cercle, aucune
        self.coupPA = coupPA
        self.dureeChargement = dureeChargement
        self.valeurReset = dureeChargement
        self.degat = degat
        super().__init__()

    def getPortee(self):
        return self.portee

    def getLigneDeVue(self):
        return self.ligneDeVue

    def getCoupPA(self):
        return self.coupPA

    def getDureeChargement(self):
        return self.dureeChargement

    def getDegat(self, distance: str):
        tupleDegat = self.degat[distance]
        return randint(tupleDegat[0], tupleDegat[1])

    def getNom(self):
        return self.nom

    def verifSort(self):
        if self.getDureeChargement() == 0:
            self.resetSort()
            return
        return

    def resetSort(self):
        self.dureeChargement = self.valeurReset
        return

    def decreaseDureeChargement(self):
        self.dureeChargement -= 1
        return

    def estUtilisable(self):
        return self.dureeChargement == self.valeurReset

    def aUneAttente(self):
        return self.valeurReset > 0


class Joueur:
    def __init__(self, coordX: int, coordY: int, couleurJoueur: str, objetMember: discord.Member,
                 couleurDiscord: discord.Colour, initiative: int):
        self.joueurID = objetMember.id
        self.coordX = coordX
        self.coordY = coordY
        self.couleurJoueur = couleurJoueur
        self.objetMember = objetMember
        self.pointsAction: int = 5
        self.pointsMouvement: int = 3
        self.couleurDiscord = couleurDiscord
        self.passeTour = False
        self.pointsDeVie = 100
        self.initiative = initiative
        super().__init__()

    def __eq__(self, o: object) -> bool:
        # checking both objects of same class
        if isinstance(o, Joueur):
            if self.joueurID == o.joueurID:
                return True
            else:
                return False

    def __lt__(self, other: object) -> bool:
        # checking both objects of same class
        if isinstance(other, Joueur):
            if self.initiative < other.initiative:
                return True
            else:
                return False

    def __repr__(self):
        return "couleur:" + self.couleurJoueur + " joueur:" + str(self.objetMember) + " initiative: " + str(
            self.initiative)

    def __str__(self):
        # print("couleur:", self.couleurJoueur, " joueur:", self.objetMember, " initiative: ", self.initiative)
        return "couleur:" + self.couleurJoueur + " joueur:" + str(self.objetMember) + " initiative: " + str(
            self.initiative)

    def setCoordX(self, coordX):
        self.coordX = coordX
        return

    def setCoordY(self, coordY):
        self.coordY = coordY
        return

    def setPointsDeVie(self, retrait):
        self.pointsDeVie -= retrait
        return

    def addPointsAction(self, valeur):
        self.pointsAction += valeur

    def removePointsAction(self, valeur):
        self.pointsAction -= valeur

    def addPointsMouvement(self, valeur):
        self.pointsMouvement += valeur

    def removePointsMouvement(self, valeur):
        self.pointsMouvement -= valeur

    def setPasseTour(self, valeur):
        self.passeTour = valeur

    def getCoordX(self):
        return self.coordX

    def getCoordY(self):
        return self.coordY

    def getJoueurID(self):
        return self.joueurID

    def getCouleurJoueur(self):
        return self.couleurJoueur

    def getObjetMember(self):
        return self.objetMember

    def getPointsAction(self):
        return self.pointsAction

    def getPointsMouvement(self):
        return self.pointsMouvement

    def getPasseTour(self):
        return self.passeTour

    def resetStat(self):
        self.pointsAction = 5
        self.pointsMouvement = 3
        self.passeTour = False

    def getDiscordCouleur(self):
        return self.couleurDiscord

    def getPointsDeVie(self):
        return self.pointsDeVie

    def getInitiative(self):
        return self.initiative

    def estMort(self):
        return self.pointsDeVie <= 0


infos = Image.open(f"{pathImage}Infos.png").convert('RGBA')
terrain = Image.open(f"{pathImage}verdure.png").convert('RGBA')
obstacles = Image.open(f"{pathImage}obstacles.png").convert('RGBA')
interface = Image.open(f"{pathImage}hud.png").convert('RGBA')
cercleVie0 = Image.open(f"{pathImage}HP Circle 00.png").convert('RGBA')
cercleVie1 = Image.open(f"{pathImage}HP Circle 01.png").convert('RGBA')
cercleVie2 = Image.open(f"{pathImage}HP Circle 02.png").convert('RGBA')
cercleVie3 = Image.open(f"{pathImage}HP Circle 03.png").convert('RGBA')
cercleVie4 = Image.open(f"{pathImage}HP Circle 04.png").convert('RGBA')
cercleVie5 = Image.open(f"{pathImage}HP Circle 05.png").convert('RGBA')
cercleVie6 = Image.open(f"{pathImage}HP Circle 06.png").convert('RGBA')
cercleVie7 = Image.open(f"{pathImage}HP Circle 07.png").convert('RGBA')
cercleVie8 = Image.open(f"{pathImage}HP Circle 08.png").convert('RGBA')
cercleVie9 = Image.open(f"{pathImage}HP Circle 09.png").convert('RGBA')
cercleVie10 = Image.open(f"{pathImage}HP Circle 10.png").convert('RGBA')
masque = Image.open(f"{pathImage}masque.png").convert('RGBA')
pionBleu = Image.open(f"{pathImage}Pion_Bleu.png").convert('RGBA')
pionRouge = Image.open(f"{pathImage}Pion_Rouge.png").convert('RGBA')
pionJaune = Image.open(f"{pathImage}Pion_Jaune.png").convert('RGBA')
pionMarron = Image.open(f"{pathImage}Pion_Marron.png").convert('RGBA')
pionOrange = Image.open(f"{pathImage}Pion_Orange.png").convert('RGBA')
pionRose = Image.open(f"{pathImage}Pion_Rose.png").convert('RGBA')
pionVert = Image.open(f"{pathImage}Pion_Vert.png").convert('RGBA')
pionViolet = Image.open(f"{pathImage}Pion_Violet.png").convert('RGBA')


def embedJeu(joueurActuel: Joueur, joueurs: List[Joueur]):
    txtPA = Image.new('RGBA', interface.size, (255, 255, 255, 0))
    txtPM = Image.new('RGBA', interface.size, (255, 255, 255, 0))
    txtPV = Image.new('RGBA', interface.size, (255, 255, 255, 0))
    # création de la police
    taille_pointsActionMouvement = 40
    police_pointsActionMouvement = ImageFont.truetype(f"fonts/arial.ttf", taille_pointsActionMouvement)

    # récupération des valeurs
    pointsAction = str(joueurActuel.getPointsAction())
    pointsMouvements = str(joueurActuel.getPointsMouvement())
    pointsDeVie = str(joueurActuel.getPointsDeVie())
    pointsDeVieInt = joueurActuel.getPointsDeVie()

    points_action = ImageDraw.Draw(txtPA)
    points_mouvement = ImageDraw.Draw(txtPM)
    points_vie = ImageDraw.Draw(txtPV)

    points_action.text((680, 1006), pointsAction, fill="white", font=police_pointsActionMouvement)
    points_mouvement.text((680, 880), pointsMouvements, fill="white", font=police_pointsActionMouvement)
    if len(pointsDeVie) == 3:
        points_vie.text((470, 945), pointsDeVie, fill="white", font=police_pointsActionMouvement)
    elif len(pointsDeVie) == 2:
        points_vie.text((485, 945), pointsDeVie, fill="white", font=police_pointsActionMouvement)
    elif len(pointsDeVie) == 1:
        points_vie.text((495, 945), pointsDeVie, fill="white", font=police_pointsActionMouvement)

    collage1 = Image.alpha_composite(obstacles, infos)
    collage2 = Image.alpha_composite(collage1, terrain)
    collage3 = Image.alpha_composite(collage2, interface)
    collage4 = Image.alpha_composite(collage3, txtPM)
    collage5 = Image.alpha_composite(collage4, txtPA)

    # 0 = vie => HP 00
    # 00 < vie <= 10 => HP 01
    # 10 < vie <= 20 => HP 02
    # 20 < vie <= 30 => HP 03
    # 30 < vie <= 40 => HP 04
    # 40 < vie <= 50 => HP 05
    # 50 < vie <= 60 => HP 06
    # 60 < vie <= 70 => HP 07
    # 70 < vie <= 80 => HP 08
    # 80 < vie <= 90 => HP 09
    # 90 < vie <= 100 => HP 10
    collage6 = ""
    if pointsDeVieInt == 0:
        collage6 = Image.alpha_composite(collage5, cercleVie0)
    elif 0 < pointsDeVieInt <= 10:
        collage6 = Image.alpha_composite(collage5, cercleVie1)
    elif 10 < pointsDeVieInt <= 20:
        collage6 = Image.alpha_composite(collage5, cercleVie2)
    elif 20 < pointsDeVieInt <= 30:
        collage6 = Image.alpha_composite(collage5, cercleVie3)
    elif 30 < pointsDeVieInt <= 40:
        collage6 = Image.alpha_composite(collage5, cercleVie4)
    elif 40 < pointsDeVieInt <= 50:
        collage6 = Image.alpha_composite(collage5, cercleVie5)
    elif 50 < pointsDeVieInt <= 60:
        collage6 = Image.alpha_composite(collage5, cercleVie6)
    elif 60 < pointsDeVieInt <= 70:
        collage6 = Image.alpha_composite(collage5, cercleVie7)
    elif 70 < pointsDeVieInt <= 80:
        collage6 = Image.alpha_composite(collage5, cercleVie8)
    elif 80 < pointsDeVieInt <= 90:
        collage6 = Image.alpha_composite(collage5, cercleVie9)
    elif 90 < pointsDeVieInt <= 100:
        collage6 = Image.alpha_composite(collage5, cercleVie10)
    # await joueurActuel.getObjetMember().display_avatar.save(f"{pathImage}pp.png")
    # background = Image.open(f"{pathImage}pp.png").resize((167, 167))
    # background.paste(masque, (211, 883), mask=masque)
    # background.save(f"{pathImage}temp/pp.png")
    # collage6 = Image.alpha_composite(collage5, collage4)
    collage7 = Image.alpha_composite(collage6, txtPV)

    # position par défaut de tous les joueurs :
    #   pion rouge : 169, 421
    #   pion bleu: 1009, 421
    for joueur in joueurs:
        if joueur.getCouleurJoueur() == "rouge":
            collage7.paste(pionRouge, (joueur.getCoordX(), joueur.getCoordY()), pionRouge)
        elif joueur.getCouleurJoueur() == "bleu":
            collage7.paste(pionBleu, (joueur.getCoordX(), joueur.getCoordY()), pionBleu)
        elif joueur.getCouleurJoueur() == "jaune":
            collage7.paste(pionJaune, (joueur.getCoordX(), joueur.getCoordY()), pionJaune)
        elif joueur.getCouleurJoueur() == "marron":
            collage7.paste(pionMarron, (joueur.getCoordX(), joueur.getCoordY()), pionMarron)
        elif joueur.getCouleurJoueur() == "orange":
            collage7.paste(pionOrange, (joueur.getCoordX(), joueur.getCoordY()), pionOrange)
        elif joueur.getCouleurJoueur() == "rose":
            collage7.paste(pionRose, (joueur.getCoordX(), joueur.getCoordY()), pionRose)
        elif joueur.getCouleurJoueur() == "vert":
            collage7.paste(pionVert, (joueur.getCoordX(), joueur.getCoordY()), pionVert)
        elif joueur.getCouleurJoueur() == "violet":
            collage7.paste(pionViolet, (joueur.getCoordX(), joueur.getCoordY()), pionViolet)

    # Convert to RGB
    rgb_im = collage7.convert('RGBA')
    rgb_im.save(f"{pathImage}temp/jeu.png")

    couleurEmbed = joueurActuel.getDiscordCouleur()
    embed = discord.Embed(
        title="PVP 1v1",
        color=couleurEmbed
        # tour du rouge DB3A3A
        # tour du bleu 0080FF
    )

    embed.set_footer(text="Tour de {}".format(joueurActuel.getObjetMember().display_name),
                     icon_url=joueurActuel.getObjetMember().avatar)

    embed.set_image(url=f"attachment://jeu.png")

    return embed


def embedListeJoueurs(listeJoueurs: dict):
    teamA = listeJoueurs["team_a"]
    teamB = listeJoueurs["team_b"]
    capitaineA = ""
    capitaineB = ""
    listeA = ""
    listeB = ""
    if len(teamA) > 0:
        capitaineA = teamA[0].display_name
        listeA = "\n".join(["- " + pseudo.display_name for pseudo in teamA])

    if len(teamB) > 0:
        capitaineB = teamB[0].display_name
        listeB = "\n".join(["- " + pseudo.display_name for pseudo in teamB])

    embed = discord.Embed(
        title="Composition des Équipes",
        description=f"Équipe de {capitaineA}:\n{listeA}\n\nÉquipe de {capitaineB}:\n{listeB}",
        color=discord.Colour(0xDB3A3A)
        # tour du rouge DB3A3A
        # tour du bleu 0080FF
    )

    return embed


def remove_emoji(string):
    return emoji.get_emoji_regexp().sub(u'', string)


def embedPVJoueurs(joueurs: List[Joueur]):
    txtJoueur = ""
    for joueur in joueurs:
        txtJoueur += "👤 : " + remove_emoji(joueur.getObjetMember().display_name) + " **-** ❤️ : " + str(
            joueur.getPointsDeVie()) + " **-** **initiative**: " + str(joueur.getInitiative()) + "\n"

    embed = discord.Embed(
        title="PVP 1v1 - Stats",
        description=txtJoueur,
        color=discord.Colour(0xDB3A3A)
        # tour du rouge DB3A3A
        # tour du bleu 0080FF
    )
    return embed


def embedActionJoueurs(ancienneDescription: str, newDescription: str):
    embed = discord.Embed(
        title="PVP 1v1 - Action",
        description=ancienneDescription + "\n" + newDescription,
        color=discord.Colour(0xDB3A3A)
        # tour du rouge DB3A3A
        # tour du bleu 0080FF
    )
    return embed
