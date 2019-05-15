# -*- coding: utf-8 -*-

"""
/***************************************************************************
  play_thread.py

  An play_thread for road_inspection_viewer QGIS plugin.
  --------------------------------------
  Date : 24-02-2018
  Copyright: (C) 2018 by Piotr Michałowski
  Email: piotrm35@hotmail.com
/***************************************************************************
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as published
 * by the Free Software Foundation.
 *
 ***************************************************************************/
"""

from PyQt5 import QtCore
import time

        
#====================================================================================================================

class play_thread(QtCore.QThread):

    Back_handleButton_signal = QtCore.pyqtSignal()
    Forward_handleButton_signal = QtCore.pyqtSignal()

    def __init__(self, parent, delay, go_forward):
        super(play_thread, self).__init__(parent)
        self._delay = delay / 1000.0
        self._go_forward = go_forward
        self._work = False

    def run(self):
        while self._work:
            if self._go_forward:
                self.Forward_handleButton_signal.emit()
            else:
                self.Back_handleButton_signal.emit()
            time.sleep(self._delay)

    def start_run(self):
        self._work = True
        self.start()

    def stop_run(self):
        self._work = False
        time.sleep(self._delay + 0.1)

        
#====================================================================================================================

    
