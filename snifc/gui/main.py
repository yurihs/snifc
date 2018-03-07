from pathlib import Path
import functools
import sys
from PyQt5 import QtCore, QtWidgets, QtChart, uic
from snifc import utils
from snifc.sniffer import capturar_continuosamente
from snifc.gui.dialogo_capturar import DialogoCapturar

class CapturaMonitor(QtCore.QObject):
    """
    Monitura uma captura de pacotes vinda de um sniffer,
    emitindo eventos a cada novo pacote.
    """
    pacote_signal = QtCore.pyqtSignal(tuple)

    @QtCore.pyqtSlot(str)
    def monitorar_pacotes(self, interface: str):
        """
        Inicia uma nova captura contínua em uma interface.

        Args:
            interface: A interface a ser monitorada.

        """
        for pacote in capturar_continuosamente(interface):
            self.pacote_signal.emit(pacote)


class SnifcWindow(QtWidgets.QMainWindow):
    """
    Janela principal.
    """
    def __init__(self):
        super().__init__()

        diretorio_gui = Path(__file__).parent
        # Carregar a interface do arquivo exportado pelo Qt Designer
        uic.loadUi(diretorio_gui / 'main.ui', self)

        self.dialogo_capturar = DialogoCapturar(self)

        self.monitor_capturas = CapturaMonitor()
        self.thread_captura = QtCore.QThread(self)
        self._init_monitor_captura()

        # Inicialização dos componentes da interface
        self._init_menu_arquivo()
        self._init_menu_capturas()
        self._init_grafico_num_pacotes()
        self._init_tabela_de_captura()
        self._init_dialogo_capturar()

    def _init_menu_arquivo(self):
        """
        Inicializa o menu "Arquivo".
        """
        # self.actionAbrir.triggered.connect()
        pass

    def _init_menu_capturas(self):
        """
        Inicializa o menu "Capturas".
        """
        self.actionIniciarCaptura.triggered.connect(self.dialogo_capturar.open)
        self.actionInterromperCaptura.triggered.connect(self.interromper_captura)

    def _init_tabela_de_captura(self):
        """
        Inicializa a tabela que mostra os pacotes da captura.
        """
        cabecalhos = ['Tempo', 'IP de origem', 'IP de destino', 'Domínio']
        self.tabelaCaptura.setColumnCount(len(cabecalhos))
        self.tabelaCaptura.setHorizontalHeaderLabels(cabecalhos)

    def _init_grafico_num_pacotes(self):
        """
        Inicializa o gráfico que representa o fluxo de pacotes.
        """
        chart = QtChart.QChart()
        chart.legend().hide()
        self.graficoNumPacotes.setChart(chart)

    def _init_dialogo_capturar(self):
        """
        Inicializa o dialogo de iniciar captura.
        """
        self.dialogo_capturar.accepted.connect(self._dialogo_capturar_aceito)

    def _dialogo_capturar_aceito(self):
        """
        Chamado quando o dialogo "Iniciar captura" é aceito (OK).
        """
        self.iniciar_captura(self.dialogo_capturar.interface_selecionada())

    def _init_monitor_captura(self):
        """
        Inicializa o objeto monitor das capturas, que será executado
        em um thread separado.
        """
        self.monitor_capturas.pacote_signal.connect(self.novo_pacote)
        self.monitor_capturas.moveToThread(self.thread_captura)

    def iniciar_captura(self, interface: str):
        """
        Inicia o processo de captura de pacotes.

        Args:
            interface

        """
        self.statusBar().showMessage('Iniciando a captura em "%s"...' % interface)
        # Configura o thread para monitorar a interface selecionada.
        self.thread_captura.started.connect(
            functools.partial(self.monitor_capturas.monitorar_pacotes, interface)
        )
        self.thread_captura.start()
        self.actionInterromperCaptura.setEnabled(True)
        self.actionIniciarCaptura.setDisabled(True)
        self.statusBar().showMessage('Captura em andamento (%s)' % interface)

    def interromper_captura(self):
        """
        Interrompe o processo de captura de pacotes.
        """
        self.statusBar().showMessage('Interrompendo a captura...')
        self.thread_captura.terminate()
        self.actionInterromperCaptura.setDisabled(True)
        self.actionIniciarCaptura.setEnabled(True)
        self.statusBar().showMessage('Captura interrompida.')


    @QtCore.pyqtSlot(tuple)
    def novo_pacote(self, pacote):
        """
        Reage a um novo pacote.
        """
        self._append_pacote_tabela(pacote)
        self._append_pacote_grafico(pacote)

    def _append_pacote_tabela(self, pacote):
        """
        Adiciona um pacote no final da tabela de captura.

        Args:
            pacote

        """
        # Criar uma nova linha no final da tabela.
        n_rows = self.tabelaCaptura.rowCount()
        self.tabelaCaptura.insertRow(n_rows)

        # Preencher as colunas com os dados do pacote.
        for i, data in enumerate(pacote):
            self.tabelaCaptura.setItem(n_rows, i, QtWidgets.QTableWidgetItem(str(data)))

    def _append_pacote_grafico(self, pacote):
        """
        Adiciona um pacote no gráfico.

        Args:
            pacote

        """

        # Obter os objetos existentes
        chart = self.graficoNumPacotes.chart()
        series = chart.series()

        if len(series) == 0:
            # Ainda não há nenhuma informação no gráfico.
            # Adicionar uma nova série de dados.
            curve = QtChart.QLineSeries()
            curve.append(QtCore.QPointF(curve.count(), float(pacote[0])))
            chart.addSeries(curve)
            chart.createDefaultAxes()
        else:
            # Anexar o novo pacote na série existente.
            curve = series[0]
            curve.append(QtCore.QPointF(curve.count(), float(pacote[0])))

            # Reajustar a escala dos eixos para mostrar todos os pontos.
            max_y = max(p.y() for p in curve.pointsVector())
            chart.axisX().setRange(0, curve.count()-1)
            chart.axisY().setRange(0, max(max_y, float(pacote[0])))

