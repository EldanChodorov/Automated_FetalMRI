# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FetalMRI_Workspace.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_workspace(object):
    def setupUi(self, workspace):
        workspace.setObjectName("workspace")
        workspace.setEnabled(True)
        workspace.resize(1309, 742)
        workspace.setStyleSheet("background-color: rgb(110, 137, 152)")
        self.gridLayout_2 = QtWidgets.QGridLayout(workspace)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.MainLayout = QtWidgets.QVBoxLayout()
        self.MainLayout.setContentsMargins(13, -1, -1, -1)
        self.MainLayout.setObjectName("MainLayout")
        self.intro_layout = QtWidgets.QHBoxLayout()
        self.intro_layout.setObjectName("intro_layout")
        self.user_initial_explanation = QtWidgets.QLabel(workspace)
        self.user_initial_explanation.setMinimumSize(QtCore.QSize(820, 278))
        self.user_initial_explanation.setStyleSheet("text-decoration: underline;\n"
"font: 75 11pt underline \"MS UI Gothic\";")
        self.user_initial_explanation.setObjectName("user_initial_explanation")
        self.intro_layout.addWidget(self.user_initial_explanation)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.intro_layout.addItem(spacerItem)
        self.frame_number = QtWidgets.QLabel(workspace)
        self.frame_number.setMinimumSize(QtCore.QSize(42, 278))
        self.frame_number.setStyleSheet("font: 75 12pt \"MS Shell Dlg 2\";\n"
"color: rgb(255, 255, 255);\n"
"font-family: Courier;")
        self.frame_number.setObjectName("frame_number")
        self.intro_layout.addWidget(self.frame_number)
        self.MainLayout.addLayout(self.intro_layout)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.MainLayout.addItem(spacerItem1)
        self.image_layout = QtWidgets.QHBoxLayout()
        self.image_layout.setObjectName("image_layout")
        self.ImageLayout = QtWidgets.QVBoxLayout()
        self.ImageLayout.setObjectName("ImageLayout")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.ImageLayout.addItem(spacerItem2)
        self.image_layout.addLayout(self.ImageLayout)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.image_layout.addItem(spacerItem3)
        self.tool_kit = QtWidgets.QFrame(workspace)
        self.tool_kit.setStyleSheet("border-color: rgb(0, 85, 127);\n"
"background-color: rgb(237, 240, 247);\n"
"border-radius: 15px; border-width: 3px; border-style: outset")
        self.tool_kit.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tool_kit.setFrameShadow(QtWidgets.QFrame.Raised)
        self.tool_kit.setObjectName("tool_kit")
        self.gridLayout = QtWidgets.QGridLayout(self.tool_kit)
        self.gridLayout.setObjectName("gridLayout")
        self.paintbrush_btn = QtWidgets.QPushButton(self.tool_kit)
        self.paintbrush_btn.setStyleSheet("background-color:\'white\'; \n"
"color: black; \n"
"border-radius: 8px; border-color: black; border-width: 1px; \n"
"border-style: outset;")
        self.paintbrush_btn.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/paintbrush.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.paintbrush_btn.setIcon(icon)
        self.paintbrush_btn.setObjectName("paintbrush_btn")
        self.gridLayout.addWidget(self.paintbrush_btn, 0, 0, 1, 1)
        self.eraser_btn = QtWidgets.QPushButton(self.tool_kit)
        self.eraser_btn.setStyleSheet("background-color:\'white\'; \n"
"color: black; \n"
"border-radius: 12px; border-color: black; border-width: 1px;\n"
"border-style: outset;")
        self.eraser_btn.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("images/erase.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.eraser_btn.setIcon(icon1)
        self.eraser_btn.setObjectName("eraser_btn")
        self.gridLayout.addWidget(self.eraser_btn, 2, 0, 1, 1)
        self.square_btn = QtWidgets.QPushButton(self.tool_kit)
        self.square_btn.setStyleSheet("background-color:\'white\'; \n"
"color: black; \n"
"border-radius: 12px; border-color: black; border-width: 1px;\n"
"border-style: outset;")
        self.square_btn.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("images/square.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.square_btn.setIcon(icon2)
        self.square_btn.setObjectName("square_btn")
        self.gridLayout.addWidget(self.square_btn, 3, 0, 1, 1)
        self.paintbrush_btn.raise_()
        self.eraser_btn.raise_()
        self.square_btn.raise_()
        self.user_initial_explanation.raise_()
        self.image_layout.addWidget(self.tool_kit)
        self.MainLayout.addLayout(self.image_layout)
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.MainLayout.addItem(spacerItem4)
        self.seg_btns_layout = QtWidgets.QHBoxLayout()
        self.seg_btns_layout.setObjectName("seg_btns_layout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem5)
        self.save_seg_btn = QtWidgets.QPushButton(workspace)
        self.save_seg_btn.setEnabled(False)
        self.save_seg_btn.setStyleSheet("background-color:#88abdb; color: black; font-weight: regular; font-size: 12pt;\n"
"border-radius: 15px; border-color: black; border-width: 3px; \n"
"border-style: outset;")
        self.save_seg_btn.setObjectName("save_seg_btn")
        self.horizontalLayout_2.addWidget(self.save_seg_btn)
        self.perform_seg_btn = QtWidgets.QPushButton(workspace)
        self.perform_seg_btn.setStyleSheet("background-color:#88abdb; color: black; font-weight: regular; font-size: 12pt;\n"
"border-radius: 15px; border-color: black; border-width: 3px; \n"
"border-style: outset;")
        self.perform_seg_btn.setObjectName("perform_seg_btn")
        self.horizontalLayout_2.addWidget(self.perform_seg_btn)
        self.seg_btns_layout.addLayout(self.horizontalLayout_2)
        self.MainLayout.addLayout(self.seg_btns_layout)
        self.MainLayout.setStretch(2, 1)
        self.gridLayout_2.addLayout(self.MainLayout, 0, 0, 1, 1)
        self.square_btn.raise_()

        self.retranslateUi(workspace)
        QtCore.QMetaObject.connectSlotsByName(workspace)

    def retranslateUi(self, workspace):
        _translate = QtCore.QCoreApplication.translate
        workspace.setWindowTitle(_translate("workspace", "Form"))
        self.user_initial_explanation.setText(_translate("workspace", "Scroll through frames, and pick 3 points in first and last frame [INSIDE THE BRAIN]."))
        self.frame_number.setText(_translate("workspace", "0/0"))
        self.save_seg_btn.setText(_translate("workspace", "Save Segmentation"))
        self.perform_seg_btn.setText(_translate("workspace", "Perform Segmentation"))

