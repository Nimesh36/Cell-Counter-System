import codecs
import os.path
import webbrowser

from functools import partial
from cellCounter import ImageOperation
from cellCounter import Spore
import numpy as np
import cv2    #pip install opencv-python
from PyQt5 import QtWidgets #pip install PyQt5

from libs.resources import *
from libs.constants import *
from libs.utils import *
from libs.settings import Settings
from libs.shape import Shape, DEFAULT_LINE_COLOR, DEFAULT_FILL_COLOR
from libs.stringBundle import StringBundle
from libs.canvas import Canvas
from libs.zoomWidget import ZoomWidget
from libs.labelDialog import LabelDialog
from libs.labelFile import LabelFile
from libs.toolBar import ToolBar
from libs.hashableQListWidgetItem import HashableQListWidgetItem

from ModifyLabel import Ui_modifyLabel
from createModelUi import Ui_crateModel
__appname__ = 'Cell Counter'

class WindowMixin(object):

    def menu(self, title, actions=None):
        menu = self.menuBar().addMenu(title)
        if actions:
            addActions(menu, actions)
        return menu

    def toolbar(self, title, actions=None):
        toolbar = ToolBar(title)
        toolbar.setObjectName(u'%sToolBar' % title)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        if actions:
            addActions(toolbar, actions)
        self.addToolBar(Qt.LeftToolBarArea, toolbar)
        return toolbar


class MainWindow(QMainWindow, WindowMixin):
    FIT_WINDOW, FIT_WIDTH, MANUAL_ZOOM = list(range(3))

    def __init__(self, defaultFilename=None, defaultPrefdefClassFile=None, defaultSaveDir=None):
        super(MainWindow, self).__init__()
        self.setWindowTitle(__appname__)
        self.settings = Settings()
        self.settings.load()
        settings = self.settings
        self.stringBundle = StringBundle.getBundle()
        getStr = lambda strId: self.stringBundle.getString(strId)
        self.defaultSaveDir = defaultSaveDir
        self.mImgList = []
        self.dirname = None
        self.labelHist = []
        self.lastOpenDir = None
        self.dirty = False
        self.countEnable = 0
        self._noSelectionSlot = False
        self._beginner = True
        self.loadPredefinedClasses(defaultPrefdefClassFile)
        self.defaultPrefdefClassFile = defaultPrefdefClassFile
        self.labelDialog = LabelDialog(parent=self, listItem=self.labelHist)
        self.itemsToShapes = {}
        self.shapesToItems = {}
        self.prevLabelText = ''
        listLayout = QVBoxLayout()
        listLayout.setContentsMargins(0, 0, 0, 0)
        self.defaultLabelTextLine = QLineEdit()
        self.labelList = QListWidget()
        self.logContainer = QListWidget()
        labelListContainer = QWidget()
        labelListContainer.setLayout(listLayout)
        self.labelList.itemClicked.connect(self.labelSelectionChanged)
        listLayout.addWidget(self.labelList)
        self.logContainer.itemChanged.connect(self.pointListChanged)
        self.logContainer.itemClicked.connect(self.pointSelectionChange)
        self.dock = QDockWidget("Log", self)
        self.dock.setObjectName(getStr('labels'))
        self.dock.setWidget(self.logContainer)
        self.logDock = QDockWidget(getStr('boxLabelText'), self)
        self.logDock.setObjectName("Log")
        self.logDock.setWidget(labelListContainer)
        self.zoomWidget = ZoomWidget()
        self.canvas = Canvas(parent=self)
        self.canvas.zoomRequest.connect(self.zoomRequest)
        self.canvas.setDrawingShapeToSquare(settings.get(SETTING_DRAW_SQUARE, False))
        scroll = QScrollArea()
        scroll.setWidget(self.canvas)
        scroll.setWidgetResizable(True)
        self.scrollBars = {
            Qt.Vertical: scroll.verticalScrollBar(),
            Qt.Horizontal: scroll.horizontalScrollBar()
        }
        self.scrollArea = scroll
        self.canvas.scrollRequest.connect(self.scrollRequest)
        self.canvas.newShape.connect(self.newShape)
        self.canvas.shapeMoved.connect(self.setDirty)
        self.canvas.selectionChanged.connect(self.shapeSelectionChanged)
        self.canvas.drawingPolygon.connect(self.toggleDrawingSensitive)
        self.setCentralWidget(scroll)
        self.addDockWidget(Qt.RightDockWidgetArea, self.logDock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock)
        self.dockFeatures = QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetFloatable
        self.logDock.setFeatures(self.logDock.features() ^ self.dockFeatures)
        self.dock.setFeatures(self.dock.features() ^ self.dockFeatures)
        action = partial(newAction, self)
        quit = action(getStr('quit'), self.close,
                      'Ctrl+Q', 'quit', getStr('quitApp'))
        open = action(getStr('openFile'), self.openFile,
                      'Ctrl+O', 'open', getStr('openFileDetail'))
        save = action(getStr('save'), self.saveFile,
                      'Ctrl+S', 'save', getStr('saveDetail'), enabled=False)
        count = action('Count', self.countCell,
                      'Ctrl+J', 'color_line', 'count', enabled=False)
        self.selectNone = action('Select None', self.selectFun,
                        'Ctrl+A','done', 'select', enabled=False)
        openNextImg = action("Next Image", self.openNextImg,
                             'd', 'next', "next image", enabled=False)
        create = action(getStr('crtBox'), self.createShape,
                        'w', 'new', getStr('crtBoxDetail'), enabled=False)
        delete = action(getStr('delBox'), self.deleteSelectedShape,
                        'Delete', 'delete', getStr('delBoxDetail'), enabled=False)
        copy = action(getStr('dupBox'), self.copySelectedShape,
                      'Ctrl+D', 'copy', getStr('dupBoxDetail'),
                      enabled=False)
        zoom = QWidgetAction(self)
        zoom.setDefaultWidget(self.zoomWidget)
        self.zoomWidget.setWhatsThis(
            u"Zoom in or out of the image. Also accessible with"
            " %s and %s from the canvas." % (fmtShortcut("Ctrl+[-+]"),
                                             fmtShortcut("Ctrl+Wheel")))
        self.zoomWidget.setEnabled(False)
        help = action('Help',self.helpDialog,None,'help')
        about = action('About',self.aboutDialog,None,'help')
        zoomIn = action(getStr('zoomin'), partial(self.addZoom, 10),
                        'Ctrl++', 'zoom-in', getStr('zoominDetail'), enabled=False)
        zoomOut = action(getStr('zoomout'), partial(self.addZoom, -10),
                         'Ctrl+-', 'zoom-out', getStr('zoomoutDetail'), enabled=False)
        zoomOrg = action(getStr('originalsize'), partial(self.setZoom, 100),
                         'Ctrl+=', 'zoom', getStr('originalsizeDetail'), enabled=False)
        fitWindow = action(getStr('fitWin'), self.setFitWindow,
                           'Ctrl+F', 'fit-window', getStr('fitWinDetail'),
                           checkable=True, enabled=False)
        fitWidth = action(getStr('fitWidth'), self.setFitWidth,
                          'Ctrl+Shift+F', 'fit-width', getStr('fitWidthDetail'),
                          checkable=True, enabled=False)
        zoomActions = (self.zoomWidget, zoomIn, zoomOut,
                       zoomOrg, fitWindow, fitWidth)
        self.zoomMode = self.MANUAL_ZOOM
        self.scalers = {
            self.FIT_WINDOW: self.scaleFitWindow,
            self.FIT_WIDTH: self.scaleFitWidth,
            self.MANUAL_ZOOM: lambda: 1,
        }
        labelMenu = QMenu()
        addActions(labelMenu, (delete,))
        self.labelList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.labelList.customContextMenuRequested.connect(
            self.popLabelListMenu)
        self.sporeCountOption = QAction('Spore count', self)
        self.sporeCountOption.setCheckable(True)
        self.sporeCountOption.setDisabled(True)
        self.sporeCountOption.triggered.connect(self.sporeCountFun)

        self.rbcCountOption = QAction('RBC count', self)
        self.rbcCountOption.setCheckable(True)
        self.rbcCountOption.setDisabled(True)
        self.rbcCountOption.triggered.connect(self.rbcCountFun)

        self.wbcCountOption = QAction('WBC count', self)
        self.wbcCountOption.setCheckable(True)
        self.wbcCountOption.setDisabled(True)
        self.wbcCountOption.triggered.connect(self.wbcCountFun)

        self.plateletsCountOption = QAction('Platelets count', self)
        self.plateletsCountOption.setCheckable(True)
        self.plateletsCountOption.setDisabled(True)
        self.plateletsCountOption.triggered.connect(self.plateletsCountFun)

        self.bacteriaCountOption = QAction('Bacteria count', self)
        self.bacteriaCountOption.setCheckable(True)
        self.bacteriaCountOption.setDisabled(True)
        self.bacteriaCountOption.triggered.connect(self.bacteriaCountFun)

        self.labelImage = QAction('Label Image', self)
        self.labelImage.setDisabled(True)
        self.labelImage.triggered.connect(self.labelImageFun)

        self.modifyLabel = QAction('Modify Label', self)
        self.modifyLabel.setDisabled(False)
        self.modifyLabel.triggered.connect(self.modifyLabelFun)

        self.createModel = QAction('Create Model', self)
        self.createModel.setDisabled(False)
        self.createModel.triggered.connect(self.createModelFun)

        self.actions = struct(save=save, open=open, count=(count,), selectNone=self.selectNone, create=create, delete=delete, copy=copy,
                              zoom=zoom, zoomIn=zoomIn, zoomOut=zoomOut, zoomOrg=zoomOrg,
                              fitWindow=fitWindow, fitWidth=fitWidth,
                              zoomActions=zoomActions,
                              fileMenuActions=(
                                  open, self.selectNone, save, quit),
                              beginner=(), advanced=(),
                              menuMenu=(self.sporeCountOption, self.rbcCountOption,
                                        self.wbcCountOption, self.plateletsCountOption,
                                        self.bacteriaCountOption),
                              toolMenu=(self.labelImage, self.modifyLabel),
                              modelMenu=(self.createModel,),
                              beginnerContext=(create, copy, delete),
                              advancedContext=(copy,
                                               delete),
                              onLoadActive=(create,),
                              onLabelSelect=(openNextImg, ),
                              resetDeActive=(count, copy, delete, create, openNextImg))
        self.menus = struct(
            file=self.menu('&File'),
            menu=self.menu('&Menu'),
            tool=self.menu('&Tools'),
            model=self.menu('&Models'),
            help=self.menu('&Help'))
        self.lastLabel = None
        addActions(self.menus.file,
                   (open, save, quit))
        addActions(self.menus.help,(help,about))

        self.menus.file.aboutToShow.connect(self.updateFileMenu)
        addActions(self.canvas.menus[0], self.actions.beginnerContext)
        addActions(self.canvas.menus[1], (
            action('&Copy here', self.copyShape),
            action('&Move here', self.moveShape)))

        self.tools = self.toolbar('Tools')
        self.actions.beginner = (
            open, count, self.selectNone, save, None, openNextImg, create, copy, delete, None,
            zoomIn, zoom, zoomOut, fitWindow, fitWidth)

        self.actions.advanced = (open, save, count, self.selectNone, None)
        self.statusBar().showMessage('%s started.' % __appname__)
        self.statusBar().show()

        self.image = QImage()
        self.filePath = defaultFilename
        self.recentFiles = []
        self.maxRecent = 7
        self.lineColor = None
        self.fillColor = None
        self.zoom_level = 100
        self.fit_window = False
        self.difficult = False

        if settings.get(SETTING_RECENT_FILES):
            if have_qstring():
                recentFileQStringList = settings.get(SETTING_RECENT_FILES)
                self.recentFiles = [i for i in recentFileQStringList]
            else:
                self.recentFiles = recentFileQStringList = settings.get(SETTING_RECENT_FILES)

        size = settings.get(SETTING_WIN_SIZE, QSize(600, 500))
        position = QPoint(0, 0)
        saved_position = settings.get(SETTING_WIN_POSE, position)
        # Fix the multiple monitors issue
        for i in range(QApplication.desktop().screenCount()):
            if QApplication.desktop().availableGeometry(i).contains(saved_position):
                position = saved_position
                break
        self.resize(size)
        self.move(position)
        saveDir = settings.get(SETTING_SAVE_DIR, None)
        self.lastOpenDir = settings.get(SETTING_LAST_OPEN_DIR, None)
        if self.defaultSaveDir is None and saveDir is not None and os.path.exists(saveDir):
            self.defaultSaveDir = saveDir
            self.statusBar().showMessage('%s started. Annotation will be saved to %s' %
                                         (__appname__, self.defaultSaveDir))
            self.statusBar().show()
        self.restoreState(settings.get(SETTING_WIN_STATE, QByteArray()))
        Shape.line_color = self.lineColor = QColor(settings.get(SETTING_LINE_COLOR, DEFAULT_LINE_COLOR))
        Shape.fill_color = self.fillColor = QColor(settings.get(SETTING_FILL_COLOR, DEFAULT_FILL_COLOR))
        self.canvas.setDrawingColor(self.lineColor)
        Shape.difficult = self.difficult
        self.updateFileMenu()
        self.zoomWidget.valueChanged.connect(self.paintCanvas)
        self.populateModeActions()
        self.labelCoordinates = QLabel('')
        self.statusBar().addPermanentWidget(self.labelCoordinates)

    def toggaleCount(self, menuObj):
        if self.countEnable == 1:
            for count in self.actions.count:
                count.setEnabled(True)
        for menu in self.actions.menuMenu:
            menu.setChecked(False)
        menuObj.setChecked(True)

    def helpDialog(self):
        webbrowser.open("resources\\pdf\\help.pdf")

    def aboutDialog(self):
            webbrowser.open('resources\\pdf\\about.pdf')

    def pointListChanged(self, item):
        tag = int(item.data(0).split(" ")[0].split("(")[1].split(")")[0])-1
        if tag in self.selectedPointList:
            item.setCheckState(Qt.Unchecked)
            self.selectedPointList.remove(tag)
        else:
            self.selectedPointList.append(tag)
            item.setCheckState(Qt.Checked)

    def selectFun(self):
        if (self.selectNone.iconText() == "Select None"):
            for i in range(len(self.pointList)):
                item = self.logContainer.item(i)
                tag = int(item.data(0).split(" ")[0].split("(")[1].split(")")[0]) - 1
                item.setCheckState(Qt.Unchecked)
            self.selectNone.setIconText("Select All")

        else:
            for i in range(len(self.pointList)):
                item = self.logContainer.item(i)
                tag = int(item.data(0).split(" ")[0].split("(")[1].split(")")[0]) - 1
                item.setCheckState(Qt.Checked)
            self.selectNone.setIconText("Select None")

    def openNextImg(self):
        self.actions.create.setEnabled(True)
        self.actions.save.setEnabled(False)
        self.logContainer.clear()
        self.labelList.clear()
        if not self.labelFlag:
            self.actions.selectNone.setEnabled(False)
            filelist = [f for f in os.listdir("images") if f.endswith(".jpg")]
            for f in filelist:
                os.remove(os.path.join("images", f))
            filelist = [f for f in os.listdir("images") if f.endswith(".xml")]
            for f in filelist:
                os.remove(os.path.join("images", f))
            for i in self.selectedPointList:
                A, B, C, D = self.pointList[i][0], self.pointList[i][1], self.pointList[i][2], self.pointList[i][3]
                cv2.imwrite("images/img_"+str(i)+".jpg", self.imageObj.frame[A[1]:D[1], B[0]:A[0]])
            self.labelFlag = True
        tempImage = read("images/img_"+str(self.selectedPointList[self.currentIndexOfSelectedPoint])+".jpg", None)
        self.canvas.verified = False
        Image = QImage.fromData(tempImage)
        self.canvas.loadPixmap(QPixmap.fromImage(Image))
        self.canvas.setEnabled(True)
        self.adjustScale(initial=True)
        self.paintCanvas()
        self.canvas.setFocus(True)
        if self.currentIndexOfSelectedPoint + 1 == len(self.selectedPointList):
            self.currentIndexOfSelectedPoint = 0
        else:
            self.currentIndexOfSelectedPoint = self.currentIndexOfSelectedPoint + 1

    def pointSelectionChange(self, item):
        tag = int(item.data(0).split(" ")[0].split("(")[1].split(")")[0])-1
        A, B, C, D = self.pointList[tag][0], self.pointList[tag][1], self.pointList[tag][2], self.pointList[tag][3]
        tempImage = np.copy(self.imageObj.ansFrame)
        cv2.line(tempImage, A, B, (0, 0, 255), 5)
        cv2.line(tempImage, B, C, (0, 0, 255), 5)
        cv2.line(tempImage, C, D, (0, 0, 255), 5)
        cv2.line(tempImage, D, A, (0, 0, 255), 5)
        self.canvas.verified = False
        Image = QImage(tempImage, tempImage.shape[1], tempImage.shape[0],
                        QImage.Format_RGB888)
        self.canvas.loadPixmap(QPixmap.fromImage(Image))
        self.canvas.setEnabled(True)
        self.adjustScale(initial=True)
        self.paintCanvas()
        self.canvas.setFocus(True)

    def countCell(self):
        self.sporeCountObj.image.ansFrame = np.copy(self.sporeCountObj.image.frame)
        sporeCountList = {}
        for i in self.selectedPointList:
            sporeCountList[i] = self.sporeCountObj.find_spore(self.pointList[i][0], self.pointList[i][1],
                                                              self.pointList[i][2], self.pointList[i][3])
        print(sporeCountList)
        self.canvas.verified = False
        tempImage = np.copy(self.sporeCountObj.image.ansFrame)
        Image = QImage(tempImage, tempImage.shape[1], tempImage.shape[0],
                       QImage.Format_RGB888)
        self.canvas.loadPixmap(QPixmap.fromImage(Image))
        self.canvas.setEnabled(True)
        self.adjustScale(initial=True)
        self.paintCanvas()
        self.canvas.setFocus(True)
        self.logContainer.clear()
        count = 0
        sporeCount = 0
        for i in self.pointList:
            if count in self.selectedPointList:
                item = QListWidgetItem("(" + str(count + 1) + ") " + str(i[4]) + " [" + str(sporeCountList[count]) + "]")
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked)
                self.logContainer.addItem(item)
                sporeCount = sporeCount + sporeCountList[count]
            else:
                item = QListWidgetItem("("+str(count+1)+") "+str(i[4]))
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                self.logContainer.addItem(item)
            count = count + 1
        self.dock.setWindowTitle("Total Count : "+str(sporeCount))

    def sporeCountFun(self):
        self.setClean()
        self.sporeCountObj = Spore("inference_graph/frozen_inference_graph_.pb", self.imageObj)
        self.sporeCountObj.loadModel()
        self.pointList=[]
        for j in range(len(self.sporeCountObj.image.intersection_point) - 1):
            for i in range(len(self.sporeCountObj.image.intersection_point[0]) - 1):
                self.pointList.append((self.sporeCountObj.image.intersection_point[j + 1][i],
                                      self.sporeCountObj.image.intersection_point[j][i],
                                      self.sporeCountObj.image.intersection_point[j][i + 1],
                                      self.sporeCountObj.image.intersection_point[j + 1][i + 1],
                                      self.sporeCountObj.image.find_area(self.sporeCountObj.image.intersection_point[j][i],
                                                                   self.sporeCountObj.image.intersection_point[j + 1][i + 1])))
        n = len(self.pointList)
        for i in range(n):
            for j in range(0, n - i - 1):
                if self.pointList[j][4] < self.pointList[j + 1][4]:
                    self.pointList[j], self.pointList[j + 1] = self.pointList[j + 1], self.pointList[j]
        count = 1
        self.selectedPointList = []
        self.logContainer.clear()
        for i in self.pointList:
            item = QListWidgetItem("("+str(count)+") "+str(i[4]))
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            if count<=16:
                item.setCheckState(Qt.Checked)
                self.selectedPointList.append(count-1)
            else:
                item.setCheckState(Qt.Unchecked)
            self.logContainer.addItem(item)
            count = count + 1
        self.toggaleCount(self.sporeCountOption)
        self.actions.selectNone.setEnabled(True)

    def rbcCountFun(self):
        print("RBC option.")
        self.toggaleCount(self.rbcCountOption)

    def wbcCountFun(self):
        print("WBC option.")
        self.toggaleCount(self.wbcCountOption)

    def plateletsCountFun(self):
        print("Platelets option.")
        self.toggaleCount(self.plateletsCountOption)

    def bacteriaCountFun(self):
        print("Bacteria option.")
        self.toggaleCount(self.bacteriaCountOption)

    def labelImageFun(self):
        self.setClean()
        self.pointList = []
        for j in range(len(self.imageObj.intersection_point) - 1):
            for i in range(len(self.imageObj.intersection_point[0]) - 1):
                self.pointList.append((self.imageObj.intersection_point[j + 1][i],
                                       self.imageObj.intersection_point[j][i],
                                       self.imageObj.intersection_point[j][i + 1],
                                       self.imageObj.intersection_point[j + 1][i + 1],
                                       self.imageObj.find_area(self.imageObj.intersection_point[j][i],
                                                                    self.imageObj.intersection_point[j + 1][
                                                                        i + 1])))
        n = len(self.pointList)
        for i in range(n):
            for j in range(0, n - i - 1):
                if self.pointList[j][4] < self.pointList[j + 1][4]:
                    self.pointList[j], self.pointList[j + 1] = self.pointList[j + 1], self.pointList[j]
        count = 1
        self.selectedPointList = []
        self.logContainer.clear()
        for i in self.pointList:
            item = QListWidgetItem("(" + str(count) + ") " + str(i[4]))
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            if count <= 16:
                item.setCheckState(Qt.Checked)
                self.selectedPointList.append(count - 1)
            else:
                item.setCheckState(Qt.Unchecked)
            self.logContainer.addItem(item)
            count = count + 1
        self.actions.selectNone.setEnabled(True)
        self.currentIndexOfSelectedPoint = 0
        self.labelFlag = False
        self.shapeFlag = False
        if self.countEnable == 1:
            for action in self.actions.onLabelSelect:
                action.setEnabled(True)

    def modifyLabelFun(self):
        self.OPEN_window = QtWidgets.QWidget()
        self.OPENModifyLabelui = Ui_modifyLabel()
        self.OPENModifyLabelui.setupUi(self.OPEN_window)
        self.OPEN_window.show()
        self.selectedLabel = ""
        self.tempLabelHist = []
        for label in self.labelHist:
            self.OPENModifyLabelui.labelListWidget.addItem(label)
            self.tempLabelHist.append(label)
        self.OPENModifyLabelui.labelListWidget.clicked.connect(self.clickOnLabel)
        self.OPENModifyLabelui.deleteButton.clicked.connect(self.deleteLabel)
        self.OPENModifyLabelui.addButton.clicked.connect(self.addLabelFun)
        self.OPENModifyLabelui.saveButton.clicked.connect(self.saveLabelHist)

    def createModelFun(self):
        self.OPENCreateModelWindow = QtWidgets.QWidget()
        self.OPENCreateModelui = Ui_crateModel()
        self.OPENCreateModelui.setupUi(self.OPENCreateModelWindow)
        self.OPENCreateModelWindow.show()
        self.selectedImageFilePath = []
        self.selectedXmlFilePath = []

        self.OPENCreateModelui.imageAddButton.clicked.connect(self.addImageLabel)
        self.OPENCreateModelui.imageDeleteButton.clicked.connect(self.deleteImageLabel)

        self.OPENCreateModelui.xmlAddButton.clicked.connect(self.addXmlLabel)
        self.OPENCreateModelui.xmlDeleteButton.clicked.connect(self.deleteXmlLabel)

        self.OPENCreateModelui.cancleButton.clicked.connect(self.closeCreateModelUi)
        self.OPENCreateModelui.nextButton.clicked.connect(self.nextCreateModelUi)

        self.OPENCreateModelui.imageListWidget.clicked.connect(self.clickOnImagePath)
        self.OPENCreateModelui.xmlListWidget.clicked.connect(self.clickOnXmlPath)


    def addImageLabel(self):
        formats = ['*.jpeg', '*.jpg', '*.png', '*.bmp']
        filters = "Image files (%s)" % ' '.join(formats)
        filename = QFileDialog.getOpenFileName(self, '%s - Choose Image or Label file' % __appname__, '.', filters)
        if filename[0]:
            self.selectedImageFilePath.append(filename[0])
            self.OPENCreateModelui.imageListWidget.addItem(filename[0])

    def addXmlLabel(self):
        formats = ['*.xml']
        filters = "Image files (%s)" % ' '.join(formats)
        filename = QFileDialog.getOpenFileName(self, '%s - Choose Image or Label file' % __appname__, '.', filters)
        if filename[0]:
            self.selectedXmlFilePath.append(filename[0])
            self.OPENCreateModelui.xmlListWidget.addItem(filename[0])

    def closeCreateModelUi(self):
        self.setEnabled(True)
        self.OPENCreateModelWindow.close()

    def clickOnImagePath(self):
        self.selectedImage = self.OPENCreateModelui.imageListWidget.currentItem().text()

    def clickOnXmlPath(self):
        self.selectedXml = self.OPENCreateModelui.xmlListWidget.currentItem().text()

    def clickOnLabel(self):
        self.selectedLabel = self.OPENModifyLabelui.labelListWidget.currentItem().text()
        self.OPENModifyLabelui.labelNameLineEdit.setText(self.selectedLabel)

    def deleteLabel(self):
        if self.selectedLabel in self.tempLabelHist:
            temp = []
            for label in self.tempLabelHist:
                if self.selectedLabel != label:
                    temp.append(label)
            self.tempLabelHist = temp
            self.OPENModifyLabelui.labelListWidget.clear()
            for label in self.tempLabelHist:
                self.OPENModifyLabelui.labelListWidget.addItem(label)

    def deleteImageLabel(self):
        if self.selectedImage in self.selectedImageFilePath:
            temp = []
            for path in self.selectedImageFilePath:
                if self.selectedImage != path:
                    temp.append(path)
            self.selectedImageFilePath = temp
            self.OPENCreateModelui.imageListWidget.clear()
            for label in self.selectedImageFilePath:
                self.OPENCreateModelui.imageListWidget.addItem(label)

    def deleteXmlLabel(self):
        if self.selectedXml in self.selectedXmlFilePath:
            temp = []
            for path in self.selectedXmlFilePath:
                if self.selectedXml != path:
                    temp.append(path)
            self.selectedXmlFilePath = temp
            self.OPENCreateModelui.xmlListWidget.clear()
            for label in self.selectedXmlFilePath:
                self.OPENCreateModelui.xmlListWidget.addItem(label)

    def nextCreateModelUi(self):
        if not self.OPENCreateModelui.modelNameLineEdit.text():
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Oops! Please Enter Model Name')
            error_dialog.exec_()
        elif len(self.selectedImageFilePath)!=len(self.selectedXmlFilePath) or not len(self.selectedImageFilePath):
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Oops! Please select same number of image and xml file.')
            error_dialog.exec_()
        else:
            print("Done")

    def addLabelFun(self):
        label = self.OPENModifyLabelui.labelNameLineEdit.text()
        if label not in self.tempLabelHist:
            self.tempLabelHist.append(label)
            self.OPENModifyLabelui.labelListWidget.addItem(label)

    def saveLabelHist(self):
        with open(self.defaultPrefdefClassFile, 'w') as filehandle:
            self.labelHist.clear()
            for label in self.tempLabelHist:
                filehandle.write(label+"\n")
                self.labelHist.append(label)
        self.OPEN_window.close()

    def populateModeActions(self):
        if self.beginner():
            tool, menu = self.actions.beginner, self.actions.beginnerContext
        else:
            tool, menu = self.actions.advanced, self.actions.advancedContext
        self.tools.clear()
        addActions(self.tools, tool)
        self.canvas.menus[0].clear()
        addActions(self.canvas.menus[0], menu)
        self.menus.menu.clear()
        addActions(self.menus.menu, self.actions.menuMenu)
        addActions(self.menus.tool, self.actions.toolMenu)
        addActions(self.menus.model, self.actions.modelMenu)

    def setDirty(self):
        self.dirty = True
        self.actions.save.setEnabled(True)

    def setClean(self):
        self.dirty = False
        self.actions.save.setEnabled(False)
        self.actions.create.setEnabled(False)
        self.logContainer.clear()
        for menu in self.actions.menuMenu:
            menu.setChecked(False)
        for menu in self.actions.resetDeActive:
            menu.setEnabled(False)
        self.sporeCountOption.setDisabled(False)
        for count in self.actions.toolMenu:
            count.setDisabled(False)


    def toggleActions(self):
        for z in self.actions.zoomActions:
            z.setEnabled(True)
        for action in self.actions.onLoadActive:
            action.setEnabled(False)
        self.countEnable = 1

    def status(self, message, delay=5000):
        self.statusBar().showMessage(message, delay)

    def resetState(self):
        self.itemsToShapes.clear()
        self.shapesToItems.clear()
        self.labelList.clear()
        self.filePath = None
        self.imageData = None
        self.labelFile = None
        self.canvas.resetState()
        self.labelCoordinates.clear()

    def currentItem(self):
        items = self.labelList.selectedItems()
        if items:
            return items[0]
        return None

    def addRecentFile(self, filePath):
        if filePath in self.recentFiles:
            self.recentFiles.remove(filePath)
        elif len(self.recentFiles) >= self.maxRecent:
            self.recentFiles.pop()
        self.recentFiles.insert(0, filePath)

    def beginner(self):
        return self._beginner

    def createShape(self):
        assert self.beginner()
        self.canvas.setEditing(False)
        self.actions.create.setEnabled(False)

    def toggleDrawingSensitive(self, drawing=True):
        if not drawing and self.beginner():
            print('Cancel creation.')
            self.canvas.setEditing(True)
            self.canvas.restoreCursor()
            self.actions.create.setEnabled(True)

    def updateFileMenu(self):
        currFilePath = self.filePath
        def exists(filename):
            return os.path.exists(filename)
        files = [f for f in self.recentFiles if f !=
                 currFilePath and exists(f)]
        for i, f in enumerate(files):
            icon = newIcon('labels')
            action = QAction(
                icon, '&%d %s' % (i + 1, QFileInfo(f).fileName()), self)
            action.triggered.connect(partial(self.loadRecent, f))

    def popLabelListMenu(self, point):
        self.menus.labelList.exec_(self.labelList.mapToGlobal(point))

    def shapeSelectionChanged(self, selected=False):
        if self._noSelectionSlot:
            self._noSelectionSlot = False
        else:
            shape = self.canvas.selectedShape
            if shape:
                self.shapesToItems[shape].setSelected(True)
            else:
                self.labelList.clearSelection()
        self.actions.delete.setEnabled(selected)
        self.actions.copy.setEnabled(selected)

    def addLabel(self, shape):
        item = HashableQListWidgetItem(shape.label)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Checked)
        item.setBackground(generateColorByText(shape.label))
        self.itemsToShapes[item] = shape
        self.shapesToItems[shape] = item
        self.labelList.addItem(item)

    def remLabel(self, shape):
        if shape is None:
            return
        item = self.shapesToItems[shape]
        self.labelList.takeItem(self.labelList.row(item))
        del self.shapesToItems[shape]
        del self.itemsToShapes[item]

    def saveFile(self):
        annotationFilePath = "images\\img_"+str(self.selectedPointList[self.currentIndexOfSelectedPoint-1])+".xml"
        filePath = "images\\img_"+str(self.selectedPointList[self.currentIndexOfSelectedPoint-1])+".jpg"
        if self.labelFile is None:
            self.labelFile = LabelFile()
            self.labelFile.verified = self.canvas.verified

        def format_shape(s):
            return dict(label=s.label,
                        line_color=s.line_color.getRgb(),
                        fill_color=s.fill_color.getRgb(),
                        points=[(p.x(), p.y()) for p in s.points],
                        difficult = s.difficult)

        shapes = [format_shape(shape) for shape in self.canvas.shapes]
        try:
            imageFilePath = os.popen('cd').read()[:-1]
            self.labelFile.savePascalVocFormat(annotationFilePath, shapes, imageFilePath+"\\"+filePath)
            return True
        except:
            self.errorMessage(u'Error', u'Error in saving label data')
            return False

    def copySelectedShape(self):
        self.addLabel(self.canvas.copySelectedShape())
        self.shapeSelectionChanged(True)

    def labelSelectionChanged(self):
        item = self.currentItem()
        if item and self.canvas.editing():
            self._noSelectionSlot = True
            self.canvas.selectShape(self.itemsToShapes[item])
            shape = self.itemsToShapes[item]

    def newShape(self):
        if not self.shapeFlag:
            if len(self.labelHist) > 0:
                self.labelDialog = LabelDialog(parent=self, listItem=self.labelHist)
            self.shapeFlag = True
        else:
            self.labelDialog = LabelDialog(parent=self, listItem=[self.lastLabel])
        text = self.labelDialog.popUp(text=self.prevLabelText)
        self.lastLabel = text

        if text is not None:
            self.prevLabelText = text
            generate_color = generateColorByText(text)
            shape = self.canvas.setLastLabel(text, generate_color, generate_color)
            self.addLabel(shape)
            if self.beginner():  # Switch to edit mode.
                self.canvas.setEditing(True)
                self.actions.create.setEnabled(True)
            self.setDirty()
            if text not in self.labelHist:
                self.labelHist.append(text)
        else:
            self.canvas.resetAllLines()

    def scrollRequest(self, delta, orientation):
        units = - delta / (8 * 15)
        bar = self.scrollBars[orientation]
        bar.setValue(bar.value() + bar.singleStep() * units)

    def setZoom(self, value):
        self.actions.fitWidth.setChecked(False)
        self.actions.fitWindow.setChecked(False)
        self.zoomMode = self.MANUAL_ZOOM
        self.zoomWidget.setValue(value)

    def addZoom(self, increment=10):
        self.setZoom(self.zoomWidget.value() + increment)

    def zoomRequest(self, delta):
        h_bar = self.scrollBars[Qt.Horizontal]
        v_bar = self.scrollBars[Qt.Vertical]
        h_bar_max = h_bar.maximum()
        v_bar_max = v_bar.maximum()
        cursor = QCursor()
        pos = cursor.pos()
        relative_pos = QWidget.mapFromGlobal(self, pos)
        cursor_x = relative_pos.x()
        cursor_y = relative_pos.y()
        w = self.scrollArea.width()
        h = self.scrollArea.height()
        margin = 0.1
        move_x = (cursor_x - margin * w) / (w - 2 * margin * w)
        move_y = (cursor_y - margin * h) / (h - 2 * margin * h)
        move_x = min(max(move_x, 0), 1)
        move_y = min(max(move_y, 0), 1)
        units = delta / (8 * 15)
        scale = 10
        self.addZoom(scale * units)
        d_h_bar_max = h_bar.maximum() - h_bar_max
        d_v_bar_max = v_bar.maximum() - v_bar_max
        new_h_bar_value = h_bar.value() + move_x * d_h_bar_max
        new_v_bar_value = v_bar.value() + move_y * d_v_bar_max
        h_bar.setValue(new_h_bar_value)
        v_bar.setValue(new_v_bar_value)

    def setFitWindow(self, value=True):
        if value:
            self.actions.fitWidth.setChecked(False)
        self.zoomMode = self.FIT_WINDOW if value else self.MANUAL_ZOOM
        self.adjustScale()

    def setFitWidth(self, value=True):
        if value:
            self.actions.fitWindow.setChecked(False)
        self.zoomMode = self.FIT_WIDTH if value else self.MANUAL_ZOOM
        self.adjustScale()

    def loadFile(self, filePath=None):
        self.resetState()
        self.canvas.setEnabled(False)
        if filePath is None:
            filePath = self.settings.get(SETTING_FILENAME)

        absFilePath = os.path.abspath(filePath)
        if absFilePath and os.path.exists(absFilePath):
            self.imageData = read(absFilePath, None)
            self.labelFile = None
            self.canvas.verified = False
            image = QImage.fromData(self.imageData)
            if image.isNull():
                self.setClean()
                self.sporeCountOption.setDisabled(True)
                self.labelImage.setDisabled(True)
                return False
            self.status("Loaded %s" % os.path.basename(absFilePath))
            self.image = image
            self.filePath = absFilePath
            self.canvas.loadPixmap(QPixmap.fromImage(image))
            self.setClean()
            self.canvas.setEnabled(True)
            self.adjustScale(initial=True)
            self.paintCanvas()
            self.addRecentFile(self.filePath)
            self.toggleActions()
            self.setWindowTitle(__appname__ + ' ' + filePath)
            self.canvas.setFocus(True)
            # print(filePath)
            self.imageObj = ImageOperation(filePath)
            self.imageObj.loadImage()
            self.imageObj.cannyConvert()
            self.imageObj.findHoughLines()
            self.imageObj.sort_lines()
            return True
        return False

    def paintCanvas(self):
        assert not self.image.isNull(), "cannot paint null image"
        self.canvas.scale = 0.01 * self.zoomWidget.value()
        self.canvas.adjustSize()
        self.canvas.update()

    def adjustScale(self, initial=False):
        value = self.scalers[self.FIT_WINDOW if initial else self.zoomMode]()
        self.zoomWidget.setValue(int(100 * value))

    def scaleFitWindow(self):
        e = 2.0
        w1 = self.centralWidget().width() - e
        h1 = self.centralWidget().height() - e
        a1 = w1 / h1
        w2 = self.canvas.pixmap.width() - 0.0
        h2 = self.canvas.pixmap.height() - 0.0
        a2 = w2 / h2
        return w1 / w2 if a2 >= a1 else h1 / h2

    def scaleFitWidth(self):
        w = self.centralWidget().width() - 2.0
        return w / self.canvas.pixmap.width()

    def loadRecent(self, filename):
        if self.mayContinue():
            self.loadFile(filename)

    def openFile(self, _value=False):
        if not self.mayContinue():
            return
        path = os.path.dirname(self.filePath) if self.filePath else '.'
        formats = ['*.%s' % fmt.data().decode("ascii").lower() for fmt in QImageReader.supportedImageFormats()]
        filters = "Image & Label files (%s)" % ' '.join(formats + ['*%s' % LabelFile.suffix])
        filename = QFileDialog.getOpenFileName(self, '%s - Choose Image or Label file' % __appname__, path, filters)
        if filename:
            if isinstance(filename, (tuple, list)):
                filename = filename[0]
            self.loadFile(filename)

    def mayContinue(self):
        return not (self.dirty and not self.discardChangesDialog())

    def discardChangesDialog(self):
        yes, no = QMessageBox.Yes, QMessageBox.No
        msg = u'You have unsaved changes, proceed anyway?'
        return yes == QMessageBox.warning(self, u'Attention', msg, yes | no)

    def errorMessage(self, title, message):
        return QMessageBox.critical(self, title,
                                    '<p><b>%s</b></p>%s' % (title, message))

    def currentPath(self):
        return os.path.dirname(self.filePath) if self.filePath else '.'

    def deleteSelectedShape(self):
        self.remLabel(self.canvas.deleteSelected())
        self.setDirty()

    def copyShape(self):
        self.canvas.endMove(copy=True)
        self.addLabel(self.canvas.selectedShape)
        self.setDirty()

    def moveShape(self):
        self.canvas.endMove(copy=False)
        self.setDirty()

    def loadPredefinedClasses(self, predefClassesFile):
        if os.path.exists(predefClassesFile) is True:
            with codecs.open(predefClassesFile, 'r', 'utf8') as f:
                for line in f:
                    line = line.strip()
                    if self.labelHist is None:
                        self.labelHist = [line]
                    else:
                        self.labelHist.append(line)

def read(filename, default=None):
    try:
        with open(filename, 'rb') as f:
            return f.read()
    except:
        return default


def get_main_app(argv=[]):
    app = QApplication(argv)
    app.setApplicationName(__appname__)
    app.setWindowIcon(newIcon("app"))
    win = MainWindow(None,os.path.join(os.path.dirname(sys.argv[0]),
                         'data', 'predefined_classes.txt'),None)
    win.show()
    return app, win

def main():
    app, _win = get_main_app(sys.argv)
    return app.exec_()

if __name__ == '__main__':
    sys.exit(main())
