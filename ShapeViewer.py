from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import shapely
from shapely.wkt import dumps,loads
from SelectTool import SelectMapTool
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
    QObject.connect(self.mBtnElevation,  SIGNAL("clicked()"),  self.setSelectionTool)

    # Set the title for the app
    self.setWindowTitle("ShapeViewer")

    # Create the map canvas
    self.canvas = QgsMapCanvas()
    self.canvas.useImageToRender(False)
    self.canvas.setCanvasColor(Qt.white)
    self.canvas.enableAntiAliasing(True)
    self.canvas.show()
    
    # Add map tools
    self.selectTool = SelectMapTool(self.canvas)
    
    self.demLayer = QgsRasterLayer()

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
	# Set extent to the extent of our layer
	self.canvas.setExtent(layer.extent())
	QgsMapLayerRegistry.instance().addMapLayer(layer)
	layers = self.canvas.mapRenderer().layerSet()
	layers.append(layer.id())
	self.canvas.mapRenderer().setLayerSet(layers)

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
	
	self.layer = layer

    # Add layer to the registry
	# Set extent to the extent of our layer
	self.canvas.setExtent(layer.extent())
	QgsMapLayerRegistry.instance().addMapLayer(layer)
	layers = self.canvas.mapRenderer().layerSet()
	layers.append(layer.id())
	self.canvas.mapRenderer().setLayerSet(layers)
	qDebug("layer loaded successfully!!" )
	
  def getElevation(self, point):
	#point is QgsPoint
	choosenBand = 0
	attr = 0
	if QGis.QGIS_VERSION_INT >= 10900: # for QGIS >= 1.9
			# this code adapted from valuetool plugin
			ident = self.demLayer.dataProvider().identify(point, QgsRasterDataProvider.IdentifyFormatValue )
			if ident is not None and ident.has_key(choosenBand+1):
					attr = ident[choosenBand+1].toDouble()[0]
					if self.demLayer.dataProvider().isNoDataValue ( choosenBand+1, attr ): 
							attr = 0
	else:
			ident = self.demLayer.identify(point)
			try:
					attr = float(ident[1].values()[choosenBand])
			except:
					pass
	return attr
					
  def getPointAtDistance(self,distance,geometry):
	  shapelyLineGeom = loads(str(geometry.exportToWkt()))
	  shapelyPoint =  shapelyLineGeom.interpolate(distance)
	  qgsPointGeom = QgsGeometry.fromWkt(shapelyPoint.wkt)
	  return qgsPointGeom
	  
  def getSegmentedPoints(self, geometry, ratio):
	  #return list of QgsPoint
	  pointList = []
	  geomLength = geometry.length()
	  perc = ratio * geomLength
	  length = -perc
	  while(length < geomLength):
		  length = length + perc
		  point = self.getPointAtDistance(length, geometry)
		  pointList.append(point)
	  return pointList
	  
  def getElevationTest(self):
	  g1 = QgsGeometry.fromWkt('LINESTRING(490351.96514423 4548291.73076923, 494542.01322115 4541976.58653846)')
	  spoints = self.getSegmentedPoints(g1,0.1)
	  for item in spoints:
		  print "print points....."
		  print item.exportToWkt()		
	   
  def showBuffer(self):
	width, ok = QtGui.QInputDialog.getDouble(iface.mapCanvas(), 'Input Dialog', 'Enter Width:')
	qDebug("Loading Vector Layer")
    # layout is set - open a layer
    # Add an OGR layer to the map
	file = QFileDialog.getOpenFileName(self, "Open Raster", ".", "Rasters (*.*)")
	fileInfo = QFileInfo(file)

  def setSelectionTool(self):
	  self.canvas.setMapTool(self.selectTool)	

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

