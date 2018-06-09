#!/usr/bin/env python

"""
Main File to run SegTool program.
Creates the MainWindow and Application instances.
User can open empty session and then load files,
or specify files straight from command line.
"""

import sys
from main_window import MainWindow
from PyQt5.QtWidgets import QApplication, QStyleFactory


if __name__ == '__main__':
    data_dir = ''

    if len(sys.argv):
        data_dir = sys.argv[0]

    # set style
    style = QStyleFactory.create('Fusion')

    # open and run app
    app = QApplication(sys.argv)
    app.setStyle(style)
    window = MainWindow(data_dir)
    window.show()
    sys.exit(app.exec_())

