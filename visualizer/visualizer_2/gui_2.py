import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QStatusBar
from PyQt5.QtWidgets import QToolBar
from PyQt5.QtWidgets import QAction

class MainWindow(QMainWindow):
    """Main Window."""
    def __init__(self, sceneView, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.setWindowTitle('QMainWindow')
        self.setModelView(sceneView)

        self.reset_scale = QAction("Fit to View", self)
        self.reset_scene = QAction("Reset", self)
        self.step_back = QAction("Step back", self)
        self.step_forward = QAction("Step forward", self)

        self.reset_scale.triggered.connect(self._centralView.resizeToFit)
        self.reset_scene.triggered.connect(self._scene.reset_scene)
        self.step_back.triggered.connect(self._scene.previous_step)
        self.step_forward.triggered.connect(self._scene.next_step)
        self._createToolBar()
        self._createMenu()
        self._createStatusBar()

    def _createMenu(self):
        self.menu = self.menuBar().addMenu("&Menu")
        self.menu.addAction('&Exit', self.close)

    def _createToolBar(self):
        tools = QToolBar()
        self.addToolBar(tools)
        tools.addAction(self.reset_scale)
        tools.addAction(self.reset_scene)
        tools.addAction(self.step_back)
        tools.addAction(self.step_forward)

    def _createStatusBar(self):
        status = QStatusBar()
        status.showMessage("Status Bar yet to be implemented.")
        self.setStatusBar(status)

    def setModelView(self, view):
        self._centralView = view
        self._scene = self._centralView.get_scene()
        self._centralView.setToolTip("ModelView")
        self._centralView.resizeToFit()
        self.setCentralWidget(view)

