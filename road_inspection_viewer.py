"""
/***************************************************************************
  road_inspection_viewer.py

  QGIS plugin displaying photos from road inspection.
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
SCRIPT_NAME = 'road_inspection_viewer'
SCRIPT_VERSION = '1.2.3'
GENERAL_INFO = u"""
author: Piotr Michałowski, Olsztyn, woj. W-M, Poland
piotrm35@hotmail.com
license: GPL v. 2
work begin: 24.02.2018
"""

BUTTON_HEIGHT = 23


from PyQt5 import QtCore, QtGui, QtWidgets, uic
import os
from .extra_window import extra_window
from .play_thread import play_thread



#====================================================================================================================

class road_inspection_viewer(QtWidgets.QMainWindow):
    
    def  __init__(self, iface):
        super(road_inspection_viewer, self).__init__()
        self.iface = iface
        self.base_path = os.path.realpath(__file__).split(os.sep + SCRIPT_NAME + os.sep)[0] + os.sep + SCRIPT_NAME
        if os.path.exists(os.path.join(os.path.expanduser('~'), 'documents')):
            self.save_path = os.path.join(os.path.expanduser('~'), 'documents')
        else:
            self.save_path = os.path.expanduser('~')    # user home directory
        self.icon = QtGui.QIcon(os.path.join(self.base_path, 'img', 'riv_ico.png'))
        self.start_image = QtGui.QImage(os.path.join(self.base_path, 'img', 'start_image.jpg'))
        self.no_file_image = QtGui.QImage(os.path.join(self.base_path, 'img', 'no_file_image.jpg'))
        self.path_to_photos = None
        self.delay = 700 # ms
        self.raw_image = None
        self.list_of_extra_windows = []
        self.extra_windows_max_number = 0
        self.p_thread = None

        
    def closeEvent(self, event):        # overriding the method
        for i in range(len(self.list_of_extra_windows)):
            if self.list_of_extra_windows[i]:
                self.list_of_extra_windows[i].close()
                self.list_of_extra_windows[i] = None
        event.accept()

    def resizeEvent(self, event):       # overriding the method
        QtWidgets.QMainWindow.resizeEvent(self, event)
        self._show_raw_image(True)

    #----------------------------------------------------------------------------------------------------------------
    # plugin methods:

    def initGui(self):
        self.action = QtWidgets.QAction(self.icon, SCRIPT_TITLE, self.iface.mainWindow())
        self.action.setObjectName('road_inspection_viewer_Action')
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        uic.loadUi(os.path.join(self.base_path, 'ui', 'road_inspection_viewer.ui'), self)
        self.setWindowTitle(SCRIPT_TITLE + ' v. ' + SCRIPT_VERSION)
        self.Delay_pushButton.setText('delay: ' + str(self.delay) + ' ms')
        # buttons' handling:
        self.Path_pushButton.clicked.connect(self.Path_handleButton)
        self.Play_back_pushButton.clicked.connect(self.Play_back_handleButton)
        self.Back_pushButton.clicked.connect(self.Back_handleButton)
        self.Stop_pushButton.clicked.connect(self.Stop_handleButton)
        self.Forward_pushButton.clicked.connect(self.Forward_handleButton)
        self.Play_forward_pushButton.clicked.connect(self.Play_forward_handleButton)
        self.Delay_pushButton.clicked.connect(self.Delay_handleButton)
        self.Save_pushButton.clicked.connect(self.Save_handleButton)
        self.Extra_window_pushButton.clicked.connect(self.Extra_window_handleButton)
        self.About_pushButton.clicked.connect(self.About_handleButton)
        # enebled buttons:
        self._set_buttons_enebled_to_state_start()
        
    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        self.action.triggered.disconnect(self.run)
        self.Stop_handleButton()
        # buttons' handling:
        self.Path_pushButton.clicked.disconnect(self.Path_handleButton)
        self.Play_back_pushButton.clicked.disconnect(self.Play_back_handleButton)
        self.Back_pushButton.clicked.disconnect(self.Back_handleButton)
        self.Stop_pushButton.clicked.disconnect(self.Stop_handleButton)
        self.Forward_pushButton.clicked.disconnect(self.Forward_handleButton)
        self.Play_forward_pushButton.clicked.disconnect(self.Play_forward_handleButton)
        self.Delay_pushButton.clicked.disconnect(self.Delay_handleButton)
        self.Save_pushButton.clicked.disconnect(self.Save_handleButton)
        self.Extra_window_pushButton.clicked.disconnect(self.Extra_window_handleButton)
        self.About_pushButton.clicked.disconnect(self.About_handleButton)
        
    def run(self):
        self.show()
        self.set_and_show_raw_image(self.start_image)

    #----------------------------------------------------------------------------------------------------------------
    # button methods

    def Path_handleButton(self):
        if self.path_to_photos is None:
            photos_folder = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select a photos folder:', self.save_path, QtWidgets.QFileDialog.ShowDirsOnly)
        else:
            photos_folder = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select a photos folder:', self.path_to_photos, QtWidgets.QFileDialog.ShowDirsOnly)
        if os.path.exists(photos_folder):
            self.path_to_photos = photos_folder
            self.Path_pushButton.setText('path')
            self._set_buttons_enebled_to_state_ready()
            file_names = self.get_first_selected_point_file_names()
            self.show_photos_list(file_names)
            
    def Play_back_handleButton(self):
        self.Play_back_pushButton.setEnabled(False)
        self.p_thread = play_thread(self, self.delay, False)
        self.p_thread.start_run()
        self.p_thread.Back_handleButton_signal.connect(self.Back_handleButton)
        self._set_buttons_enebled_to_state_play()
        
    def Back_handleButton(self):
        if self.Back_pushButton.isEnabled():
            self.Back_pushButton.setEnabled(False)
            file_names = self.get_next_feature_file_names(False)
            self.show_photos_list(file_names)
            self.Back_pushButton.setEnabled(True)

    def Stop_handleButton(self):
        if self.Stop_pushButton.isEnabled():
            self.Stop_pushButton.setEnabled(False)
            if self.p_thread:
                self.p_thread.stop_run()
                try:
                    self.p_thread.Back_handleButton_signal.disconnect(self.Back_handleButton)
                except:
                    pass
                try:
                    self.p_thread.Forward_handleButton_signal.disconnect(self.Forward_handleButton)
                except:
                    pass
                self.p_thread = None
            self._set_buttons_enebled_to_state_ready()

    def Forward_handleButton(self):
        if self.Forward_pushButton.isEnabled():
            self.Forward_pushButton.setEnabled(False)
            file_names = self.get_next_feature_file_names(True)
            self.show_photos_list(file_names)
            self.Forward_pushButton.setEnabled(True)
        
    def Play_forward_handleButton(self):
        self.Play_forward_pushButton.setEnabled(False)
        self.p_thread = play_thread(self, self.delay, True)
        self.p_thread.start_run()
        self.p_thread.Forward_handleButton_signal.connect(self.Forward_handleButton)
        self._set_buttons_enebled_to_state_play()

    def Delay_handleButton(self):
        num,ok = QtWidgets.QInputDialog.getInt(self, SCRIPT_TITLE, 'Enter a delay [ms]:', self.delay)
        if ok:
            self.delay = num
            self.Delay_pushButton.setText('delay: ' + str(self.delay) + ' ms')

    def Save_handleButton(self):
        if self.raw_image:
            path_to_file_tuple = QtWidgets.QFileDialog.getSaveFileName(self, 'Save photo', self.save_path, '*.jpg')
            if path_to_file_tuple and len(path_to_file_tuple) >= 1:
                self.raw_image.save(path_to_file_tuple[0])
                self.save_path = os.path.dirname(unicode(path_to_file_tuple[0]))

    def Extra_window_handleButton(self):
        lew_length = len(self.list_of_extra_windows)
        for i in range(lew_length):
            if self.list_of_extra_windows[i] is None:
                extra_window_tmp = extra_window(i + 1, self.start_image, self)
                self.list_of_extra_windows[i] = extra_window_tmp
                file_names = self.get_first_selected_point_file_names()
                self.show_photos_list(file_names)
                extra_window_tmp.show()
                return
        no = lew_length + 1
        if no <= self.extra_windows_max_number:
            extra_window_tmp = extra_window(no, self.start_image, self)
            self.list_of_extra_windows.append(extra_window_tmp)
            file_names = self.get_first_selected_point_file_names()
            self.show_photos_list(file_names)
            extra_window_tmp.show()

    def About_handleButton(self):
        QtWidgets.QMessageBox.information(self, SCRIPT_TITLE, GENERAL_INFO)

    def _set_buttons_enebled_to_state_start(self):
        self.Path_pushButton.setEnabled(True)
        self.Play_back_pushButton.setEnabled(False)
        self.Back_pushButton.setEnabled(False)
        self.Stop_pushButton.setEnabled(False)
        self.Forward_pushButton.setEnabled(False)
        self.Play_forward_pushButton.setEnabled(False)
        self.Delay_pushButton.setEnabled(False)
        self.Extra_window_pushButton.setEnabled(False)
        self.Save_pushButton.setEnabled(False)

    def _set_buttons_enebled_to_state_ready(self):
        self.Path_pushButton.setEnabled(True)
        self.Play_back_pushButton.setEnabled(True)
        self.Back_pushButton.setEnabled(True)
        self.Stop_pushButton.setEnabled(False)
        self.Forward_pushButton.setEnabled(True)
        self.Play_forward_pushButton.setEnabled(True)
        self.Delay_pushButton.setEnabled(True)
        self.Extra_window_pushButton.setEnabled(True)
        self.Save_pushButton.setEnabled(True)

    def _set_buttons_enebled_to_state_play(self):
        self.Path_pushButton.setEnabled(False)
        self.Play_back_pushButton.setEnabled(False)
        self.Back_pushButton.setEnabled(True)
        self.Stop_pushButton.setEnabled(True)
        self.Forward_pushButton.setEnabled(True)
        self.Play_forward_pushButton.setEnabled(False)
        self.Delay_pushButton.setEnabled(False)
        self.Extra_window_pushButton.setEnabled(False)
        self.Save_pushButton.setEnabled(False)

    #----------------------------------------------------------------------------------------------------------------
    # work methods:

    def get_first_selected_point_file_names(self):
        layer = self.iface.activeLayer()
        if layer:
            selection = layer.selectedFeatures()
            if selection and len(selection) > 0:
                try:
                    file_names = selection[0]['file_names']
                    if file_names and len(file_names) > 0:
                        self.extra_windows_max_number = len(file_names.split(';')) - 1
                        return file_names
                    else:
                        self.extra_windows_max_number = 0
                        return None
                except:
                    self.extra_windows_max_number = 0
                    return None
            else:
                self.Stop_handleButton()
                QtWidgets.QMessageBox.critical(self, SCRIPT_TITLE, 'Please select a POINT in selected layer of road inspection.')
                return None
        else:
            self.Stop_handleButton()
            QtWidgets.QMessageBox.critical(self, SCRIPT_TITLE, 'Please select a LAYER of road inspection.')
            return None

    def get_first_selected_point_id(self):
        layer = self.iface.activeLayer()
        if layer:
            selection = layer.selectedFeatures()
            if selection and len(selection) > 0:
                return selection[0].id()
            else:
                self.Stop_handleButton()
                QtWidgets.QMessageBox.critical(self, SCRIPT_TITLE, 'Please select a POINT in selected layer of road inspection.')
                return None
        else:
            self.Stop_handleButton()
            QtWidgets.QMessageBox.critical(self, SCRIPT_TITLE, 'Please select a LAYER of road inspection.')
            return None
        
    def get_next_feature_file_names(self, go_forward):
        current_id = self.get_first_selected_point_id()
        if current_id is not None:  # because current_id = 0 should be True
            self.iface.activeLayer().selectByIds([])            # To clear the selection, just pass an empty list.
            if go_forward:
                current_id += 1
            else:
                current_id -= 1
            self.iface.activeLayer().selectByIds([current_id])   # Add this features to the selected list.
            file_names = self.get_first_selected_point_file_names()
            if file_names:
                return file_names
            self.Stop_handleButton()
            QtWidgets.QMessageBox.information(self, 'Stop', 'Points list ended.')
        return None

    def show_photos_list(self, file_names):
        if file_names:
            file_names_list = file_names.split(';')
            n_file = len(file_names_list)
            if n_file > 0:
                self.show_photo(self, file_names_list[0])
                for i in range(len(self.list_of_extra_windows)):
                    if i + 1 < n_file:
                        self.show_photo(self.list_of_extra_windows[i], file_names_list[i + 1])
                    else:
                        self.show_photo(self.list_of_extra_windows[i], None)
                        
    def show_photo(self, window, file_name):
        if window:
            if file_name and os.path.exists(os.path.join(self.path_to_photos, file_name)):
                image = QtGui.QImage(os.path.join(self.path_to_photos, file_name))
                window.set_and_show_raw_image(image)
            else:
                window.set_and_show_raw_image(self.no_file_image)

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

    def extra_window_is_closing(self, no):
        self.list_of_extra_windows[no - 1] = None


#====================================================================================================================

    
