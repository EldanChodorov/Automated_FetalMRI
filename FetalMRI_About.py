# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FetalMRI_About.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(788, 715)
        Dialog.setStyleSheet("background-color: rgb(233, 233, 233);")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(120, -10, 521, 521))
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(40, 560, 131, 131))
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap("images/casmip_small.ico"))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(620, 560, 131, 121))
        self.label_3.setText("")
        self.label_3.setPixmap(QtGui.QPixmap("images/huji_small.ico"))
        self.label_3.setObjectName("label_3")
        self.okBtn = QtWidgets.QPushButton(Dialog)
        self.okBtn.setGeometry(QtCore.QRect(320, 550, 112, 34))
        self.okBtn.setObjectName("okBtn")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "<html><head/><body><p align=\"center\"><span style=\" font-size:9pt; font-weight:600; text-decoration: underline;\">About SegTool</span></p><p align=\"center\"><span style=\" font-size:9pt;\"><br/></span></p><p><span style=\" font-size:9pt;\">SegTool is used to perform semi-automatic segmentation on fetal brain mri scans.</span></p><p><span style=\" font-size:9pt;\"><br/></span></p><p><span style=\" font-size:9pt;\">Usage: Load either Nifti file or directory of Dicom files. Manually mark points inside the brain in the first and last frames. \'Perform Segmentation\' will return the brain segmented. You may make adjustments before saving the result.</span></p><p><span style=\" font-size:9pt;\"><br/></span></p><p><span style=\" font-size:9pt;\">This tool was developed at CASMIP lab at the Hebrew University of Jerusalem, conducted by Keren Meron and Eldan Chodorov under the guidance of Professor Leo Joskowicz and Adi Szeskin.</span></p></body></html>"))
        self.okBtn.setText(_translate("Dialog", "Ok"))

