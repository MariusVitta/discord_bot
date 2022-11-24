# Bot
from imports import *


# ------------------------------------------------------------------------------------------------------------#
# Gestion des commandes du bot
descriptionBot = "Bot pour le Davy Back Fight"
prefixBot = '!'
messageStart = 'dbf'
usageBot = "Usage: {0}start {1} {2} or {0}s {1} {2}".format(prefixBot, messageStart, "<nombre de joueurs>")
intents = discord.Intents().all()

# CLIENT
client = commands.Bot(command_prefix=prefixBot, description=descriptionBot, intents=intents)

# ------------------------------------------------------------------------------------------------------------#
# Gestion des Equipes
# https://emojipedia.org/ pour les différents Emojis
tabEmoji = ["☠", "🦊"]  # emoji mugiwara, foxy
medaillePremier = "🥇"
medailleSecond = "🥈"
indiceEquipe1 = 0
indiceEquipe2 = 1
tabRole = ["Mugiwara", "Foxy"]
tabRoleBold = ["**Mugiwara**", "**Foxy**"]
mugiBoutonBlanc = "▫️ {}️ {} : ".format(tabEmoji[indiceEquipe1], tabRole[indiceEquipe1])
foxyBoutonBlanc = "▫️ {} {} : ".format(tabEmoji[indiceEquipe2], tabRole[indiceEquipe2])
minimumPlayer = 1
# ------------------------------------------------------------------------------------------------------------#
# MESSAGES DAVYBACKFIGHT

titreDBV = "🎮 Davy Back Fight"
descriptionDBV = "🔹 La partie va débuter dans 30 secondes... \n\n🔸 Pour rejoindre une équipe réagis à l'un des émojis \n\n ▫️ {} {} \n\n ▫️ {} {}\n‏".format(
    tabEmoji[indiceEquipe1], tabRole[indiceEquipe1], tabEmoji[indiceEquipe2], tabRole[indiceEquipe2])
colorEmbedWhiteDBV = discord.Color.from_rgb(255, 255, 255)
debutPartieDBV = "🔹 La première épreuve va commencer\n\n"
tabTextEpreuve = ["🔹 **Epreuve 1 / 3**", "🔹 **Epreuve 2 / 3**", "🔹 **Epreuve 3 / 3** "]
carreBlanc = "▫️"
tabEpreuves = ["Epreuve 1", "Epreuve 2", "Epreuve 3"]

# ------------------------------------------------------------------------------------------------------------#
# QUESTIONS

indiceQuestion = 0
indiceReponses = 1
indiceTypeQuestion = 2
indiceBonneReponse = 3
indiceImageQuiz = 4
choixSimple = 1
choixMultiple = 2
choixSimpleAvecBouton = 3
listeMangas = ['Black Clover', 'Bleach', 'Code Geass', 'Death Note', 'Dragon Ball', 'Fairy Tail', 'Food Wars',
               'FullMetal Alchemist', 'Gintama', 'Haikyuu', 'Hajime No Ippo', 'Hunter x Hunter',
               'JoJo Bizarre Adventure', 'Jujutsu Kaisen', 'Kimetsu No Yaiba', 'Kuroko No Basket', 'My Hero Academia',
               'Nanatsu No Taizai', 'Naruto', 'One Piece', 'One Punch Man', 'Shingeki No Kyojin', 'Sword Art Online',
               'Tokyo Ghoul', 'Tokyo Revengers']
listesQuestions = ["One Piece", "Death Note"]
fichiersQuestions = "One Piece.txt"
DossierQuestion = "Questions"

nomEpreuve1 = "Quiz"
nomEpreuve2 = "Qui est-ce ?"
nomEpreuve3 = "nom épreuve 3"
losangeOrange = "🔸 "
losangeBleu = "🔹 "
# ------------------------------------------------------------------------------------------------------------#
# GESTIONS DES REPONSES

# ----- MAUVAISES REPONSES -----
timeout = "⏰  **Temps écoulé**"
noAns = "🚨 **Pas de bonne réponse**"
reponseText = "▫️ Réponse : "
colorEmbedTimeout = discord.Color.from_rgb(204, 61, 61)

# ----- BONNES REPONSES -----
pointVert = "<:rond3:922472655100190730> "
textGoodAnswer = " a donné la bonne réponse"
colorEmbedGoodAnswer = discord.Color.from_rgb(120, 177, 89)

# ----- INDICES -----
nombreTentatives = 2  # nombre de fois que le bot va attendre avant d'envoyer la bonne réponse (envoie un incide à `nombreTentatives`\2`)

nbQuestions = 7  # nombre de questions pour l'épreuve 1

# ------------------------------------------------------------------------------------------------------------#
# GESTIONS DU DELAI
delaiEntreEpreuves = 5
delaiEntreQuestions = 10
delaiJoinMessage = 30
delaiQuestions = 30
delaiQuestionsImages = 40
delaiDebutPartieTrois = 3
delaiDebutPartieCinq = 5
delaiReponse = 5
delaiTroisCinq = 3.5
delaiDeux = 2
delaiZeroCinq = 0.5

# ------------------------------------------------------------------------------------------------------------#
# GESTION DES IMAGES
path = 'images'
pathFlou = 'imagesFloues'
pathImageQuiz = "imagesQuiz"
noneString = "none"
tabTailleResize = [8, 12, 16, -1,
                   200]  # résolution des images pour les pixeliser, le '200' correspond à l'image non pixelisée

# ------------------------------------------------------------------------------------------------------------#
# GESTION DES SCORES
fichierScore = "scores.txt"
