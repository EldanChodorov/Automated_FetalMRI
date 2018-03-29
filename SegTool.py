#!/usr/bin/env python

# Main File to run program.
# User can open empty session and then load files,
# or specify files straight from command line.

import sys
from main_window import MainWindow
from PyQt5.QtWidgets import QApplication, QStyleFactory


if __name__ == '__main__':
    data_dir = ''

    # TODO: use python options args module
    if len(sys.argv):
        data_dir = sys.argv[0]

    # set style
    style = QStyleFactory.create('Fusion')

    app = QApplication(sys.argv)
    app.setStyle(style)
    try:
        window = MainWindow(data_dir)
        window.show()
    except Exception as e:
        print('{}: {}'.format(type(e), str(e)))

    sys.exit(app.exec_())

