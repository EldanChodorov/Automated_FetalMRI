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
        workspace.resize(913, 883)
        workspace.setAutoFillBackground(True)
        workspace.setStyleSheet("background-color: rgb(110, 137, 152)")
        self.gridLayout_2 = QtWidgets.QGridLayout(workspace)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.MainLayout = QtWidgets.QVBoxLayout()
        self.MainLayout.setContentsMargins(13, -1, -1, -1)
        self.MainLayout.setObjectName("MainLayout")
        self.initial_into = QtWidgets.QHBoxLayout()
        self.initial_into.setObjectName("initial_into")
        self.user_explanation = QtWidgets.QLabel(workspace)
        self.user_explanation.setStyleSheet("text-decoration: underline;\n"
"font: 75 11pt underline \"MS UI Gothic\";\n"
"")
        self.user_explanation.setObjectName("user_explanation")
        self.initial_into.addWidget(self.user_explanation)
        self.frame_number = QtWidgets.QLabel(workspace)
        self.frame_number.setMinimumSize(QtCore.QSize(42, 278))
        self.frame_number.setMaximumSize(QtCore.QSize(70, 16777215))
        self.frame_number.setAutoFillBackground(False)
        self.frame_number.setStyleSheet("font: 75 12pt \"MS Shell Dlg 2\";\n"
"color: rgb(255, 255, 255);\n"
"font-family: Courier;")
        self.frame_number.setObjectName("frame_number")
        self.initial_into.addWidget(self.frame_number)
        self.MainLayout.addLayout(self.initial_into)
        self.ImageLayout = QtWidgets.QHBoxLayout()
        self.ImageLayout.setObjectName("ImageLayout")
        self.tool_kit = QtWidgets.QFrame(workspace)
        self.tool_kit.setStyleSheet("border-color: rgb(0, 85, 127);\n"
"background-color: rgb(237, 240, 247);\n"
"border-radius: 15px; border-width: 3px; border-style: outset")
        self.tool_kit.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tool_kit.setFrameShadow(QtWidgets.QFrame.Raised)
        self.tool_kit.setObjectName("tool_kit")
        self.gridLayout = QtWidgets.QGridLayout(self.tool_kit)
        self.gridLayout.setObjectName("gridLayout")
        self.inner_square_btn = QtWidgets.QPushButton(self.tool_kit)
        self.inner_square_btn.setStyleSheet("background-color:\'white\'; \n"
"color: black; \n"
"border-radius: 12px; border-color: purple; border-width:3px;\n"
"border-style: outset;")
        self.inner_square_btn.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/purple_square.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.inner_square_btn.setIcon(icon)
        self.inner_square_btn.setObjectName("inner_square_btn")
        self.gridLayout.addWidget(self.inner_square_btn, 4, 0, 1, 1)
        self.paintbrush_btn = QtWidgets.QPushButton(self.tool_kit)
        self.paintbrush_btn.setStyleSheet("background-color:\'white\'; \n"
"color: black; \n"
"border-radius: 8px; border-color: black; border-width: 1px; \n"
"border-style: outset;")
        self.paintbrush_btn.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("images/paintbrush.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.paintbrush_btn.setIcon(icon1)
        self.paintbrush_btn.setObjectName("paintbrush_btn")
        self.gridLayout.addWidget(self.paintbrush_btn, 0, 0, 1, 1)
        self.outer_square_btn = QtWidgets.QPushButton(self.tool_kit)
        self.outer_square_btn.setStyleSheet("background-color:\'white\'; \n"
"color: black; \n"
"border-radius: 12px; border-color: red; border-width: 3px;\n"
"border-style: outset;")
        self.outer_square_btn.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("images/red_square.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.outer_square_btn.setIcon(icon2)
        self.outer_square_btn.setObjectName("outer_square_btn")
        self.gridLayout.addWidget(self.outer_square_btn, 3, 0, 1, 1)
        self.eraser_btn = QtWidgets.QPushButton(self.tool_kit)
        self.eraser_btn.setStyleSheet("background-color:\'white\'; \n"
"color: black; \n"
"border-radius: 12px; border-color: black; border-width: 1px;\n"
"border-style: outset;")
        self.eraser_btn.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("images/erase.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.eraser_btn.setIcon(icon3)
        self.eraser_btn.setObjectName("eraser_btn")
        self.gridLayout.addWidget(self.eraser_btn, 2, 0, 1, 1)
        self.ImageLayout.addWidget(self.tool_kit)
        self.MainLayout.addLayout(self.ImageLayout)
        self.seg_btns_layout = QtWidgets.QHBoxLayout()
        self.seg_btns_layout.setObjectName("seg_btns_layout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
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
        self.MainLayout.setStretch(1, 1)
        self.gridLayout_2.addLayout(self.MainLayout, 0, 0, 1, 1)

        self.retranslateUi(workspace)
        QtCore.QMetaObject.connectSlotsByName(workspace)

    def retranslateUi(self, workspace):
        _translate = QtCore.QCoreApplication.translate
        workspace.setWindowTitle(_translate("workspace", "Form"))
        self.user_explanation.setText(_translate("workspace", "Scroll through frames, and pick 3 points in first and last frame [INSIDE THE BRAIN]."))
        self.frame_number.setText(_translate("workspace", "20/20"))
        self.inner_square_btn.setToolTip(_translate("workspace", "Mark middle first and last frame with square CONTAINED in brain."))
        self.outer_square_btn.setToolTip(_translate("workspace", "Mark middle frame with square ENCLOSING brain."))
        self.save_seg_btn.setText(_translate("workspace", "Save Segmentation"))
        self.perform_seg_btn.setText(_translate("workspace", "Perform Segmentation"))

