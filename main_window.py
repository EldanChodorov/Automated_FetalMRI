from PyQt5 import QtWidgets
from PyQt5 import QtGui, QtCore
import os
from workspace import WorkSpace
import dicom2nifti
import shutil
import numpy as np
import nibabel as nib
import FetalMRI_mainwindow
import FetalMRI_About


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

        # create local folder for files generated in any session
        self._local_folder = None

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
        self.actionSave_Segmentation.triggered.connect(self._save_segmentation)
        self.actionOpen_Segmentation.triggered.connect(self._open_segmentation)

        # Help menu
        self.actionAbout.triggered.connect(self._about_dialog)

    def _connect_workspace_opened(self):
        '''Connect all actions that are valid only when workspace has been opened.'''
        self.actionSave_Points.triggered.connect(self._workspace.save_points)
        self.actionLoad_Points.triggered.connect(self._workspace.load_points)
        self.actionSave_Segmentation.setEnabled(True)
        self.actionOpen_Segmentation.setEnabled(True)
        self.actionSave_Points.setEnabled(True)
        self.actionLoad_Points.setEnabled(True)
        self.actionContrast_View.triggered.connect(self._workspace.contrast_view_btn.click)
        self.actionContrast_View.setEnabled(True)


    def _open_workspace(self):
        '''
        Open workspace window with selected scans, set workspace to be central widget.
        '''
        if self._source:
            try:
                self._workspace = WorkSpace(self._source, self)
                self._connect_workspace_opened()
            except Exception as ex:
                print(ex)
            self.setCentralWidget(self._workspace)

    def _create_local_folder(self, path):
        '''
        Create local folder with unique name.
        :param path: [str] create folder with this as base name.
        :return: [str] full path of local folder
        '''
        if path.endswith('.gz'):
            path = path[:-3]
        if path.endswith('.nii'):
            path = path[:-4]
        local_folder = os.getcwd() + '\\Nifti Files\\' + os.path.basename(path)
        if not os.path.isdir(local_folder):
            try:
                os.mkdir(local_folder)
            except NotImplementedError:
                # dir_fd not implemented on platform
                print('Unable to create directory %s' % local_folder)
                local_folder = ''
        self._local_folder = local_folder
        return local_folder

    def _create_local_nifti_copy(self, nifti_path):
        '''Create copy of nifti in local folder.'''
        local_folder = self._create_local_folder(nifti_path)
        base_name = os.path.basename(nifti_path)
        dest = os.path.join(local_folder, base_name)
        try:
            shutil.copyfile(nifti_path, dest)
        except shutil.SameFileError:
            # will raise if copy of file already exists
            pass
        except IOError:
            print('Permission denied.')

    def _create_local_nifti_from_dicom(self, directory):
        '''
        Create nifti files from dicoms and save as a Nifti file in a local folder.
        Will override existing nifti file.
        :param directory [str]: path to directory containing dicoms
        :return [str]: path to nifti file, if successfully created
        '''
        local_folder = self._create_local_folder(os.path.normpath(directory))
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
        chosen_file = self._user_choose_file(dir_only)
        # file_dialog = QtWidgets.QFileDialog()
        # options = QtWidgets.QFileDialog.Options()
        # options |= QtWidgets.QFileDialog.DontUseNativeDialog
        # if dir_only:
        #     file_dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        #     file_dialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly, True)
        # if not file_dialog.exec_():
        #     print('Error in File Dialog.')
        #     return

        # create nifti if dicoms were selected, and open workspace with nifti object
        # chosen_files = file_dialog.selectedFiles()
        if chosen_file:
            # user can choose only one file at a time
            self._source = chosen_file
            if dir_only:
                self._source = self._create_local_nifti_from_dicom(self._source)
            else:
                if '.nii' not in self._source:
                    self._source = None
                self._create_local_nifti_copy(self._source)
            self._open_workspace()

    def _save_segmentation(self):
        if self._workspace:
            self._workspace.save_segmentation()

    def _user_choose_file(self, dir_only=False):

        file_dialog = QtWidgets.QFileDialog()
        options = QtWidgets.QFileDialog.Options()
        # options |= QtWidgets.QFileDialog.DontUseNativeDialog
        if not dir_only:
            file_name, _ = QtWidgets.QFileDialog.getOpenFileName(file_dialog, "Open segmentation Nifti file", "",
                                                             "Nifti Files (*.nii, *.nii.gz)", options=options)
            return file_name
        else:
            dir_name = QtWidgets.QFileDialog.getExistingDirectory(file_dialog, "Select directory of dicoms", "",
                                                                 options=options)
            return dir_name

    def _open_segmentation(self):
        try:
            nifti_path = self._user_choose_file()
            if not nifti_path.endswith('.nii') and not nifti_path.endswith('.nii.gz'):
                print("Must choose Nifti format file.")
                return
            segmentation = np.array(nib.load(nifti_path).get_data())
            segmentation = segmentation.transpose(2, 0, 1)  # convert to (num_frames, x, y)
            if self._workspace:
                self._workspace.set_segmentation(segmentation)
        except Exception as ex:
            print('open_segmentation error:', ex)

    def _about_dialog(self):
        '''Display the `About` dialog.'''
        dialog = QtWidgets.QDialog(self)
        dialog.ui = FetalMRI_About.Ui_Dialog()
        dialog.ui.setupUi(dialog)
        dialog.ui.okBtn.clicked.connect(dialog.close)
        dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        dialog.exec_()