from PyQt5.QtWidgets import QGraphicsView, QOpenGLWidget
from PyQt5.QtCore import Qt

class ModelView(QGraphicsView):
    """
    Shows a ModelScene.
    """

    def __init__(self, scene):
        super(self.__class__, self).__init__(scene)
        self._scene = scene
        self.setViewport(QOpenGLWidget())
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)
        self._scene.get_sprites().set_scale(self.transform().m11())
        self.update()

    def resizeToFit(self):
        print("Resizing Window...")
        self.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)
        self._scene.get_sprites().set_scale(self.transform().m11())

    def get_scene(self):
        return self._scene

    def scale_up(self):
        self._scene.get_sprites().set_scale(64)
        print("Scaling up")

    # TODO: smooth scaling
    def scale_down(self):
        self._scene.get_sprites().set_scale(16)
        print("Scaling down")

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self._scene.get_sprites().set_scale(self.transform().m11() * 1.25)
            self.scale(1.25, 1.25)
            print(self.transform().m11())
            # self._scene.get_sprites().scale(1.2)

        else:
            self._scene.get_sprites().set_scale(self.transform().m11() * 0.8)
            self.scale(0.8, 0.8)
            print(self.transform().m11())
            # self._scene.get_sprites().scale(0.8)
