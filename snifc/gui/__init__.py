import sys
from PyQt5 import QtWidgets
from snifc.gui.main import SnifcWindow

def run():
    app = QtWidgets.QApplication(sys.argv)
    window = SnifcWindow()
    window.show()
    sys.exit(app.exec_())
