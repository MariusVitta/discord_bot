from affichage import *
from config import *
import boutons

load_dotenv()

IDCHANNEL = int(os.getenv('IDCHANNEL'))
GUILD = str(os.getenv('DISCORD_GUILD'))
global pointsTeam2, pointsTeam1, numeroJeu, valTeam1, channelMessage, valTeam2, tabPlayer, questionActuelle, reponsesActuelles, tabPlayerDiscriminator, ctxExecution, partieEnCours, trace


def initVar():
    """ Méthode d'initialisation des variables globales."""
    global pointsTeam2, pointsTeam1, numeroJeu, valTeam1, valTeam2, channelMessage, questionActuelle, reponsesActuelles
    pointsTeam2, pointsTeam1, numeroJeu = 0, 0, 0
    valTeam1, valTeam2 = "", ""
    channelMessage = client.get_channel(IDCHANNEL)
    questionActuelle = []
    reponsesActuelles = ""


async def calculPoints(messageAuthor, tabJoueurDiscriminator: [str]):
    """ Méthode de mise à jour du score actuel.

        Parameters
        ----------
        messageAuthor : Message
            instance de Message
        tabJoueurDiscriminator : [str]
            tableau des joueurs avec leurs discriminants, nous sert essentiellement pour sauvegarder les points des joueurs en fin de partie
    """
    global pointsTeam2, pointsTeam1, valTeam1, valTeam2, tabPlayerDiscriminator
    tabPlayerDiscriminator = tabJoueurDiscriminator
    if tabRole[indiceEquipe1].lower() in [y.name.lower() for y in messageAuthor.roles]:
        pointsTeam1 += 1
        valTeam1 = " :```diff\n+ "
        valTeam2 = " :``` "
    else:
        pointsTeam2 += 1
        valTeam1 = " :``` "
        valTeam2 = " :```diff\n+ "
    joueurDiscriminator = messageAuthor.name + "#" + messageAuthor.discriminator
    for joueur in tabPlayerDiscriminator:
        # si le joueur avait déjà un score auparavant, on va mettre à jour son score simplement
        if joueur[0] == joueurDiscriminator:
            joueur[1] += 1
    return


def traitementImage(fichier: str, valeurResize: int, dossier: str):
    """ Methode de traitement de l'image.
        Cette méthode va resize l'image afin de lui donner un effet pixelisé
        on va créer une nouvelle image qui se trouvera dans le dossier `magesFloues`

        Parameters
        ----------
        fichier :str
            nom de l'image que l'on veut pixeliser
        valeurResize :int
            taille du resize de l'image
        dossier :str
            dossier ou se trouve l'image

        Returns
        -------
        str
            nom du fichier modifié
    """
    word = RandomWords()
    word = word.get_random_word()
    while word is None:
        word = RandomWords()
        word = word.get_random_word()
    tabNomFichier = os.path.splitext(fichier)
    extension = tabNomFichier[1]
    if os.path.exists("{}/{}/{}".format(path, dossier, fichier)):
        img = Image.open(path + "/" + dossier + "/" + fichier)
        imgSmall = img.resize((valeurResize, valeurResize), resample=Image.BILINEAR)
        result = imgSmall.resize(img.size, Image.NEAREST)
        if not os.path.exists(pathFlou + "/" + dossier):
            os.makedirs(pathFlou + "/" + dossier, mode=0o777,
                        exist_ok=False)  # création du dossier s'il n'existe pas encore
        result.save("{}/{}/{}".format(pathFlou, dossier, word + extension))
    else:
        print("l'image {}/{}/{} n'existe pas".format(path, dossier, fichier))

    return word + extension


def selectManga():
    """ Methode de selectin d'un manga dans la liste des mangas disponibles"""
    mangas = listeMangas
    # Random number with system time
    random.seed(datetime.now())
    random.shuffle(mangas)
    return mangas[0]


async def jeuImage(numJeu: int, tabJDiscriminator: [str]):
    """ Méthode principale du jeu version image.

        Parameters
        ----------
        numJeu : int
            Numéro du jeu actuel
        tabJDiscriminator : [str]
            tableaux des joueurs avec leurs discriminants
    """
    global numeroJeu, pointsTeam1, pointsTeam2, valTeam1, valTeam2, tabPlayerDiscriminator
    tabPlayerDiscriminator = tabJDiscriminator
    numeroJeu = numJeu
    tabBonnesReponse = []
    imagesVues = []
    reponse = ""

    def traitementNom(nomFichier: str):
        tempName = os.path.splitext(nomFichier)
        tabRep = tempName[0].split("-")
        return tabRep

    def checkMessage(m):
        """Méthode de verification de la validité d'une réponse.
            1) on va verifier que le nom que l'on cherche n'est pas dans la chaine → :
                - Sabo ✅
                - aSabo ❌ Pas validé, car le mot forme aSabo
                - a Sabo → ✅ Car le bot prend en compte seulement le "Sabo" et pas les caractères qui sont devant et derrière lorsqu'il y a un espace

            2) on va verifier qu'il y a qu'un seul caractère de faux dans la réponse
                - Lufyf au lieu de Luffy ❌ Pas validé, car ne dépasse pas 7 caractères
                - Sentomaur au lieu de Sentomaru ✅ Validé, car dépasse 7 caractères

            3) dans tous les autres cas on retourne False

            Parameters
            ----------
            m : Message
                instance de Message

            Returns
            -------
            bool
                True si la réponse donnée est bonne et si le message a été envoyé dans le bon salon
        """
        guild = discord.utils.find(lambda g: g.name == GUILD, client.guilds)
        roleTeam1 = discord.utils.get(guild.roles, name=tabRole[0])
        roleTeam2 = discord.utils.get(guild.roles, name=tabRole[1])

        if m.channel != channelMessage:
            return False
        # on empêche aux non-joueurs de jouer simplement
        if roleTeam1 not in m.author.roles and roleTeam2 not in m.author.roles:
            return False

        trace.saveTraceAnswer(m.author.name, m.content)

        # 1)
        def contains_word(userAnswer, toGuess):
            return (' ' + userAnswer + ' ') in (' ' + toGuess + ' ')

        for rep in tabBonnesReponse:
            if "_" in rep:  # on va différencier les réponses ou un ensemble de mot ne peuvent pas être séparé des autres
                rep = rep.replace("_", " ").lower()
                if contains_word(unidecode(rep.lower()), unidecode(m.content.lower())):
                    return True
            else:
                for word in m.content.split(" "):
                    if unidecode(rep.lower()) in unidecode(word.lower()):
                        return True
        return False

    for numQuestion in range(nbQuestions):

        # récuperation d'un manga différent à chaque tour de jeu
        dossier = selectManga()
        if os.path.exists("{}/{}".format(path, dossier)):
            files = os.listdir(path + "/" + dossier)
            # Random number with system time
            random.seed(datetime.now())
            random.shuffle(files)
            file = files[0]

            if file in imagesVues:
                while file in imagesVues:
                    dossier = selectManga()
                    files = os.listdir(path + "/" + dossier)
                    # Random number with system time
                    random.seed(datetime.now())
                    random.shuffle(files)
                    file = files[0]
            """dossier = "Hunter x Hunter"
            file = "Knuckle_Bine-Knuckle.png"""
            imagesVues.append(file)
            trace.saveTraceQuestionsImage(numQuestion, file)

            # récuperation du bon nom de l'image
            tabBonnesReponse = traitementNom(file)
            nomImageOriginale = file

            # pixelisation de l'image
            file = traitementImage(nomImageOriginale, tabTailleResize[0], dossier)
            await printEmbedImage(file, dossier)

            """# récuperation du bon nom de l'image
            tabBonnesReponse = traitementNom(file)"""

            for valeurResize in tabTailleResize[1:]:  # on exclut le premier item, car on l'a deja traité
                # attente d'un message des joueurs puis verification de la réponse à l'aide la méthode de verification
                try:
                    message = await client.wait_for("message", timeout=delaiQuestionsImages / len(tabTailleResize),
                                                    check=checkMessage)
                # si le timeout est dépassé, on envoie un message embed contenant la bonne réponse
                except asyncio.TimeoutError:
                    if valeurResize != tabTailleResize[-1] and valeurResize != -1:
                        file = traitementImage(nomImageOriginale, valeurResize, dossier)
                        await printEmbedImage(file, dossier)
                    elif valeurResize == -1:
                        indice, reponse = await printClueImage(tabBonnesReponse)
                        trace.saveTraceIndice(indice)
                    else:  # on est arrivé au bout du tableau et on affiche la bonne réponse
                        await printEmbedTimeoutImage(nomImageOriginale, reponse, dossier)

                        if numQuestion != nbQuestions - 1:
                            await nextQuestion()
                        break

                # sinon on met à jour les points de l'equipe qui a marqué un point,
                # on affiche l'auteur du bon message dans un
                # embed et les points des equipes
                else:
                    await calculPoints(message.author, tabPlayerDiscriminator)
                    reponse = tabBonnesReponse
                    await printEmbedBonneReponseImage(nomImageOriginale, reponse, message, dossier, pointsTeam1, pointsTeam2,
                                                      valTeam1,
                                                      valTeam2)
                    await asyncio.sleep(delaiQuestionsImages / len(tabTailleResize))
                    if numQuestion != nbQuestions - 1:
                        await nextQuestion()
                    break
        else:
            print("le dossier {}/{} n'existe pas".format(path, dossier))

    # await nextEpreuve(nomEpreuve3)
    return


def selectQuestion():
    """ Methode de selection d'un manga dans la liste des mangas disponibles """

    global data, question, tabRep, typeQuestion, imageQuiz
    fichierQuestions = ""
    if os.path.exists("{}".format(DossierQuestion)):
        questions = os.listdir(DossierQuestion)
        random.seed(datetime.now())
        random.shuffle(questions)
        fichierQuestions = questions[0]
        with open("{}/{}".format(DossierQuestion, fichierQuestions), 'r', encoding="utf-8") as source:
            data = [line for line in source]
        random.seed(datetime.now())
        random.shuffle(data)
        s = data[0].split(":")
        data = s[1].split(";")
        question = data[indiceQuestion]
        tabRep = data[indiceReponses]
        typeQuestion = data[indiceTypeQuestion]
        imageQuiz = data[-1].rstrip("\n")
        return data
    else:
        print("le dossier {} n'existe pas".format(fichierQuestions))


def getQuestion():
    return questionActuelle


def getReponses():
    return reponsesActuelles


def traitementImageQuiz(fichier: str, valeurResize: int, dossier: str):
    """ Methode de traitement de l'image.
        Cette méthode va resize l'image afin de lui donner un effet pixelisé
        on va créer une nouvelle image qui se trouvera dans le dossier `magesFloues`

        Parameters
        ----------
        fichier :str
            nom de l'image que l'on veut pixeliser
        valeurResize :int
            taille du resize de l'image
        dossier :str
            dossier ou se trouve l'image actuellement
    """
    if os.path.exists("{}/{}".format(dossier, fichier)):
        img = Image.open(dossier + "/" + fichier)
        imgSmall = img.resize((valeurResize, valeurResize), resample=Image.BILINEAR)
        result = imgSmall.resize(img.size, Image.NEAREST)
        result.save(dossier + "/" + fichier)
    else:
        print("l'image {}/{} n'existe pas".format(dossier, fichier))


async def jeu(numJeu: int, tabJoueurDiscriminator: list):
    """ Méthode principale du jeu version quiz.

        Parameters
        ----------
        numJeu : int
            Numéro du jeu actuel
        tabJoueurDiscriminator : list
            tableau des joueurs avec leurs discriminants
    """
    global numeroJeu, questionActuelle, reponsesActuelles, tabPlayerDiscriminator
    numeroJeu = numJeu
    questionsVues = []
    tabPlayerDiscriminator = tabJoueurDiscriminator
    reponse = ""

    def checkMessage(m):
        """Méthode de verification de la validité d'une réponse.
            1) on va verifier que le nom que l'on cherche n'est pas dans la chaine → :
                - Sabo ✅
                - aSabo ❌ Pas validé, car le mot forme aSabo
                - a Sabo → ✅ Car le bot prend en compte seulement le "Sabo" et pas les caractères qui sont devant et derrière lorsqu'il y a un espace

            2) on va verifier qu'il y a qu'un seul caractère de faux dans la réponse
                - Lufyf au lieu de Luffy ❌ Pas validé, car ne dépasse pas 7 caractères
                - Sentomaur au lieu de Sentomaru ✅ Validé, car dépasse 7 caractères

            3) dans tous les autres cas on retourne False

            Parameters
            ----------
            m : Message
                instance de Message

            Returns
            -------
            bool
                True si la réponse donnée est bonne et si le message a été envoye dans le bon salon
                True si la réponse donnée est bonne et si le message a été envoye dans le bon salon
        """
        guild = discord.utils.find(lambda g: g.name == GUILD, client.guilds)
        roleTeam1 = discord.utils.get(guild.roles, name=tabRole[0])
        roleTeam2 = discord.utils.get(guild.roles, name=tabRole[1])
        if m.channel != channelMessage:
            return False

        if roleTeam1 not in m.author.roles and roleTeam2 not in m.author.roles:
            return False
        trace.saveTraceAnswer(m.author.name, m.content)

        # 1)
        def contains_word(userAnswer, toGuess):
            return (' ' + userAnswer + ' ') in (' ' + toGuess + ' ')

        reponses = getReponses()
        tableauReps = reponses.split("/")
        for bonneReponse in tableauReps:
            if contains_word(unidecode(bonneReponse.lower()), unidecode(m.content.lower())):
                return True

        # 2)

    for numQuestion in range(nbQuestions * 2):

        # récuperation d'un manga différent à chaque tour de jeu

        """question = "Est-ce que ce t-shirt de Luffy existe ?"
        tabRep = "Vrai/Faux"
        bonneRep = "Vrai"
        typeQuestion = "1"
        imageQuiz = "None"""
        # "Est-ce que ce t-shirt de Luffy existe ?;Vrai/Faux;1;Vrai;ASL.png"
        trace.saveTraceQuestions(numQuestion, question, tabRep, typeQuestion)
        questionsVues.append(question)
        questionActuelle = question
        reponsesActuelles = tabRep

        # Si la question comporte plusieurs réponses possibles, on lance la question à choix multiple
        #
        # Si la question comporte plusieurs réponses possibles, on lance la question à choix multiple
        if int(typeQuestion) == choixMultiple:
            if imageQuiz.lower() != noneString:
                traitementImageQuiz(imageQuiz, 200, pathImageQuiz)
                msgv = await printEmbedImageQuiz(losangeOrange, questionActuelle, imageQuiz, pathImageQuiz)
            else:
                msgv = await printEmbedQuestions(losangeOrange, questionActuelle)

            rep = data[indiceBonneReponse].rstrip("\n")
            await asyncio.sleep(delaiTroisCinq)
            # dataV = []
            reps = tabRep.replace("\n", "").split("/")
            random.seed(datetime.now())
            random.shuffle(reps)
            view = boutons.Quiz(reps, rep, len(tabPlayerDiscriminator))
            await msgv.edit(view=view)
            finView = await view.wait()
            if finView:
                await printEmbedTimeout(rep)
            else:
                if boutons.dataV[0]:
                    await calculPoints(boutons.dataV[1], tabPlayerDiscriminator)
                    await printEmbedBonneReponse(rep, boutons.dataV[1].display_name, pointsTeam1, pointsTeam2, valTeam1,
                                                 valTeam2)
                    trace.saveTraceBoutons(boutons.dataV[1].display_name, rep)
                elif not boutons.dataV[0]:
                    await printEmbedNoAnswer(rep)
                    trace.traceTimeoutBoutons(rep)
            selectQuestion()
            if question in questionsVues:
                while question in questionsVues:
                    selectQuestion()
            numeroJeu = await affichage(numeroJeu, numQuestion, nomEpreuve2, typeQuestion)
            boutons.dataV = []
            boutons.tentative = []
            pass

        elif int(typeQuestion) == choixSimple:
            if imageQuiz.lower() != noneString:
                traitementImageQuiz(imageQuiz, 200, pathImageQuiz)
                await printEmbedImageQuiz(losangeBleu, questionActuelle, imageQuiz, pathImageQuiz)
            else:
                await printEmbedQuestions(losangeBleu, questionActuelle)
            await asyncio.sleep(delaiZeroCinq)
            for nbAffichage in range(nombreTentatives):
                # attente d'un message des joueurs puis verification de la réponse à l'aide la méthode de verification
                try:
                    message = await client.wait_for("message", timeout=delaiQuestions / nombreTentatives,
                                                    check=checkMessage)

                # si le timeout est dépassé, on envoie un message embed contenant la bonne réponse
                except asyncio.TimeoutError:
                    if nbAffichage == nombreTentatives / 2:  # affichage de la bonne réponse
                        # reponse = tabRep
                        await printEmbedTimeout(reponse)
                        selectQuestion()
                        if question in questionsVues:
                            while question in questionsVues:
                                selectQuestion()
                        numeroJeu = await affichage(numeroJeu, numQuestion, nomEpreuve2, typeQuestion)
                        trace.traceTimeout()
                        break
                    else:  # affichage de l'indice
                        indice, reponse = await printClue(tabRep)
                        trace.saveTraceIndice(indice)

                # sinon on met à jour les points de l'equipe qui a marqué un point,
                # on affiche l'auteur du bon message dans un
                # embed et les points des equipes
                else:
                    await calculPoints(message.author, tabPlayerDiscriminator)
                    reponse = tabRep
                    await printEmbedBonneReponse(reponse, message.author.display_name, pointsTeam1, pointsTeam2,
                                                 valTeam1,
                                                 valTeam2)

                    selectQuestion()
                    if question in questionsVues:
                        while question in questionsVues:
                            selectQuestion()
                    numeroJeu = await affichage(numeroJeu, numQuestion, nomEpreuve2, typeQuestion)
                    break
        else:
            if imageQuiz.lower() != noneString:
                traitementImageQuiz(imageQuiz, 200, pathImageQuiz)
                msgv = await printEmbedImageQuiz(losangeBleu, questionActuelle, imageQuiz, pathImageQuiz)
                await asyncio.sleep(delaiTroisCinq)
                # dataV = []
                bonneRep = data[indiceBonneReponse].rstrip("\n")
                reps = tabRep.replace("\n", "").split("/")
                random.seed(datetime.now())
                random.shuffle(reps)
                view = boutons.Quiz(reps, bonneRep,
                                    len(tabPlayerDiscriminator))
                await msgv.edit(view=view)
                finView = await view.wait()
                if finView:
                    await printEmbedTimeout(bonneRep)
                else:
                    if boutons.dataV[0]:
                        await calculPoints(boutons.dataV[1], tabPlayerDiscriminator)
                        await printEmbedBonneReponse(bonneRep, boutons.dataV[1].display_name, pointsTeam1, pointsTeam2,
                                                     valTeam1,
                                                     valTeam2)
                        trace.saveTraceBoutons(boutons.dataV[1].display_name, bonneRep)
                    elif not boutons.dataV[0]:
                        await printEmbedNoAnswer(bonneRep)
                        trace.traceTimeoutBoutons(bonneRep)
                numeroJeu = await affichage(numeroJeu, numQuestion, nomEpreuve2)
                boutons.dataV = []
                boutons.tentative = []
    return


def sauvegardeScore(tabJDiscriminator: list):
    """ Methode de sauvegarde du score des joueurs.

           Parameters
           ----------
           tabJDiscriminator : list
               tableau de string contenant le nom de l'ensemble des joueurs avec leurs discriminants

    """
    if not os.path.exists("{}".format(fichierScore)):
        open(fichierScore, "x")  # création du fichier s'il n'existe pas encore

    data = []
    # récuperation de l'ensemble des scores actuels
    with open(fichierScore, 'r', encoding="utf-8") as source:
        for line in source:
            if line != "\n":
                line = line.rstrip("\n")
                line = line.split("/")
                data.append([line[0], int(line[1])])

    # joueurDiscriminator = messageAuthor.name + "#" + messageAuthor.discriminator
    # on parcourt le tableau des resultats pour modifier le score des joueurs déjà existant
    for joueur in tabJDiscriminator:
        # si le joueur avait déjà un score auparavant, on va mettre à jour son score simplement
        if joueur[0] in [j[0] for j in data]:
            for i in range(len(data)):
                if data[i][0] == joueur[0]:
                    data[i][1] += joueur[1]
        else:
            data.append([joueur[0], joueur[1]])
    # sauvegarde de tous les scores après les avoir mis à jour
    with open(fichierScore, 'w') as target:
        for i in range(len(data)):
            target.write(data[i][0] + "/" + str(data[i][1]) + "\n")

    pass


async def lancerJeux(tabJoueur: list, ctx, tabJoueurDiscriminator: list, traceGame):
    """ Methode de lancement du jeu.
        Initialise les variables et lance l'ensemble des jeux

        Parameters
        ----------
        tabJoueur : list
            tableau de string contenant le nom de l'ensemble des joueurs
        ctx : Context
            contexte d'execution, nous sert principalement afin d'afficher les messages avec des boutons
        tabJoueurDiscriminator : list
            tableau de string contenant le nom de l'ensemble des joueurs avec leurs discriminants
        traceGame : Traces
            instance de la classe Traces qui nous permettra de sauvegarder l'ensemble des parties dans un fichier de trace

        Returns
        ------
        bool
            booleen représentant la fin de partie
    """
    global partieEnCours, pointsTeam1, pointsTeam2, ctxExecution, channelMessage, tabPlayerDiscriminator, trace
    initVar()
    tabJoueurs = tabJoueur
    ctxExecution = ctx
    tabPlayerDiscriminator = tabJoueurDiscriminator
    trace = traceGame

    await printPlayer(tabJoueurs)
    await asyncio.sleep(delaiDebutPartieCinq)
    await printEmbedDebutPartie()
    await asyncio.sleep(delaiDebutPartieTrois)
    selectQuestion()
    await printEmbedFirstQuestion(typeQuestion)
    await asyncio.sleep(delaiDebutPartieCinq)
    # quiz
    trace.traceQuestionQuiz()
    await jeu(0, tabPlayerDiscriminator)
    trace.traceFinQuestionQuiz()

    # "qui est-ce"
    trace.traceQuestionImage()
    await jeuImage(1, tabPlayerDiscriminator)
    trace.traceFinQuestionImage()

    await asyncio.sleep(delaiDebutPartieCinq)
    # affichage des vainqueurs
    await printWinners(pointsTeam1, pointsTeam2)

    # Sauvegarde des points
    trace.saveTracePoints(pointsTeam1, pointsTeam2)

    # tabPlayerDiscriminator = [["un_ancian#8649", 5], ["xRock#9091", 5]]
    sauvegardeScore(tabPlayerDiscriminator)

    # reset
    pointsTeam1 = 0
    pointsTeam2 = 0
    partieEnCours = False

    return partieEnCours
