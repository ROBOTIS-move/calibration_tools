from PySide6.QtCore import QCoreApplication, QMetaObject, QSize, Qt
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QLayout,
    QPushButton,
    QSizePolicy,
    QTextBrowser,
    QWidget)


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u'MainWindow')
        MainWindow.setEnabled(True)
        MainWindow.resize(1024, 600)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.actionFull_screen = QAction(MainWindow)
        self.actionFull_screen.setObjectName(u'actionFull_screen')
        self.actionFull_screen.setCheckable(True)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u'centralwidget')
        self.centralwidget.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy1)
        self.centralwidget.setMinimumSize(QSize(1024, 600))
        self.centralwidget.setSizeIncrement(QSize(0, 0))
        self.gridLayout_2 = QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName(u'gridLayout_2')
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u'gridLayout')
        self.gridLayout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.initialization_push_button = QPushButton(self.centralwidget)
        self.initialization_push_button.setObjectName(u'initialization_push_button')
        self.initialization_push_button.setEnabled(False)
        sizePolicy1.setHeightForWidth(
            self.initialization_push_button.sizePolicy().hasHeightForWidth())
        self.initialization_push_button.setSizePolicy(sizePolicy1)
        self.initialization_push_button.setMinimumSize(QSize(250, 100))
        font = QFont()
        font.setPointSize(25)
        font.setBold(True)
        self.initialization_push_button.setFont(font)
        self.initialization_push_button.setCheckable(True)

        self.gridLayout.addWidget(self.initialization_push_button, 1, 1, 1, 1)

        self.pass_fail_label = QLabel(self.centralwidget)
        self.pass_fail_label.setObjectName(u'pass_fail_label')
        self.pass_fail_label.setEnabled(False)
        sizePolicy1.setHeightForWidth(
            self.pass_fail_label.sizePolicy().hasHeightForWidth())
        self.pass_fail_label.setSizePolicy(sizePolicy1)
        self.pass_fail_label.setMinimumSize(QSize(250, 100))
        self.pass_fail_label.setFont(font)
        self.pass_fail_label.setStyleSheet(u'')
        self.pass_fail_label.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.pass_fail_label, 3, 1, 1, 1)

        self.calibration_push_button = QPushButton(self.centralwidget)
        self.calibration_push_button.setObjectName(
            u'calibration_push_button')
        self.calibration_push_button.setEnabled(False)
        sizePolicy1.setHeightForWidth(
            self.calibration_push_button.sizePolicy().hasHeightForWidth())
        self.calibration_push_button.setSizePolicy(sizePolicy1)
        self.calibration_push_button.setMinimumSize(QSize(250, 100))
        self.calibration_push_button.setFont(font)
        self.calibration_push_button.setCheckable(True)

        self.gridLayout.addWidget(self.calibration_push_button, 2, 1, 1, 1)

        self.connection_push_button = QPushButton(self.centralwidget)
        self.connection_push_button.setObjectName(u'connection_push_button')
        sizePolicy1.setHeightForWidth(
            self.connection_push_button.sizePolicy().hasHeightForWidth())
        self.connection_push_button.setSizePolicy(sizePolicy1)
        self.connection_push_button.setMinimumSize(QSize(250, 100))
        self.connection_push_button.setFont(font)
        self.connection_push_button.setCheckable(True)

        self.gridLayout.addWidget(self.connection_push_button, 0, 1, 1, 1)

        self.rom_writing_push_button = QPushButton(self.centralwidget)
        self.rom_writing_push_button.setObjectName(u'rom_writing_push_button')
        self.rom_writing_push_button.setEnabled(False)
        sizePolicy1.setHeightForWidth(
            self.rom_writing_push_button.sizePolicy().hasHeightForWidth())
        self.rom_writing_push_button.setSizePolicy(sizePolicy1)
        self.rom_writing_push_button.setMinimumSize(QSize(250, 100))
        self.rom_writing_push_button.setFont(font)
        self.rom_writing_push_button.setCheckable(True)
        self.rom_writing_push_button.setChecked(False)

        self.gridLayout.addWidget(self.rom_writing_push_button, 4, 1, 1, 1)

        self.image_stream = QLabel(self.centralwidget)
        self.image_stream.setObjectName(u'image_stream')
        sizePolicy1.setHeightForWidth(self.image_stream.sizePolicy().hasHeightForWidth())
        self.image_stream.setSizePolicy(sizePolicy1)
        self.image_stream.setMinimumSize(QSize(748, 463))
        self.image_stream.setSizeIncrement(QSize(0, 0))
        self.image_stream.setBaseSize(QSize(0, 0))
        self.image_stream.setFrameShape(QFrame.NoFrame)

        self.gridLayout.addWidget(self.image_stream, 0, 0, 4, 1)

        self.log_text_browser = QTextBrowser(self.centralwidget)
        self.log_text_browser.setObjectName(u'log_text_browser')
        font1 = QFont()
        font1.setPointSize(10)
        self.log_text_browser.setFont(font1)

        self.gridLayout.addWidget(self.log_text_browser, 4, 0, 1, 1)

        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate('MainWindow', u'MainWindow', None))
        self.actionFull_screen.setText(
            QCoreApplication.translate('MainWindow', u'Full-screen', None))
        self.initialization_push_button.setText(
            QCoreApplication.translate('MainWindow', u'Initialization', None))
        self.pass_fail_label.setText(
            QCoreApplication.translate('MainWindow', u'Result', None))
        self.calibration_push_button.setText(
            QCoreApplication.translate('MainWindow', u'Calibration', None))
        self.connection_push_button.setText(
            QCoreApplication.translate('MainWindow', u'Connection', None))
        self.rom_writing_push_button.setText(
            QCoreApplication.translate('MainWindow', u'ROM writing', None))
        self.image_stream.setText('')
