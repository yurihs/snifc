from pathlib import Path
import functools
import sys
from PyQt5 import QtCore, QtWidgets, QtChart, uic
from snifc import utils
from snifc.sniffer import capturar_continuosamente

class CapturaMonitor(QtCore.QObject):
    pacote_signal = QtCore.pyqtSignal(tuple)
    def __init__(self):
        super().__init__()

    @QtCore.pyqtSlot(str)
    def monitorar_pacotes(self, interface):
        for pacote in capturar_continuosamente(interface):
            self.pacote_signal.emit(pacote)


class SnifcWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        diretorio_projeto = Path(__file__).parent
        uic.loadUi(diretorio_projeto / 'snifc.ui', self)

        self._init_menu_arquivo()
        self._init_menu_capturas()
        self._init_grafico_num_pacotes()
        self._init_tabela_de_captura()

    def _init_menu_arquivo(self):
        self.actionAbrir.triggered.connect(lambda x: print('HI'))

    def _init_menu_capturas(self):
        self.monitor_capturas = CapturaMonitor()
        self.thread_captura = QtCore.QThread(self)
        self.monitor_capturas.pacote_signal.connect(self.append_pacote)
        self.monitor_capturas.moveToThread(self.thread_captura)
        self.menuIniciarCaptura.clear()
        self.menuIniciarCaptura.addActions(self._construir_acoes_de_captura())

    def _init_tabela_de_captura(self):
        cabecalhos = ['Tempo', 'De', 'Para', 'Domínio']
        self.tabelaCaptura.setColumnCount(len(cabecalhos))
        self.tabelaCaptura.setHorizontalHeaderLabels(cabecalhos)

    def _init_grafico_num_pacotes(self):
        chart = QtChart.QChart()
        chart.legend().hide()
        self.graficoNumPacotes.setChart(chart)

    def _construir_acoes_de_captura(self):
        actions = []
        for name in utils.get_tshark_interface_names():
            action = QtWidgets.QAction(name, self)
            action.triggered.connect(functools.partial(self._iniciar_captura, name))
            actions.append(action)
        return actions

    def _iniciar_captura(self, interface):
            self.thread_captura.started.connect(
                functools.partial(self.monitor_capturas.monitorar_pacotes, interface)
            )
            self.thread_captura.start()

    @QtCore.pyqtSlot(tuple)
    def append_pacote(self, pacote):
        self._append_pacote_tabela(pacote)
        self._append_pacote_grafico(pacote)

    def _append_pacote_tabela(self, pacote):
        n_rows = self.tabelaCaptura.rowCount()
        self.tabelaCaptura.insertRow(n_rows)
        for i, data in enumerate(pacote):
            self.tabelaCaptura.setItem(n_rows, i, QtWidgets.QTableWidgetItem(str(data)))

    def _append_pacote_grafico(self, pacote):
        chart = self.graficoNumPacotes.chart()
        series = chart.series()
        if len(series) == 0:
            curve = QtChart.QLineSeries()
            curve.append(QtCore.QPointF(curve.count(), float(pacote[0])))
            chart.addSeries(curve)
            chart.createDefaultAxes()
        else:
            curve = series[0]
            max_y = max(p.y() for p in curve.pointsVector())
            curve.append(QtCore.QPointF(curve.count(), float(pacote[0])))
            chart.axisX().setRange(0, curve.count()-1)
            chart.axisY().setRange(0, max(max_y, float(pacote[0])))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = SnifcWindow()
    window.show()
    sys.exit(app.exec_())
