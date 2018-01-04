from PyQt5 import QtWidgets
from PyQt5 import QtGui, QtCore
import os
from workspace import WorkSpace
import dicom2nifti
import shutil
import numpy as np
import nibabel as nib
import FetalMRI_mainwindow


class MainWindow(QtWidgets.QMainWindow, FetalMRI_mainwindow.Ui_MainWindow):
    '''
    Main window display of the program. Displays upon startup. 
    User can load directory from this window and open the workspace window.
    '''

    def __init__(self, data_dir_path):

        QtWidgets.QMainWindow.__init__(self)
        FetalMRI_mainwindow.Ui_MainWindow.__init__(self)

        # defined in FetalMRI_design.Ui_MainWindow
        self.setupUi(self)

        # setup customary design options
        self.init_ui()

        # path to directory holding scans
        self._source = data_dir_path

    def init_ui(self):
        # self.setGeometry(100, 50, 1500, 900)
        self.setWindowTitle('Fetal Brain Seg Tool')
        self.setWindowIcon(QtGui.QIcon('images/buttons_PNG103.png'))

        # connect buttons
        self.load_nii_btn.clicked.connect(self._load_source)
        self.load_dir_btn.clicked.connect(lambda: self._load_source(True))

        self._connect_menus()

        # self._set_menus()

        # main startup window layout
        # main_widget = QtWidgets.QWidget()
        # main_layout = QtWidgets.QVBoxLayout()
        # main_widget.setStyleSheet('border-image: url(images/brain_bgnd.jpg)')
        # main_widget.setStyleSheet('background-color: #c6d8ec;')

        # main logo on display
        # main_logo_layout = QtWidgets.QHBoxLayout()
        # main_logo = QtWidgets.QLabel()
        # main_logo.setText('Fetal MRI Seg Tool')
        # logo_style_sheet = 'background-color:#9db8e1; color: black; font-weight: regular; font-size: 22pt;'\
        #                     'border-radius: 25px; border-color: gray; border-width: 6px; '\
        #                     'border-style: outset;'
        # main_logo.setStyleSheet(logo_style_sheet)
        # main_logo.setAlignment(QtCore.Qt.AlignCenter)
        # main_logo.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # main_logo.resize(800, 800)

        # main_logo_layout.addStretch()
        # main_logo_layout.addWidget(main_logo)
        # main_logo_layout.addStretch()
        # main_layout.addStretch()
        # main_layout.addLayout(main_logo_layout)
        # main_layout.addStretch()

        # buttons
        # button_style_sheet = 'background-color:#b1c7e7; color: black; font-weight: regular; font-size: 12pt;'\
        #                       'border-radius: 20px; border-color: gray; border-width: 3px; '\
        #                       'border-style: outset;'

        # dir_open_button = QtWidgets.QPushButton('Load Scans From Directory')
        # dir_open_button.setIcon(QtGui.QIcon('images/buttons_PNG103.png'))
        # dir_open_button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # dir_open_button.resize(400,20)
        # dir_open_button.clicked.connect(lambda: self._load_source(True))
        # dir_open_button.setStyleSheet(button_style_sheet)

        # nii_open_button = QtWidgets.QPushButton('Load Nifti File')
        # nii_open_button.setIcon(QtGui.QIcon('images/buttons_PNG103.png'))
        # nii_open_button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # nii_open_button.resize(400,20)
        # nii_open_button.clicked.connect(self._load_source)
        # nii_open_button.setStyleSheet(button_style_sheet)

        # open_layout = QtWidgets.QHBoxLayout()
        # open_layout.addStretch()
        # open_layout.addWidget(dir_open_button)
        # open_layout.addStretch()
        # open_layout.addWidget(nii_open_button)
        # open_layout.addStretch()

        # main_layout.addLayout(open_layout)
        # main_layout.addStretch()

        # main_widget.setLayout(main_layout)
        # self.setCentralWidget(main_widget)

    def _connect_menus(self):

        # File menu
        self.actionOpen_Nifti_File.setShortcut('Ctrl+o')
        self.actionOpen_Nifti_File.setStatusTip('Open Nii File')
        self.actionOpen_Nifti_File.triggered.connect(self._load_source)

        self.actionOpen_Directory.setShortcut('Ctrl+d')
        self.actionOpen_Directory.setStatusTip('Open directory of dicoms')
        self.actionOpen_Directory.triggered.connect(lambda: self._load_source(True))

        self.actionExit.setShortcut('Ctrl+Q')
        self.actionExit.setStatusTip('Exit')
        self.actionExit.triggered.connect(self.close)

        # Workspace menu
        self.actionSave_Segmentation.setShortcut('Ctrl+S')
        self.actionSave_Segmentation.triggered.connect(self._save_segmentation)

        self.actionOpen_Segmentation.setShortcut('Ctrl+Shift+W')
        self.actionOpen_Segmentation.setStatusTip('Open previous segmentation')
        self.actionOpen_Segmentation.triggered.connect(self._open_segmentation)

    def _open_workspace(self):
        '''
        Open workspace window with selected scans, set workspace to be central widget.
        '''
        if self._source:
            try:
                self._workspace = WorkSpace(self._source, self)
            except Exception as ex:
                print(ex)
            self.setCentralWidget(self._workspace)

    def _create_local_nifti(self, directory):
        '''
        Create nifti files from dicoms and save as .nii/.nii.gz file in a local folder.
        :param directory [str]: path to directory containing dicoms
        :return [str]: path to nifti file, if successfully created
        '''
        local_folder = os.getcwd() + '\\Nifti Files\\' + os.path.basename(os.path.normpath(directory))
        if os.path.isdir(local_folder):
            # override and create a new nifti file, even if already exists under this name
            shutil.rmtree(local_folder)
        try:
            os.mkdir(local_folder)
        except:
            print('Unable to create directory %s' %local_folder)
            return
        dicom2nifti.convert_directory(self._source, local_folder)

        nii_files = os.listdir(local_folder)
        if nii_files:
            return local_folder + "\\" + nii_files[0]
        else:
            print('Error in dicom directory.')

    @QtCore.pyqtSlot()
    def _load_source(self, dir_only=False):
        '''
        Allow user to choose scans which will be loaded into program.
        If directory was successfully chosen, open workspace.
        :param dir_only [bool]: if True, allow user to choose a directory. If false, must choose nifti file.
        '''
        file_dialog = QtWidgets.QFileDialog()
        if dir_only:
            file_dialog.setFileMode(QtWidgets.QFileDialog.Directory)
            file_dialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly, True)
        if not file_dialog.exec_():
            print('Error in File Dialog.')
            return

        # create nifti if dicoms were selected, and open workspace with nifti object
        chosen_files = file_dialog.selectedFiles()
        if chosen_files:
            # user can choose only one file at a time
            self._source = chosen_files[0]
            if dir_only:
                self._source = self._create_local_nifti(self._source)
            else:
                if '.nii' not in self._source:
                    self._source = None
            self._open_workspace()

    def _save_segmentation(self):
        if self._workspace:
            self._workspace.save_segmentation()

    def _user_choose_file(self):
        file_dialog = QtWidgets.QFileDialog()
        if not file_dialog.exec_():
            raise ValueError("Error in File Dialog.")

        chosen_files = file_dialog.selectedFiles()
        if chosen_files:
            # user can choose only one file at a time
            return chosen_files[0]

    def _open_segmentation(self):
        nifti_path = self._user_choose_file()
        if not nifti_path.endswith('.nii') and not nifti_path.endswith('.nii.gz'):
            print("Must choose Nifti format file.")
            return
        segmentation = np.array(nib.load(nifti_path).get_data())
        print('Segmentation shape', segmentation.shape)
        if self._workspace:
            self._workspace.image_display.set_segmentation(segmentation)