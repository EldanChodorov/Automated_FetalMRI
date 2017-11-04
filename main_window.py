from PyQt5 import QtWidgets
from PyQt5 import QtGui, QtCore
import os
from workspace import WorkSpace
import dicom2nifti
import shutil

class MainWindow(QtWidgets.QMainWindow):
    '''
    Main window display of the program. Displays upon startup. 
    User can load directory from this window and open the workspace window.
    '''

    def __init__(self, data_dir_path):

        QtWidgets.QMainWindow.__init__(self)
        self.init_ui()

        # path to directory holding scans
        self._source = data_dir_path

    def init_ui(self):
        self.setGeometry(100, 50, 1500, 900)
        self.setWindowTitle('Fetal Brain Seg Tool')
        self.setWindowIcon(QtGui.QIcon('images/buttons_PNG103.png'))
        self._set_menus()

        # main startup window layout
        main_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout()
        main_widget.setStyleSheet('background-color:#cac3db;')

        # icon image on display
        display_img = QtWidgets.QLabel(self)
        display_img.setPixmap(QtGui.QPixmap(os.getcwd() + '/images/Seg Tool Logo.png'))
        display_img.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addStretch()
        main_layout.addWidget(display_img)
        main_layout.addStretch()

        # buttons
        button_style_sheet = 'background-color:#88abdb; color: black; font-weight: regular; font-size: 12pt;'\
                              'border-radius: 15px; border-color: black; border-width: 3px; '\
                              'border-style: outset;'

        dir_open_button = QtWidgets.QPushButton('Load Scans From Directory')
        dir_open_button.setIcon(QtGui.QIcon('images/buttons_PNG103.png'))
        dir_open_button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        dir_open_button.resize(400,20)
        dir_open_button.clicked.connect(lambda: self._load_source(True))
        dir_open_button.setStyleSheet(button_style_sheet)

        nii_open_button = QtWidgets.QPushButton('Load Nifti File')
        nii_open_button.setIcon(QtGui.QIcon('images/buttons_PNG103.png'))
        nii_open_button.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        nii_open_button.resize(400,20)
        nii_open_button.clicked.connect(self._load_source)
        nii_open_button.setStyleSheet(button_style_sheet)

        open_layout = QtWidgets.QHBoxLayout()
        open_layout.addStretch()
        open_layout.addWidget(dir_open_button)
        open_layout.addStretch()
        open_layout.addWidget(nii_open_button)
        open_layout.addStretch()

        main_layout.addLayout(open_layout)
        main_layout.addStretch()

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def _set_menus(self):

        self.statusBar()
        main_menu = self.menuBar()
        main_menu.setStyleSheet('background-color:#bbb7c5;')

        # File menu
        file_menu = main_menu.addMenu('&File')

        open_nii_action = QtWidgets.QAction('&Open Nii File', self)
        open_nii_action.setShortcut('Ctrl+o')
        open_nii_action.setStatusTip('Open Nii File')
        open_nii_action.triggered.connect(self._load_source)

        open_dir_action = QtWidgets.QAction('Open &Directory', self)
        open_dir_action.setShortcut('Ctrl+d')
        open_dir_action.setStatusTip('Open directory of dicoms')
        open_dir_action.triggered.connect(lambda: self._load_source(True))

        exit_action = QtWidgets.QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit')
        exit_action.triggered.connect(self.close)

        file_menu.addAction(open_nii_action)
        file_menu.addAction(open_dir_action)
        file_menu.addAction(exit_action)

        # Workspace menu
        workspace_menu = main_menu.addMenu('&Workspace')

        save_work_action = QtWidgets.QAction('&Save Workspace', self)
        save_work_action.setShortcut('Ctrl+S')
        save_work_action.setStatusTip('Save opened workspace')
        save_work_action.triggered.connect(self._save_workspace)

        open_work_action = QtWidgets.QAction('Open Previous Workspace', self)
        open_work_action.setShortcut('Ctrl+Shift+W')
        open_work_action.setStatusTip('Open previous workspace')
        open_work_action.triggered.connect(self._open_previous_workspace)

        workspace_menu.addAction(save_work_action)
        workspace_menu.addAction(open_work_action)

        view_menu = main_menu.addMenu('&View')

        tools_menu = main_menu.addMenu('&Tools')

        help_menu = main_menu.addMenu('&Help')

    def _open_workspace(self):
        '''
        Open workspace window with selected scans, set workspace to be central widget.
        '''
        if self._source:
            self._workspace = WorkSpace(self._source, self)
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

    def _save_workspace(self):
        print('''Implement _save_workspace''')

    def _open_previous_workspace(self):
        print('''Implement _open_workspace''')