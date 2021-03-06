#     This code is a part of program Science Articles Orderliness
#     Copyright (C) 2021  Valerii Goncharuk (aka tagezi)
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

from gettext import gettext as _
from itertools import zip_longest

from PyQt5 import QtGui
from PyQt5.QtWidgets import QComboBox, QDialog, QHBoxLayout, QLabel, \
    QLineEdit, QMessageBox, QPushButton, QTextEdit, QVBoxLayout

from mli.gui.file_dialogs import OpenFileDialog
from mli.lib.config import ConfigProgram
from mli.lib.sql import SQL
from mli.lib.str import text_to_list


class HComboBox(QHBoxLayout):
    """ The class creates a block that units QLabel, QComboBox and QLineEdit.
    Also, it creates methods that change parameters inside block without direct
    access.
    """
    def __init__(self, oParent=None):
        super(QHBoxLayout, self).__init__(oParent)
        oLabel = QLabel()
        oLineEdit = QLineEdit()
        oComboBox = QComboBox()
        oComboBox.setLineEdit(oLineEdit)
        self.addWidget(oLabel)
        self.addWidget(oComboBox)
        self.set_combo_width()

    def clear_list(self):
        """ Clean up a list of QComboBox.

        :return: None
        """
        oComboBox = self.itemAt(1).widget()
        oComboBox.clear()

    def get_text(self):
        """ The function gets text from QLineEdit of QComboBox.

        :return: Selected text from QComboBox.
        :rtype: str
        """
        oComboBox = self.itemAt(1).widget()
        return oComboBox.currentText()

    def set_text(self, sString=''):
        """ Set up text into QLineEdit of the block.

        :param sString: A string which display by default in QLineEdit.
        :type sString: str
        :return: None
        """
        oComboBox = self.itemAt(1).widget()
        oLineEdit = oComboBox.lineEdit()
        oLineEdit.setText(sString)

    def set_label(self, sString=''):
        """ Set up text into Label of block.

        :param sString: A string which needs to display as Label in the block.
        :type sString: str
        :return: None
        """
        oLabel = self.itemAt(0).widget()
        oLabel.setText(sString)

    def set_combo_list(self, lItems=None):
        """ Set up a list of QComboBox.

        :param lItems: A list of elements for QComboBox.
        :type lItems: list
        :return: None
        """
        oComboBox = self.itemAt(1).widget()
        oComboBox.addItems(lItems)

    def set_combo_width(self, iSize=300):
        """ Set up width of QComboBox.

        :param iSize: A number which point to width of QComboBox.
        :type iSize: int
        :return: None
        """
        oComboBox = self.itemAt(1).widget()
        oComboBox.setFixedWidth(iSize)


class HLineEdit(QHBoxLayout):
    """ The class creates a block that units QLabel and QLineEdit.
    Also, it creates methods that change parameters inside block without direct
    access.
    """

    def __init__(self, oParent=None):
        super(QHBoxLayout, self).__init__(oParent)
        oLabel = QLabel()
        oLineEdit = QLineEdit()
        self.addWidget(oLabel)
        self.addWidget(oLineEdit)
        self.set_line_width()

    def get_text(self):
        """ The function gets text from QLineEdit.

        :return: Selected text from QLineEdit.
        :rtype: str
        """
        oLineEdit = self.itemAt(1).widget()
        return oLineEdit.text().strip()

    def set_text(self, sString=''):
        """ Set up text into QLineEdit of the block.

        :param sString: A string which display by default in QLineEdit.
        :type sString: str
        :return: None
        """
        oLineEdit = self.itemAt(1).widget()
        oLineEdit.setText(sString)

    def set_label(self, sString=''):
        """ Set up text into Label of block.

        :param sString: A string which needs to display as Label in the block.
        :type sString: str
        :return: None
        """
        oLabel = self.itemAt(0).widget()
        oLabel.setText(sString)

    def set_line_width(self, iSize=300):
        """ Set up width of QLineEdit.

        :param iSize: A number which point to width of QComboBox.
        :type iSize: int
        :return: None
        """
        oLineEdit = self.itemAt(1).widget()
        oLineEdit.setFixedWidth(iSize)


class HTextEdit(QHBoxLayout):
    """ The class creates a block that units QLabel and QTextEdit.
    Also, it creates methods that change parameters inside block without direct
    access.
    """

    def __init__(self, oParent=None):
        super(QHBoxLayout, self).__init__(oParent)
        oLabel = QLabel()
        oTextEdit = QTextEdit()
        self.addWidget(oLabel)
        self.addWidget(oTextEdit)
        self.set_textedit_size()

    def get_text(self):
        """ The function gets text from QLineEdit of QTextEdit.

        :return: Selected text from QTextEdit.
        :rtype: str
        """
        oTextEdit = self.itemAt(1).widget()
        return oTextEdit.toPlainText()

    def set_text(self, sString=''):
        """ Set up text into QTextEdit of the block.

        :param sString: A string which display by default in QTextEdit.
        :type sString: str
        :return: None
        """
        oTextEdit = self.itemAt(1).widget()
        oTextEdit.insertPlainText(sString)

    def set_label(self, sString=''):
        """ Set up text into Label of block.

        :param sString: A string which needs to display as Label in the block.
        :type sString: str
        :return: None
        """
        oLabel = self.itemAt(0).widget()
        oLabel.setText(sString)

    def set_textedit_size(self, iWidth=300, iHeight=120):
        """ Set up width of QTextEdit.

        :param iWidth: A number which point to width of QTextEdit.
        :type iWidth: int
        :param iHeight: A number which point to height of QTextEdit.
        :type iHeight: int
        :return: None
        """
        oTextEdit = self.itemAt(1).widget()
        oTextEdit.setFixedSize(iWidth, iHeight)


if __name__ == '__main__':
    pass
