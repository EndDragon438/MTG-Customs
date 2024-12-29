# Graphical interface for interacting with the database for this project.
# Provides statistics for each deck, as well as [i dunno]

import sqlite3

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QGridLayout,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QTabWidget,
    QLineEdit,
    QLabel,
    QDialog,
    QMenuBar
)

### Database stuff

# Absolute path to the database file
dbpath = 'E:\\Creations\\Programming\\WebDev\\MTG Customs\\MTG-Customs\\Organization\\mtgc.db'
conn = sqlite3.connect(dbpath)
cursor = conn.cursor()

def queryDB(query):
    cursor.execute(query)

decks = cursor.execute('''SELECT name FROM sqlite_schema WHERE type='table' AND name NOT LIKE 'cards';''').fetchall()
for deck in decks:
    decks[decks.index(deck)] = decks[decks.index(deck)][0]
deckIndex = 0

# if there are no cards in the all cards table, create the table (i don't know sql)
try:
    queryDB("SELECT * FROM cards")
except sqlite3.OperationalError as e:
    print(e)
    queryDB("CREATE TABLE cards(NAME TEXT PRIMARY KEY, URL TEXT, TYPE TEXT, RULES TEXT, ACOST INTEGER DEFAULT 0, WCOST INTEGER DEFAULT 0, BCOST INTEGER DEFAULT 0, UCOST INTEGER DEFAULT 0, RCOST INTEGER DEFAULT 0, GCOST INTEGER DEFAULT 0, CCOST INTEGER DEFAULT 0)")
except Exception as e:
    print(f"ok something weird happened: {e}")

deckName = ""

# TODO: Create a constant for each deck (table)
# TODO: Columns: Name, URL (absolute filepath to image), Type (subtype seperate or combined with Type?), Cost (seperate column for each color, or use formatting?)
# TODO: Create table for ALL cards created.
# TODO: Deck tables have 1 column (NAME TEXT) and pull from card masterlist

### GUI stuff

class viewTab(QWidget):
    def __init__(self):
        super().__init__()

        # TODO: display table for currently selected deck

class editTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QGridLayout()

        addButton = QPushButton("Add Card")
        addButton.clicked.connect(self.addCard)
        layout.addWidget(addButton, 0, 0)

        addButton = QPushButton("Edit Card")
        addButton.clicked.connect(self.editCard)
        layout.addWidget(addButton, 1, 0)

        removeButton = QPushButton("Remove Card")
        removeButton.clicked.connect(self.removeCard)

        layout.addWidget(removeButton, 2, 0)
        
        removeCardName = QLineEdit()
        # Arbitrary limit just to make it so there's no overflow.
        removeCardName.setMaxLength(45)
        removeCardName.setPlaceholderText("Enter card name to be removed")
        removeCardName.textChanged.connect(self.textChanged)
        layout.addWidget(removeCardName, 2, 1)

        self.cardName = ""

        # TODO: implement Generate Deck button (going to the TTSdeckbuilder application and creating a deck) (this might be going too far for right now)

        self.setLayout(layout)

    def textChanged(self, text):
        self.cardName = text

    # TODO: implement Add Card button. Add to deck, and cards (update if already exists)
    def addCard(self):
        # TODO: open popup window with inputs for each column for the currently selected deck
        print("addCard called")
        queryDB(f'''INSERT IF NOT EXISTS INTO {deckName}''')

    # TODO: implement Edit Card button. Update card in `cards` table
    def editCard(self):
        # TODO: open popup window with inputs for each column for the currently selected deck
        print("editCard called")

    # TODO: implement Remove Card button. Removes card from `cards` table and current deck
    def removeCard(self):
        print("Removed " + self.cardName)
        queryDB()
        # TODO: remove `name` card from the current deck

class statsTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Card Count: "))
        layout.addWidget(QLabel("Colors: "))
        layout.addWidget(QLabel("Average Mana Cost: "))
        layout.addWidget(QLabel("there should be a pie chart here"))
        layout.addWidget(QLabel("Types: "))

        # TODO: add Card Count label
        # TODO: add Colors label (shows what colors the deck is by mana cost)
        # TODO: add Average CMC label
        # TODO: add pie chart for color makeup
        # TODO: add Types table (showing types and subtypes, with counts)

        self.setLayout(layout)

class newDeckDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Create New Deck")

        layout = QVBoxLayout()

        textInput = QLineEdit()
        textInput.setPlaceholderText("Enter Deck Name")
        textInput.textChanged.connect(self.textChanged)
        layout.addWidget(textInput)

        submitButton = QPushButton("Submit")
        submitButton.pressed.connect(self.createDeck)
        layout.addWidget(submitButton)

        self.setLayout(layout)

    def textChanged(self, text):
        self.name = text

    def createDeck(self):
        queryDB("CREATE TABLE " + self.name + "(NAME TEXT)")
        decks.append(self.name)
        self.close()

class aboutDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("About")

        layout = QVBoxLayout()
        label = QLabel(
            '''
            Graphical interface for editing the
            custom MTG card database & decks.

            Made by End, December 2024
            ''')
        label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(label)
        
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        ## Generic window stuff
        self.setWindowTitle("MTGC Database Interface")
        self.setMinimumSize(QSize(400, 400))
        self.drawMenu()

        ## All the tabs stuff
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)

        # Tab for viewing the deck list
        tabs.addTab(viewTab(), "View")
        # Tab for editing the database
        tabs.addTab(editTab(), "Edit")
        # Tab for viewing deck statistics
        tabs.addTab(statsTab(), "Statistics")

        self.setCentralWidget(tabs)

    def drawMenu(self):
        menu = QMenuBar()

        deckMenu = menu.addMenu("&Deck")
        
        # Add all the decks
        for deck in decks:
            print("new deck: " + deck)
            action = QAction(deck, self)
            action.triggered.connect(lambda deckAction, index = decks.index(deck): self.deckSelect(deckAction, index))
            deckMenu.addAction(action)

        deckMenu.addSeparator()

        # Add the New Deck button
        newDeckButton = QAction("+ New Deck", self)
        newDeckButton.triggered.connect(self.createNewDeck)
        deckMenu.addAction(newDeckButton)

        # Add the Help menu
        aboutMenu = menu.addMenu("&Help")
        aboutAction = QAction("About", self)
        aboutAction.triggered.connect(self.openAboutDialog)
        aboutMenu.addAction(aboutAction)

        self.setMenuBar(menu)

    def deckSelect(self, x, index):
        deckIndex = index
        print("Deck Selected: " + decks[deckIndex])

    def createNewDeck(self):
        # TODO: Popup asking for name of the deck. Create new deck (table) in  DB with supplied name. if deck of same name already exists, popup error and DO NOT OVERWRITE
        print("createNewDeck called")
        dialog = newDeckDialog()
        dialog.exec()
        self.drawMenu()

    def openAboutDialog(self):
        dialog = aboutDialog()
        dialog.exec()

app = QApplication([])

window = MainWindow()
window.show()


### Other stuff

app.exec()