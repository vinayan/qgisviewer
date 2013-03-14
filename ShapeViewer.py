from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import sys
import os
# Import our GUI
from shapeviewer_gui import Ui_MainWindow

# Environment variable QGISHOME must be set to the install directory
# before running the application
qgis_prefix = os.getenv("QGISHOME")

class ShapeViewer(QMainWindow, Ui_MainWindow):

  def __init__(self):
    QMainWindow.__init__(self)

    # Required by Qt4 to initialize the UI
    self.setupUi(self)
    #self.ui = Ui_MainWindow()
    #self.ui.setupUi(self)
    qDebug("trying to configure signals" )
    QObject.connect(self.mBtnZoomIn,  SIGNAL("clicked()"),  self.zoomIn)
    QObject.connect(self.mBtnZoomOut,  SIGNAL("clicked()"),  self.zoomOut)
    QObject.connect(self.mBtnAddVector,  SIGNAL("clicked()"),  self.loadVectorLayer)
    QObject.connect(self.mBtnAddRaster,  SIGNAL("clicked()"),  self.loadRasterLayer)

    # Set the title for the app
    self.setWindowTitle("ShapeViewer")

    # Create the map canvas
    self.canvas = QgsMapCanvas()
    self.canvas.useImageToRender(False)
    self.canvas.setCanvasColor(Qt.white)
    self.canvas.enableAntiAliasing(True)
    self.canvas.show()

    # Lay our widgets out in the main window using a 
    # vertical box layout
    self.layout = QVBoxLayout(self.frame)
    self.layout.addWidget(self.canvas)


    
  def zoomIn(self):
	  qDebug("Zoom In Activated")
	  self.canvas.zoomIn();
	  
  def zoomOut(self):
	qDebug("Zoom Out Activated")
	self.canvas.zoomOut();

  def loadVectorLayer(self):
	qDebug("Loading Vector Layer")
    # layout is set - open a layer
    # Add an OGR layer to the map
	file = QFileDialog.getOpenFileName(self, "Open Shapefile", ".", "Shapefiles (*.shp)")
	fileInfo = QFileInfo(file)
	
	# Add the layer
	layer = QgsVectorLayer(file, fileInfo.fileName(), "ogr")
	
	if not layer.isValid():
		return

    # Add layer to the registry
	QgsMapLayerRegistry.instance().addMapLayer(layer)
	
	# Set extent to the extent of our layer
	self.canvas.setExtent(layer.extent())

    # Set up the map canvas layer set
	cl = QgsMapCanvasLayer(layer)
	layers = [cl]
	self.canvas.setLayerSet(layers)
	qDebug("layer loaded successfully!!" )
	
  def loadRasterLayer(self):
	qDebug("Loading Vector Layer")
    # layout is set - open a layer
    # Add an OGR layer to the map
	file = QFileDialog.getOpenFileName(self, "Open Raster", ".", "Rasters (*.*)")
	fileInfo = QFileInfo(file)
	
	# Add the layer
	#layer = QgsVectorLayer(file, fileInfo.fileName(), "ogr")
	layer = QgsRasterLayer(file, fileInfo.fileName())
	
	if not layer.isValid():
		return

    # Add layer to the registry
	QgsMapLayerRegistry.instance().addMapLayer(layer)
	
	# Set extent to the extent of our layer
	self.canvas.setExtent(layer.extent())

    # Set up the map canvas layer set
	cl = QgsMapCanvasLayer(layer)
	layers = [cl]
	self.canvas.setLayerSet(layers)
	qDebug("layer loaded successfully!!" )

def main(argv):
  # create Qt application
  app = QApplication(argv)

  # Initialize qgis libraries
  QgsApplication.setPrefixPath(qgis_prefix, True)
  QgsApplication.initQgis()

  # create main window
  wnd = ShapeViewer()
  # Move the app window to upper left
  wnd.move(100,100)
  wnd.show()

  # run!
  retval = app.exec_()
  
  # exit
  QgsApplication.exitQgis()
  sys.exit(retval)


if __name__ == "__main__":
  main(sys.argv)

