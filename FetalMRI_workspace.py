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
        self.ImageLayout.setContentsMargins(-1, 0, -1, -1)
        self.ImageLayout.setSpacing(9)
        self.ImageLayout.setObjectName("ImageLayout")
        self.toolkitLayout = QtWidgets.QVBoxLayout()
        self.toolkitLayout.setObjectName("toolkitLayout")
        self.tool_kit = QtWidgets.QFrame(workspace)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tool_kit.sizePolicy().hasHeightForWidth())
        self.tool_kit.setSizePolicy(sizePolicy)
        self.tool_kit.setStyleSheet("border-color: rgb(0, 85, 127);\n"
"background-color: rgb(237, 240, 247);\n"
"border-radius: 15px; border-width: 3px; border-style: outset")
        self.tool_kit.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tool_kit.setFrameShadow(QtWidgets.QFrame.Raised)
        self.tool_kit.setObjectName("tool_kit")
        self.gridLayout = QtWidgets.QGridLayout(self.tool_kit)
        self.gridLayout.setVerticalSpacing(9)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.paintbrush_size2_btn = QtWidgets.QPushButton(self.tool_kit)
        self.paintbrush_size2_btn.setStyleSheet("background-color: rgb(231, 248, 243);\n"
"color: rgb(0, 0, 0);\n"
"border-radius: 4px; border-color: black; border-width: 2px; \n"
"border-style: outset;\n"
"font: 10pt \"MS Shell Dlg 2\";")
        self.paintbrush_size2_btn.setObjectName("paintbrush_size2_btn")
        self.gridLayout_3.addWidget(self.paintbrush_size2_btn, 2, 0, 1, 1)
        self.eraser_size2_btn = QtWidgets.QPushButton(self.tool_kit)
        self.eraser_size2_btn.setMaximumSize(QtCore.QSize(16777, 16777215))
        self.eraser_size2_btn.setStyleSheet("background-color: rgb(231, 248, 243);\n"
"color: rgb(0, 0, 0);\n"
"border-radius: 4px; border-color: black; border-width: 2px; \n"
"border-style: outset;\n"
"font: 10pt \"MS Shell Dlg 2\";")
        self.eraser_size2_btn.setObjectName("eraser_size2_btn")
        self.gridLayout_3.addWidget(self.eraser_size2_btn, 2, 1, 1, 1)
        self.paintbrush_btn = QtWidgets.QPushButton(self.tool_kit)
        self.paintbrush_btn.setStyleSheet("background-color:\'white\'; \n"
"color: black; \n"
"border-radius: 8px; border-color: black; border-width: 3px; \n"
"border-style: outset;")
        self.paintbrush_btn.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../../../../.designer/backup/images/paintbrush.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.paintbrush_btn.setIcon(icon)
        self.paintbrush_btn.setObjectName("paintbrush_btn")
        self.gridLayout_3.addWidget(self.paintbrush_btn, 0, 0, 1, 1)
        self.eraser_size1_btn = QtWidgets.QPushButton(self.tool_kit)
        self.eraser_size1_btn.setMaximumSize(QtCore.QSize(16777, 16777215))
        self.eraser_size1_btn.setStyleSheet("background-color: rgb(231, 248, 243);\n"
"color: rgb(0, 0, 0);\n"
"border-radius: 4px; border-color: black; border-width: 2px; \n"
"border-style: outset;\n"
"font: 8pt \"MS Shell Dlg 2\";")
        self.eraser_size1_btn.setObjectName("eraser_size1_btn")
        self.gridLayout_3.addWidget(self.eraser_size1_btn, 1, 1, 1, 1)
        self.eraser_btn = QtWidgets.QPushButton(self.tool_kit)
        self.eraser_btn.setMaximumSize(QtCore.QSize(16777, 16777215))
        self.eraser_btn.setStyleSheet("background-color:\'white\'; \n"
"color: black; \n"
"border-radius: 12px; border-color: black; border-width: 3px;\n"
"border-style: outset;\n"
"")
        self.eraser_btn.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("../../../../.designer/backup/images/erase.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.eraser_btn.setIcon(icon1)
        self.eraser_btn.setIconSize(QtCore.QSize(24, 24))
        self.eraser_btn.setObjectName("eraser_btn")
        self.gridLayout_3.addWidget(self.eraser_btn, 0, 1, 1, 1)
        self.paintbrush_size1_btn = QtWidgets.QPushButton(self.tool_kit)
        self.paintbrush_size1_btn.setStyleSheet("background-color: rgb(231, 248, 243);\n"
"color: rgb(0, 0, 0);\n"
"border-radius: 4px; border-color: black; border-width: 2px; \n"
"border-style: outset;\n"
"font: 8pt \"MS Shell Dlg 2\";")
        self.paintbrush_size1_btn.setObjectName("paintbrush_size1_btn")
        self.gridLayout_3.addWidget(self.paintbrush_size1_btn, 1, 0, 1, 1)
        self.paintbrush_size3_btn = QtWidgets.QPushButton(self.tool_kit)
        self.paintbrush_size3_btn.setStyleSheet("background-color: rgb(231, 248, 243);\n"
"color: rgb(0, 0, 0);\n"
"border-radius: 4px; border-color: black; border-width: 2px; \n"
"border-style: outset;\n"
"font: 12pt \"MS Shell Dlg 2\";")
        self.paintbrush_size3_btn.setObjectName("paintbrush_size3_btn")
        self.gridLayout_3.addWidget(self.paintbrush_size3_btn, 3, 0, 1, 1)
        self.eraser_size3_btn = QtWidgets.QPushButton(self.tool_kit)
        self.eraser_size3_btn.setMaximumSize(QtCore.QSize(16777, 16777215))
        self.eraser_size3_btn.setStyleSheet("background-color: rgb(231, 248, 243);\n"
"color: rgb(0, 0, 0);\n"
"border-radius: 4px; border-color: black; border-width: 2px; \n"
"border-style: outset;\n"
"font: 12pt \"MS Shell Dlg 2\";")
        self.eraser_size3_btn.setObjectName("eraser_size3_btn")
        self.gridLayout_3.addWidget(self.eraser_size3_btn, 3, 1, 1, 1)
        self.inner_square_btn = QtWidgets.QPushButton(self.tool_kit)
        self.inner_square_btn.setStyleSheet("background-color:\'white\'; \n"
"color: rgb(133, 13, 255);\n"
"border-radius: 12px; border-color: purple; border-width:3px;\n"
"border-style: outset;\n"
"font: 75 8pt \"MS Shell Dlg 2\";\n"
"")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("../../../../.designer/backup/images/purple_square.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.inner_square_btn.setIcon(icon2)
        self.inner_square_btn.setObjectName("inner_square_btn")
        self.gridLayout_3.addWidget(self.inner_square_btn, 0, 3, 1, 1)
        self.outer_square_btn = QtWidgets.QPushButton(self.tool_kit)
        self.outer_square_btn.setStyleSheet("background-color:\'white\'; \n"
"color: rgb(255, 0, 0);\n"
"font: 75 8pt \"MS Shell Dlg 2\";\n"
"border-radius: 12px; border-color: red; border-width: 3px;\n"
"border-style: outset;")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("../../../../.designer/backup/images/red_square.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.outer_square_btn.setIcon(icon3)
        self.outer_square_btn.setObjectName("outer_square_btn")
        self.gridLayout_3.addWidget(self.outer_square_btn, 1, 3, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_3, 0, 0, 1, 1)
        self.toolkitLayout.addWidget(self.tool_kit)
        self.jump_frame_lineedit = QtWidgets.QLineEdit(workspace)
        self.jump_frame_lineedit.setStyleSheet("font: 75 12pt \"MS Shell Dlg 2\";\n"
        # self.jump_paint = QtWidgets.(workspace)
"color: black;\n"
"font-family: Courier;\n"
"background-color: rgb(209, 211, 211);\n"
"border-radius: 12px; border-color: rgb(4, 51, 57); border-width: 3px;\n"
"")
        self.jump_frame_lineedit.setObjectName("jump_frame_lineedit")
        self.toolkitLayout.addWidget(self.jump_frame_lineedit)
        self.frame_number = QtWidgets.QLabel(workspace)
        self.frame_number.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_number.sizePolicy().hasHeightForWidth())
        self.frame_number.setSizePolicy(sizePolicy)
        self.frame_number.setMaximumSize(QtCore.QSize(500, 100))
        self.frame_number.setAutoFillBackground(False)
        self.frame_number.setStyleSheet("font: 75 12pt \"MS Shell Dlg 2\";\n"
"color: rgb(255, 255, 255);\n"
"font-family: Courier;\n"
"background-color: rgb(4, 51, 57);\n"
"border-radius: 12px; border-color: rgb(4, 51, 57); border-width: 3px;\n"
"")
        self.frame_number.setAlignment(QtCore.Qt.AlignCenter)
        self.frame_number.setWordWrap(False)
        self.frame_number.setObjectName("frame_number")
        self.toolkitLayout.addWidget(self.frame_number)
        self.instructions = QtWidgets.QLabel(workspace)
        self.instructions.setMaximumSize(QtCore.QSize(800, 800))
        self.instructions.setStyleSheet("background-color: rgb(56, 112, 83);\n"
" color: white; font-weight: regular; font-size: 12pt;\n"
"border-radius: 15px; border-color: black; border-width: 3px; \n"
"border-style: outset;\n"
"")
        self.instructions.setObjectName("instructions")
        self.toolkitLayout.addWidget(self.instructions)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.perform_seg_btn = QtWidgets.QPushButton(workspace)
        self.perform_seg_btn.setStyleSheet("background-color:#88abdb; color: black; font-weight: regular; font-size: 12pt;\n"
"border-radius: 15px; border-color: black; border-width: 3px; \n"
"border-style: outset;\n"
"")
        self.perform_seg_btn.setObjectName("perform_seg_btn")
        self.horizontalLayout_3.addWidget(self.perform_seg_btn)
        self.save_seg_btn = QtWidgets.QPushButton(workspace)
        self.save_seg_btn.setEnabled(False)
        self.save_seg_btn.setStyleSheet("background-color:#88abdb; color: black; font-weight: regular; font-size: 12pt;\n"
"border-radius: 15px; border-color: black; border-width: 3px; \n"
"border-style: outset;")
        self.save_seg_btn.setObjectName("save_seg_btn")
        self.horizontalLayout_3.addWidget(self.save_seg_btn)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        self.contrast_label = QtWidgets.QLabel(workspace)
        self.contrast_label.setStyleSheet("background-color: rgb(158, 51, 158);\n"
" color: white; font-weight: regular; font-size: 12pt;\n"
"border-radius: 15px; border-color: black; border-width: 3px; \n"
"border-style: outset;\n"
"")
        self.contrast_label.setObjectName("contrast_label")
        self.verticalLayout_3.addWidget(self.contrast_label)
        self.contrast_slider = QtWidgets.QSlider(workspace)
        self.contrast_slider.setMaximum(10)
        self.contrast_slider.setProperty("value", 5)
        self.contrast_slider.setOrientation(QtCore.Qt.Horizontal)
        self.contrast_slider.setObjectName("contrast_slider")
        self.verticalLayout_3.addWidget(self.contrast_slider)
        self.toolkitLayout.addLayout(self.verticalLayout_3)
        self.toolkitLayout.setStretch(0, 1)
        self.toolkitLayout.setStretch(1, 1)
        self.toolkitLayout.setStretch(2, 1)
        self.toolkitLayout.setStretch(3, 1)
        self.ImageLayout.addLayout(self.toolkitLayout)
        self.scrollLayout = QtWidgets.QVBoxLayout()
        self.scrollLayout.setSpacing(9)
        self.scrollLayout.setObjectName("scrollLayout")
        self.ImageLayout.addLayout(self.scrollLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(workspace)
        self.label.setStyleSheet("font: 75 12pt \"MS Shell Dlg 2\";\n"
"color: rgb(255, 255, 255);\n"
"font-family: Courier;\n"
"background-color: rgb(4, 51, 57);\n"
"border-radius: 12px; border-color: rgb(4, 51, 57); border-width: 3px;\n"
"")
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.runAll_btn = QtWidgets.QPushButton(workspace)
        self.runAll_btn.setStyleSheet("background-color:#88abdb; color: black; font-weight: regular; font-size: 12pt;\n"
"border-radius: 15px; border-color: black; border-width: 3px; \n"
"border-style: outset;\n"
"")
        self.runAll_btn.setObjectName("runAll_btn")
        self.horizontalLayout.addWidget(self.runAll_btn)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.tableWidget = QtWidgets.QTableWidget(workspace)
        self.tableWidget.setStyleSheet("color: rgb(255, 255, 255);\n"
"font: 75 8pt \"MS Shell Dlg 2\";\n"
"background-color: rgb(4, 51, 57)")
        self.tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.tableWidget.setRowCount(1)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setObjectName("tableWidget")
        self.verticalLayout_2.addWidget(self.tableWidget)
        self.verticalFrame = QtWidgets.QFrame(workspace)
        self.verticalFrame.setObjectName("verticalFrame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalFrame)
        self.verticalLayout.setObjectName("verticalLayout")
        self.quantizationLabel = QtWidgets.QLabel(self.verticalFrame)
        self.quantizationLabel.setObjectName("quantizationLabel")
        self.verticalLayout.addWidget(self.quantizationLabel)
        self.quantizationSlider = QtWidgets.QSlider(self.verticalFrame)
        self.quantizationSlider.setAutoFillBackground(False)
        self.quantizationSlider.setStyleSheet("")
        self.quantizationSlider.setMaximum(10)
        self.quantizationSlider.setSliderPosition(5)
        self.quantizationSlider.setTracking(False)
        self.quantizationSlider.setOrientation(QtCore.Qt.Horizontal)
        self.quantizationSlider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.quantizationSlider.setTickInterval(1)
        self.quantizationSlider.setObjectName("quantizationSlider")
        self.verticalLayout.addWidget(self.quantizationSlider)
        self.brain_volume_label = QtWidgets.QLabel(self.verticalFrame)
        self.brain_volume_label.setObjectName("brain_volume_label")
        self.verticalLayout.addWidget(self.brain_volume_label)
        self.show_convex_btn = QtWidgets.QPushButton(self.verticalFrame)
        self.show_convex_btn.setObjectName("show_convex_btn")
        self.verticalLayout.addWidget(self.show_convex_btn)
        self.show_brain_halves_btn = QtWidgets.QPushButton(self.verticalFrame)
        self.show_brain_halves_btn.setObjectName("show_brain_halves_btn")
        self.verticalLayout.addWidget(self.show_brain_halves_btn)
        self.show_full_seg_btn = QtWidgets.QPushButton(self.verticalFrame)
        self.show_full_seg_btn.setObjectName("show_full_seg_btn")
        self.verticalLayout.addWidget(self.show_full_seg_btn)
        self.verticalLayout_2.addWidget(self.verticalFrame)
        self.verticalLayout_2.setStretch(0, 1)
        self.verticalLayout_2.setStretch(1, 20)
        self.ImageLayout.addLayout(self.verticalLayout_2)
        self.ImageLayout.setStretch(0, 1)
        self.ImageLayout.setStretch(1, 8)
        self.ImageLayout.setStretch(2, 4)
        self.MainLayout.addLayout(self.ImageLayout)
        self.gridLayout_2.addLayout(self.MainLayout, 0, 2, 1, 1)

        self.retranslateUi(workspace)
        QtCore.QMetaObject.connectSlotsByName(workspace)

    def retranslateUi(self, workspace):
        _translate = QtCore.QCoreApplication.translate
        workspace.setWindowTitle(_translate("workspace", "Form"))
        self.paintbrush_size2_btn.setText(_translate("workspace", "2"))
        self.eraser_size2_btn.setText(_translate("workspace", "2"))
        self.paintbrush_btn.setToolTip(_translate("workspace", "<html><head/><body><p>Use paintbrush to mark points on image.</p></body></html>"))
        self.eraser_size1_btn.setText(_translate("workspace", "1"))
        self.eraser_btn.setToolTip(_translate("workspace", "<html><head/><body><p>Use eraser to remove points or parts of segmentation.</p></body></html>"))
        self.paintbrush_size1_btn.setText(_translate("workspace", "1"))
        self.paintbrush_size3_btn.setText(_translate("workspace", "3"))
        self.eraser_size3_btn.setText(_translate("workspace", "3"))
        self.inner_square_btn.setToolTip(_translate("workspace", "Mark middle first and last frame with square CONTAINED in brain."))
        self.inner_square_btn.setText(_translate("workspace", "Inner"))
        self.outer_square_btn.setToolTip(_translate("workspace", "Mark middle frame with square ENCLOSING brain."))
        self.outer_square_btn.setText(_translate("workspace", "Outer"))
        self.jump_frame_lineedit.setPlaceholderText(_translate("workspace", "Jump to Frame..."))
        self.frame_number.setText(_translate("workspace", "<html><head/><body><p align=\"center\">20/20</p></body></html>"))
        self.instructions.setToolTip(_translate("workspace", "<html><head/><body><pre style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-family:\'Courier New\'; font-size:9pt; font-weight:600; color:#008080;\">Choose the first and last frames in which the brain can be seen.</span></pre><pre style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-family:\'Courier New\'; font-size:9pt; font-weight:600; color:#008080;\">When finished, load more scans to mark, or press \'Perform Segmentation\'</span></pre></body></html>"))
        self.instructions.setStatusTip(_translate("workspace", "<html><head/><body><pre style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-family:\'Courier New\'; font-size:9pt; font-weight:600; color:#008080;\">In the first and last frame: draw a purple square inside the brain area.<br/>In the middle frame: draw a red square around [enclosing] the brain area.<br/>Finally: press \'Perform Segmentation\'.</span></pre></body></html>"))
        self.instructions.setWhatsThis(_translate("workspace", "<html><head/><body><p>In the first and last frame: draw a purple square inside the brain area.</p><p>In the middle frame: draw a red square around [enclosing] the brain area.</p><p>Finally: press \'Perform Segmentation\'.</p></body></html>"))
        self.instructions.setText(_translate("workspace", "<html><head/><body><p align=\"center\"><span style=\" text-decoration: underline;\">Stage 1</span><span style=\" text-decoration: underline;\">: Boundary Marking</span></p><p>Outline the brain in the first, </p><p>last and middle frames.</p></body></html>"))
        self.perform_seg_btn.setText(_translate("workspace", "Perform \n"
"Segmentation"))
        self.save_seg_btn.setText(_translate("workspace", "Save \n"
"Segmentation"))
        self.contrast_label.setText(_translate("workspace", "Adjust Contrast:"))
        self.label.setText(_translate("workspace", "Workspace"))
        self.runAll_btn.setText(_translate("workspace", "Run All"))
        self.quantizationLabel.setText(_translate("workspace", "Adjust Segmentation Level"))
        self.brain_volume_label.setText(_translate("workspace", "Brain Volume: "))
        self.show_convex_btn.setText(_translate("workspace", "Show Convex"))
        self.show_brain_halves_btn.setText(_translate("workspace", "Show Brain Halves"))
        self.show_full_seg_btn.setText(_translate("workspace", "Show Full Segmentation"))

