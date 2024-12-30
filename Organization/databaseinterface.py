# Graphical interface for interacting with the database for this project.
# Provides statistics for each deck, as well as [i dunno]

import sqlite3

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QPalette, QBrush, QColor, QPainter
from PySide6.QtCharts import QChart, QPieSeries, QChartView, QPieSlice
from PySide6.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QTabWidget,
    QLineEdit,
    QLabel,
    QDialog,
    QMenuBar,
    QTableWidget,
    QTableWidgetItem
)

### Database stuff

# Absolute path to the database file
dbpath = 'E:\\Creations\\Programming\\WebDev\\MTG Customs\\MTG-Customs\\Organization\\mtgc.db'
con = sqlite3.connect(dbpath)
cursor = con.cursor()

def editDB(query):
    cursor.execute(query)
    con.commit()

def fetchValue(query):
    try:
        return cursor.execute(query).fetchone()[0]
    except:
        print("Bad Fetch")

decks = cursor.execute('''SELECT name FROM sqlite_schema WHERE type='table' AND name NOT LIKE 'cards';''').fetchall()
for deck in decks:
    decks[decks.index(deck)] = decks[decks.index(deck)][0]
deckIndex = 0

# if there are no cards in the all cards table, create the table (i don't know sql)
try:
    editDB("SELECT * FROM cards")
except sqlite3.OperationalError as e:
    print(e)
    editDB("CREATE TABLE cards(name TEXT PRIMARY KEY, url TEXT DEFAULT '', type TEXT, rules TEXT, acost INTEGER DEFAULT 0, wcost INTEGER DEFAULT 0, bcost INTEGER DEFAULT 0, ucost INTEGER DEFAULT 0, rcost INTEGER DEFAULT 0, gcost INTEGER DEFAULT 0, ccost INTEGER DEFAULT 0, mcost AS (acost + wcost + bcost + ucost + rcost + gcost + ccost))")
    # editDB("CREATE TABLE FILLER_DECK(name TEXT DEFAULT '')")
    # editDB("INSERT INTO cards(name) VALUES('FILLER_CARD')")
    # editDB("INSERT INTO FILLER_DECK VALUES('FILLER_CARD')")
    # decks.append("FILLER_DECK")
except Exception as e:
    print(f"ok something weird happened: {e}")

deckName = ""

### GUI stuff

class viewTab(QWidget):
    def __init__(self):
        super().__init__()

        if len(decks) > 0:
            table = QTableWidget(0, 11)
            table.setHorizontalHeaderLabels(["Name","Type","Rules", "Any Color", "White", "Black", "Blue", "Red", "Green", "Colorless", "Total Cost"])

            cards = cursor.execute(f'''SELECT name, type, rules, acost, wcost, bcost, ucost, rcost, gcost, ccost, mcost FROM cards WHERE name IN (SELECT name FROM {decks[deckIndex]})''').fetchall()

            for row in range(len(cards)):
                table.insertRow(row)
                for column in range(table.columnCount()):
                    table.setCurrentCell(row, column)
                    item = QTableWidgetItem(str(cards[row][column]))
                    match column:
                        case 3:
                            item.setBackground(QBrush(QColor(Qt.lightGray)))
                        case 4:
                            item.setBackground(QBrush(QColor(Qt.yellow)))
                        case 5:
                            item.setBackground(QBrush(QColor(Qt.darkGray)))
                        case 6:
                            item.setBackground(QBrush(QColor(Qt.cyan)))
                        case 7:
                            item.setBackground(QBrush(QColor(Qt.magenta)))
                        case 8:
                            item.setBackground(QBrush(QColor(Qt.green)))
                        case 9:
                            item.setBackground(QBrush(QColor(Qt.gray)))
                        case _:
                            item.setBackground(QBrush(QColor(Qt.white)))
                    table.setItem(row, column, item)
            table.setSortingEnabled(True)
            table.setCurrentCell(0, 0)

            layout = QGridLayout()
            layout.addWidget(table, 0, 0)

            self.setLayout(layout)

class addCardDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Add Card")

        # Declaring default values
        self.name = ''
        self.url = ''
        self.type = ''
        self.rules = ''
        self.mana = ''
        self.acost = 0
        self.wcost = 0
        self.bcost = 0
        self.ucost = 0
        self.rcost = 0
        self.gcost = 0
        self.ccost = 0

        layout = QHBoxLayout()

        nameField = QLineEdit()
        nameField.setPlaceholderText("Enter Card Name")
        nameField.textChanged.connect(lambda text: self.fieldChanged(text, "name"))
        layout.addWidget(nameField)

        ## I'm not sure I actually want to add the URL. I can't think of anything i'd use it for, except the auto-deck-creation which is iffy anyways.
        # urlField = QLineEdit()
        # urlField.setPlaceholderText("Enter Card URL")
        # urlField.textChanged.connect(lambda text: self.fieldChanged(text, "url"))
        # layout.addWidget(urlField)

        # Adding all the input fields
        typeField = QLineEdit()
        typeField.setPlaceholderText("Enter Card Type")
        typeField.textChanged.connect(lambda text: self.fieldChanged(text, "type"))
        layout.addWidget(typeField)

        rulesField = QLineEdit()
        rulesField.setPlaceholderText("Enter Card Rules Text")
        rulesField.textChanged.connect(lambda text: self.fieldChanged(text, "rules"))
        layout.addWidget(rulesField)

        manaField = QLineEdit()
        manaField.setPlaceholderText("Enter Card Mana Cost")
        manaField.textChanged.connect(lambda text: self.fieldChanged(text, "mana"))
        layout.addWidget(manaField)

        # Button to trigger adding the card
        submitButton = QPushButton("Submit")
        submitButton.pressed.connect(self.addCard)
        layout.addWidget(submitButton)

        self.setLayout(layout)

    def fieldChanged(self, text, field):
        match field:
            case "name":
                self.name = text
            case "url":
                print("URL not supported yet")
            case "type":
                self.type = text
            case "rules":
                self.rules = text
            case "mana":
                self.mana = text
            case _:
                print("Unknown Field")

    def addCard(self):
        # Looping over the Mana string, using standard MTG color keys
        for char in self.mana:
                    if char.isdigit():
                        # Any color mana
                        self.acost += int(char)
                    elif char == 'w':
                        # White mana
                        self.wcost += 1
                    elif char == 'b':
                        # Black mana
                        self.bcost += 1
                    elif char == 'u':
                        # Blue mana
                        self.ucost += 1
                    elif char == 'r':
                        # Red mana
                        self.rcost += 1
                    elif char == 'g':
                        # Green mana
                        self.gcost += 1
                    elif char == 'c':
                        # Colorless mana
                        self.ccost += 1
                    else:
                        print("Unknown mana")
        # Query to add the card to the `cards` masterlist
        cardsQuery = f'''INSERT INTO cards VALUES('{self.name}', '{self.url}', '{self.type}', '{self.rules}', {self.acost}, {self.wcost}, {self.bcost}, {self.ucost}, {self.rcost}, {self.gcost}, {self.ccost});'''
        # Try adding it, if it already exists move on.
        try:
            editDB(cardsQuery)
        except sqlite3.IntegrityError:
            pass
        except Exception as e:
            print(f"Something broke adding a card: {e}")
        # Add the card to the deck
        deckQuery = f'''INSERT INTO {decks[deckIndex]} VALUES('{self.name}');'''
        editDB(deckQuery)
        self.close()

class editCardDialog(QDialog):
    def __init__(self, cardName):
        super().__init__()

        self.setWindowTitle("Edit Card")

        self.passedName = cardName

        # Check if the card exists
        if fetchValue(f'''SELECT name FROM cards WHERE name='{cardName}';''') != cardName:
            return
        # Assign the variables
        self.name = fetchValue(f'''SELECT name FROM cards WHERE name='{cardName}';''')
        self.url = fetchValue(f'''SELECT url FROM cards WHERE name='{cardName}';''')
        self.type = fetchValue(f'''SELECT type FROM cards WHERE name='{cardName}';''')
        self.rules = fetchValue(f'''SELECT rules FROM cards WHERE name='{cardName}';''')
        self.acost = fetchValue(f'''SELECT acost FROM cards WHERE name='{cardName}';''')
        self.wcost = fetchValue(f'''SELECT wcost FROM cards WHERE name='{cardName}';''')
        self.bcost = fetchValue(f'''SELECT bcost FROM cards WHERE name='{cardName}';''')
        self.ucost = fetchValue(f'''SELECT ucost FROM cards WHERE name='{cardName}';''')
        self.rcost = fetchValue(f'''SELECT rcost FROM cards WHERE name='{cardName}';''')
        self.gcost = fetchValue(f'''SELECT gcost FROM cards WHERE name='{cardName}';''')
        self.ccost = fetchValue(f'''SELECT ccost FROM cards WHERE name='{cardName}';''')

        self.values = [self.name, self.url, self.type, self.rules, self.acost, self.wcost, self.bcost, self.ucost, self.rcost, self.gcost, self.ccost]
        print(self.values)

        layout = QGridLayout()

        nameField = QLineEdit()
        nameField.setText(self.name)
        nameField.setToolTip("Name Field")
        nameField.textChanged.connect(lambda text: self.fieldChanged(text, "name"))
        layout.addWidget(nameField, 0, 0)

        urlField = QLineEdit()
        urlField.setText(self.url)
        urlField.setToolTip("URL Field")
        urlField.textChanged.connect(lambda text: self.fieldChanged(text, "url"))
        layout.addWidget(urlField, 0, 1)

        typeField = QLineEdit()
        typeField.setText(self.type)
        typeField.setToolTip("Type Field")
        typeField.textChanged.connect(lambda text: self.fieldChanged(text, "type"))
        layout.addWidget(typeField, 0, 2)

        rulesField = QLineEdit()
        rulesField.setText(self.rules)
        rulesField.setToolTip("Rules Field")
        rulesField.textChanged.connect(lambda text: self.fieldChanged(text, "rules"))
        layout.addWidget(rulesField, 1, 0)

        # Tried setting the background color of the text boxes but none of it worked i don't know why and i don't really care right now.
        acostField = QLineEdit()
        acostField.setText(str(self.acost))
        acostField.setToolTip("Any Mana Field")
        acostField.palette().setColor(QPalette.Window, 'lightGray')
        acostField.textChanged.connect(lambda text: self.fieldChanged(text, "acost"))
        layout.addWidget(acostField, 1, 1)

        wcostField = QLineEdit()
        wcostField.setText(str(self.wcost))
        wcostField.setToolTip("White Mana Field")
        wcostField.palette().setColor(QPalette.Window, 'yellow')
        wcostField.textChanged.connect(lambda text: self.fieldChanged(text, "wcost"))
        layout.addWidget(wcostField, 1, 2)

        bcostField = QLineEdit()
        bcostField.setText(str(self.bcost))
        bcostField.setToolTip("Black Mana Field")
        bcostField.palette().setColor(QPalette.Window, 'darkGray')
        bcostField.textChanged.connect(lambda text: self.fieldChanged(text, "bcost"))
        layout.addWidget(bcostField, 2, 0)

        ucostField = QLineEdit()
        ucostField.setText(str(self.ucost))
        ucostField.setToolTip("Blue Mana Field")
        ucostField.palette().setColor(QPalette.Window, 'blue')
        ucostField.textChanged.connect(lambda text: self.fieldChanged(text, "ucost"))
        layout.addWidget(ucostField, 2, 1)

        rcostField = QLineEdit()
        rcostField.setText(str(self.rcost))
        rcostField.setToolTip("Red Mana Field")
        rcostField.palette().setColor(QPalette.Window, 'red')
        rcostField.textChanged.connect(lambda text: self.fieldChanged(text, "rcost"))
        layout.addWidget(rcostField, 2, 2)

        gcostField = QLineEdit()
        gcostField.setText(str(self.gcost))
        gcostField.setToolTip("Red Mana Field")
        gcostField.palette().setColor(QPalette.Window, 'green')
        gcostField.textChanged.connect(lambda text: self.fieldChanged(text, "gcost"))
        layout.addWidget(gcostField, 3, 0)

        ccostField = QLineEdit()
        ccostField.setText(str(self.ccost))
        ccostField.setToolTip("Colorless Mana Field")
        ccostField.palette().setColor(QPalette.Window, 'gray')
        ccostField.textChanged.connect(lambda text: self.fieldChanged(text, "ccost"))
        layout.addWidget(ccostField, 3, 1)

        # Button to trigger adding the card
        submitButton = QPushButton("Submit")
        submitButton.pressed.connect(self.editCard)
        layout.addWidget(submitButton, 3, 2)

        self.setLayout(layout)

    def fieldChanged(self, text, field):
        match field:
            case "name":
                self.name = text
            case "url":
                print("URL not supported yet")
            case "type":
                self.type = text
            case "rules":
                self.rules = text
            case "acost":
                self.acost = text
            case "wcost":
                self.wcost = text
            case "bcost":
                self.bcost = text
            case "ucost":
                self.ucost = text
            case "rcost":
                self.rcost = text
            case "gcost":
                self.gcost = text
            case "ccost":
                self.ccost = text
            case _:
                print("Unknown Field")

    def editCard(self):
        deckQuery = f'''UPDATE cards 
                    SET name='{self.name}', url='{self.url}', type='{self.type}', rules='{self.rules}', acost={self.acost}, wcost={self.wcost}, bcost={self.bcost}, ucost={self.ucost}, rcost={self.rcost}, gcost={self.gcost}, ccost={self.ccost} 
                    WHERE name='{self.passedName}';'''
        editDB(deckQuery)
        self.close()

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

        editCardName = QLineEdit()
        # Arbitrary limit just to make it so there's no overflow.
        editCardName.setMaxLength(45)
        editCardName.setPlaceholderText("Enter card name to edit")
        editCardName.textChanged.connect(self.editTextChanged)
        layout.addWidget(editCardName, 1, 1)

        removeButton = QPushButton("Remove Card")
        removeButton.clicked.connect(self.removeCard)

        layout.addWidget(removeButton, 2, 0)
        
        removeCardName = QLineEdit()
        # Arbitrary limit just to make it so there's no overflow.
        removeCardName.setMaxLength(45)
        removeCardName.setPlaceholderText("Enter card name to be removed")
        removeCardName.textChanged.connect(self.removeTextChanged)
        layout.addWidget(removeCardName, 2, 1)

        self.removeName = ""
        self.editName = ""

        # TODO: implement Generate Deck button (going to the TTSdeckbuilder application and creating a deck) (this might be going too far for right now)

        self.setLayout(layout)

    def editTextChanged(self, text):
        self.editName = text

    def removeTextChanged(self, text):
        self.removeName = text

    def addCard(self):
        dialog = addCardDialog()
        dialog.exec()

    def editCard(self):
        dialog = editCardDialog(self.editName)
        dialog.exec()

    def removeCard(self):
        editDB(f'''DELETE FROM {decks[deckIndex]} WHERE name='{self.removeName}';''')
        print("Removed " + self.removeName)

class statsTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QGridLayout()

        cardCount = cursor.execute(f'''SELECT COUNT(*) FROM cards WHERE name IN (SELECT name FROM {decks[deckIndex]})''').fetchone()[0]
        if cardCount > 0:
            countLabel = QLabel(f"{cardCount} cards")
            countLabel.setAlignment(Qt.AlignHCenter)

            total = cursor.execute(f'''SELECT SUM(mcost) FROM cards WHERE name IN (SELECT name FROM {decks[deckIndex]})''').fetchone()[0]
            totalColor = total - cursor.execute(f'''SELECT SUM(acost) FROM cards WHERE name IN(SELECT name FROM {decks[deckIndex]})''').fetchone()[0]
            
            meanCost = str(total / cardCount)[:5]

            meanLabel = QLabel(f"{meanCost} mean CMC")
            meanLabel.setAlignment(Qt.AlignHCenter)

            colorData = QPieSeries()
            try:
                colorData.append(str((cursor.execute(f'''SELECT SUM(wcost) FROM cards WHERE name IN (SELECT name FROM {decks[deckIndex]}) AND wcost>0''').fetchone()[0] / totalColor) * 100)[:5] + "%", cursor.execute(f'''SELECT SUM(wcost) FROM cards WHERE name IN (SELECT name FROM {decks[deckIndex]})''').fetchone()[0])
            except TypeError:
                colorData.append("0", 0)
            try:
                colorData.append(str((cursor.execute(f'''SELECT SUM(bcost) FROM cards WHERE name IN (SELECT name FROM {decks[deckIndex]}) AND bcost>0''').fetchone()[0] / totalColor) * 100)[:5] + "%", cursor.execute(f'''SELECT SUM(bcost) FROM cards WHERE name IN (SELECT name FROM {decks[deckIndex]})''').fetchone()[0])
            except TypeError:
                colorData.append("0", 0)
            try:
                colorData.append(str((cursor.execute(f'''SELECT SUM(ucost) FROM cards WHERE name IN (SELECT name FROM {decks[deckIndex]}) AND ucost>0''').fetchone()[0] / totalColor) * 100)[:5] + "%", cursor.execute(f'''SELECT SUM(ucost) FROM cards WHERE name IN (SELECT name FROM {decks[deckIndex]})''').fetchone()[0])
            except TypeError:
                colorData.append("0", 0)
            try:
                colorData.append(str((cursor.execute(f'''SELECT SUM(rcost) FROM cards WHERE name IN (SELECT name FROM {decks[deckIndex]}) AND rcost>0''').fetchone()[0] / totalColor) * 100)[:5] + "%", cursor.execute(f'''SELECT SUM(rcost) FROM cards WHERE name IN (SELECT name FROM {decks[deckIndex]})''').fetchone()[0])
            except TypeError:
                colorData.append("0", 0)
            try:
                colorData.append(str((cursor.execute(f'''SELECT SUM(gcost) FROM cards WHERE name IN (SELECT name FROM {decks[deckIndex]}) AND gcost>0''').fetchone()[0] / totalColor) * 100)[:5] + "%", cursor.execute(f'''SELECT SUM(gcost) FROM cards WHERE name IN (SELECT name FROM {decks[deckIndex]})''').fetchone()[0])
            except TypeError:
                colorData.append("0", 0)
            try:
                colorData.append(str((cursor.execute(f'''SELECT SUM(ccost) FROM cards WHERE name IN (SELECT name FROM {decks[deckIndex]}) AND ccost>0''').fetchone()[0] / totalColor) * 100)[:5] + "%", cursor.execute(f'''SELECT SUM(ccost) FROM cards WHERE name IN (SELECT name FROM {decks[deckIndex]})''').fetchone()[0])
            except TypeError:
                colorData.append("0", 0)
            colorData.setPieSize(1)

            colors = [QColor(Qt.yellow), QColor(Qt.darkGray), QColor(Qt.cyan), QColor(Qt.magenta), QColor(Qt.green), QColor(Qt.gray)]
            colorIterator = 0
            for slice in colorData.slices():
                slice.setLabelPosition(QPieSlice.LabelInsideHorizontal)
                slice.setLabelVisible()
                slice.setColor(colors[colorIterator])
                colorIterator += 1

            colorChart = QChart()
            colorChart.addSeries(colorData)
            colorChart.setTitle("Color Percentage")
            colorChart.legend().hide()

            colorChartView = QChartView(colorChart)
            colorChartView.setRenderHint(QPainter.RenderHint.Antialiasing)

            typeData = QPieSeries()
            typeData.append("Creatures", cursor.execute(f'''SELECT COUNT(*) FROM cards WHERE name IN (SELECT name FROM {decks[deckIndex]}) AND type LIKE '%Creature%';''').fetchone()[0])
            typeData.append("Artifacts", cursor.execute(f'''SELECT COUNT(*) FROM cards WHERE name IN (SELECT name FROM {decks[deckIndex]}) AND type LIKE '%Artifact%';''').fetchone()[0])
            typeData.append("Sorceries", cursor.execute(f'''SELECT COUNT(*) FROM cards WHERE name IN (SELECT name FROM {decks[deckIndex]}) AND type LIKE '%Sorcery%';''').fetchone()[0])
            typeData.append("Enchantments", cursor.execute(f'''SELECT COUNT(*) FROM cards WHERE name IN (SELECT name FROM {decks[deckIndex]}) AND type LIKE '%Enchantment%';''').fetchone()[0])

            typeData.setPieSize(1)

            for slice in typeData.slices():
                slice.setLabelPosition(QPieSlice.LabelInsideHorizontal)
                slice.setLabelVisible()

            typeChart = QChart()
            typeChart.addSeries(typeData)
            typeChart.setTitle("Card Type Percentage")
            typeChart.legend().hide()

            typeChartView = QChartView(typeChart)
            typeChartView.setRenderHint(QPainter.RenderHint.Antialiasing)

            layout.addWidget(countLabel, 0, 0)
            layout.addWidget(meanLabel, 0, 1)
            layout.addWidget(colorChartView, 1, 0)
            layout.addWidget(typeChartView, 1, 1)

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
        editDB("CREATE TABLE " + self.name + "(NAME TEXT)")
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

        if len(decks) < 1:
            self.createNewDeck()
        
        ## Call the menu setup function
        self.drawMenu()

        ## Call the tabs setup function
        self.drawTabs()

    def drawMenu(self):
        menu = QMenuBar()

        deckMenu = menu.addMenu("&Deck")
        
        # Add all the decks
        for deck in decks:
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

        # Add the Refresh button
        refreshAction = QAction("&Refresh", self)
        refreshAction.triggered.connect(self.update)
        menu.addAction(refreshAction)

        self.setMenuBar(menu)

    def drawTabs(self):
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)

        # Tab for viewing the deck list
        self.tabs.addTab(viewTab(), "View")
        # Tab for editing the database
        self.tabs.addTab(editTab(), "Edit")
        # Tab for viewing deck statistics
        self.tabs.addTab(statsTab(), "Statistics")

        self.setCentralWidget(self.tabs)

    def deckSelect(self, x, index):
        global deckIndex
        deckIndex = index
        self.update()
        print("Deck Selected: " + decks[deckIndex])

    def createNewDeck(self):
        dialog = newDeckDialog()
        dialog.exec()
        self.update()

    def openAboutDialog(self):
        dialog = aboutDialog()
        dialog.exec()

    def update(self):
        self.drawTabs()
        self.drawMenu()

app = QApplication([])

window = MainWindow()
window.show()


### Other stuff

app.exec()