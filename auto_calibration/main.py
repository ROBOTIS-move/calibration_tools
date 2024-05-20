import sys

import gui_control

from PySide6 import QtWidgets


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ui = gui_control.GuiControl()
    ui.show()
    sys.exit(app.exec())
