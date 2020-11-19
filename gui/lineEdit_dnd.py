import os.path
from PyQt4.QtCore import QObject, QEvent


class LineEditDropHandler(QObject):

    def __init__(self, parent=None):
        QObject.__init__(self, parent)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.DragEnter:
            # we need to accept this event explicitly to be able to receive QDropEvents!
            event.accept()
        if event.type() == QEvent.Drop:
            md = event.mimeData()
            if md.hasUrls():
                for url in md.urls():
                    path = os.path.abspath(str(url.path()).lstrip('/'))
                    if os.path.isdir(path):
                        obj.setText(path)
                    break
            event.accept()
        return QObject.eventFilter(self, obj, event)
