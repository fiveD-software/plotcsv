import sys

from PyQt4 import QtGui
from src.CsvConvert import PlotCsvApp


def main():
    # A new instance of QApplication
    app = QtGui.QApplication(sys.argv)
    # Set the form to PlotCsvApp (main_win)
    win = PlotCsvApp()
    # Show the form
    win.show()
    # Execute the application
    app.exec_()


if __name__ == '__main__':
    main()
