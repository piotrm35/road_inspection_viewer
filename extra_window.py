# -*- coding: utf-8 -*-

"""
/***************************************************************************
  extra_window.py

  An extra_window for road_inspection_viewer QGIS plugin.
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

SCRIPT_TITLE = 'Road Inspection Viewer'
BUTTON_HEIGHT = 23


from PyQt5 import QtCore, QtGui, QtWidgets, uic
import os

#====================================================================================================================

class extra_window(QtWidgets.QMainWindow):
    
    def  __init__(self, no, image, parent):
        super(extra_window, self).__init__(parent)
        self.no = no
        self.parent = parent
        self.raw_image = image
        uic.loadUi(os.path.join(self.parent.base_path, 'ui', 'extra_window.ui'), self)
        self.setObjectName('extra_window(' + str(self.no) + ')')
        self.setWindowTitle(SCRIPT_TITLE + '  extra window(' + str(self.no) + ')')
        self.resize(self.parent.width(), self.parent.height())
        self.Save_pushButton.clicked.connect(self.Save_handleButton)
        self.Set_parent_size_pushButton.clicked.connect(self.Set_parent_size_handleButton)
        self.current_img_file_name = None

    def  __del__(self):
        self.Save_pushButton.clicked.disconnect(self.Save_handleButton)
        self.Set_parent_size_pushButton.clicked.disconnect(self.Set_parent_size_handleButton)
        super(extra_window, self).__del__(parent)

    def closeEvent(self, event):        # overriding the method
        self.parent.extra_window_is_closing(self.no)
        event.accept()

    def resizeEvent(self, event):       # overriding the method
        QtWidgets.QMainWindow.resizeEvent(self, event)
        self._show_raw_image(True)

    def Save_handleButton(self):
        if self.raw_image:
            if self.current_img_file_name:
                path_to_file_tuple = QtWidgets.QFileDialog.getSaveFileName(self, 'Save photo', os.path.join(self.parent.save_path, self.current_img_file_name), '*.jpg')
            else:
                path_to_file_tuple = QtWidgets.QFileDialog.getSaveFileName(self, 'Save photo', self.parent.save_path, '*.jpg')
            if path_to_file_tuple and len(path_to_file_tuple) >= 1:
                self.raw_image.save(path_to_file_tuple[0])
                self.parent.save_path = os.path.dirname(unicode(path_to_file_tuple[0]))

    def Set_parent_size_handleButton(self):
        self.resize(self.parent.width(), self.parent.height())
        self.update()

    def set_and_show_raw_image(self, image):
        self.raw_image = image
        self._show_raw_image(False)

    def _show_raw_image(self, resize_the_label):
        if self.raw_image:
            width = self.width()
            height = self.height() - BUTTON_HEIGHT - 4
            image = QtGui.QImage(self.raw_image)
            image = image.scaled(width, height, aspectRatioMode=QtCore.Qt.KeepAspectRatio, transformMode=QtCore.Qt.SmoothTransformation)
            if resize_the_label:
                self.label.setGeometry(QtCore.QRect(0, BUTTON_HEIGHT + 2, width, height))
            self.label.setPixmap(QtGui.QPixmap.fromImage(image))


#====================================================================================================================

    
