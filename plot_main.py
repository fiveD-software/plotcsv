import sys

from PyQt4 import QtGui
from src.PlotView import PlotView


def main():
    # A new instance of QApplication
    app = QtGui.QApplication(sys.argv)
    # Set the form to PlotViewer
    widget = PlotView()
    widget.setDataPath('C:\\Users\\mdasco\\Desktop\\dummyTest')
    # Show the form
    # widget.show()
    # Execute the application
    app.exec_()


if __name__ == '__main__':
    main()
