from config import *

load_dotenv()

global channel
IDCHANNEL = int(os.getenv('IDCHANNEL'))


# * AFFICHAGE JEU ------------------------------------------------------------------- #
async def printPlayer(tabJ: list):
    """ Méthode d'affichage de l'ensemble des joueurs

        Parameters
        ----------
        tabJ : list
            tableau contenant le nom de tous les joueurs

    """
    global channel
    channel = client.get_channel(IDCHANNEL)
    team1 = '\n'.join(["- `" + player + "`" for player in tabJ[indiceEquipe1]])
    team2 = '\n'.join(["- `" + player + "`" for player in tabJ[indiceEquipe2]])
    embed = discord.Embed(
        title=titreDBV,
        description="{}{}{} {}\n{}\n\n{}{} {}\n{}\n\n🔸 Question à choix multiple\n\n🔹 Question simple".format(
            debutPartieDBV, carreBlanc, tabEmoji[indiceEquipe1], tabRoleBold[
                indiceEquipe1], team1, carreBlanc, tabEmoji[indiceEquipe2], tabRoleBold[indiceEquipe2], team2),
        color=colorEmbedWhiteDBV
    )
    await channel.send(embed=embed)


async def printWinners(pointsTeam1: int, pointsTeam2: int):
    """ Méthode d'affichage du score final.
        Affiche le resultat dans un embed

        Parameters
        ---------
        pointsTeam1 : int
            représente les points de l'équipe 1
        pointsTeam2 : int
            représente les points de l'équipe 2

    """
    descriptionWinners = "🏆  Vainqueur\n\n"
    if pointsTeam2 > pointsTeam1:
        vainqueurs = "{} `{} points` {}".format(foxyBoutonBlanc, pointsTeam2, medaillePremier)
        perdants = "{} `{} points` {}".format(mugiBoutonBlanc, pointsTeam1, medailleSecond)
    else:
        vainqueurs = "{} `{} points` {}".format(mugiBoutonBlanc, pointsTeam1, medaillePremier)
        perdants = "{} `{} points` {}".format(foxyBoutonBlanc, pointsTeam2, medailleSecond)

    embed = discord.Embed(
        title=titreDBV,
        description="{}{}\n\n{}".format(descriptionWinners, vainqueurs, perdants),
        color=colorEmbedWhiteDBV
    )
    await channel.send(embed=embed)
    pass


async def printScore(numEpreuve: int, pointsTeam1: int, pointsTeam2: int):
    """ Méthode d'affichage du score actuel pour les equipes.

        Parameters
        ----------
        numEpreuve : int
            numéro de l'épreuve en cours
        pointsTeam1 : int
            représente les points de l'équipe 1
        pointsTeam2 : int
            représente les points de l'équipe 2

    """

    descriptionScore = "{}\n\n{}\n{}\n`Score :{}`\n\n{}\n{}\n`Score :{}`\n".format(tabTextEpreuve[numEpreuve],
                                                                                   tabEmoji[indiceEquipe1],
                                                                                   tabRoleBold[indiceEquipe1],
                                                                                   pointsTeam1, tabEmoji[indiceEquipe2],
                                                                                   tabRoleBold[indiceEquipe2],
                                                                                   pointsTeam2)
    embed = discord.Embed(
        title=titreDBV,
        description=descriptionScore,
        color=colorEmbedWhiteDBV
    )
    await channel.send(embed=embed)
    pass


def traitementReponses(stringReponses: str):
    """ Méthode formattage du tableau de réponse(s), on retourne uniquement la première réponse parmi toutes celles disponible

        Parameters
        ----------
        stringReponses : str
            réponse(s) sous forme de string que l'on va transforme en [str] grâce à un séparateur

        Returns
        -------
        string
            chaine des réponses
    """
    reps = stringReponses.split("/")
    premiereReponse = reps[0]
    return premiereReponse


async def nextQuestion(typeQ=None):
    """ Methode d'attente entre 2 questions."""
    await asyncio.sleep(delaiEntreQuestions)
    await printEmbedNextQuestion(typeQ)
    await asyncio.sleep(delaiDebutPartieCinq)


async def nextEpreuve(nomEpreuve: str):
    """ Methode d'attente entre 2 épreuves.

        Parameters
        ----------
        nomEpreuve : str
            nom de la prochaine épreuve
    """
    await asyncio.sleep(delaiEntreEpreuves)
    await printEmbedNextEpreuve(nomEpreuve)
    await asyncio.sleep(delaiEntreEpreuves)


async def printEmbedNextEpreuve(nomEpreuve: str):
    """ Methode de construction de l'embed d'affichage de la prochaine épreuve.

        Parameters
        ----------
        nomEpreuve : str
            nom de la prochaine épreuve
    """
    embed = discord.Embed(
        title="Epreuve suivante",
        description="▫️ {}".format(nomEpreuve),
        color=discord.Color.blue()
    )
    await channel.send(embed=embed)


async def printEmbedNextQuestion(typeQ=None):
    """ Methode de construction de l'embed d'affichage de la prochaine question."""
    embed = discord.Embed(
        title="Prochaine question",
        color=colorEmbedWhiteDBV
    )
    if typeQ:
        embed.description = f"{'🔹 Question réponse simple' if typeQ == '1' else '🔸  Question choix multiples'}"
    await channel.send(embed=embed)


async def printEmbedFirstQuestion(typeQ=None):
    """ Methode de construction de l'embed d'affichage de la prochaine question."""
    embed = discord.Embed(
        title="Première question",
        description=f"{'🔹 Question réponse simple' if typeQ == '1' else '🔸  Question choix multiples'}",
        color=colorEmbedWhiteDBV
    )
    await channel.send(embed=embed)


async def printEmbedDebutPartie():
    """ Methode de construction de l'embed d'affichage du début de la partie."""
    embed = discord.Embed(
        title="Première épreuve",
        description="{}{}".format(carreBlanc, nomEpreuve1),
        color=discord.Color.blue()
    )
    await channel.send(embed=embed)


# * AFFICHAGE JEU QUIZ ------------------------------------------------------------------- #

async def affichage(numJeu: int, numQuestion: int, nomEpreuve: str, typeQ):
    """ Méthode d'affichage du texte "Question suivante" ou "Epreuve suivante"

        Parameters
        ----------
        numJeu : int
            numéro du jeu actuel
        numQuestion : int
            numéro de la question acutelle
        nomEpreuve : str
            nom de l'epreuve
        typeQ :
            type de question 1: choix multiple
                             2 : QCM

        Returns
        -------
        int
            nouvel indice du tableau de question
    """
    if numQuestion != (nbQuestions * 2) - 1:
        await nextQuestion(typeQ)
    elif numJeu != (len(tabEpreuves) - 1):
        await nextEpreuve(nomEpreuve)
    numQuestion += 1
    return numQuestion


async def printEmbedTimeout(answer: str):
    """ Methode de construction de l'embed d'affichage du délai ecoulé.

        Parameters
        ----------
        answer : str
           liste des réponses formattées (reponse1/reponse2/reponse3/.../reponseX)
    """
    reponse = traitementReponses(answer)
    embed = discord.Embed(
        title=timeout,
        description="{}`{}`".format(reponseText, reponse),
        color=colorEmbedTimeout
    )
    await channel.send(embed=embed)


async def printEmbedQuestions(couleurLosange: str, question: str):
    """ Methode de construction de l'embed d'affichage de la question actuelle.

        Parameters
        ----------
        couleurLosange : str
            couleur du losange
        question : str
            question actuelle à faire afficher

    """
    embed = discord.Embed(
        title="{}{}".format(couleurLosange, question),
        color=colorEmbedWhiteDBV
    )
    await channel.send(embed=embed)


async def printEmbedBonneReponse(answer: str, messageSender: str, pointsTeam1: int, pointsTeam2: int, valTeam1: str,
                                 valTeam2: str):
    """ Methode de construction de l'embed d'affichage de la bonne réponse.

        Parameters
        ----------
        answer : str
            bonne réponse
        messageSender : str
            tuple sur l'expéditeur du message de la bonne réponse
        pointsTeam1 : int
            points de l'equipe 1
        pointsTeam2 : int
            points de l'equipe 2
        valTeam1 : str
            string pour gerer l'affichage
        valTeam2 : str
            string pour gerer l'affichage
    """

    reponse = traitementReponses(answer)
    embed = discord.Embed(
        title="{}{}{}\n\n".format(pointVert, messageSender, textGoodAnswer),
        description="{}`{}`\n\n{} {} {}{}{} points```\n\n{} {} {}{}{} points```\n\n".format(reponseText, reponse,
                                                                                            carreBlanc,
                                                                                            tabEmoji[indiceEquipe1],
                                                                                            tabRoleBold[indiceEquipe1],
                                                                                            valTeam1, pointsTeam1,
                                                                                            carreBlanc,
                                                                                            tabEmoji[indiceEquipe2],
                                                                                            tabRoleBold[indiceEquipe2],
                                                                                            valTeam2, pointsTeam2),

        color=colorEmbedGoodAnswer,
    )
    await channel.send(embed=embed)


async def printClue(reponses):
    """ Methode d'affichage des indices du jeu.
        Si le mot fait 1 caractère, on n'affiche rien
        si le mot fait entre 2 et 3 caractères on affiche un seul caractère
        Si le mot fait entre 4 et 6 caractères, on affiche un deux caractere pr l'indice
        si le mot fait entre et entre 7 et 9 caractères, on affiche trois caractères
        sinon si plus de 9 caractères, on affiche quatre caractères

        Parameters
        ---------
        reponses : str
            liste des réponses formattées (reponse1/reponse2/reponse3/.../reponseX)

        Returns
        -------
        indice : str
            le mot qui a été transformé sous forme d'un indice
        rep : str
            la bonne réponse sans transformation
    """
    mots = reponses.split("/")
    random.seed(datetime.now())
    random.shuffle(mots)
    indice = mots[0]
    rep = mots[0]
    tailleMot = len(indice)

    if tailleMot < 2:
        return

    listMot = list(indice)
    espace = " "
    underscore = "_"
    charArray = [",", "\"", "'", ":", "(", ")", "."]  # caractères que l'on va pas transformer en underscore
    car1, car2, car3, car4 = 1, 1, 1, 1

    if 2 <= tailleMot <= 3:
        car1 = random.randrange(0, len(listMot))
        for i in range(len(listMot)):  # on transforme tout sauf la lettre selectionné en underscore
            if listMot[i].isspace():
                listMot[i] = espace
            elif i != car1 and listMot[i] not in charArray:
                listMot[i] = underscore
        indice = "".join(listMot)

    elif 4 <= tailleMot <= 7:
        while car1 == car2:  # on évite de choisir 2 fois la meme lettres à faire afficher en indice
            car1 = random.randrange(0, len(listMot))
            car2 = random.randrange(0, len(listMot))
        for i in range(len(listMot)):  # on transforme tout sauf les 2 lettres selectionnés en underscore
            if listMot[i].isspace():
                listMot[i] = espace
            elif i != car1 and i != car2 and listMot[i] not in charArray:
                listMot[i] = underscore
        indice = "".join(listMot)
    elif 7 <= tailleMot <= 9:
        while car1 == car2 and car2 == car3:  # on évite de choisir 3 fois la meme lettre à faire afficher en indice
            car1 = random.randrange(0, len(listMot))
            car2 = random.randrange(0, len(listMot))
            car3 = random.randrange(0, len(listMot))
        for i in range(len(listMot)):  # on transforme tout sauf les 2 lettres selectionnés en underscore
            if listMot[i].isspace():
                listMot[i] = espace
            elif i != car1 and i != car2 and i != car3 and listMot[i] not in charArray:
                listMot[i] = underscore
        indice = "".join(listMot)
    else:
        while car1 == car2 and car2 == car3 and car3 == car4:  # on évite de choisir 3 fois la meme lettre à faire afficher en indice
            car1 = random.randrange(0, len(listMot))
            car2 = random.randrange(0, len(listMot))
            car3 = random.randrange(0, len(listMot))
            car4 = random.randrange(0, len(listMot))
        for i in range(len(listMot)):  # on transforme tout sauf les 2 lettres selectionnés en underscore
            if listMot[i].isspace():
                listMot[i] = espace
            elif i != car1 and i != car2 and i != car3 and i != car4 and listMot[i] not in charArray:
                listMot[i] = underscore
        indice = "".join(listMot)

    embed = discord.Embed(
        title="💡 Indice : `{}`".format(indice),
        color=discord.Color.from_rgb(255, 216, 63)
    )
    await channel.send(embed=embed)

    return indice, rep


async def printEmbedImageQuiz(couleurLosange: str, question: str, fichier: str, dossier: str):
    """ Methode de construction de l'embed d'affichage de la question lors d'une question avec une image

        Parameters
        ----------
        couleurLosange : str
            couleur du losange
        question : str
            question
        fichier : str
            nom du fichier à faire afficher dans l'embed
        dossier : str
            nom du dossier contenant `fichier`

        Returns
        -------
        msg : Message
            pointeur sur le message envoyé
    """
    embed = discord.Embed(
        title="{}{}".format(couleurLosange, question),
        color=colorEmbedWhiteDBV
    )
    embed.set_image(url="attachment://" + fichier)
    msg = await channel.send(file=discord.File(dossier + "/" + fichier), embed=embed)
    return msg


# * AFFICHAGE JEU QUIZ (BOUTONS)  ------------------------------------------------------------------- #

async def printEmbedNoAnswer(answer: str):
    """ Methode de construction de l'embed d'affichage de la bonne réponse lors d'une question à choix multiple (boutons),
        lorsque le délai est ecoulé

        Parameters
        ----------
        answer : str
            liste des réponses formattées (reponse1/reponse2/reponse3/.../reponseX)
    """
    reponse = traitementReponses(answer)
    embed = discord.Embed(
        title=noAns,
        description="{}`{}`".format(reponseText, reponse),
        color=colorEmbedTimeout
    )
    await channel.send(embed=embed)


# * AFFICHAGE JEU IMAGE ------------------------------------------------------------------- #

async def printClueImage(reponses: list):
    """ Methode d'affichage des indices du jeu.
        Si le mot fait 1 caractère, on n'affiche rien
        si le mot fait entre 2 et 3 caractères on affiche un seul caractère
        Si le mot fait entre 4 et 6 caractères, on affiche un deux caractere pr l'indice
        si le mot fait entre et entre 7 et 9 caractères, on affiche trois caractères
        sinon si plus de 9 caractères, on affiche quatre caractères

        Parameters
        ---------
        reponses : [str]
            liste des réponses [reponse_1, reponse2,reponse_3, ..., reponseX]

        Returns
        -------
        indice : str
            le mot qui a été transformé sous forme d'un indice
        rep : str
            la bonne réponse sans transformation
    """

    random.seed(datetime.now())
    random.shuffle(reponses)
    if "_" in reponses[0]:
        indice = reponses[0].replace("_", " ")
    else:
        indice = reponses[0]

    rep = indice
    tailleMot = len(indice)

    if tailleMot < 2:
        return

    listMot = list(indice)
    espace = " "
    underscore = "_"
    charArray = [",", "\"", "'", ":", "(", ")", "."]  # caractères que l'on va pas transformer en underscore
    car1, car2, car3, car4 = 1, 1, 1, 1

    if 2 <= tailleMot <= 3:
        car1 = random.randrange(0, len(listMot))
        for i in range(len(listMot)):  # on transforme tout sauf la lettre selectionné en underscore
            if listMot[i].isspace():
                listMot[i] = espace
            elif i != car1 and listMot[i] not in charArray:
                listMot[i] = underscore
        indice = "".join(listMot)

    elif 4 <= tailleMot <= 7:
        while car1 == car2:  # on évite de choisir 2 fois la meme lettres à faire afficher en indice
            car1 = random.randrange(0, len(listMot))
            car2 = random.randrange(0, len(listMot))
        for i in range(len(listMot)):  # on transforme tout sauf les 2 lettres selectionnés en underscore
            if listMot[i].isspace():
                listMot[i] = espace
            elif i != car1 and i != car2 and listMot[i] not in charArray:
                listMot[i] = underscore
        indice = "".join(listMot)
    elif 7 <= tailleMot <= 9:
        while car1 == car2 and car2 == car3:  # on évite de choisir 3 fois la meme lettre à faire afficher en indice
            car1 = random.randrange(0, len(listMot))
            car2 = random.randrange(0, len(listMot))
            car3 = random.randrange(0, len(listMot))
        for i in range(len(listMot)):  # on transforme tout sauf les 2 lettres selectionnés en underscore
            if listMot[i].isspace():
                listMot[i] = espace
            elif i != car1 and i != car2 and i != car3 and listMot[i] not in charArray:
                listMot[i] = underscore
        indice = "".join(listMot)
    else:
        while car1 == car2 and car2 == car3 and car3 == car4:  # on évite de choisir 3 fois la meme lettre à faire afficher en indice
            car1 = random.randrange(0, len(listMot))
            car2 = random.randrange(0, len(listMot))
            car3 = random.randrange(0, len(listMot))
            car4 = random.randrange(0, len(listMot))
        for i in range(len(listMot)):  # on transforme tout sauf les 2 lettres selectionnés en underscore
            if listMot[i].isspace():
                listMot[i] = espace
            elif i != car1 and i != car2 and i != car3 and i != car4 and listMot[i] not in charArray:
                listMot[i] = underscore
        indice = "".join(listMot)

    embed = discord.Embed(
        title="💡 Indice : `{}`".format(indice),
        color=discord.Color.from_rgb(255, 216, 63)
    )
    await channel.send(embed=embed)

    return indice, rep


async def printEmbedBonneReponseImage(fichier: str, reponses: list, messageSender: any, dossier: str, pointsTeam1: int,
                                      pointsTeam2: int, valTeam1: str, valTeam2: str):
    """ Methode de construction de l'embed d'affichage de la bonne réponse lors d'une question avec une image


        Parameters
        ----------
        fichier : str
            nom du fichier à faire afficher dans l'embed
        reponses : list
            tableau des réponses pour l'image
        messageSender :
            tuple sur l'expéditeur du message de la bonne réponse
        dossier : str
            nom du dossier contenant `fichier`
        pointsTeam1 : int
            points de l'equipe 1
        pointsTeam2 : int
            points de l'equipe 2
        valTeam1 : str
            string pour gerer l'affichage
        valTeam2 : str
            string pour gerer l'affichage
    """
    if "_" in reponses[0]:
        reponse = reponses[0].replace("_", " ")
    else:
        reponse = reponses[0]

    embed = discord.Embed(
        title="{}{}{}\n\n".format(pointVert, messageSender.author.display_name, textGoodAnswer),
        description="{}`{} ({})`\n\n{} {} {}{}{} points```\n\n{} {} {}{}{} points```\n\n".format(reponseText, reponse,
                                                                                                 dossier,
                                                                                                 carreBlanc,
                                                                                                 tabEmoji[
                                                                                                     indiceEquipe1],
                                                                                                 tabRoleBold[
                                                                                                     indiceEquipe1],
                                                                                                 valTeam1, pointsTeam1,
                                                                                                 carreBlanc,
                                                                                                 tabEmoji[
                                                                                                     indiceEquipe2],
                                                                                                 tabRoleBold[
                                                                                                     indiceEquipe2],
                                                                                                 valTeam2, pointsTeam2),
        color=colorEmbedGoodAnswer,
    )
    embed.set_image(url="attachment://" + fichier)
    await channel.send(file=discord.File(path + "/" + dossier + "/" + fichier), embed=embed)


async def printEmbedImage(fichier: str, dossier: str):
    """ Methode de construction de l'embed d'affichage de la question lors d'une question avec une image

        Parameters
        ----------
        fichier : str
            nom du fichier à faire afficher dans l'embed
        dossier : str
            nom du dossier contenant `fichier`
    """
    embed = discord.Embed(
        title="{}Qui est ce personnage ?".format(carreBlanc),
        color=colorEmbedWhiteDBV
    )
    embed.set_image(url="attachment://" + fichier)
    await channel.send(file=discord.File(pathFlou + "/" + dossier + "/" + fichier), embed=embed)


async def printEmbedTimeoutImage(fichier: str, reponse: str, dossier: str):
    """ Methode de construction de l'embed d'affichage de la bonne réponse lors d'une question avec une image,
        lorsque le délai est ecoulé

        Parameters
        ----------
        fichier : str
            nom du fichier à faire afficher dans l'embed
        reponse : list
            ensemble des réponses pour l'image
        dossier : str
            nom du dossier contenant `fichier`
    """
    """if "_" in reponses[0]:
        reponse = reponses[0].replace("_", " ")
    else:
        reponse = reponses[0]"""
    embed = discord.Embed(
        title=timeout,
        description="{}`{} ({})`".format(reponseText, reponse, dossier),
        color=colorEmbedTimeout
    )
    embed.set_image(url="attachment://" + fichier)
    await channel.send(file=discord.File(path + "/" + dossier + "/" + fichier), embed=embed)
