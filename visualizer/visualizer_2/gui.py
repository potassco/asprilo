import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QStatusBar
from PyQt5.QtWidgets import QToolBar
from PyQt5.QtWidgets import QAction, QCheckBox, QComboBox, QDockWidget, QGraphicsView, QOpenGLWidget, QTabWidget, QTextEdit, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from modelscene import ModelScene
from modelview import ModelView
from os import path
import solveutils


class MainWindow(QMainWindow):
    """Main Window."""

    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)

        self.setWindowTitle("MAPF-Visualizer")

        self.mainpane = self._create_central_pane()
        self.sidebar = self._create_sidebar()
        self.scenecontrol = self._createToolBar()
        self.menu = self._createMenu()
        self.statusbar = self._createStatusBar()

    def _create_central_pane(self):
        cpane = QTabWidget()
        cpane.setMovable(True)
        cpane.setTabsClosable(True)
        cpane.currentChanged.connect(self._sync_active_scene)
        self.setCentralWidget(cpane)
        return cpane

    def solve_and_add(self, file, config):
        name = path.basename(file.name)
        with file as source:
            scene = ModelScene(solveutils.solve_from_file(source, config["atom"]))
        self.add_scene(scene, name)

    def add_scene(self, scene: ModelScene, name="Scene"):
        view = ModelView(scene)
        view.setViewport(QOpenGLWidget())
        self.mainpane.addTab(ViewPane(view), name)
        self._sync_active_scene()

    def _sync_active_scene(self):
        scene = self.mainpane.currentWidget().view.get_scene()
        self.sidebar.connect_scene(scene)
        self.scenecontrol.connect_scene(scene)


    def _create_sidebar(self):
        sidebar = SidePanel("Step Overview")
        self.addDockWidget(Qt.LeftDockWidgetArea, sidebar)
        return sidebar

    def _createMenu(self):
        self.menu = self.menuBar().addMenu("&Menu")
        self.menu.addAction('&Exit', self.close)

    # def _createAnimationCheckbox(self):
    #     abox = QCheckBox("Animate")
    #     abox.stateChanged.connect(self._scene.set_animation)
    #     return abox

    def _createToolBar(self):
        scenecontrol = SceneControl()
        self.addToolBar(Qt.BottomToolBarArea, scenecontrol)
        return scenecontrol

    def _createStatusBar(self):
        status = QStatusBar()
        status.showMessage("Status Bar yet to be implemented.")
        self.setStatusBar(status)
        return status


class SceneControl(QToolBar):
    def __init__(self, scene=None, parent=None):
        super().__init__(parent)
        self.scene = None
        self._init_buttons()
        self.connect_scene(scene)

    def connect_scene(self, scene):
        if self.scene != None:
            self.reset_scene.triggered.disconnect(scene.reset_scene)
            self.step_back.triggered.disconnect(scene.previous_step)
            self.step_forward.triggered.disconnect(scene.next_step)
            self.step_last.triggered.disconnect(scene.last_step)
            self.save_to_png.triggered.disconnect(scene.save_to_png)
            self.toggle_paths.triggered.disconnect(scene.toggle_paths)
        
        self.scene = scene
        if scene == None:
            return

        self.reset_scene.triggered.connect(scene.reset_scene)
        self.step_back.triggered.connect(scene.previous_step)
        self.step_forward.triggered.connect(scene.next_step)
        self.step_last.triggered.connect(scene.last_step)
        self.save_to_png.triggered.connect(scene.save_to_png)
        self.toggle_paths.triggered.connect(scene.toggle_paths)
    
    def _init_buttons(self):
        self.reset_scene = QAction("Reset")
        self.step_back = QAction("Step back")
        self.step_forward = QAction("Step forward")
        self.step_last = QAction("Go to last step")
        self.save_to_png = QAction("Save Image")
        self.toggle_paths = QAction("Toggle Paths")

        self.addAction(self.toggle_paths)
        self.addSeparator()

        # Add timestep options
        self.addAction(self.reset_scene)
        self.addAction(self.step_back)
        self.addAction(self.step_forward)
        self.addAction(self.step_last)
        self.addSeparator()

        # Add other options
        self.addAction(self.save_to_png)


class ViewControl(QToolBar):
    def __init__(self, view=None, parent=None):
        super().__init__(parent)
        self._init_buttons()
        self.connect_view(view)

    def connect_view(self, view):
        self.view = view
        if view == None:
            return

        self.reset_scale.triggered.connect(view.resizeToFit)

    def _init_buttons(self):
        self.reset_scale = QAction("Fit to screen")
        
        self.addAction(self.reset_scale)


class SidePanel(QDockWidget):
    def __init__(self, title, scene=None, parent=None):
        super().__init__(title, parent)
        self.setWidget(QWidget())
        self.scene = None
        self.stepbox = QComboBox()
        self.steptext = QTextEdit()
        self.stepbox.currentTextChanged.connect(self.report)
        layout = QVBoxLayout(self.widget())
        layout.addSpacing(20)
        layout.addWidget(self.stepbox)
        layout.addSpacing(10)
        layout.addWidget(self.steptext)
        layout.addSpacing(20)

        self.connect_scene(scene)

    def connect_scene(self, scene):
        self.disconnect()
        self.scene = scene

        if scene == None:
            self.atoms = {0: ""}
        
        else:
            self.atoms = scene._model.get_atoms()
            self._init_stepbox()
            self.set_to_step(scene._current_step)
            self.scene.currentStepChanged.connect(self.set_to_step)
            self.stepbox.currentTextChanged.connect(self.scene.go_to_step)

    def disconnect(self):
        if self.scene != None:
            self.scene.currentStepChanged.disconnect(self.set_to_step)
            self.stepbox.currentTextChanged.disconnect(self.scene.go_to_step)

    def report(self, step):
        print(f"Sending request to go to step {step}!")

    def set_to_step(self, step: int):
        if step in self.atoms:
            self.stepbox.blockSignals(True)
            self.stepbox.setCurrentText(str(step))
            self.stepbox.blockSignals(False)
            self.steptext.setText(".\n".join(self.atoms[step]))

    def _init_stepbox(self):
        self.stepbox.blockSignals(True)
        self.stepbox.clear()
        if "0" not in self.atoms:
            self.stepbox.addItem("0")
        for step in sorted(self.atoms):
            self.stepbox.addItem(str(step))
        self.stepbox.blockSignals(False)



class ViewPane(QWidget):
    def __init__(self, view, parent=None):
        super().__init__(parent)
        
        self.view = view

        layout = QVBoxLayout(self)
        layout.addWidget(view)
        layout.addWidget(ViewControl(view))