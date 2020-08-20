#!/usr/bin/python3

"""
    Autor: Jasper Bremenkamp
    Version: 1.1.3
    Datum: 2020-04-10
    Beschreibung: 
        - Spiel mit dem Ziel Viren zu eleminieren
        - das Spielprinzip gleicht dem von Moorhuhn
"""

import os
from math import cos            #Benutzt fuer Bewegung
from numpy import clip          #für zulässige Intervalle
from ast import literal_eval    #Auswertung von Literalen
from datetime import datetime
from random import randint as rdi

#pygame Meldung verstcken 
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import pygame as pg

pg.init()

pg.display.set_caption("Corona-Jäger")

#Farben
WHITE   = (255,255,255)
BLACK   = (  0,  0,  0)
RED     = (255,  0,  0)
GREEN   = (  0,255,  0)
D_GREEN = (  0,128,  0)
BLUE    = (  0,  0,255)
GRAY    = (128,128,128)
L_GRAY  = (192,192,192)
COLOR2  = (250,100, 30)

#Display Daten
DISPLAYWIDTH = 900         #Standard Fensterbreite
DISPLAYHEIGHT= 700         #Standard Fensterhoehe
DISPLAYFLAG = pg.RESIZABLE #veraenderbare Fenstergroessen
DISPLAYCOLBIT = 32         #Farbtiefe
FRAMERATE = 60
display = pg.display.set_mode((DISPLAYWIDTH, DISPLAYHEIGHT), DISPLAYFLAG, DISPLAYCOLBIT)
clock = pg.time.Clock()

pg.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0)) #Mauszeiger vestecken
location = os.path.dirname(__file__) #Pfad des Pythonskripts ermitteln

fadenkreuzIMG = pg.image.load(os.path.join(location, "assets", "fadenkreuz.png")) #Quelle: https://pixabay.com/de/vectors/scharfschütze-ziel-fadenkreuz-297661/
fadenkreuzIMG = pg.transform.scale(fadenkreuzIMG, (50, 50)) #Skalierung des Fadenkreuzes

class Viren:
    """
    Beschreibung:
        - Klasse für Viren-Objekte (Ziele)
        - enthaelt alle Interaktionslogiken mit den Viren
    """

    virenliste = [] #alle erstellten Viren
    totenliste = [] #tote Viren bzw. Blutflecken, die dargestellt werden sollen
    zerstoert = 0   #Counter fuer insgesamt zerstoerte Viren

    virengroesse = 100  

    _coronaIMG = pg.image.load(os.path.join(location, "assets", "corona.png")) #Quelle: https://pixabay.com/de/illustrations/virus-freigestellt-corona-4930122/
    _coronaIMG = pg.transform.scale(_coronaIMG, (virengroesse, virengroesse)) #Skalierung der Virengrafik
    _fleckIMG  = pg.image.load(os.path.join(location, "assets", "fleck.png")) #basiert auf: https://publicdomainvectors.org/de/kostenlose-vektorgrafiken/Blut/52377.html
    _fleckIMG  = pg.transform.scale(_fleckIMG, (virengroesse, virengroesse)) #Skalierung der Virengrafik

    def __init__(self, x, y, speed=1, bewegung=1):
        """
        Beschreibung:
            - Konstruktor für Viren-Objekte
        Parameter:
            - X-Koordinate, Y-Koordinate, Bewegungsgeschwindigkeit, Bewegungsart
        Rueckgabe:
            - Keine
        """
        self.__x_pos = int(x)
        self.__y_pos = int(y)
        self.__groesse = Viren.virengroesse
        self.__zufallsverschiebung = rdi(0, Level.breite) #fuer unterschiedliche Bewegungsmuster
        self.__geschwindigkeit = 1
        self.__bewegung = bewegung #Bewegungsart (rechts, links, oben, unten)
        if(bewegung >= 3):
            self.__geschwindigkeit *= -1
        self.__img = Viren._coronaIMG

        Viren.virenliste.append(self) 

    def bewegen(self):
        """
        Beschreibung:
            - Bewegen der Viren nach verschiedenen Bewegungsmustern
            - Bewegung abhaengig von Bewegungsgeschwindigkeit und Bewegungsart des Viren-Objekts 
        Parameter:
            - Keine
        Rueckgabe:
            - Keine

        Test:
            beobachten ob die Viren folgende Kriterien erfuellen:
            - entlang der Route wird nicht das sichtbare Feld verlassen
            - am Ende der Route wird am Anfang der Route wieder begonnen
            - Anzahl der aktiven Viren stimmt mit sichtabren Viren überein
        """
        if(self.__bewegung == 1 or self.__bewegung == 3):
            self.__x_pos += self.__geschwindigkeit
            self.__y_pos += int(5*cos(self.__x_pos*0.02-self.__zufallsverschiebung))

            # Verhindern, dass der Virus den sichtbaren Bereich verlaesst
            if(self.__y_pos <= 0):
                self.__y_pos = 0
            if(self.__y_pos >= Level.hoehe - self.__groesse):
                self.__y_pos = Level.hoehe - self.__groesse

            # Durchlauf des Virus von rechts nach links
            if(self.__x_pos >= Level.breite):
                self.__x_pos = -self.__groesse

            # Durchlauf des Virus von links nach rechts
            if(self.__x_pos <= -self.__groesse):
                self.__x_pos = Level.breite

        if(self.__bewegung == 2 or self.__bewegung == 4):
            self.__y_pos += self.__geschwindigkeit
            self.__x_pos += int(5*cos(self.__y_pos*0.02-self.__zufallsverschiebung))

            # Verhindern, dass der Virus den sichtbaren Bereich verlaesst
            if(self.__x_pos <= 0):
                self.__x_pos = 0
            if(self.__x_pos >= Level.breite- self.__groesse):
                self.__x_pos = Level.breite - self.__groesse

            # Durchlauf des Virus von unten nach oben
            if(self.__y_pos >= Level.hoehe):
                self.__y_pos = -self.__groesse

            # Durchlauf des Virus von oben nach unten
            if(self.__y_pos <= -self.__groesse):
                self.__y_pos = Level.hoehe


    def zerstoerung(self):
        """
        Beschreibung:
            - Zerstoerung der aktiven Viren
            - Wechsel von der Virenliste in die Totenliste
            - Aenderung des Virenerscheinungsbild
                - Normal zu tot
        Parameter:
            - Keine
        Rueckgabe:
            - Keine

        Test:
            beobachten ob die Viren im Spiel folgende Kriterien erfuellen:
            - Virus wird nach Aufruf zu einem Fleck
            - Fleck bewegt sich nicht
            - die Werte oben rechts passen
                - aktive Viren werden um eins dekrementiert
                - Zerstoert-Counter wird inkrementiert
        """
        self.__img = Viren._fleckIMG
        self.zeichnen()
        Viren.zerstoert += 1
        Viren.virenliste.remove(self)
        Viren.totenliste.append(self)

    def zeichnen(self):
        """
        Beschreibung:
            - Zeichnen des Virus
        Parameter:
            - Keine
        Rueckgabe:
            - Keine
        """
        display.blit(self.__img, (self.__x_pos, self.__y_pos))
        
    def pruefeTreffer(self, maus_pos):
        """
        Beschreibung:
            - Prueft ob der Maus-Cursor ueber dem Virus ist
        Parameter:
            - Maus-Position
        Rueckgabe:
            - Maus ueberm Ziel: True/False
        """
        x = maus_pos[0]
        y = maus_pos[1]
        
        if self.__bewegung > 0 and self.__x_pos < x < (self.__x_pos + self.__groesse)  and self.__y_pos < y < (self.__y_pos + self.__groesse):
            return True

class Level:
    """
    Beschreibung:
        - Klasse fuer Level-Objekte
        - enthaelt Spiellogik und die Darstellung der Oberflaechen
        - Menues alle statisch implementiert
    """

    levelliste = []     #alle erstellten Level
    highscoreliste = [] #alle Highscores aus allen Spielen

    #zu zeichnende Fensterdimension
    hoehe = DISPLAYHEIGHT 
    breite = DISPLAYWIDTH

    __aktiv = True     # Flag fuer Game Over (False)
    __esc = False      # Flag fuer pausiertes Spiel
    __menu_auswahl = 0 # Variable zur Festlegung welches Menu dargestellt werden soll
    __last_tick = 0    # Zeitmarke für Erstellung der Viren

    #Hintergruende
    _hintergundIMG0_orig = pg.image.load(os.path.join(location, "assets", "hintergrund0.jpg")) #Quelle: https://commons.wikimedia.org/wiki/File:Bali,_Goa_Lawah_2.jpg
    _hintergundIMG0 = pg.transform.smoothscale(_hintergundIMG0_orig, (breite, hoehe)) #Skalierung des Hintergrunds
    _hintergundIMG1_orig = pg.image.load(os.path.join(location, "assets", "hintergrund1.jpg")) #Quelle: https://pixnio.com/de/wissenschaft/mikroskopische-aufnahmen/parvovirus-virionen-parvoviridae-familie-dna-viren
    _hintergundIMG1 = pg.transform.smoothscale(_hintergundIMG1_orig, (breite, hoehe))
    _hintergundIMG2_orig = pg.image.load(os.path.join(location, "assets", "hintergrund2.jpg")) #Quelle: https://pixabay.com/de/illustrations/blut-zellen-rot-medizinische-1813410/
    _hintergundIMG2 = pg.transform.smoothscale(_hintergundIMG2_orig, (breite, hoehe))

    def __init__(self):
        """
        Beschreibung:
            - Konstruktor für Level-Objekte
        Parameter:
            - Keine
        Rueckgabe:
            - Keine
        """
        self.score = 0
        if(len(Level.levelliste) == 0):
            self.__zerstoert = 20 #Zerstoerte Viren bis zum naechsten Level
            self.__spawnspeed = 1
        else:
            letztesLevel = Level.levelliste[-1]
            self.__zerstoert = int(letztesLevel.__zerstoert * 1.5)
            self.__spawnspeed = letztesLevel.__spawnspeed + 1
        self.__maxViren = int(self.__zerstoert * 0.5) + 10

        if(self.__maxViren >= 100):
            self.__maxViren = 100

        Level.levelliste.append(self)

        #Flecken beseitigen
        Viren.totenliste.clear()

    @staticmethod
    def __zeichnen():
        """
        Beschreibung:
            - Zeichnen des Hintergrunds der Level
        Parameter:
            - Keine
        Rueckgabe:
            - Keine

        Test:
            - Pruefen ob die richtigen Hintergruende gezeigt werden
        """
        if(len(Level.levelliste) <= 0):
            hintergund = Level._hintergundIMG1
        elif(len(Level.levelliste) < 3):
            hintergund = Level._hintergundIMG0
        elif(len(Level.levelliste) < 5):
            hintergund = Level._hintergundIMG1
        else:
            hintergund = Level._hintergundIMG2

        display.fill(WHITE)
        display.blit(hintergund, [0,0])

    def __berechneLevelscore(self):
        """
        Beschreibung:
            - Berechnung des Scores fuer ein Level
        Parameter:
            - Keine
        Rueckgabe:
            - Keine
        """
        self.score = len(Level.levelliste) * 10 * Viren.zerstoert

    @staticmethod
    def berechneHighscore():
        """
        Beschreibung:
            - statische Methode zur Berechnung des Highscores aus allen Levelscores
        Parameter:
            - Keine
        Rueckgabe:
            - Summe der Levelscores
        """
        summe = 0
        for element in Level.levelliste:
            summe += element.score
        return summe

    @staticmethod
    def __reset():
        """
        Beschreibung:
            - statische Methode zum Zuruecksetzen des Spiels
            - Fuegt berechneten Highscore eines Spiels in die Highscoreliste
        Parameter:
            - Keine
        Rueckgabe:
            - Keine

            Test:
                Pruefung:
                - Hauptmenu wird angezeigt
                - das Spiel ist in Ausgangsituation zurueckgekehrt
                - Highscore wird unter dem Highscore Menu angezeigt 

        """
        Level.highscoreliste.append((datetime.now().strftime("%Y-%m-%d %H:%M"), len(Level.levelliste), Level.berechneHighscore()))

        Level.__menu_auswahl = 0
        Viren.virenliste.clear()
        Viren.zerstoert = 0
        Level.levelliste.clear()
        Level.__aktiv = True
        Level.__esc = False

    @staticmethod
    def __neustarten():
        """
        Beschreibung:
            - fuehrt Reset durch und startet ein neues Spiel
        Parameter:
            - Keine
        Rueckgabe:
            - Keine
        
        Test:
            - Pruefung: Spiel startet neu
        """
        Level.__reset()
        Level()

    @staticmethod 
    def __hauptmenu(maus_pos, klick):
        """
        Beschreibung:
            - Darstellung des Hauptmenu
            - Erstellung aller Steuerelemete fuer das Hauptmenu
        Parameter:
            - Maus-Position, Linker Maus Klickstatus
        Rueckgabe:
            - Keine
        
        Test:
            - Pruefung: Menu enthaelt alle Elemente und jedes laesst sich anklicken
        """

        #Einstellungen Menu
        x_pos = int(Level.breite/2)
        y_anfang = 100
        y_abstand = 60
        btn_breite = 300
        btn_hoehe = 50

        Level.__menu_auswahl = 0
        
        Level.__zeichnen()

        nachricht("Corona-Jäger", (x_pos, y_anfang), 40)
        
        btnStart = Steuerelement(x_pos, y_abstand+y_anfang, btn_breite, btn_hoehe, "Spiel starten")
        btnStart.darstellen(maus_pos, klick, lambda: Level())
        btnHighscore = Steuerelement(x_pos, 2*y_abstand+y_anfang, btn_breite, btn_hoehe, "Highscore")
        btnHighscore.darstellen(maus_pos, klick, lambda: Level.__highscore(maus_pos, klick))
        btnHilfe = Steuerelement(x_pos, 3*y_abstand+y_anfang, btn_breite, btn_hoehe, "Hilfe")
        btnHilfe.darstellen(maus_pos, klick, lambda: Level.__hilfe(maus_pos, klick))
        btnInfo = Steuerelement(x_pos, 4*y_abstand+y_anfang, btn_breite, btn_hoehe, "Info")
        btnInfo.darstellen(maus_pos, klick, lambda: Level.__info(maus_pos, klick))
        btnExit = Steuerelement(x_pos, 5*y_abstand+y_anfang, btn_breite, btn_hoehe, "Exit")
        btnExit.darstellen(maus_pos, klick, beenden)

    @staticmethod
    def __hilfe(maus_pos, klick):
        """
        Beschreibung:
            - Darstellung des Hilfe-Menu
            - Erstellung aller Steuerelemete und Texte fuer das Hilfe-Menu
        Parameter:
            - Maus-Position, Linker Maus Klickstatus
        Rueckgabe:
            - Keine

        Test:
            - Pruefung: Menu enthaelt Button und Infotext
        """

        #Einstellungen Menu
        x_pos = int(Level.breite/2)
        y_anfang = 100
        y_abstand = 20
        btn_breite = 300
        btn_hoehe = 50
        y_button = Level.hoehe-110
        schriftgroesse = 20

        Level.__menu_auswahl = 1

        Level.__zeichnen()

        pg.draw.rect(display, L_GRAY, (80, 80, Level.breite-80*2, Level.hoehe-80*2))
        nachricht("Hilfe", (x_pos, y_anfang), 40)

        nachricht("Ziel des Spiels ist es, so viele Viren zu eliminieren wie möglich.", (x_pos, 3*y_abstand+y_anfang), schriftgroesse)
        nachricht("Hält man lange genug durch, gelangt man zum nächsten Level.", (x_pos, 4*y_abstand+y_anfang), schriftgroesse)
        nachricht("Oben rechts steht eine Anzeige mit Informationen", (x_pos, 6*y_abstand+y_anfang), schriftgroesse)
        nachricht("über Anzahl der aktiven Viren und die zu erledigenden Viren.", (x_pos, 7*y_abstand+y_anfang), schriftgroesse)
        nachricht("Ist die maximal erlaubte Anzahl aktiver Viren erreicht,", (x_pos, 8*y_abstand+y_anfang), schriftgroesse)
        nachricht("hat man verloren.", (x_pos, 9*y_abstand+y_anfang), schriftgroesse)
        nachricht("Viren müssen mit der Maus angeklickt werden!", (x_pos, 11*y_abstand+y_anfang), schriftgroesse)
        nachricht("[ESC]: Spiel pausieren", (x_pos, 12*y_abstand+y_anfang), schriftgroesse)

        btnZurueck = Steuerelement(x_pos, y_button, btn_breite, btn_hoehe, "Zurück")
        btnZurueck.darstellen(maus_pos, klick, lambda: Level.__hauptmenu(maus_pos, klick) )

    @staticmethod
    def __info(maus_pos, klick):
        """
        Beschreibung:
            - Darstellung des Info-Menu
            - Erstellung aller Steuerelemete und Texte fuer das Info-Menu
        Parameter:
            - Maus-Position, Linker Maus Klickstatus
        Rueckgabe:
            - Keine

        Test:
            -Pruefung: Menu enthaelt Button und Infotext
        """

        #Einstellungen Menu
        x_pos = int(Level.breite/2)
        y_anfang = 100
        y_abstand = 20
        btn_breite = 300
        btn_hoehe = 50
        y_button = Level.hoehe-110
        schriftgroesse = 22

        Level.__menu_auswahl = 2

        Level.__zeichnen()

        pg.draw.rect(display, L_GRAY, (80, 80, Level.breite-80*2, Level.hoehe-80*2))
        nachricht("Info", (x_pos, y_anfang), 40)

        nachricht("Autor: Jasper Bremenkamp", (x_pos, 3*y_abstand+y_anfang), schriftgroesse)
        nachricht("Erstellungsdatum: 2020-04-10", (x_pos, 4*y_abstand+y_anfang), schriftgroesse)
        nachricht("Erstellung im Rahmen des Python Kurs WiSe 2019/2020", (x_pos, 6*y_abstand+y_anfang), schriftgroesse)
        nachricht("an der DHBW Stuttgart", (x_pos, 7*y_abstand+y_anfang), schriftgroesse)

        btnHauptmenu = Steuerelement(x_pos, y_button, btn_breite, btn_hoehe, "Zurück ins Hauptmenü")
        btnHauptmenu.darstellen(maus_pos, klick, lambda: Level.__hauptmenu(maus_pos, klick))

    
    @staticmethod
    def __highscore(maus_pos, klick):
        """
        Beschreibung:
            - Darstellung des Highscore Menu
            - Erstellung aller Steuerelemete und Texte fuer das Highscore Menu
        Parameter:
            - Maus-Position, Linker Maus Klickstatus
        Rueckgabe:
            - Keine
        
        Test:
            Pruefung:
            - Menu enthaelt einen Button und eine Highscoreliste
            - Button laesst sich anklicken und fuehrt zurueck ins Menu
            - Highscoreliste bleibt ueber dem Button stehen und wird nicht weiter gezeichnet 
        """

        #Einstellungen Menu
        x_pos = int(Level.breite/2)
        uberschrift_y = 100             #Y-Position Ueberschrift
        button_y = Level.hoehe-110      #Y-Position Button
        abstand = 30                    #Abstand zwischen den Scores

        maxScores = int((button_y-uberschrift_y)/abstand)-2 #maximale Anzahl gut sichbarer Scores

        Level.__menu_auswahl = 3

        Level.__zeichnen()

        pg.draw.rect(display, L_GRAY, (80, 80, Level.breite-80*2, Level.hoehe-80*2))

        nachricht("Highscore", (x_pos, uberschrift_y), 40)

        Level.highscoreliste.sort(key=lambda x: x[2], reverse=True) #nach Punktzahl sortieren, von oben nach unten
        
        y_pos = 110
        for i in range(0,clip(0, maxScores, len(Level.highscoreliste))): #iteriert nur durch so viele Scores wie sichtbar sind
            y_pos += abstand
            score = Level.highscoreliste[i]
            nachricht(str(score[0]) +  ", Level: " + str(score[1]) + ", Punkte: " + str(score[2]), (x_pos, y_pos), 24)

        btnHauptmenu = Steuerelement(x_pos, button_y, 300, 50, "Zurück ins Hauptmenü")
        btnHauptmenu.darstellen(maus_pos, klick, lambda: Level.__hauptmenu(maus_pos, klick))

    @staticmethod
    def __menu(maus_pos, klick):
        """
        Beschreibung:
            - Auswahl des richtigen Menues anhand von Klassenvariable
        Parameter:
            - Maus-Position, Linker Maus Klickstatus
        Rueckgabe:
            - Keine

        Test:
            - Pruefung: Auswahl der richtigen Menues
        """
        if(Level.__menu_auswahl == 0):
            Level.__hauptmenu(maus_pos, klick)
        if(Level.__menu_auswahl == 1):
            Level.__hilfe(maus_pos, klick)
        if(Level.__menu_auswahl == 2):
            Level.__info(maus_pos, klick)
        if(Level.__menu_auswahl == 3):
            Level.__highscore(maus_pos, klick)

    @staticmethod
    def __verloren(maus_pos, klick):
        """
        Beschreibung:
            - Darstellung des Game Over Menu
            - Erstellung aller Steuerelemete und Texte fuer das Game Over Menu
        Parameter:
            - Maus-Position, Linker Maus Klickstatus
        Rueckgabe:
            - Keine

        Test:
            - Pruefung: Menu enthaelt alle Elemente und jedes laesst sich anklicken
        """

        #Einstellungen Menu
        x_pos = int(Level.breite/2)
        y_anfang = int(Level.hoehe/2)-60
        y_abstand = 60
        btn_breite = 300
        btn_hoehe = 50

        nachricht("Game Over", (x_pos, int(Level.hoehe/2)-60), 40)
        nachricht("Highscore: " + str(Level.berechneHighscore()), (x_pos, y_abstand+y_anfang), 35)
        btnNeustart = Steuerelement(x_pos, 2*y_abstand+y_anfang, btn_breite, btn_hoehe, "Spiel neustarten")
        btnNeustart.darstellen(maus_pos, klick, Level.__neustarten)
        btnHilfe = Steuerelement(x_pos, 3*y_abstand+y_anfang, btn_breite, btn_hoehe, "Hilfe")
        btnHilfe.darstellen(maus_pos, klick, lambda: Level.__hilfe(maus_pos, klick))
        btnHauptmenu = Steuerelement(x_pos, 4*y_abstand+y_anfang, btn_breite, btn_hoehe, "Zurück ins Hauptmenü")
        btnHauptmenu.darstellen(maus_pos, klick, Level.__reset)
        btnExit = Steuerelement(x_pos, 5*y_abstand+y_anfang, btn_breite, btn_hoehe, "Exit")
        btnExit.darstellen(maus_pos, klick, beenden)

    @staticmethod
    def __pause(maus_pos, klick):
        """
        Beschreibung:
            - Darstellung des Pause Menu
            - Erstellung aller Steuerelemete und Texte fuer das Pause Menu
        Parameter:
            - Maus-Position, Linker Maus Klickstatus
        Rueckgabe:
            - Keine

        Test:
            - Pruefung: Menu enthaelt alle Elemente und jedes laesst sich anklicken
        """

        #Einstellungen Menu
        x_pos = int(Level.breite/2)
        y_anfang = int(Level.hoehe/2)-60
        y_abstand = 60
        btn_breite = 300
        btn_hoehe = 50

        Level.__menu_auswahl = 0
        nachricht("Pause", (x_pos, y_anfang), 40)
        btnFortsetzung = Steuerelement(x_pos, y_abstand+y_anfang, btn_breite, btn_hoehe, "Spiel fortsetzen")
        btnFortsetzung.darstellen(maus_pos, klick, Level.toggleEsc)
        btnNeustart = Steuerelement(x_pos, 2*y_abstand+y_anfang, btn_breite, btn_hoehe, "Spiel neustarten")
        btnNeustart.darstellen(maus_pos, klick, Level.__neustarten)
        btnHilfe = Steuerelement(x_pos, 3*y_abstand+y_anfang, btn_breite, btn_hoehe, "Hilfe")
        btnHilfe.darstellen(maus_pos, klick, lambda: Level.__hilfe(maus_pos, klick))
        btnHauptmenu = Steuerelement(x_pos, 4*y_abstand+y_anfang, btn_breite, btn_hoehe, "Zurück ins Hauptmenü")
        btnHauptmenu.darstellen(maus_pos, klick, Level.__reset)
        btnExit = Steuerelement(x_pos, 5*y_abstand+y_anfang, btn_breite, btn_hoehe, "Exit")
        btnExit.darstellen(maus_pos, klick, beenden)

    @staticmethod
    def toggleEsc():
        """
        Beschreibung:
            - Fortsetzen des Spiels
        Parameter:
            - Keine
        Rueckgabe:
            - Keine
        """
        if(Level.__esc == False):
            Level.__esc = True
        else:
            Level.__esc = False

    @staticmethod
    def anpassen_Hintergruende():
        """
        Beschreibung:
            - Passt Hinterguende neue Level-Groessen an
        Parameter:
            - Keine
        Rueckgabe:
            - Keine

        Tests:
            Pruefung:
            - Hintergrund ist richtig skaliert
            - kein weißen Ränder
        """
        Level._hintergundIMG0 = pg.transform.smoothscale(Level._hintergundIMG0_orig, (Level.breite, Level.hoehe)) #Skalierung des Hintergrunds
        Level._hintergundIMG1 = pg.transform.smoothscale(Level._hintergundIMG1_orig, (Level.breite, Level.hoehe))
        Level._hintergundIMG2 = pg.transform.smoothscale(Level._hintergundIMG2_orig, (Level.breite, Level.hoehe))

    @staticmethod
    def main_Level(maus_pos, klick):
        """
        Beschreibung:
            - statische Main-Methode der Levelklasse
            - Zentrum der Spiellogik
            - Darstellung des eigentlichen Spiels
        Parameter:
            - Maus-Position, Linker Maus Klickstatus
        Rueckgabe:
            - Keine

        Tests:
            Pruefung:
            - Viren werden zyklisch erstellt
            - Game Over erscheint beim Ueberschreiten der maximal zulaessigen Viren
            - Druecken der ESC Taste laesst das Pause Menu erscheinen
            - Spielinfos werden oben rechts korrekt angezeigt
        """

        if(len(Level.levelliste) == 0): #Falls noch kein Level erstellt wurde
            Level.__menu(maus_pos, klick)
        else:
            if(Level.__esc and Level.__aktiv):
                Level.levelliste[-1].__zeichnen()

                if(Level.__menu_auswahl == 1):
                    Level.__hilfe(maus_pos, klick)
                else:
                    Level.__pause(maus_pos, klick)
            else:
                aktuellesLevel = Level.levelliste[-1]
                if Viren.zerstoert >= aktuellesLevel.__zerstoert:
                    Level()

                aktuellesLevel.__berechneLevelscore()
                aktuellesLevel.__zeichnen()

                #==== Viren erstellen und zeichnen ====#

                if Level.__aktiv:
                    if ((pg.time.get_ticks() - Level.__last_tick) > 1000/aktuellesLevel.__spawnspeed ):
                        bewegung = rdi(1, 4)
                        if bewegung == 1 or bewegung == 3:
                            Viren(-Viren.virengroesse, rdi(0, Level.hoehe), rdi(1, 3), bewegung=bewegung)
                        if bewegung == 2 or bewegung == 4:
                             Viren(rdi(0, Level.breite), -Viren.virengroesse, rdi(1, 3), bewegung=bewegung)
                        Level.__last_tick = pg.time.get_ticks()

                for tote in Viren.totenliste:
                    tote.zeichnen()

                for virus in Viren.virenliste:
                    if(Level.__aktiv and klick and virus.pruefeTreffer(maus_pos)):
                        virus.zerstoerung()
                    else:
                        virus.bewegen()
                        virus.zeichnen()

                aktiveViren = len(Viren.virenliste)
                if aktiveViren >= aktuellesLevel.__maxViren: #Verloren -> Spiel vorbei
                    Level.__aktiv = False
                    if(Level.__menu_auswahl == 1):
                        Level.__hilfe(maus_pos, klick)
                    else:
                        Level.__verloren(maus_pos, klick)

                #Zeichnen der Spielinfo
                nachricht("Level: " + str(len(Level.levelliste)), (Level.breite-120, 15))
                nachricht("Zerstört: " + str(Viren.zerstoert) + "/" + str(aktuellesLevel.__zerstoert), (Level.breite-120, 45))
                nachricht("Aktiv: " + str(aktiveViren) + "/" + str(aktuellesLevel.__maxViren), (Level.breite-120, 75))

class Steuerelement:
    """
        Beschreibung:
            - Klasse fuer Steuerelemente bzw. die Buttons
    """

    def __init__(self, x, y, width, height, text, farbe=GREEN, farbe2=D_GREEN, text_farbe=BLACK, rahmenfarbe=GRAY, rahmendicke=3):
        """
        Beschreibung:
            - Konstruktor für Steuerelemente
        Parameter:
            - X-Koordinate, Y-Koordinate, Breite, Hoehe, Text, Farbe, Farbe beim Ueberfliegen, Textfarbe, Rahmenfarbe, Rahmendicke
            - X- und Y-Koordinate stellen das Zentrum des Steuerelements dar
        Rueckgabe:
            - Keine
        """
        self.__x_pos = int(x)
        self.__y_pos = int(y)
        self.__height = int(height)
        self.__width = int(width)
        self.__farbe = farbe
        self.__farbe2 = farbe2
        self.__text = text
        self.__text_farbe = text_farbe
        self.__rahmenfarbe = rahmenfarbe
        self.__rahmendicke = rahmendicke

    def darstellen(self, maus_pos, klick, funktion):
        """
        Beschreibung:
            - Darstellung der Steuerelemenete
            - Enthaelt das Zeichnen und die Interaktion
        Parameter:
            - Maus-Position, Linker Maus Klickstatus, aufzurufende Funktion beim Klick
        Rueckgabe:
            - Keine

        Tests:
            pruefen der Dimensionen:
            - Text befindet sich mittig im Button
            - X und Y-Position ist mittig im Button
            pruefen der Funktion:
            - ein Anklicken ruft die gewuenschte Funktion auf
            - beim Ueberfliegen veraendert sich die Farbe
        """

        #Position der Box wird von der Mitte ausgehend berechnet
        x_pos_box = int(self.__x_pos-self.__width/2)
        y_pos_box = int(self.__y_pos-self.__height/2)

        rahmendicke = self.__rahmendicke
        pg.draw.rect(display, self.__rahmenfarbe, (x_pos_box, y_pos_box, self.__width, self.__height)) #Zeichnen Rahmen

        if x_pos_box < maus_pos[0] < (x_pos_box + self.__width)  and y_pos_box < maus_pos[1] < (y_pos_box + self.__height):
            pg.draw.rect(display, self.__farbe, (x_pos_box+rahmendicke, y_pos_box+rahmendicke, self.__width-rahmendicke*2, self.__height-rahmendicke*2)) #Farbe beim Ueberfliegen
            if(klick):
                funktion() #wird aufgerufen beim Klicken
        else:
            pg.draw.rect(display, self.__farbe2, (x_pos_box+rahmendicke, y_pos_box+rahmendicke, self.__width -rahmendicke*2, self.__height-rahmendicke*2)) #normale Farbe

        nachricht(self.__text, (self.__x_pos, self.__y_pos), farbe=self.__text_farbe) #Text innerhalb des Steuerelements

def nachricht(text, pos=(0,0), size=25, farbe=BLUE):
    """
    Beschreibung:
        - Darstellung eines Textes
    Parameter:
        - darzustellender Text, Positions-Tupel fuer Zentrum (X, Y), Farbe des Textes
    Rueckgabe:
        - Keine

    Tests:
        Pruefung:
        - Text an gewuenschter Stelle im Spiel sichtbar
    """
    font = pg.font.Font("freesansbold.ttf", size)
    TextSurf = font.render(text, True, farbe)
    TextRect = TextSurf.get_rect()
    TextRect.center = pos
    display.blit(TextSurf, TextRect)

def lade_Highscore():
    """
    Beschreibung:
        - Laden des Highscores aus Datei
        - Daten aus der Datei werden in Level.highscoreliste geladen
    Parameter:
        - Keine
    Rueckgabe:
        - Keine

    Tests:
        Pruefung:
        - nach Aufruf muss im Menu Highscore der Inhalt der Liste stehen
        - Test der Exception bei fehlender Datei oder Unsinn in Datei
    """
    try:
        with open(os.path.join(location, "highscore.txt"), "r") as f:
            liste = [list(literal_eval(line)) for line in f]
            Level.highscoreliste = liste.copy()
    except:
        print("Datei konnte nicht gelesen werden!")

def speichere_Highscore(liste):
    """
    Beschreibung:
        - Speichern des Highscores aus Datei
        - Daten aus dem Level.highscoreliste werden in der Datei gespeichert
    Parameter:
        - Keine
    Rueckgabe:
        - Keine

    Tests:
        - pruefen ob nach Aufruf eine Datei mit dem Namen highscore.txt existiert
        - pruefen ob der Highscore aus dem Spiel in die Datei uebernommen wurde
            - kein Highscore => nichts in Datei
            - mehrere Highscore => Auflistung der Scores
    """
    if(len(Level.levelliste) != 0): #falls noch nicht abgelegte Highscores existieren
        Level.highscoreliste.append((datetime.now().strftime("%Y-%m-%d %H:%M"), len(Level.levelliste), Level.berechneHighscore()))

    try:
        with open(os.path.join(location, "highscore.txt"), "w") as f:
            for item in liste:
                f.write(str(item) + "\n")
    except:
        print("Datei konnte nicht geschrieben werden!")


def events():
    """
    Beschreibung:
        - Erfassung aller relevanten Events
        - relevante Daten: ESC-Taste, Linke Maustaste, Mausposition, Schließen des Spiels
    Parameter:
        - Keine
    Rueckgabe:
        - Maus-Position, Linker Maus Klickstatus

    Tests:
        - Ausgabe der Return Values um richtige Werte zu pruefen
        - print bei den Funktionsaufrufen um Erkennung der Events zu checken
        - Fenstergroesse veraendern um richtige Darstellung zu pruefen
    """

    maus_klick_flag = False 

    for event in pg.event.get():
        if event.type == pg.QUIT:
            beenden()

        if event.type == pg.MOUSEBUTTONUP:
            maus_klick_flag = True

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                if(len(Level.levelliste) > 0):
                    Level.toggleEsc()

        if event.type == pg.VIDEORESIZE: #bei Veraenderung der Fenstergroesse
            Level.breite, Level.hoehe = event.size
            pg.display.set_mode(event.size, DISPLAYFLAG, DISPLAYCOLBIT)
            Level.anpassen_Hintergruende()
            
    mouse = pg.mouse.get_pos()

    return mouse, maus_klick_flag

def beenden():
    """
    Beschreibung:
        - kontrolliertes Schließen des Spiels
        - Speichern des Highscores vorm Beenden
    Parameter:
        - Keine
    Rueckgabe:
        - Maus-Position, Linker Maus Klickstatus

    Tests:
        - Anwendung auf verschiedene Weisen schließen und schauen, dass das Speichern des Highscores noch aufgerufen wurde
    """

    speichere_Highscore(Level.highscoreliste)
    pg.quit()
    quit()

def mainloop():
    """
    Beschreibung:
        - Mainloop des Spiels
        - Ausgangspunkt aller Funktionen
    Parameter:
        - Keine
    Rueckgabe:
        - Keine

    Tests:
        Pruefung:
        - korrektes Aufrufen der Funktionen
    """
    lade_Highscore() #laden eines moeglicherweise gespeicherten Highscores

    while True:
        maus_pos, klick = events()

        Level.main_Level(maus_pos, klick) #Logik findet im Level statt
        display.blit(fadenkreuzIMG, (maus_pos[0] - 25, maus_pos[1] - 25)) #Mauszeiger zeichnen

        pg.display.update()
        clock.tick(FRAMERATE)

if __name__ == "__main__":
    mainloop()