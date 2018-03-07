from pathlib import Path
from PyQt5 import Qt, QtCore, QtWidgets, QtChart, uic
from snifc.utils import get_tshark_interface_names, get_project_dir

class DialogoCapturar(QtWidgets.QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Carregar a interface do arquivo exportado pelo Qt Designer
        uic.loadUi(get_project_dir() / 'gui/dialogo_capturar.ui', self)

        self.buttonGroup = Qt.QButtonGroup(self)

        botoes = (Qt.QRadioButton(nome) for nome in get_tshark_interface_names())
        for i, botao in enumerate(botoes):
            if i == 0:
                botao.setChecked(True)
            self.layoutBotoes.addWidget(botao)
            self.buttonGroup.addButton(botao)

    def interface_selecionada(self) -> str:
        return self.buttonGroup.checkedButton().text()
