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
        workspace.resize(1186, 883)
        workspace.setAutoFillBackground(True)
        workspace.setStyleSheet("")
        self.gridLayout_2 = QtWidgets.QGridLayout(workspace)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.MainLayout = QtWidgets.QHBoxLayout()
        self.MainLayout.setContentsMargins(13, -1, -1, -1)
        self.MainLayout.setObjectName("MainLayout")
        self.ImageLayout = QtWidgets.QHBoxLayout()
        self.ImageLayout.setObjectName("ImageLayout")
        self.toolkitLayout = QtWidgets.QVBoxLayout()
        self.toolkitLayout.setObjectName("toolkitLayout")
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
"border-radius: 8px; border-color: black; border-width: 3px; \n"
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
"border-radius: 12px; border-color: black; border-width: 3px;\n"
"border-style: outset;\n"
"")
        self.eraser_btn.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("images/erase.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.eraser_btn.setIcon(icon1)
        self.eraser_btn.setObjectName("eraser_btn")
        self.gridLayout.addWidget(self.eraser_btn, 2, 0, 1, 1)
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
        self.inner_square_btn = QtWidgets.QPushButton(self.tool_kit)
        self.inner_square_btn.setStyleSheet("background-color:\'white\'; \n"
"color: black; \n"
"border-radius: 12px; border-color: purple; border-width:3px;\n"
"border-style: outset;")
        self.inner_square_btn.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("images/purple_square.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.inner_square_btn.setIcon(icon3)
        self.inner_square_btn.setObjectName("inner_square_btn")
        self.gridLayout.addWidget(self.inner_square_btn, 4, 0, 1, 1)
        self.toolkitLayout.addWidget(self.tool_kit)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.toolkitLayout.addItem(spacerItem)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.frame_number = QtWidgets.QLabel(workspace)
        self.frame_number.setMinimumSize(QtCore.QSize(42, 278))
        self.frame_number.setMaximumSize(QtCore.QSize(70, 16777215))
        self.frame_number.setAutoFillBackground(False)
        self.frame_number.setStyleSheet("font: 75 12pt \"MS Shell Dlg 2\";\n"
"color: rgb(255, 255, 255);\n"
"font-family: Courier;\n"
"background-color: rgb(4, 51, 57);\n"
"border-radius: 12px; border-color: rgb(4, 51, 57); border-width: 3px;\n"
"")
        self.frame_number.setObjectName("frame_number")
        self.verticalLayout_3.addWidget(self.frame_number)
        self.toolkitLayout.addLayout(self.verticalLayout_3)
        self.toolkitLayout.setStretch(0, 1)
        self.ImageLayout.addLayout(self.toolkitLayout)
        self.performSegBtnsLayout = QtWidgets.QVBoxLayout()
        self.performSegBtnsLayout.setObjectName("performSegBtnsLayout")
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.performSegBtnsLayout.addItem(spacerItem1)
        self.perform_seg_btn = QtWidgets.QPushButton(workspace)
        self.perform_seg_btn.setStyleSheet("background-color:#88abdb; color: black; font-weight: regular; font-size: 12pt;\n"
"border-radius: 15px; border-color: black; border-width: 3px; \n"
"border-style: outset;")
        self.perform_seg_btn.setObjectName("perform_seg_btn")
        self.performSegBtnsLayout.addWidget(self.perform_seg_btn)
        self.save_seg_btn = QtWidgets.QPushButton(workspace)
        self.save_seg_btn.setEnabled(False)
        self.save_seg_btn.setStyleSheet("background-color:#88abdb; color: black; font-weight: regular; font-size: 12pt;\n"
"border-radius: 15px; border-color: black; border-width: 3px; \n"
"border-style: outset;")
        self.save_seg_btn.setObjectName("save_seg_btn")
        self.performSegBtnsLayout.addWidget(self.save_seg_btn)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.performSegBtnsLayout.addItem(spacerItem2)
        self.standard_view_btn = QtWidgets.QPushButton(workspace)
        self.standard_view_btn.setEnabled(False)
        self.standard_view_btn.setStyleSheet("background-color:rgb(145, 0, 109); color: white; font-weight: regular; font-size: 12pt;\n"
"border-radius: 15px; border-color: black; border-width: 3px; \n"
"border-style: outset;")
        self.standard_view_btn.setObjectName("standard_view_btn")
        self.performSegBtnsLayout.addWidget(self.standard_view_btn)
        self.contrast_view_btn = QtWidgets.QPushButton(workspace)
        self.contrast_view_btn.setStyleSheet("background-color:rgb(145, 0, 109); color: white; font-weight: regular; font-size: 12pt;\n"
"border-radius: 15px; border-color: black; border-width: 3px; \n"
"border-style: outset;")
        self.contrast_view_btn.setObjectName("contrast_view_btn")
        self.performSegBtnsLayout.addWidget(self.contrast_view_btn)
        self.instructions = QtWidgets.QLabel(workspace)
        self.instructions.setStyleSheet("background-color: rgb(56, 112, 83);\n"
" color: white; font-weight: regular; font-size: 12pt;\n"
"border-radius: 15px; border-color: black; border-width: 3px; \n"
"border-style: outset;\n"
"")
        self.instructions.setObjectName("instructions")
        self.performSegBtnsLayout.addWidget(self.instructions)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.performSegBtnsLayout.addItem(spacerItem3)
        self.ImageLayout.addLayout(self.performSegBtnsLayout)
        self.ImageLayout.setStretch(1, 1)
        self.MainLayout.addLayout(self.ImageLayout)
        self.gridLayout_2.addLayout(self.MainLayout, 0, 2, 1, 1)

        self.retranslateUi(workspace)
        QtCore.QMetaObject.connectSlotsByName(workspace)

    def retranslateUi(self, workspace):
        _translate = QtCore.QCoreApplication.translate
        workspace.setWindowTitle(_translate("workspace", "Form"))
        self.paintbrush_btn.setToolTip(_translate("workspace", "<html><head/><body><p>Use paintbrush to mark points on image.</p></body></html>"))
        self.eraser_btn.setToolTip(_translate("workspace", "<html><head/><body><p>Use eraser to remove points or parts of segmentation.</p></body></html>"))
        self.outer_square_btn.setToolTip(_translate("workspace", "Mark middle frame with square ENCLOSING brain."))
        self.inner_square_btn.setToolTip(_translate("workspace", "Mark middle first and last frame with square CONTAINED in brain."))
        self.frame_number.setText(_translate("workspace", "<html><head/><body><p align=\"right\">20/20</p></body></html>"))
        self.perform_seg_btn.setText(_translate("workspace", "Perform Segmentation"))
        self.save_seg_btn.setText(_translate("workspace", "Save Segmentation"))
        self.standard_view_btn.setText(_translate("workspace", "Standard View"))
        self.contrast_view_btn.setText(_translate("workspace", "Contrast View"))
        self.instructions.setToolTip(_translate("workspace", "<html><head/><body><pre style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-family:\'Courier New\'; font-size:9pt; font-weight:600; color:#008080;\">In the first and last frame: draw a purple square inside the brain area.<br/>In the middle frame: draw a red square around [enclosing] the brain area.<br/>Finally: press \'Perform Segmentation\'.</span></pre></body></html>"))
        self.instructions.setText(_translate("workspace", "<html><head/><body><p align=\"center\">Instructions</p></body></html>"))

