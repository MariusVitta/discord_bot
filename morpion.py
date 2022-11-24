import discord


class JoueurMorpion:
    def __init__(self, valeur: int, member: discord.Member):
        self.valeur = valeur
        self.member = member

    def getValeur(self):
        return self.valeur

    def getMember(self):
        return self.member


class Morpion:

    def __init__(self, joueur1, joueur2):
        self.partieEnCours = True
        self.joueur1 = joueur1
        self.joueur2 = joueur2
        self.joueurActuel = 1
        self.tableauJeu = [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']]
        self.tableauStateButton = [[(False, '-'), (False, '-'), (False, '-')],
                                    [(False, '-'), (False, '-'), (False, '-')],
                                    [(False, '-'), (False, '-'), (False, '-')]]
        self.estGagnant = False
        self.estComplet = False
        self.adversaire = joueur2

    def changerJoueur(self):
        if self.joueurActuel == 1:
            self.setJoueurActuel(2)
            self.adversaire = self.joueur1
        else:
            self.setJoueurActuel(1)
            self.adversaire = self.joueur2

    def getTableauJeu(self):
        return self.tableauJeu

    def getTableauStateButton(self):
        return self.tableauStateButton

    def getPartieEnCours(self):
        return self.partieEnCours

    def getJoueurActuel(self) -> JoueurMorpion:
        if self.joueurActuel == 1:
            return self.joueur1
        else:
            return self.joueur2

    def getEstGagnant(self):
        return self.estGagnant

    def getEstComplet(self):
        return self.estComplet

    def getAdversaire(self) -> JoueurMorpion:
        return self.adversaire

    def setEstGagnant(self, boolean):
        self.estGagnant = boolean
        return

    def setEstComplet(self, boolean):
        self.estComplet = boolean
        return

    def setJoueurActuel(self, val: int):
        self.joueurActuel = val
        return

    def setTableauStateButton(self, indiceLigne, indiceCol, valeur):
        self.tableauStateButton[indiceLigne][indiceCol] = (True, valeur)
        return

    def setTableauJeu(self, indiceLigne, indiceCol, valeur):
        self.tableauJeu[indiceLigne][indiceCol] = valeur
        return



