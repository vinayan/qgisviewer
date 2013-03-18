# PyQt4 includes for python bindings to QT
from PyQt4.QtCore import *
from PyQt4.QtGui import *
# QGIS bindings for mapping functions
from qgis.core import *
from qgis.gui import *

class SelectMapTool(QgsMapTool):   
    def __init__(self, canvas):
        QgsMapTool.__init__(self,canvas)
        self.dragging=False
        self.rubberBand = 0
        self.canvas=canvas
        self.ll = None
        self.ur = None
        self.o = QObject()
        self.cursor = QCursor(QPixmap(["13 13 3 1",
                                       "# c None","a c #222222",". c #dddddd",
                                       "#####...#####",
                                       "#####.a.#####",
                                       "#####.a.#####",
                                       "#####.a.#####",
                                       "#####.a.#####",
                                       "......a......",
                                       ".aaaaaaaaaaa.",
                                       "......a......",
                                       "#####.a.#####",
                                       "#####.a.#####",
                                       "#####.a.#####",
                                       "#####.a.#####",
                                       "#####...#####"]))
        
    def canvasPressEvent(self,event):
        self.selectRect.setRect(event.pos().x(),event.pos().y(),0,0)
        capture_string = QString("Starting Rectangle")
        print capture_string

    def canvasMoveEvent(self,event):
        if not event.buttons() == Qt.LeftButton:
            return
        if not self.dragging:
            self.dragging=True
            self.rubberBand = QRubberBand(QRubberBand.Rectangle,self.canvas)
        self.selectRect.setBottomRight(event.pos())
        self.rubberBand.setGeometry(self.selectRect.normalized())
        self.rubberBand.show()

    def canvasReleaseEvent(self,e):
        if not self.dragging:
            return
        self.rubberBand.hide()
        self.selectRect.setRight(e.pos().x())
        self.selectRect.setBottom(e.pos().y())
        transform = self.canvas.getCoordinateTransform()
        ll = transform.toMapCoordinates(self.selectRect.left(),
                                        self.selectRect.bottom())
        ur = transform.toMapCoordinates(self.selectRect.right(),
                                        self.selectRect.top())
        self.bb = QgsRectangle(
            QgsPoint(ll.x(),ll.y()),
            QgsPoint(ur.x(),ur.y())
            )
        self.o.emit(SIGNAL("finished()"))
        capture_string = QString("releasing event completed")
        print capture_string
        
    def activate(self):
        #print "Start Rectangle Tool"
        capture_string = QString("Starting Rectangle")
        self.canvas.setCursor(self.cursor)
        capture_string = QString("Draw rectangle on canvas " +
                                 "to capture coordinates...")
        print capture_string

    def deactivate(self):
        capture_string = QString("End Rectangle Tool")
        print capture_string


    def isZoomTool(self):
        return False
