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

from gettext import gettext as _
from PyQt6.QtWidgets import QVBoxLayout

from mli.gui.dialog_elements import ADialogApplyButtons, HComboBox, HLineEdit


class EditSubstrateDialog(ADialogApplyButtons):
    """ Dialog window which allows user to change substrate type. """

    def __init__(self, oConnector, oParent=None):
        """ Initiating a class. """
        super(EditSubstrateDialog, self).__init__(oConnector, oParent)
        self.init_UI()

    def init_UI(self):
        """ Creating a dialog window. """
        self.setWindowTitle(_('Edit substrate...'))
        self.setModal(True)

        self.oComboSubstrateLevel = HComboBox(_('Старое название субстрата:'))
        self.oLineEditSubstrate = HLineEdit(_('Новое название субстрата:'))
        self.oComboSubstrateLevel.set_combo_list(
            sorted(self.create_substrate_list('Substrates')))

        oVLayout = QVBoxLayout()
        oVLayout.addLayout(self.oComboSubstrateLevel)
        oVLayout.addLayout(self.oLineEditSubstrate)
        oVLayout.addLayout(self.oHLayoutButtons)
        self.setLayout(oVLayout)

    def create_substrate_list(self, sDB):
        """ Filling the drop-down list with substrate types.

        :param sDB: A name table when information on substrate is saved.
        :type sDB: str
        :return: A list of substrate types.
        :rtype: list[str]
        """
        oCursor = self.oConnector.sql_get_all(sDB)
        return [tRow[2] for tRow in oCursor]

    def onClickApply(self):
        """ Realization of the abstract method of the parent class. """
        sOldSubstrate = self.oComboSubstrateLevel.get_text()
        sSubstrate = self.oLineEditSubstrate.get_text()
        bSubstrate = self.oConnector.get_substrate_id(sSubstrate)

        if sOldSubstrate == bSubstrate or bSubstrate:
            return

        iSubstrateID = self.oConnector.get_substrate_id(sOldSubstrate)
        self.save_((sSubstrate, iSubstrateID,))
        self.oLineEditSubstrate.set_text('')

    def save_(self, tValues):
        """ Method for saving information about the substrate in the database.

        :param tValues: Type of substrate to be entered into the database.
        :type tValues: tuple
        """
        self.oConnector.update('Substrates', 'substrateLocalName',
                               'substrateID', tValues)


class NewSubstrateDialog(ADialogApplyButtons):
    """ Dialog window which adds new substrate type. """

    def __init__(self, oConnector, oParent=None):
        """ Initiating a class. """
        super(NewSubstrateDialog, self).__init__(oConnector, oParent)
        self.init_UI()

    def init_UI(self):
        """ Creating a dialog window. """
        self.setWindowTitle(_('Добавить новый субстрат...'))
        self.setModal(True)

        self.oComboSubstrateLevel = HComboBox(_('Старое название субстрата:'))
        self.oLineEditSubstrate = HLineEdit(_('Новое название субстрата:'))

        oVLayout = QVBoxLayout()
        oVLayout.addLayout(self.oLineEditSubstrate)
        oVLayout.addLayout(self.oHLayoutButtons)
        self.setLayout(oVLayout)

    def onClickApply(self):
        """ Realization of the abstract method of the parent class. """
        sSubstrate = self.oLineEditSubstrate.get_text()
        bSubstrate = self.oConnector.get_substrate_id(sSubstrate)

        if bSubstrate:
            return

        self.save_((sSubstrate,))
        self.oLineEditSubstrate.set_text('')

    def save_(self, tValues):
        """ Method for saving information about the substrate in the database.

        :param tValues: Type of substrate to be entered into the database.
        :type tValues: tuple
        """
        self.oConnector.insert_row('Substrates',
                                   'substrateLocalName', tValues)


if __name__ == '__main__':
    pass
