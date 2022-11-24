import os
from datetime import datetime


class Traces:
    """
        Classe qui nous sert à sauvegarder toutes les parties lancées dans un fichier
        au format .txt, afin d'avoir une trace sur l'ensemble des parties

        Attributes
        ----------
        dossier : str
            dossier de sauvegarde de toutes les parties
        nomFichier : str
            dossier du fichier de la partie YYYY-MM-DD_HH-MM-SS_name
    """
    def __init__(self):
        """ Constructeur de classe
            création d'une instance"""

        self.dossier = "Parties"
        if not os.path.exists(self.dossier):
            os.makedirs(self.dossier, mode=0o777, exist_ok=False)  # création de trace dossier s'il n'existe pas encore
            print("dossier bien crée")
        self.nomFichier = ""

    def createFile(self, name):
        """ Méthode de création du fichier de trace du jeu, le format du nom du fichier sera donc
            YYYY-MM-DD_HH-MM-SS_name

            Parameters
            ---------
            name : str
                nom de celui qui a lancé la partie
        """
        now = datetime.now()

        # YYYY-MM-DD_H-M-S
        dt_string = now.strftime("%Y-%m-%d_%H-%M-%S")
        self.nomFichier = dt_string + "_" + name
        try:
            with open('{0}/{1}.txt'.format(self.dossier, self.nomFichier), 'a', encoding="utf-8") as target:
                target.write("# --- Davy Back Fight ---#\n")
                target.write("Session lancée par: {0}\n\n".format(name))
        except FileNotFoundError:
            print("Le dossier {} ou le fichier {} n'existe pas".format(self.dossier, self.nomFichier))
        finally:
            target.close()
        return

    def writePlayers(self, tabJoueur: [str]):
        """ Méthode de sauvegarde des joueurs de la partie YYYY-MM-DD_HH:MM:SS_name

                Parameters
                ---------
                tabJoueur : [str]
                    tableau contenant le nom des joueurs
        """
        try:
            with open('{0}/{1}.txt'.format(self.dossier, self.nomFichier), 'a', encoding="utf-8") as target:
                target.write("# --- JOUEURS ---#\n")
                target.write("# --- [EQUIPE 1] ---#\n")
                for playerTeam1 in range(len(tabJoueur[0])):
                    target.write("#{0} - {1}\n".format(playerTeam1 + 1, tabJoueur[0][playerTeam1]))
                target.write("# --- [EQUIPE 2] ---#\n")
                for playerTeam2 in range(len(tabJoueur[1])):
                    target.write("#{0} - {1}\n".format(playerTeam2 + 1, tabJoueur[1][playerTeam2]))
                target.write("\n")
        except FileNotFoundError:
            print("Le dossier {} ou le fichier {} n'existe pas".format(self.dossier, self.nomFichier))
        finally:
            target.close()
        return

    def traceQuestionQuiz(self):
        """ Méthode d'annonce que l'on est sur la partie quiz des questions"""
        try:
            with open('{0}/{1}.txt'.format(self.dossier, self.nomFichier), 'a', encoding="utf-8") as target:
                target.write("\n")
                target.write("# ---*** [QUIZ] ***---#\n")
                target.write("\n")
        except FileNotFoundError:
            print("Le dossier {} ou le fichier {} n'existe pas".format(self.dossier, self.nomFichier))
        finally:
            target.close()
        return

    def traceFinQuestionQuiz(self):
        """ Méthode d'annonce que l'on est sur la fin de la partie quiz des questions"""
        try:
            with open('{0}/{1}.txt'.format(self.dossier, self.nomFichier), 'a', encoding="utf-8") as target:
                target.write("\n")
                target.write("# ---*** [FIN DE QUIZ] ***---#\n")
                target.write("\n")
        except FileNotFoundError:
            print("Le dossier {} ou le fichier {} n'existe pas".format(self.dossier, self.nomFichier))
        finally:
            target.close()
        return

    def traceTimeout(self):
        """ Méthode d'annonce que personne a donné la bonne réponse dans le temps imparti"""
        try:
            with open('{0}/{1}.txt'.format(self.dossier, self.nomFichier), 'a', encoding="utf-8") as target:
                target.write("\n")
                target.write("# ----- [TIMEOUT] -----#\n")
                target.write("\n")
        except FileNotFoundError:
            print("Le dossier {} ou le fichier {} n'existe pas".format(self.dossier, self.nomFichier))
        finally:
            target.close()
        return

    def saveTraceIndice(self, indice):
        """ Méthode de sauvegarde de l'indice donne

            Parameters
            ---------
            indice : str
                indice de la réponse actuelle

        """
        try:
            with open('{0}/{1}.txt'.format(self.dossier, self.nomFichier), 'a', encoding="utf-8") as target:
                target.write("\n")
                target.write("# --- Indice: {} -----#\n".format(indice))
                target.write("\n")
        except FileNotFoundError:
            print("Le dossier {} ou le fichier {} n'existe pas".format(self.dossier, self.nomFichier))
        finally:
            target.close()
        return

    def traceQuestionImage(self):
        """ Méthode de sauvagarde du nom de l'image sur la partie Image"""
        try:
            with open('{0}/{1}.txt'.format(self.dossier, self.nomFichier), 'a', encoding="utf-8") as target:
                target.write("\n# ---*** [IMAGES] ***---#\n")
                target.write("\n")
        except FileNotFoundError:
            print("Le dossier {} ou le fichier {} n'existe pas".format(self.dossier, self.nomFichier))
        finally:
            target.close()
        return

    def traceFinQuestionImage(self):
        """ Méthode d'annonce que l'on est sur la fin de la partie Image"""
        try:
            with open('{0}/{1}.txt'.format(self.dossier, self.nomFichier), 'a', encoding="utf-8") as target:
                target.write("\n")
                target.write("# ---*** [FIN DE QUIZ IMAGE] ***---#\n")
                target.write("\n")
        except FileNotFoundError:
            print("Le dossier {} ou le fichier {} n'existe pas".format(self.dossier, self.nomFichier))
        finally:
            target.close()
        return

    def saveTraceQuestions(self, numQuestion, question, answer, typeQuestion):
        """ Méthode de sauvegarde des questions de la partie YYYY-MM-DD_HH:MM:SS_name

                Parameters
                ---------
                numQuestion : int
                    numéro de la question en cours
                question : str
                    question
                answer : [str]
                    réponse de la question
                typeQuestion : str
                    type de question
        """
        try:
            with open('{0}/{1}.txt'.format(self.dossier, self.nomFichier), 'a', encoding="utf-8") as target:
                target.write("\n# --- [Question {}] ---#\n".format(numQuestion + 1))
                target.write("# --- Question: {} ---#\n".format(question))
                target.write("# --- Réponse(s): {} ---#\n".format(answer))
                target.write("# --- type de questions: {} ---#\n\n".format(typeQuestion.replace("\n", "")))
        except FileNotFoundError:
            print("Le dossier {} ou le fichier {} n'existe pas".format(self.dossier, self.nomFichier))
        finally:
            target.close()
        return

    def saveTraceBoutons(self, namePlayer, answer):
        """ Méthode de sauvegarde des questions (boutons) de la partie YYYY-MM-DD_HH:MM:SS_name

                Parameters
                ---------
                namePlayer : str
                    nom du joueur qui a donné la bonne réponse
                answer : [str]
                    réponse de la question

        """
        try:
            with open('{0}/{1}.txt'.format(self.dossier, self.nomFichier), 'a', encoding="utf-8") as target:
                target.write("[MULTIPLE] Joueur : {} , réponse : {}".format(namePlayer, answer))
                target.write("\n")
        except FileNotFoundError:
            print("Le dossier {} ou le fichier {} n'existe pas".format(self.dossier, self.nomFichier))
        finally:
            target.close()
        return

    def traceTimeoutBoutons(self, reponse):
        """ Méthode d'annonce que personne a donné la bonne réponse dans le temps imparti pour une question à choix multiple

            Parameters
            ----------
            reponse : str
                bonne réponse
        """
        try:
            with open('{0}/{1}.txt'.format(self.dossier, self.nomFichier), 'a', encoding="utf-8") as target:
                target.write("\n")
                target.write("# ----- [TIMEOUT No answer]  -----#\n")
                target.write("# Bonne réponse: {}\n".format(reponse))
                target.write("\n")
        except FileNotFoundError:
            print("Le dossier {} ou le fichier {} n'existe pas".format(self.dossier, self.nomFichier))
        finally:
            target.close()
        return

    def saveTraceAnswer(self, namePlayer, answer):
        """ Méthode de sauvegarde des réponses de la partie YYYY-MM-DD_HH:MM:SS_name

            Parameters
            ---------
            namePlayer : str
                nom du joueur
            answer : str
                réponse de la question
        """
        try:
            with open('{0}/{1}.txt'.format(self.dossier, self.nomFichier), 'a', encoding="utf-8") as target:
                target.write("[SIMPLE] Joueur : {} , réponse : {}".format(namePlayer, answer))
                target.write("\n")
        except FileNotFoundError:
            print("Le dossier {} ou le fichier {} n'existe pas".format(self.dossier, self.nomFichier))
        finally:
            target.close()
        return

    def saveTraceQuestionsImage(self, numQuestion, answer):
        """ Méthode de sauvegarde des questions sur les images de la partie YYYY-MM-DD_HH:MM:SS_name

                Parameters
                ---------
                numQuestion : int
                    numéro de la question en cours
                answer : [str]
                    réponse de la question

        """
        try:
            answer = os.path.splitext(answer)
            with open('{0}/{1}.txt'.format(self.dossier, self.nomFichier), 'a', encoding="utf-8") as target:
                target.write("# --- [Question {}] ---#\n".format(numQuestion + 1))
                target.write("# --- Réponse(s): {} ---#\n".format(answer[0]))
        except FileNotFoundError:
            print("Le dossier {} ou le fichier {} n'existe pas".format(self.dossier, self.nomFichier))
        finally:
            target.close()
        return

    def saveTracePoints(self, pointsT1, pointsT2):
        """ Méthode de sauvegarde des points de la partie YYYY-MM-DD_HH:MM:SS_name

                Parameters
                ---------
                pointsT1 : int
                    points de l'equipe 1
                pointsT2 : int
                    points de l'equipe 1
        """
        try:
            with open('{0}/{1}.txt'.format(self.dossier, self.nomFichier), 'a', encoding="utf-8") as target:
                target.write("\n")
                target.write("# --- [TEAM 1] points: {} ---#\n".format(pointsT1))
                target.write("# --- [TEAM 2] points: {} ---#\n".format(pointsT2))
                target.write("\n")
        except FileNotFoundError:
            print("Le dossier {} ou le fichier {} n'existe pas".format(self.dossier, self.nomFichier))
        finally:
            target.close()
        return

    def saveTracePointsEachPlayer(self, tabPlayerDiscriminator):
        """ Méthode de sauvegarde des points de chaque joueur de la partie  YYYY-MM-DD_HH:MM:SS_name

                Parameters
                ---------
                tabPlayerDiscriminator : [array]
                    tableau des joueurs avec leurs discriminants

        """
        try:
            with open('{0}/{1}.txt'.format(self.dossier, self.nomFichier), 'a', encoding="utf-8") as target:
                target.write("\n")
                for player in tabPlayerDiscriminator:
                    target.write("# --- Joueur:  {} points: {} ---#\n".format(player[0], player[1]))
                target.write("\n")
        except FileNotFoundError:
            print("Le dossier {} ou le fichier {} n'existe pas".format(self.dossier, self.nomFichier))
        finally:
            target.close()
        return

    def traceEndGame(self):
        """ Méthode d'annonce que l'on est sur la fin de la partie  YYYY-MM-DD_HH:MM:SS_name

        """
        try:
            with open('{0}/{1}.txt'.format(self.dossier, self.nomFichier), 'a', encoding="utf-8") as target:
                target.write("\n")
                target.write("# ---*** [FIN DE PARTIE] ***---#\n")
                target.write("\n\n")
        except FileNotFoundError:
            print("Le dossier {} ou le fichier {} n'existe pas".format(self.dossier, self.nomFichier))
        finally:
            target.close()
        return

    def traceStopGame(self):
        """ Méthode d'annone que l'on est sur la fin de la partie  YYYY-MM-DD_HH:MM:SS_name

        """
        try:
            with open('{0}/{1}.txt'.format(self.dossier, self.nomFichier), 'a', encoding="utf-8") as target:
                target.write("\n")
                target.write("# ---*** [PARTIE STOPPEE] ***---#\n")
                target.write("\n\n")
        except FileNotFoundError:
            print("Le dossier {} ou le fichier {} n'existe pas".format(self.dossier, self.nomFichier))
        finally:
            target.close()
        return


