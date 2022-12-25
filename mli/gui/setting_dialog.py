#     This code is a part of program Manual Lichen identification
#     Copyright (C) 2022 contributors Manual Lichen identification
#     The full list is available at the link
#     https://github.com/tagezi/mli/blob/master/contributors.txt
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QPushButton, QVBoxLayout, QHBoxLayout, \
    QLineEdit

from mli.gui.file_dialogs import OpenFileDialog
from mli.gui.message_box import warning_restart_app
from mli.lib.config import ConfigProgram
from mli.lib.sql import SQL, check_connect_db


class SettingDialog(QDialog):
    def __init__(self, oConnector, sPathApp, oParent=None):
        super(SettingDialog, self).__init__(oParent)
        self.oConnector = oConnector
        self.oConfigProgram = ConfigProgram(sPathApp)
        self.init_UI()
        self.connect_actions()

    def init_UI(self):
        self.setWindowTitle('Setting')
        self.setModal(Qt.ApplicationModal)
        self.oButtonApply = QPushButton('Apply', self)
        self.oButtonOk = QPushButton('Ok', self)
        self.oButtonCancel = QPushButton('Cancel', self)
        self.oButtonOpenFile = QPushButton('...', self)
        oVLayout = QVBoxLayout()
        oHLayoutFiledPath = QHBoxLayout()
        oHLayoutButtons = QHBoxLayout()
        sFileNameDB = self.oConfigProgram.get_config_value('DB', 'db_path')
        self.oTextFiled = QLineEdit(sFileNameDB)
        oHLayoutFiledPath.addWidget(self.oTextFiled)
        oHLayoutFiledPath.addWidget(self.oButtonOpenFile)
        oHLayoutButtons.addWidget(self.oButtonApply)
        oHLayoutButtons.addWidget(self.oButtonOk)
        oHLayoutButtons.addWidget(self.oButtonCancel)
        oVLayout.addLayout(oHLayoutFiledPath)
        oVLayout.addLayout(oHLayoutButtons)
        self.setLayout(oVLayout)

    def connect_actions(self):
        self.oButtonOpenFile.clicked.connect(self.onClickOpenFile)
        self.oButtonApply.clicked.connect(self.onClickApply)
        self.oButtonOk.clicked.connect(self.onClickOk)
        self.oButtonCancel.clicked.connect(self.onCancel)

    def onClickOpenFile(self):
        dParameter = {'name': 'Selecting directory',
                      'filter': 'DB file (*.db)'}
        oFileDialog = OpenFileDialog(self, dParameter)
        lFileName = oFileDialog.exec()
        sFileName = ''
        if lFileName:
            sFileName = str(lFileName[0])

        self.oTextFiled.setText(sFileName)

    def onClickApply(self):
        sDBPath = self.oTextFiled.text()
        self.oConfigProgram.set_config_value('DB', 'db_path', sDBPath)
        self.oConnector = SQL(sDBPath)

        sBasePath = self.oConfigProgram.sDir
        sDBDir = self.oConfigProgram.get_config_value('DB', 'db_dir')
        check_connect_db(self.oConnector, sBasePath, sDBDir)

        warning_restart_app()

    def onClickOk(self):
        self.onClickApply()
        self.close()

    def onCancel(self):
        self.close()


if __name__ == '__main__':
    pass
