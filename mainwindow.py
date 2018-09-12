
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(930, 640)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.comboBox_ramge = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_ramge.setObjectName("comboBox_ramge")
        self.horizontalLayout.addWidget(self.comboBox_ramge)
        self.dateEdit_begin = QtWidgets.QDateEdit(self.centralwidget)
        self.dateEdit_begin.setObjectName("dateEdit_begin")
        self.horizontalLayout.addWidget(self.dateEdit_begin)
        self.timeEdit_begin = QtWidgets.QTimeEdit(self.centralwidget)
        self.timeEdit_begin.setObjectName("timeEdit_begin")
        self.horizontalLayout.addWidget(self.timeEdit_begin)
        self.label_to = QtWidgets.QLabel(self.centralwidget)
        self.label_to.setMaximumSize(QtCore.QSize(15, 16777215))
        self.label_to.setObjectName("label_to")
        self.horizontalLayout.addWidget(self.label_to)
        self.dateEdit_end = QtWidgets.QDateEdit(self.centralwidget)
        self.dateEdit_end.setObjectName("dateEdit_end")
        self.horizontalLayout.addWidget(self.dateEdit_end)
        self.timeEdit_end = QtWidgets.QTimeEdit(self.centralwidget)
        self.timeEdit_end.setObjectName("timeEdit_end")
        self.horizontalLayout.addWidget(self.timeEdit_end)
        self.pushButton_query = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_query.setObjectName("pushButton_query")
        self.horizontalLayout.addWidget(self.pushButton_query)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 1, 1, 2)
        spacerItem = QtWidgets.QSpacerItem(660, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.horizontalLayout_button = QtWidgets.QHBoxLayout()
        self.horizontalLayout_button.setObjectName("horizontalLayout_button")
        self.pushButton_manual = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_manual.setObjectName("pushButton_manual")
        self.horizontalLayout_button.addWidget(self.pushButton_manual)
        self.pushButton_setting = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_setting.setObjectName("pushButton_setting")
        self.horizontalLayout_button.addWidget(self.pushButton_setting)
        self.pushButton_quit = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_quit.setObjectName("pushButton_quit")
        self.horizontalLayout_button.addWidget(self.pushButton_quit)
        self.gridLayout.addLayout(self.horizontalLayout_button, 0, 0, 1, 2)
        self.treeWidget_menu = QtWidgets.QTreeWidget(self.centralwidget)
        self.treeWidget_menu.setMaximumSize(QtCore.QSize(200, 16777215))
        self.treeWidget_menu.setObjectName("treeWidget_menu")
        self.treeWidget_menu.headerItem().setText(0, "1")
        self.gridLayout.addWidget(self.treeWidget_menu, 1, 0, 3, 1)
        self.tableView_log = QtWidgets.QTableView(self.centralwidget)
        self.tableView_log.setObjectName("tableView_log")
        self.gridLayout.addWidget(self.tableView_log, 2, 1, 1, 2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 930, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "数据传输中心"))
        self.label_to.setText(_translate("MainWindow", "至"))
        self.pushButton_query.setText(_translate("MainWindow", "查询"))
        self.pushButton_manual.setText(_translate("MainWindow", "手动传输"))
        self.pushButton_setting.setText(_translate("MainWindow", "设置"))
        self.pushButton_quit.setText(_translate("MainWindow", "退出"))
