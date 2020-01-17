
from PyQt5.QtGui import QPixmapCache, QPixmap, QImage, QPainter
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtCore import QRectF, Qt


class SpriteContainer(object):

    def __init__(self, spriteconfig):
        print("Constructing new SpriteContainer")
        super().__init__()
        self._renderer = {}
        self._pixmapdict = {}
        self._placeholder = QPixmap(["2 2 2 1", "a c #ffffff", "b c #000000", "ab", "ba"])
        self._init_renderer(spriteconfig)
        self._render_sprites(10)

    def _init_renderer(self, spriteconfig):
        self._renderer = {x[0]: QSvgRenderer(x[1]) for x in spriteconfig.items()}

    def _render_sprites(self, length):
        rect = QRectF(0, 0, length, length)
        for item in self._renderer.items():
            image = QImage(length, length, QImage.Format_ARGB32)
            image.fill(Qt.transparent)
            item[1].render(QPainter(image), rect)
            self._pixmapdict[item[0]] = QPixmap.fromImage(image)

    # Probably inefficient use of QPainter, but should not be relevant.
    def update_sprites(self, length):
        rect = QRectF(0, 0, length, length)
        for name in self._pixmapdict:
            painter = QPainter(self._pixmapdict["name"])
            painter.drawPixmap(QPixmap.fromImage(item[1].render(QPainter(QImage()), rect)))

    def get_pixmap(self, name):
        return self._pixmapdict.setdefault(name, self._placeholder)

    