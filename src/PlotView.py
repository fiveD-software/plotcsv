import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtGui
import fnmatch as fm
import pandas as pd
import os
from functools import partial
from PyQt4.QtCore import pyqtSignal


class Color:
    def __init__(self):
        self.background = pg.mkColor('#2E2E2E')
        self.border = pg.mkColor('#555555')
        self.sborder = pg.mkColor('#999999')

        self.marker = pg.mkColor('#FFFF005A')

        self.red = pg.mkColor('#FF6B68')
        self.brRed = pg.mkColor('#FF8785')
        self.green = pg.mkColor('#A8C023')
        self.yellow = pg.mkColor('#D6BF55')
        self.brYellow = pg.mkColor('#FFFF00')
        self.blue = pg.mkColor('#5394EC')
        self.brBlue = pg.mkColor('#7EAEF1')
        self.magenta = pg.mkColor('#AE8ABE')
        self.brMagenta = pg.mkColor('#FF99FF')
        self.cyan = pg.mkColor('#299999')
        self.brCyan = pg.mkColor('#6CDADA')
        self.gray = pg.mkColor('#999999')
        self.dkGray = pg.mkColor('#555555')
        self.white = pg.mkColor('#1F1F1F')
        self.charcoal = pg.mkColor('#1E1E1E')

        self.fontColor = pg.mkColor('#D5D5D5')

        self.WeatherPython = ['#FFD700', '#FF4500', '#9ACD32', '#836FFF', '#63B8FF']
        self.Disneyland = ['#193BCF', '#EDEA18', '#DE2323', '#B319AF', '#E2A31A']
        self.TucnaRainbow = ['#F4190D', '#E18718', '#ECEE11', '#34F92D', '#2338D6']
        self.StratlS = ['#2E93CE', '#76BD1D', '#F7941D', '#750070', '#8EEDFB']
        self.AllTheHomo = ['#FF0000', '#FF8D00', '#F0FF00', '#09FF00', '#001EFF']
        self.ScorpiosWorry = ['#8E0303', '#FFA200', '#C2FF64', '#2998E4', '#1F1663']
        self.HorseHockey = ['#FF7912', '#FF149F', '#246910', '#442ED0', '#FD0E0E']
        self.Prospanica = ['#004A8F', '#64A24C', '#00BCD7', '#E79824', '#5451A2']
        self.Qeventos = ['#51B46D', '#53BBB4', '#7D669E', '#E15258', '#F9845B']
        self.SadToBeLeaving = ['#397FA6', '#E3D4A3', '#D88981', '#E5A35B', '#A28C87']
        self.Commiserate = ['#769473', '#BFC194', '#FBC48F', '#EF946D', '#D7A29E']
        self.UnNamed = ['#3D9DAB', '#F04D4D', '#5B38B4', '#54D269', '#C35E5E']
        self.DullRainbow = ['#AC6363', '#C6B37F', '#C7CA80', '#89B185', '#7394B1']
        self.DrownedAutumn = ['#4525D2', '#7FC974', '#D6634E', '#29A4B6', '#5280A9']
        self.NeighboursMakeNoise = ['#FE9923', '#A8FFB0', '#4C6699', '#166B2A', '#E64C4C']


class Pen:
    def __init__(self):
        self.solid = pg.mkPen(style=QtCore.Qt.SolidLine)
        self.dotted = pg.mkPen(style=QtCore.Qt.DotLine)
        self.dashed = pg.mkPen(style=QtCore.Qt.DashLine)
        self.dashDot = pg.mkPen(style=QtCore.Qt.DashDotLine)
        self.dashDotDot = pg.mkPen(style=QtCore.Qt.DashDotDotLine)


class Button(pg.ButtonItem):
    def __init__(self):
        super(Button, self).__init__()


class VarList(QtGui.QWidget):
    def __init__(self, group):
        super(VarList, self).__init__()
        self.groupName = group
        self.dataFile = DataFile()

        self.listLayout = QtGui.QVBoxLayout()
        self.groupLabel = QtGui.QLabel()
        self.searchBox = QtGui.QLineEdit()
        self.viewList = QtGui.QListView()

        # Setup Layout
        self.listLayout.setContentsMargins(3, 3, 5, 5)
        self.listLayout.setSpacing(5)

        # Setup List View
        self.listModel = QtGui.QStandardItemModel()
        self.listModel.setParent(self.viewList)

        self.viewList.setModel(self.listModel)
        self.viewList.setDragDropMode(QtGui.QListView.DragOnly)

        self.proxy = QtGui.QSortFilterProxyModel(self.viewList)
        self.proxy.setSourceModel(self.listModel)
        self.proxy.setDynamicSortFilter(True)
        self.proxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.viewList.setModel(self.proxy)

        # Setup Search Box
        self.searchBox.setFocus()
        self.connect(self.searchBox, QtCore.SIGNAL('textChanged(QString)'), self.proxy.setFilterFixedString)

        self.listLayout.addWidget(self.groupLabel)
        self.listLayout.addWidget(self.searchBox)
        self.listLayout.addWidget(self.viewList)
        self.setLayout(self.listLayout)

        # self.setMaximumSize(256, 192)
        self.setMinimumWidth(200)
        self.setMaximumWidth(200)

    def addToList(self, varList: list):
        for varName in varList:
            # self.listWidget.addItem(varName)

            item = QtGui.QStandardItem()
            item.setText(varName)
            self.listModel.appendRow(item)

            # self.listModel.insertRow(self.listModel.rowCount())
            # rowIdx = self.listModel.index(self.listModel.rowCount() - 1)
            # self.listModel.setData(rowIdx, varName)

    def getDataSeries(self, series):
        return self.dataFile.df[series]


class SubPlotWidget(QtGui.QWidget):
    def __init__(self):
        super(SubPlotWidget, self).__init__()

        self.vBoxLayout = QtGui.QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.vBoxLayout)

        self.plotWindow = PlotWindow()
        self.plotWindow.setMinimumHeight(130)

        self.vBoxLayout.addWidget(self.plotWindow)

        self.dragEnterEvent = self.dragEnterEv
        # Scroll Area [Not Used]
        #
        # self.scrollPlot = QtGui.QWidget()
        # scrollLayout = QtGui.QVBoxLayout(self.scrollPlot)
        # scrollLayout.addWidget(self.plotWindow)
        # scrollLayout.setContentsMargins(0, 0, 0, 0)
        # self.scrollPlot.setLayout(scrollLayout)

        # self.scrollArea = QtGui.QScrollArea()
        # self.scrollArea.setParent(self)
        # self.scrollArea.setViewportMargins(0, 0, 0, 0)
        # self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        # self.scrollArea.setFrameShape(QtGui.QFrame.NoFrame)
        # self.scrollArea.setWidgetResizable(True)
        #
        # self.scrollArea.setWidget(self.scrollPlot)

    def dragEnterEv(self, ev):
        ev.accept()


class PlotWindow(pg.GraphicsWindow):
    def __init__(self):
        super(PlotWindow, self).__init__()
        color = Color()

        self.setMinimumSize(1080, 600)
        self.setBackground(color.background)

        self.setContentsMargins(2, 2, 2, 2)
        self.gfxLayout = pg.GraphicsLayout()
        self.gfxLayout.setContentsMargins(5, 5, 5, 5)

        self.setCentralItem(self.gfxLayout)

        self.dragEnterEvent = self.dragEnterEv

    def dragEnterEv(self, ev):
        ev.accept()

    def addNewPlot(self):
        newPlot = PlotTag()
        self.gfxLayout.nextRow()

        self.linkXAxis(newPlot.plot)
        self.gfxLayout.addItem(newPlot.plot)
        index = self.gfxLayout.itemIndex(newPlot.plot)
        print('Created Plot Row ' + str(index))

        # The SECRET!!!!!
        cbk = partial(self.plotClose, newPlot.plot)
        newPlot.closeBtn.clicked.connect(cbk)

    def plotClose(self, plot):
        index = self.gfxLayout.itemIndex(plot)
        self.gfxLayout.removeItem(plot)
        print('Closed Plot Row ' + str(index))

    def linkXAxis(self, plot):
        plotList = list(self.gfxLayout.items)
        for p in reversed(plotList):
            plot.setXLink(p)

    # def dragEnterEv(self, ev):
    #     ev.accept()
    #     print('Entering PlotWindow!')
    #
    # def dragMoveEv(self, ev):
    #     ev.accept()
    #     print('Drag Move on PlotWindow!')
    #
    # def dragLeaveEv(self, ev):
    #     ev.accept()
    #     print('Leaving PlotWindow!')
    #
    # def dropEv(self, ev):
    #     ev.accept()
    #     print('Dropped on PlotWindow!')
    #     modelIndex = ev.source().selectedIndexes()
    #     print(modelIndex[0].data())

    # def dropEv(self, ev):
    #     ev.accept()
    #     print('Dropped!')


class PlotGroup:
    def __init__(self, group):
        self.varList = VarList(group)

    def setData(self, csvPath):
        self.varList.dataFile.readCsvFile(csvPath)
        self.varList.addToList(list(self.varList.dataFile.df))


class PlotTag:
    def __init__(self):
        # super(PlotTag, self).__init__()
        self.cwd = os.getcwd()
        print(self.cwd)

        self.plot = Plot()

        self.closeBtn = Button()
        self.closeBtn.setParentItem(self.plot)
        iconPath = os.path.join(self.cwd, 'gui\\delete_01.png')
        # iconPath = 'D:\\MyDrive\\_workspaces\\Python\\00_projects\\PlotCsv\\gui\\delete_01.png'
        delIcon = pg.QtGui.QPixmap(iconPath).scaled(10, 10, pg.QtCore.Qt.KeepAspectRatio)
        self.closeBtn.setPixmap(delIcon)

        x = self.plot.size().width() + 5
        self.closeBtn.setPos(x, 0)


class LineMarker(pg.InfiniteLine):
    def __init__(self):
        self.nextValue = 2
        super(LineMarker, self).__init__()

        self.setMovable(True)
        self.sigDragged.connect(self.isDragged_emit)
        self.savedPos = None

        pen = pg.mkPen(color=Color().marker, style=QtCore.Qt.DotLine)
        self.setPen(pen)

        self.txt = TextMarker()
        # self.txt.border = Pen().solid
        self.txt.setAnchor(0.5, 0.5)
        self.txt.setParentItem(self)

    def isDragged_emit(self):   
        self.initialPos = self.pos()
        modifiers = QtGui.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ShiftModifier:     
            self.setValue(int(self.value()))
        elif modifiers == QtCore.Qt.ControlModifier:
            self.currentValue,success = QtGui.QInputDialog.getDouble(QtGui.QWidget(), 
                "Marker Position", "Enter marker value", self.value(), -2147483647, 2147483647, 3)
            if success:
                self.nextValue = 0

        if not self.nextValue == 2:            
            self.setValue(self.currentValue)
            if self.angle == 0:
                self.setPos((self.initialPos[0], self.currentValue))
            else:
                self.setPos((self.currentValue, self.initialPos[1]))
            self.nextValue += 1
        else:
            if self.angle == 0:
                self.setPos((self.initialPos[0], self.value()))
            else:
                self.setPos((self.value(), self.initialPos[1]))
        
        self.txt.setText('[ %0.3f ]' % self.value())   

class TextMarker(pg.TextItem):
    def __init__(self):
        super(TextMarker, self).__init__()

        self.setText('[--]')
        self.fill = pg.mkBrush(color=Color().charcoal)

    def setAnchor(self, x, y):
        self.anchor = pg.Point(x, y)

    def updateTxt(self, i: float):
        self.setText(i)


class Trace(pg.PlotItem):
    def __init__(self, x, y, name):
        super(Trace, self).__init__()

        self.selectFlag = False
        self.savedPen = None
        self.pen = None
        self.dataItem = pg.PlotDataItem(x, y, name=name)
        self.dataItem.sigClicked.connect(self.traceClicked)

    def makeClickable(self):
        self.dataItem.curve.setClickable(True)

    def setSelectFlag(self, s):
        self.selectFlag = s

    def getSelectFlag(self):
        return self.selectFlag

    def traceClicked(self):
        if self.getSelectFlag():
            self.dataItem.setPen(self.savedPen)
            self.setSelectFlag(False)
            print('Trace Unselected! ' + str(self))
        else:
            self.savedPen = self.dataItem.curve.opts.get('pen')
            self.dataItem.curve.setPen(width=2, dash=Pen().dashed.dashPattern())
            self.setSelectFlag(True)
            print('Trace Selected!')
        # self.dataItem.curve.setPen(width=2)
        # self.setSelectFlag(True)
        # print('Trace Selected!')

    def setColor(self, color):
        self.dataItem.setPen(color)


class Plot(pg.PlotItem):
    def __init__(self):
        super(Plot, self).__init__()

        self.setMinimumHeight(120)
        self.showGrid(x=True, y=True, alpha=0.2)

        self.penColors = Color().WeatherPython
        self.traceList = []
        self.markerList = []
        self.plotLegend = pg.LegendItem(offset=(45, 15))

        self.setAcceptDrops(True)

        self.dropEvent = self.dropTraceEv
        self.keyReleaseEvent = self.keyRelEv
        self.mouseDoubleClickEvent = self.doubleClickEv

    def addVLine(self, loc):
        vLine = LineMarker()
        vLine.setAngle(90)
        vLine.setValue(loc.x())
        vLine.txt.setPos(loc.y(), 0)

        self.addItem(vLine)

    def addHLine(self, loc):
        hLine = LineMarker()
        hLine.setAngle(0)
        hLine.setValue(loc.y())
        hLine.txt.setPos(loc.x(), 0)

        self.addItem(hLine)

    def reDrawLegend(self):
        self.plotLegend.items = []
        for di in self.items:
            if isinstance(di, pg.PlotDataItem):
                self.plotLegend.addItem(di, di.name())

        self.plotLegend.setVisible(True)
        if len(self.traceList) == 0:
            self.plotLegend.setVisible(False)

    def colorTraces(self):
        nowColor = 0
        for di in self.items:
            if isinstance(di, pg.PlotDataItem):
                di.setPen(self.penColors[nowColor])
                nowColor += 1

    def keyRelEv(self, ev):
        if ev.key() == QtCore.Qt.Key_Delete:
            for p in self.traceList:
                if p.getSelectFlag():
                    print('Removing: ' + str(p))
                    self.removeTrace(p)
                    ev.accept()

        if ev.key() == QtCore.Qt.Key_Escape:
            self.updatePlot()

    def updatePlot(self):

        self.traceList = []
        self.markerList = []
        for i in self.items:
            if isinstance(i, LineMarker):
                i.savedPos = i.getPos()
                self.markerList.append(i)

            if isinstance(i, pg.PlotDataItem):
                t = Trace(i.xData, i.yData, i.opts.get('name'))
                t.dataItem = i
                t.makeClickable()
                t.dataItem.sigClicked.connect(t.traceClicked)
                self.traceList.append(t)

        self.clear()

        for t in self.traceList:
            self.addItem(t.dataItem)

        for m in self.markerList:
            m.setPos(m.savedPos)
            self.addItem(m)

        self.colorTraces()
        self.reDrawLegend()

        # print('Plot Items')
        # for i in self.items:
        #     print(i)
        #
        # print('\nMarkers')
        # for m in self.markerList:
        #     print(m)
        #
        # print('\nTraces')
        # for t in self.traceList:
        #     print(t)

    def removeTrace(self, p):
        self.removeItem(p.dataItem)
        self.updatePlot()

    def doubleClickEv(self, ev):
        ev.accept()
        # print(ev.scenePos())

        # modifier = QtGui.QApplication.keyboardModifiers()
        modifier = ev.modifiers()
        mouseLoc = self.vb.mapSceneToView(ev.scenePos())
        # print(mouseLoc)

        if modifier == QtCore.Qt.ShiftModifier:
            print('Shift-DoubleClicked!')
            self.addHLine(mouseLoc)
        else:
            print('DoubleClicked!')
            self.addVLine(mouseLoc)

    def dropTraceEv(self, ev):
        ev.accept()
        evSource = ev.source()
        modelIndex = evSource.selectedIndexes()
        varName = modelIndex[0].data()
        varList = evSource.parent()
        grpName = varList.groupName

        x = None
        y = varList.getDataSeries(varName)
        if grpName == 'stPlotGrp':
            x = varList.getDataSeries('Time<s>')

        if grpName == 'rtPlotGrp':
            x = varList.getDataSeries('Sim Time')

        plotData = pg.PlotDataItem(x, y, name=varName)

        # Add to List
        self.addItem(plotData)

        # self.enableAutoRange(self.vb.XAxis, True)
        # self.enableAutoRange(self.vb.YAxis, True)

        self.updatePlot()
        self.plotLegend.setParentItem(self)


class DataFile:
    def __init__(self):
        self.file = None
        self.df = pd.DataFrame()

    def readCsvFile(self, csvFile):
        self.file = csvFile
        # Read the file and have it as DataFrame
        with open(self.file, 'rb') as f:
            self.df = pd.read_csv(f, encoding='iso-8859-1', index_col=False, skipinitialspace=True)


class PlotView(pg.GraphicsLayoutWidget):
    def __init__(self):
        super(PlotView, self).__init__()

        # Initialize Properties
        self.dataPath = None
        self.testName = ''
        self.doAlignment = False

        # Setup Window Appearance
        self.setWindowTitle('Plot Viewer [TestName]')
        self.setMinimumSize(1440, 720)
        self.setBackground(Color().charcoal)
        # self.setWindowState(QtCore.Qt.WindowMaximized)
        self.setContentsMargins(5, 5, 5, 5)
        self.setAntialiasing(True)

        # Setup Main Layout
        self.mainLayout = QtGui.QGridLayout(self)
        self.mainLayout.setContentsMargins(5, 5, 5, 5)
        self.mainLayout.setHorizontalSpacing(2)
        self.mainLayout.setVerticalSpacing(2)
        self.setLayout(self.mainLayout)

        # Setup Variable List Views
        self.stPlotGrp = PlotGroup('stPlotGrp')
        self.rtPlotGrp = PlotGroup('rtPlotGrp')
        self.stPlotGrp.varList.groupLabel.setText('Smart Terminal Variables')
        self.rtPlotGrp.varList.groupLabel.setText('RT-Lab Variables')
        self.mainLayout.addWidget(self.stPlotGrp.varList, 0, 0, 1, 1)
        self.mainLayout.addWidget(self.rtPlotGrp.varList, 1, 0, 1, 1)

        # Setup the Main SubPlot
        self.mainSubPlot = SubPlotWidget()
        self.mainLayout.addWidget(self.mainSubPlot, 0, 1, 2, 1)

        # Setup Data Alignment PlotWindow
        self.dataAlignPlot = SubPlotWidget()
        self.dataAlignPlot.setMaximumHeight(130)
        self.mainLayout.addWidget(self.dataAlignPlot, 2, 1, 1, 1)

        # Setup 'Add New Plot' button
        self.addPlotBtn = QtGui.QPushButton()
        self.addPlotBtn.setMaximumHeight(50)
        # self.addPlotBtn.setMaximumWidth(180)
        self.addPlotBtn.setText('Add New Plot')
        self.addPlotBtn.clicked.connect(self.mainSubPlot.plotWindow.addNewPlot)
        self.mainLayout.addWidget(self.addPlotBtn, 2, 0, 1, 1)

        self.setStyleSheet("""
            QListView    { background-color: #D5D5D5; }

            QLabel       {
                           color:  #999999;
                           font-family: "Consolas";
                           font-size: 12px;
                         }

            QLineEdit    {
                           background-color: #999999;
                           border-style: outset;
                         }
        """)

        self.dragEnterEvent = self.dragEnterEv
        self.show()

    def dragEnterEv(self, ev):
        ev.accept()

    def setDataPath(self, dPath):
        if os.path.isdir(dPath):
            self.dataPath = dPath

            # TODO: Index must be changed accordingly based on the set path format
            self.testName = dPath.split('\\')[-2]
            self.setWindowTitle('Plot Viewer [ ' + self.testName + ' ]')

            print(self.testName)

            fPaths = []

            for root, directories, files in os.walk(self.dataPath):
                for fName in files:
                    f_path = os.path.join(root, fName)
                    fPaths.append(f_path)

            for f in fPaths:
                if fm.fnmatch(str(f).split('\\')[-1], '*_ALIGNED*'):
                    self.stPlotGrp.setData(f)
                    self.doAlignment = True
                # elif fm.fnmatch(str(f).split('\\')[-1], '*_SCALED*'):
                #     self.stPlotGrp.setData(f)
                #     self.doAlignment = False

                if fm.fnmatch(str(f).split('\\')[-1], '*_MERGED*'):
                    self.rtPlotGrp.setData(f)

            # Plot Data Alignment
            if self.doAlignment:
                self.plotAlignment()
            else:
                for f in fPaths:
                    if fm.fnmatch(str(f).split('\\')[-1], '*_SCALED*'):
                        self.stPlotGrp.setData(f)

        else:
            QtGui.QMessageBox.critical(self, 'Invalid Parameter', 'Invalid path provided!', QtGui.QMessageBox.Ok)

    def plotAlignment(self):
        st_Stop_series = self.stPlotGrp.varList.getDataSeries('a429data.stop')
        # st_Stop_series = self.stPlotGrp.varList.getDataSeries('Stop')
        timeSec_series = self.stPlotGrp.varList.getDataSeries('Time<s>')
        stPen = Pen().dotted
        stPen.setColor(QtGui.QColor(172, 99, 99))

        plotData_st = pg.PlotDataItem(timeSec_series, st_Stop_series, name='a429data.stop')
        # plotData_st = pg.PlotDataItem(timeSec_series, st_Stop_series, name='Stop')
        plotData_st.setPen(stPen)

        rt_Stop_series = self.rtPlotGrp.varList.getDataSeries('STOP_CMD')
        simTime_series = self.rtPlotGrp.varList.getDataSeries('Sim Time')
        rtPen = Pen().dotted
        rtPen.setColor(QtGui.QColor(198, 179, 127))

        plotData_rt = pg.PlotDataItem(simTime_series, rt_Stop_series, name='STOP_CMD')
        plotData_rt.setPen(rtPen)

        plot = Plot()
        plot.addItem(plotData_st)
        plot.addItem(plotData_rt)

        plot.setAcceptDrops(False)

        plot.getViewBox().setMouseEnabled(x=True, y=False)

        legend = pg.LegendItem(offset=(45, 5))
        for p in plot.items:
            legend.addItem(p, p.name())
        legend.setParentItem(plot)

        self.dataAlignPlot.plotWindow.gfxLayout.addItem(plot)
