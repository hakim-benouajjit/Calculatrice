import sys
import speech_recognition as sr
import pytesseract
import easygui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWidget
from functools import partial
from PIL import Image

ERROR_MSG = 'ERROR'


#                       VIEW        #####################
class CalculatriceUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Calculatrice')
        self.setFixedSize(450, 540)
        self.generalLayout = QVBoxLayout()
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)
        self._createDisplay()
        self._createButtons()

    def _createDisplay(self):
        self.display = QLineEdit()
        self.display.setFixedHeight(70)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setReadOnly(True)
        self.generalLayout.addWidget(self.display)

    def _createButtons(self):
        self.buttons = {}
        buttonsLayout = QGridLayout()

        buttons = {'7': (0, 0), '8': (0, 1), '9': (0, 2), '/': (0, 3), 'C': (0, 4),
                   '4': (1, 0), '5': (1, 1), '6': (1, 2), '*': (1, 3), '(': (1, 4),
                   '1': (2, 0), '2': (2, 1), '3': (2, 2), '-': (2, 3), ')': (2, 4),
                   '0': (3, 0), '00': (3, 1), '.': (3, 2), '+': (3, 3), '=': (3, 4),

                   'Image': (5, 0),                                  'Talk': (5, 4),
                   }

        for btnText, pos in buttons.items():
            self.buttons[btnText] = QPushButton(btnText)
            self.buttons[btnText].setFixedSize(80, 80)
            buttonsLayout.addWidget(self.buttons[btnText], pos[0], pos[1])
        self.generalLayout.addLayout(buttonsLayout)

    def setDisplayText(self, text):
        self.display.setText(text)
        self.display.setFocus()

    def displayText(self):
        return self.display.text()

    def clearDisplay(self):
        self.setDisplayText('')


#                 CONTROLLER        #####################
class CalculatriceCtrl:
    def __init__(self, model, view):
        self._evaluate = model
        self._view = view
        self._connectSignals()

    def _calculateResult(self):
        result = self._evaluate(expression = self._view.displayText())
        self._view.setDisplayText(result)

    def _buildExpression(self, sub_exp):
        if self._view.displayText() == ERROR_MSG:
            self._view.clearDisplay()
        expression = self._view.displayText() + sub_exp
        self._view.setDisplayText(expression)

    def _speech(self):

        r = sr.Recognizer()
        with sr.Microphone() as mic:
            r.adjust_for_ambient_noise(mic)
            self._view.clearDisplay()
            audio = r.listen(mic)
            try:
                expression = r.recognize_google(audio)
                self._view.setDisplayText(expression)
            except Exception as e:
                self._view.setDisplayText(ERROR_MSG)

    def _image(self):
        image = easygui.fileopenbox()
        pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract'
        TESSDATA_PREFIX = 'C:/Program Files/Tesseract-OCR'
        expression = pytesseract.image_to_string(Image.open(image))
        self._view.clearDisplay()
        self._view.setDisplayText(expression)


    def _connectSignals(self):
        for btnText, btn in self._view.buttons.items():
            if btnText not in {'=', 'C', 'Talk', 'Image'}:
                btn.clicked.connect(partial(self._buildExpression, btnText))
        self._view.buttons['='].clicked.connect(self._calculateResult)
        self._view.buttons['C'].clicked.connect(self._view.clearDisplay)
        self._view.buttons['Talk'].clicked.connect(self._speech)
        self._view.buttons['Image'].clicked.connect(self._image)

#                    MODEL        #####################


def evaluateExpression(expression):
    try:
        result = str(eval(expression, {}, {}))
    except:
        result = ERROR_MSG

    return result

#                      MAIN        #####################


def main():
    calculatrice = QApplication(sys.argv)
    view = CalculatriceUI()
    view.show()
    model = evaluateExpression
    CalculatriceCtrl(model=model, view=view)
    sys.exit(calculatrice.exec())

if __name__ == '__main__':
    main()
