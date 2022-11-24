import os
from datetime import datetime

path = "/home/minecraft/multicraft/servers/server248791/DavyBackFight/"


# path = ""

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
            os.makedirs(self.dossier, mode=0o777,
                        exist_ok=False)  # création de trace dossier s'il n'existe pas encore
            print("dossier bien crée")
        self.nomFichier = ""
        self.tabText = []

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
                target.write("# --- Jeu PVP ---#\n")
                target.write("Session lancée par: {0}\n\n".format(name))
        except FileNotFoundError:
            print("Le dossier {} ou le fichier {} n'existe pas".format(self.dossier, self.nomFichier))
        finally:
            target.close()
        return

    def writePlayers(self, listesJoueurs: str):
        """ Méthode de sauvegarde des joueurs de la partie YYYY-MM-DD_HH:MM:SS_name

                Parameters
                ---------
                listesJoueurs
                tabJoueur : [str]
                    tableau contenant le nom des joueurs
        """
        try:
            with open('{0}/{1}.txt'.format(self.dossier, self.nomFichier), 'a', encoding="utf-8") as target:
                target.write("# --- JOUEURS ---#\n")
                target.write(listesJoueurs)
        except FileNotFoundError:
            print("Le dossier {} ou le fichier {} n'existe pas".format(path + self.dossier, self.nomFichier))
        finally:
            target.close()
        return

    def addText(self, txt: str):
        self.tabText.append(txt)
        return

    def writeTxt(self):
        """ Méthode de sauvegarde des joueurs de la partie YYYY-MM-DD_HH:MM:SS_name
        """
        try:
            with open('{0}/{1}.txt'.format(self.dossier, self.nomFichier), 'a', encoding="utf-8") as target:
                target.write("# --- INFORMATIONS ---#\n")
                target.write("\n".join(self.tabText))
        except FileNotFoundError:
            print("Le dossier {} ou le fichier {} n'existe pas".format(path + self.dossier, self.nomFichier))
        finally:
            target.close()
        return
