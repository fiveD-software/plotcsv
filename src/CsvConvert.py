from PyQt4 import QtGui
from PyQt4.QtCore import QObject, QThread, QTimer, pyqtSlot
import fnmatch as fm
import os

from src.DataProcessor import DataProcessor
from src.PlotView import PlotView

from gui import main_win
from gui.lineEdit_dnd import LineEditDropHandler


# class ProcessThread(QThread):
#     def __int__(self, parent=None):
#         QThread.__init__(self, parent)
#
#         self.exiting = False
#
#     def __del__(self):
#         self.exiting = True
#         self.wait()


class PlotCsvApp(QtGui.QMainWindow, main_win.Ui_main_win):
    def __init__(self):
        # This is to access variables, methods etc in the main_window.py file
        super(PlotCsvApp, self).__init__()
        # Defined in the main_window.py automatically
        # Sets up layout and widgets that are defined
        self.setupUi(self)

        self.wd = os.getcwd()

        # Instantiate a ProcessThread object
        self.processorThread = QThread()
        # Instantiate a DataProcessor object
        self.prepData = DataProcessor()

        # Move the DataProcessor to ProcessThread
        self.prepData.moveToThread(self.processorThread)

        self.testName = None
        self.plot = None

        self.header_ledit.setDragEnabled(True)
        self.workspace_ledit.setDragEnabled(True)
        self.header_ledit.installEventFilter(LineEditDropHandler(self))
        self.workspace_ledit.installEventFilter(LineEditDropHandler(self))
        self.process_btn.setEnabled(False)
        self.newProcess_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.goAnalyze_btn.setEnabled(False)

        # Signal connections
        self.header_tb.clicked.connect(self.browse_header)
        self.testdata_tb.clicked.connect(self.browse_workspace)
        self.process_btn.clicked.connect(self.process_data)
        self.goAnalyze_btn.clicked.connect(self.run_plot)
        self.header_ledit.textChanged.connect(self.check_paths)
        self.workspace_ledit.textChanged.connect(self.check_paths)

        # Connect signals
        self.processorThread.started.connect(self.prepData.preProcessData)
        self.prepData.print_out.connect(self.output_te.append)
        self.prepData.prog_out.connect(self.progressBar.setValue)
        self.prepData.fin_out.connect(self.processing_done)
        self.cancel_btn.clicked.connect(self.process_cancelled)

        self.getHeaderfilePathInSVN()

    def getHeaderfilePathInSVN(self):
        owd_true = os.getcwd()
        try:
            os.chdir("../Convert/Header_Files/")
            owd = os.getcwd()
            self.header_ledit.setText(owd)
            print("1 :" + owd)
        except:
            print("Header File path not found")
        # get back to original directory
        os.chdir(owd_true)
        owd = os.getcwd()
        print("2 :" + owd)

    def browse_header(self):
        self.header_ledit.clear()
        headDir = QtGui.QFileDialog.getExistingDirectory(self, 'Pick header files folder', '*.*')

        if headDir:
            self.header_ledit.setText(headDir)

    def browse_workspace(self):
        self.workspace_ledit.clear()
        testDir = QtGui.QFileDialog.getExistingDirectory(self, 'Pick a workspace folder', '')

        if testDir:
            self.workspace_ledit.setText(testDir)

    def check_paths(self):
        stFileExist = False
        rtFileExist = False

        hd = os.path.exists(self.header_ledit.text())
        ws = os.path.exists(self.workspace_ledit.text())

        self.process_btn.setEnabled(True) if (hd & ws) else self.process_btn.setEnabled(False)

        # Check if data files already exist and can be analyzed
        dPath = os.path.join(self.workspace_ledit.text(), 'csv')
        if os.path.exists(dPath):
            f = []
            for root, directories, files in os.walk(dPath):
                f.append(files)

            for x in f:
                if fm.fnmatch(str(x), '*_ALIGNED*'):
                    stFileExist = True
                if fm.fnmatch(str(x), '*_MERGED*'):
                    rtFileExist = True

            if stFileExist or rtFileExist:
                self.goAnalyze_btn.setEnabled(True)
            else:
                self.goAnalyze_btn.setEnabled(False)
        else:
            self.goAnalyze_btn.setEnabled(False)

    def return_paths(self):
        return self.header_ledit.text(), self.workspace_ledit.text()

    def process_data(self):
        if not self.processorThread.isRunning():
            # Clear the texts from output_te
            self.output_te.clear()
            # self.cancel_btn.setEnabled(True)
            self.cancel_btn.setEnabled(False)

            # Get the workspace paths
            hd, td = self.return_paths()
            # Instantiate a PrepareData object
            self.prepData.setPath(hd, td)

            # Extract the name of the test
            self.testName = str(self.workspace_ledit.text()).split('\\')[-1]

            self.processorThread.start()

    def process_cancelled(self):
        if self.processorThread.isRunning():
            QtGui.QMessageBox.critical(self, 'Terminating Thread!', 'Processing of <TestDataName> data was cancelled!', QtGui.QMessageBox.Ok)

            # Quit thread
            self.prepData.interrupt = True
            # Update needed buttons
            self.newProcess_btn.setEnabled(False)
            self.cancel_btn.setEnabled(False)
            self.goAnalyze_btn.setEnabled(False)

    @pyqtSlot()
    def processing_done(self):
        if self.processorThread.isRunning():
            # Quit thread
            self.processorThread.quit()
            # Update needed buttons
            self.newProcess_btn.setEnabled(False)
            self.goAnalyze_btn.setEnabled(True)

            self.output_te.append('\n\n\'%s\' test data is now ready for analysis.\n' % self.testName)

            print(os.getcwd())
            os.chdir(self.wd)

    def run_plot(self):
        testDir = self.workspace_ledit.text()

        imgDir = os.path.join(testDir, '_img')

        # Make images directory if it does not exist
        if not os.path.exists(imgDir):
            self.output_te.append('Creating Screen Capture folder: %s' % imgDir)
            os.makedirs(imgDir)
            self.output_te.append('This subfolder shall contain the test\'s screenshots.')
        else:
            self.output_te.append('Screenshots folder: %s already exist.' % imgDir)

        self.output_te.append('Plot is running...')

        self.plot = PlotView()
        self.plot.setDataPath(os.path.join(testDir, 'csv'))

        self.plot.show()

    def running_plot(self):
        # Disable buttons
        self.process_btn.setEnabled(False)
        self.goAnalyze_btn.setEnabled(False)


# def start_process(dataProcessor):
#     processorThread = QThread()
#     # timer = QTimer()
#     # timer.timeout.connect(dataProcessor.preProcessData)
#     processorThread.started.connect(dataProcessor.preProcessData)
#
#     dataProcessor.moveToThread(processorThread)
#
#     processorThread.dataProcessor = dataProcessor
#     # timer.start(1000)
#     processorThread.start()
#
#     return processorThread
