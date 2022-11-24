from config import *

# Définition de deux variables globales qu'on utilisera dans games.py
global tentative, dataV, nombreJoueursActuel, estCompletTeam1, estCompletTeam2, playersDiscriminator, players

load_dotenv()


def initVar():
    global tentative, dataV
    tentative = []
    dataV = []


class QuizButton(discord.ui.Button):
    """
    Classe qui représente un bouton d'interface Discord
    On subclass les boutons pour pouvoir associer une fonction de callback à chacun d'eux sans problème

    ...

    Attributes
    -----
    tabReponses : list
        Tableau contenant les réponses possibles
    rep : str
        La réponse correspondant au bouton
    bonneReponse : str
        La bonne réponse à la question
    row : int
        La ligne sur laquelle s'affiche le bouton (commence à 0)

    Methods
    -----
    callback()
        Action associée au bouton créé (dépendamment de quelle réponse est sélectionnée)
    """

    def __init__(self, tabReponses, rep, bonneReponse, row):
        """
        Parameters
        -----
        tabReponses : list
            Tableau contenant les réponses possibles
        rep : str
            La réponse correspondant au bouton
        bonneReponse : str
            La bonne réponse à la question
        row : int
            La ligne sur laquelle s'affiche le bouton (commence à 0)
        """
        self.tabReponses = tabReponses
        self.bonneReponse = bonneReponse
        self.rep = rep
        self.row = row
        # Création du bouton en lui donnant sa couleur, son texte et la ligne sur laquelle il est
        super().__init__(style=discord.ButtonStyle.blurple, label=rep, row=row)

    async def callback(self, interaction: Interaction):
        """
        Fonction appelée quand on appuie sur le bouton
        Renvoie à l'utilisateur qu'il ne peut pas réponse s'il ne joue pas la session
        Renvoie à l'utilisateur qu'il a droit à une seule tentative s'il a déjà répondu
        Renvoie à l'utilisateur qu'il a faux s'il s'est trompé
        Si tout le monde a répondu ou que quelqu'un a donné une bonne réponse, on arrête la vue qui contient le bouton
        et tous les boutons sont désactivés en rouge, la bonne réponse en vert.

        Parameters
        -----
        interaction : Interaction
            L'interaction liée au message
        """
        assert self.view is not None
        view: Quiz = self.view

        # Vérification que c'est bien un joueur de la session en cours. Si ce n'en est pas un, on lui dit
        guild = interaction.guild
        roleTeam1 = discord.utils.get(guild.roles, name=tabRole[indiceEquipe1])
        roleTeam2 = discord.utils.get(guild.roles, name=tabRole[indiceEquipe2])
        member = guild.get_member(interaction.user.id)
        if roleTeam1 not in member.roles and roleTeam2 not in member.roles:
            await interaction.response.send_message("Vous ne pouvez pas répondre ! Vous ne jouez pas cette session.",
                                                    ephemeral=True)
            return

        # Cas où le joueur a déjà répondu
        if interaction.user.display_name in tentative:
            await interaction.response.send_message("Vous avez déjà répondu ! Une seule tentative par personne.",
                                                    ephemeral=True)

        # Cas final : soit tout le monde a répondu OU le temps est écoulé soit un joueur a trouvé la bonne réponse
        elif self.rep == self.bonneReponse or (len(tentative) + 1) == view.nbJoueurs:
            if self.rep == self.bonneReponse:  # Cas où un joueur a trouvé la bonne réponse
                for i in view.children:  # Ici on désactive tous les boutons et on le met en rouge, sauf la bonne réponse qui est mise en vert
                    i.disabled = True
                    if i.rep == self.bonneReponse:
                        i.style = discord.ButtonStyle.green
                    else:
                        i.style = discord.ButtonStyle.red
                await interaction.response.edit_message(
                    view=self.view)  # On édite le message qui contient la vue avec les boutons mis à jour
                dataV.extend([True,
                              interaction.user])  # On exporte dans dataV qu'une bonne réponse a été trouvée et le nom de celui qui a la bonne réponse
                view.stop()

            else:  # Cas où tout le monde a répondu, mais il n'y a pas de bonne réponse OU que le temps est écoulé
                for i in view.children:  # Ici on désactive tous les boutons et on le met en rouge, sauf la bonne réponse qui est mise en vert
                    i.disabled = True
                    if i.rep == self.bonneReponse:
                        i.style = discord.ButtonStyle.green
                    else:
                        i.style = discord.ButtonStyle.red
                await interaction.response.edit_message(view=self.view)
                dataV.extend([False, None])  # On exporte dans dataV que personne n'a trouvé la bonne réponse
                view.stop()

        # Cas où le joueur répond faux
        else:
            await interaction.response.send_message("Mauvaise reponse ! Vous n'avez plus de tentative.", ephemeral=True)
            tentative.append(
                interaction.user.display_name)  # On ajoute son pseudo à la liste de ceux qui ont déjà répondu, pour qu'il ne puisse pas répondre à nouveau


class Quiz(discord.ui.View):
    """
    Classe qui représente une interface Discord

    ...

    Attributes
    -----
    tabReponses : list
        Tableau contenant les réponses possibles
    bonneReponse : str
        La bonne réponse à la question
    nbJoueurs : int
        Le nombre de joueurs dans la partie

    Methods
    -----
    on_error()
        Renvoyé si une erreur se produit avec l'interface
    """
    children: typing.List[QuizButton]

    def __init__(self, tabReponses, bonneReponse, nbJoueurs):
        """
        Parameters
        -----
        tabReponses : list
            Tableau contenant les réponses possibles
        bonneReponse : str
            La bonne réponse à la question
        nbJoueurs : int
            Le nombre de joueurs dans la partie
        """
        initVar()
        self.tabReponses = tabReponses
        self.bonneReponse = bonneReponse
        self.nbJoueurs = nbJoueurs

        # On définit le timeout de l'interface, autrement dit le temps maximal pour répondre à la question
        super().__init__(timeout=20.0)

        # Pour chaque proposition de réponse, on crée le bouton correspondant à la réponse puis on les ajoute à l'interface
        for i in range(len(tabReponses)):
            self.add_item(QuizButton(tabReponses, tabReponses[i], bonneReponse, i))

    async def on_error(self, error: Exception, item: Item, interaction: Interaction):
        """
        Parameters
        -----
        error : Exception
            L'exception à l'origine de l'erreur
        item : Item
            L'item Discord lié à l'erreur s'il y en a un
        interaction : Interaction
            L'interaction liée au message d'origine
        """

        await interaction.response.send_message(str(error))


def initVarJoueur():
    global nombreJoueursActuel, estCompletTeam1, estCompletTeam2, playersDiscriminator, players
    nombreJoueursActuel = 0
    estCompletTeam1 = False
    estCompletTeam2 = False
    players = [[], []]
    playersDiscriminator = []


def addPlayerName(name: str, indice: int):
    global players
    players[indice].append(name)
    return


def delPlayerName(name: str, indice: int):
    global players
    players[indice].remove(name)
    return


def addPlayerNameDiscriminator(user):
    global playersDiscriminator
    playersDiscriminator.append(["{}#{}".format(user.name, user.discriminator), 0])
    return


def delPlayerNameDiscriminator(user):
    global playersDiscriminator
    playersDiscriminator.remove(["{}#{}".format(user.name, user.discriminator), 0])
    return


def addPlayer():
    global nombreJoueursActuel
    nombreJoueursActuel += 1


def delPlayer():
    global nombreJoueursActuel
    nombreJoueursActuel -= 1


def getNumberPlayer():
    global nombreJoueursActuel
    return nombreJoueursActuel


def partieEstComplet():
    global estCompletTeam1, estCompletTeam2
    return estCompletTeam1 and estCompletTeam2


class ButtonInitJoueur(discord.ui.Button):
    """
    Classe qui représente un bouton d'interface Discord
    On subclass les boutons pour pouvoir associer une fonction de callback à chacun d'eux sans problème

    ...

    Attributes
    -----
    role : str
            role qui sera affiché dans le label
    emoji : str
        emoji associé au role

    Methods
    -----
    callback()
        Action associée au bouton créé (dépendamment de quelle réponse est sélectionnée)
    """

    def __init__(self, role, emoji, nbMaxJoueur):
        """
        Parameters
        -----
        role : str
            role qui sera affiché dans le label
        emoji : str
            emoji associé au role
        nbMaxJoueur : int
            nombre max de joueur par équipe

        """
        self.role = role
        self.nbPlayer = 0
        self.estComplet = False
        # Création du bouton en lui donnant sa couleur, son texte et la ligne sur laquelle il est
        super().__init__(style=discord.ButtonStyle.blurple, label="{} ({}/{})".format(role, self.nbPlayer, nbMaxJoueur), row=1,
                         emoji=emoji)

    async def callback(self, interaction: Interaction):
        """
        Fonction appelée quand on appuie sur le bouton
        Renvoie à l'utilisateur qu'il ne peut pas réponse s'il ne joue pas la session
        Renvoie à l'utilisateur qu'il a droit à une seule tentative s'il a déjà répondu
        Renvoie à l'utilisateur qu'il a faux s'il s'est trompé
        Si tout le monde a répondu ou que quelqu'un a donné une bonne réponse, on arrête la vue qui contient le bouton
        et tous les boutons sont désactivés en rouge, la bonne réponse en vert.

        Parameters
        -----
        interaction : Interaction
            L'interaction liée au message
        """
        global nombreJoueursActuel, estCompletTeam1, estCompletTeam2, playersDiscriminator, players
        assert self.view is not None
        view: ViewInitJoueur = self.view

        # Vérification que c'est bien un joueur de la session en cours. Si ce n'en est pas un, on lui dit
        guild = interaction.guild
        roleTeam1 = discord.utils.get(guild.roles, name=tabRole[indiceEquipe1])
        roleTeam2 = discord.utils.get(guild.roles, name=tabRole[indiceEquipe2])
        member = guild.get_member(interaction.user.id)
        # await interaction.channel.send_message("{} a cliqué son surnom: {}".format(interaction.user, interaction.user.display_name))
        if member is not None:
            """# s'il a déjà le role on va le faire swip de rôle
            if roleTeam1 in member.roles or roleTeam2 in member.roles:"""
            if roleTeam1 in member.roles and not self.estComplet:
                if self.role == roleTeam1.name:  # s'il a recliqué sur le meme bouton que son rôle actuel
                    await interaction.response.send_message("Vous ne pouvez pas reprendre le même rôle !",
                                                            ephemeral=True)
                    return
                elif self.nbPlayer < view.getNbJoueur():
                    for i in view.children:  # Ici on désactive tous les boutons et on le met en rouge, sauf la bonne réponse qui est mise en vert
                        if roleTeam1.name in i.label:
                            i.nbPlayer -= 1
                            i.label = "{} ({}/{})".format(roleTeam1.name, i.nbPlayer, view.nbJoueur)
                            i.estComplet = False
                            estCompletTeam1 = False
                        else:
                            i.nbPlayer += 1
                            i.label = "{} ({}/{})".format(roleTeam2.name, i.nbPlayer, view.nbJoueur)
                            if i.nbPlayer == view.getNbJoueur():
                                i.estComplet = True
                                estCompletTeam2 = True
                    await interaction.response.edit_message(view=self.view)
                    await member.remove_roles(roleTeam1, reason=None, atomic=True)
                    await member.add_roles(roleTeam2)
                    addPlayerName(interaction.user.display_name, 1)
                    addPlayerNameDiscriminator(interaction.user)
                    delPlayerName(interaction.user.display_name, 0)
                    delPlayerNameDiscriminator(interaction.user)
                    if partieEstComplet():
                        view.stop()
                    return
                else:
                    self.estComplet = True
                    estCompletTeam1 = True
                    await interaction.response.send_message(
                        "Il ne reste plus de place dans l'équipe {} !".format(roleTeam2.name), ephemeral=True)
                    return

            elif roleTeam2 in member.roles and not self.estComplet:
                if self.role == roleTeam2.name:  # s'il a recliqué sur le meme bouton que son rôle actuel
                    await interaction.response.send_message("Vous ne pouvez pas reprendre le même rôle !",
                                                            ephemeral=True)
                    return
                elif self.nbPlayer < view.getNbJoueur():
                    for i in view.children:  # Ici on désactive tous les boutons et on le met en rouge, sauf la bonne réponse qui est mise en vert
                        if roleTeam2.name in i.label:
                            i.nbPlayer -= 1
                            i.label = "{} ({}/{})".format(roleTeam2.name, i.nbPlayer, view.nbJoueur)
                            i.estComplet = False
                            estCompletTeam2 = False
                        else:
                            i.nbPlayer += 1
                            i.label = "{} ({}/{})".format(roleTeam1.name, i.nbPlayer, view.nbJoueur)
                            if i.nbPlayer == view.getNbJoueur():
                                i.estComplet = True
                                estCompletTeam1 = True
                    await interaction.response.edit_message(view=self.view)
                    await member.remove_roles(roleTeam2, reason=None, atomic=True)
                    await member.add_roles(roleTeam1)
                    addPlayerName(interaction.user.display_name, 0)
                    addPlayerNameDiscriminator(interaction.user)
                    delPlayerName(interaction.user.display_name, 1)
                    delPlayerNameDiscriminator(interaction.user)
                    if partieEstComplet():
                        view.stop()
                    return
                else:
                    self.estComplet = True
                    estCompletTeam2 = True
                    await interaction.response.send_message(
                        "Il ne reste plus de place dans l'équipe {} !".format(roleTeam1.name), ephemeral=True)
                    return
            elif self.role == roleTeam1.name and not self.estComplet:
                addPlayer()
                self.nbPlayer += 1
                if self.nbPlayer == view.getNbJoueur():
                    self.estComplet = True
                    estCompletTeam1 = True

                self.label = "{} ({}/{})".format(roleTeam1.name, self.nbPlayer, view.nbJoueur)
                await member.add_roles(roleTeam1)
                await interaction.response.edit_message(view=self.view)
                addPlayerName(interaction.user.display_name, 0)
                addPlayerNameDiscriminator(interaction.user)
                if partieEstComplet():
                    view.stop()

            elif self.role == roleTeam2.name and not self.estComplet:
                addPlayer()
                self.nbPlayer += 1
                if self.nbPlayer == view.getNbJoueur():
                    self.estComplet = True
                    estCompletTeam2 = True
                self.label = "{} ({}/{})".format(roleTeam2.name, self.nbPlayer, view.nbJoueur)
                await member.add_roles(roleTeam2)
                await interaction.response.edit_message(view=self.view)
                addPlayerName(interaction.user.display_name, 1)
                addPlayerNameDiscriminator(interaction.user)
                if partieEstComplet():
                    view.stop()

            elif self.estComplet and not partieEstComplet():
                await interaction.response.send_message(
                    "Il ne reste plus de place dans l'équipe {} !".format(self.role), ephemeral=True)
            else:
                await interaction.response.send_message("Il ne reste plus de place dans les deux équipes !",
                                                        ephemeral=True)
                view.stop()
                return
        else:
            print("Member Not found")


class ViewInitJoueur(discord.ui.View):
    """
    Classe qui représente une interface Discord

    ...

    Attributes
    -----
    tabRoles : list
            Tableau contenant les roles possibles [["role1", "emoji1"], ["role2", "emoji2"]]
    nbJoueur : str
        La bonne réponse à la question

    Methods
    -----
    on_error()
        Renvoyé si une erreur se produit avec l'interface
    """
    children: typing.List[ButtonInitJoueur]

    def __init__(self, tabRoles, nbJoueur=0):
        """
        Parameters
        -----
        tabRoles : list
            Tableau contenant les roles possibles [["role1", "emoji1"], ["role2", "emoji2"]]
        nbJoueur : int
            La bonne réponse à la question
        """
        initVarJoueur()
        self.nbJoueur = nbJoueur
        self.tabRole = tabRole

        # On définit le timeout de l'interface, autrement dit le temps maximal pour répondre à la question
        super().__init__()

        # Pour chaque proposition de réponse, on crée le bouton correspondant à la réponse puis on les ajoute à l'interface
        for i in range(len(tabRoles)):
            self.add_item(ButtonInitJoueur(tabRoles[i][0], tabRoles[i][1], nbJoueur))

    def getNbJoueur(self):
        return self.nbJoueur

    async def on_error(self, error: Exception, item: Item, interaction: Interaction):
        """
        Parameters
        -----
        error : Exception
            L'exception à l'origine de l'erreur
        item : Item
            L'item Discord lié à l'erreur s'il y en a un
        interaction : Interaction
            L'interaction liée au message d'origine
        """

        await interaction.response.send_message(str(error))
