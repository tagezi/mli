#     This code is a part of program Manual Lichen identification
#     Copyright (C) 2022  Valerii Goncharuk (aka tagezi)
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
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QPushButton, QVBoxLayout

from mli.gui.dialog_elements import HComboBox, HTextEdit, HLineEdit
from mli.gui.message_box import warning_synonym_exist, warning_synonym_more,\
     warning_this_exist
from mli.lib.config import ConfigProgram
from mli.lib.sql import SQL
from mli.lib.str import text_to_list


def zip_taxon_lists(iTaxName, lSynonyms, lAuthors):
    """ Creates a list of lists from the taxon ID, taxon synonyms, and synonym
    authors.

    :param iTaxName: The ID of the modern taxon name.
    :type iTaxName: int
    :param lSynonyms: A synonym list of the modern taxon name.
    :type lSynonyms: list
    :param lAuthors: An author of the synonym.
    :type lAuthors: list
    :return: Return a list with elements of the form - taxon ID, taxon synonym,
     and synonym author.
    :rtype: list[int, str, str]
    """
    lTaxName = []
    iNum = len(lSynonyms)
    while iNum:
        lTaxName.append(iTaxName)
        iNum -= 1

    return list(zip_longest(lTaxName, lSynonyms, lAuthors, fillvalue=''))


class ADialog(QDialog):
    """ Creates abstract class that contain common elements."""
    def __init__(self, oParent=None):
        """ initiating a dialog view """
        super(ADialog, self).__init__(oParent)
        oConfigProgram = ConfigProgram()
        sDBFile = oConfigProgram.get_config_value('DB', 'filepath')
        self.oConnector = SQL(sDBFile)
        self.init_UI_button_block()
        self.init_UI_failed()
        self.init_UI()
        self.connect_actions()

    def init_UI(self):
        """ Redundancy method """
        pass

    def init_UI_button_block(self):
        """ Creates a block of buttons for further use in child dialog classes.
        """
        self.oHLayoutButtons = QHBoxLayout()
        self.oButtonApply = QPushButton(_('Apply'), self)
        self.oButtonApply.setFixedWidth(80)
        self.oButtonOk = QPushButton(_('Ok'), self)
        self.oButtonOk.setFixedWidth(80)
        self.oButtonCancel = QPushButton(_('Cancel'), self)
        self.oButtonCancel.setFixedWidth(80)
        self.oHLayoutButtons.addWidget(self.oButtonApply,
                                       alignment=Qt.AlignRight)
        self.oHLayoutButtons.addWidget(self.oButtonOk)
        self.oHLayoutButtons.addWidget(self.oButtonCancel)

    def init_UI_failed(self):
        self.oComboMainTax = HComboBox(_('Main Taxon:'))
        self.oComboTaxLevel = HComboBox(_('Taxon level:'))
        self.oLineEditLatName = HLineEdit(_('Latin name:'))
        self.oLineEditAuthor = HLineEdit(_('Author & year:'))
        self.oLineEditEnName = HLineEdit(_('English name:'))
        self.oLineEditLocaleName = HLineEdit(_('Local name:'))
        self.oTextEditSynonyms = HTextEdit(_('Synonyms:'))
        self.oTextEditAuthors = HTextEdit(_('Authors:'))
        self.oComboTaxNames = HComboBox(_('Taxon name: '))

        self.fill_combobox()

    def connect_actions(self):
        """ Connects buttons with actions they should perform. """
        self.oButtonApply.clicked.connect(self.onClickApply)
        self.oButtonOk.clicked.connect(self.onClickOk)
        self.oButtonCancel.clicked.connect(self.onCancel)
        (self.oComboMainTax.get_widget()).currentTextChanged.connect(
            self.onCurrentMainTaxonChanged)

    def clean_field(self):
        self.oComboMainTax.clear_list()
        self.oComboTaxLevel.clear_list()
        self.oLineEditLatName.set_text('')
        self.oLineEditAuthor.set_text('')
        self.oLineEditEnName.set_text('')
        self.oLineEditLocaleName.set_text('')
        self.oTextEditSynonyms.set_text('')
        self.oTextEditAuthors.set_text('')
        self.oComboTaxNames.clear_list()

    def create_level_list(self, sTaxon='', bGetAll=None):
        oCursor = self.oConnector.sql_get_all('TaxonLevel')
        lLevels, lValues = [], []
        for tRow in oCursor:
            lValues.append(tRow[3])

        if bGetAll is None:
            sLevelMainTaxon = sTaxon.split('(')[1].split(')')[0]
            sRow = lValues[0]
            while sRow != sLevelMainTaxon:
                lValues.pop(0)
                sRow = lValues[0]
        lLevels = lValues
        lLevels.pop(0)

        return lLevels

    def create_taxon_list(self, lTaxonLevel):
        """ Creates a list of taxon names for further use in dialog elements.

        :param lTaxonLevel: A list of taxon level.
        :type lTaxonLevel: list
        :return: A list in form - (Taxon Level) Taxon Name
        :type: list[str]
        """
        lValues = []
        for sTaxonLevel in lTaxonLevel:

            sSQL = 'SELECT TaxonLevel.level_name, Taxon.taxon_lat_name ' \
                   'FROM Taxon JOIN TaxonLevel ' \
                   'ON Taxon.id_level=TaxonLevel.id_level ' \
                   f"WHERE TaxonLevel.level_name='{sTaxonLevel}'"\
                   'ORDER BY Taxon.taxon_lat_name ASC;'
            oCursor = self.oConnector.execute_query(sSQL)

            for tRow in oCursor:
                lValues.append(f'({tRow[0]}) {tRow[1]}')
        return lValues

    def fill_combobox(self):
        lTaxonLevel = self.create_level_list(bGetAll=True)
        self.oComboMainTax.set_combo_list(self.create_taxon_list(lTaxonLevel))
        self.oComboTaxLevel.set_combo_list(lTaxonLevel)
        self.oComboTaxLevel.set_text(lTaxonLevel[1])
        self.oComboTaxNames.set_combo_list(self.create_taxon_list(lTaxonLevel))

    def onCancel(self):
        """ The method closes the dialog without saving the data. """
        self.close()

    def onClickApply(self):
        """ Reserves the Apply dialog button method for future use. """
        pass

    def onClickOk(self):
        """ The method saves the data and closes the dialog In order for the
        data to be saved, you must override the method onClickApply."""
        self.onClickApply()
        self.close()

    def onCurrentMainTaxonChanged(self, sTaxon=''):
        """ TODO: Do a name lookup on the parent taxon field.
             Traceback (most recent call last):
             File "/home/lera/project/mli/mli/gui/tool_dialogs.py", line 228, in onCurrentMainTaxonChanged
             lTaxonLevel = self.create_level_list(sTaxon)
             File "/home/lera/project/mli/mli/gui/tool_dialogs.py", line 174, in create_level_list
             sLevelMainTaxon = sTaxon.split('(')[1].split(')')[0]
             IndexError: list index out of range"""

        lTaxonLevel = self.create_level_list(sTaxon)
        self.oComboTaxLevel.clear_list()
        self.oComboTaxLevel.set_combo_list(lTaxonLevel)
        self.oComboTaxLevel.set_text(lTaxonLevel[0])

    def check_synonyms(self, sTaxName, sSynonyms, sAuthors):
        """ Checks if there are such synonyms in the list of taxon and if the
        number of synonyms matches the number of authors.

        :param sTaxName: Latin name of taxon.
        :type sTaxName: str
        :param sSynonyms: A list of synonyms.
        :type sSynonyms: str
        :param sAuthors: A author list of synonyms.
        :type sAuthors: str
        :return:Returns a dictionary in the form of a taxon name, a list of
         synonyms, and a list of authors, or False
        :rtype: dict[int, list[str], list[str]] | bool
        """
        iTaxName = self.oConnector.sql_get_id('Taxon', 'id_taxon',
                                              'taxon_lat_name', (sTaxName,))
        bOk = True
        lSynonyms = []
        if sSynonyms:
            lSynonyms.extend(text_to_list(sSynonyms))
            for sSynonym in lSynonyms:
                bExist = self.oConnector.sql_get_id('TaxonOtherNames',
                                                    'id_other_names',
                                                    'id_taxon, taxon_name',
                                                    (sSynonym,))
                if bExist:
                    bOk = warning_synonym_exist(sTaxName)

        lAuthors = []
        if sAuthors:
            lAuthors.extend(text_to_list(sAuthors))
        if len(lSynonyms) < len(lAuthors):
            bOk = warning_synonym_more()

        if bOk:
            return {'taxname': iTaxName,
                    'listsyn': lSynonyms,
                    'listauth': lAuthors}
        return False

    def save_synonyms(self, iTaxName, lSynonyms, lAuthors):
        """ Save a list of synonyms.

        :param iTaxName: The ID of the modern taxon name.
        :type iTaxName: int
        :param lSynonyms: A synonym list of the modern taxon name.
        :type lSynonyms: list
        :param lAuthors: An author of the synonym.
        :type lAuthors: list
        """
        if lSynonyms:
            lValues = zip_taxon_lists(iTaxName, lSynonyms, lAuthors)
            for tValues in lValues:
                self.oConnector.insert_row('TaxonOtherNames',
                                           'id_taxon, taxon_name, authors',
                                           tValues)


class AddSynonymsDialog(ADialog):
    def __init__(self, oParent=None):
        super(AddSynonymsDialog, self).__init__(oParent)

    def init_UI(self):
        self.setWindowTitle(_('Add new synonyms to taxon name'))
        self.setModal(Qt.ApplicationModal)

        oVLayout = QVBoxLayout()
        oVLayout.addLayout(self.oComboTaxNames)
        oVLayout.addLayout(self.oTextEditSynonyms)
        oVLayout.addLayout(self.oTextEditAuthors)
        oVLayout.addLayout(self.oHLayoutButtons)
        self.setLayout(oVLayout)

    def onClickApply(self):
        sTaxName = self.oComboTaxNames.get_text().split(') ')[1]
        sSynonyms = self.oTextEditSynonyms.get_text()
        sAuthors = self.oTextEditAuthors.get_text()
        dSynonyms = self.check_synonyms(sTaxName, sSynonyms, sAuthors)
        if not dSynonyms:
            return

        self.save_synonyms(dSynonyms['taxname'],
                           dSynonyms['listsyn'],
                           dSynonyms['listauth'])

        self.oComboTaxNames.clear_list()
        self.oComboTaxNames.set_combo_list(self.create_taxon_list())
        self.oComboTaxNames.set_text(sTaxName)
        self.oTextEditSynonyms.set_text('')
        self.oTextEditAuthors.set_text('')


class EditTaxonDialog(ADialog):
    def __init__(self, oParent=None):
        super(EditTaxonDialog, self).__init__(oParent)

    def init_UI(self):
        self.setWindowTitle(_('Add new taxon to tree'))
        self.setModal(Qt.ApplicationModal)

        oVLayout = QVBoxLayout()
        oVLayout.addLayout(self.oComboTaxLevel)
        oVLayout.addLayout(self.oComboMainTax)
        oVLayout.addLayout(self.oLineEditAuthor)
        oVLayout.addLayout(self.oLineEditAuthor)
        oVLayout.addLayout(self.oLineEditEnName)
        oVLayout.addLayout(self.oLineEditLocaleName)
        oVLayout.addLayout(self.oTextEditSynonyms)
        oVLayout.addLayout(self.oTextEditAuthors)
        oVLayout.addLayout(self.oHLayoutButtons)
        self.setLayout(oVLayout)

    def onClickApply(self):
        pass


class NewTaxonDialog(ADialog):
    def __init__(self, oParent=None):
        super(NewTaxonDialog, self).__init__(oParent)

    def init_UI(self):
        self.setWindowTitle(_('Add new taxon to tree'))
        self.setModal(Qt.ApplicationModal)

        oVLayout = QVBoxLayout()
        oVLayout.addLayout(self.oComboMainTax)
        oVLayout.addLayout(self.oComboTaxLevel)
        oVLayout.addLayout(self.oLineEditLatName)
        oVLayout.addLayout(self.oLineEditAuthor)
        oVLayout.addLayout(self.oLineEditLocaleName)
        oVLayout.addLayout(self.oTextEditSynonyms)
        oVLayout.addLayout(self.oTextEditAuthors)
        oVLayout.addLayout(self.oHLayoutButtons)
        self.setLayout(oVLayout)

    def onClickApply(self):
        sTaxLevel = self.oComboTaxLevel.get_text()
        sMainTax = self.oComboMainTax.get_text().split()[1]
        sLatName = self.oLineEditLatName.get_text()
        sAuthor = self.oLineEditAuthor.get_text()
        sLocalName = self.oLineEditLocaleName.get_text()
        sSynonyms = self.oTextEditSynonyms.get_text()
        sAuthors = self.oTextEditAuthors.get_text()

        iTaxLevel = self.oConnector.sql_get_id('TaxonLevel', 'id_level',
                                               'level_name', (sTaxLevel,))
        iMainTax = self.oConnector.sql_get_id('Taxon', 'id_taxon',
                                              'taxon_lat_name', (sMainTax,))
        bTaxonName = self.oConnector.sql_get_id('Taxon', 'id_taxon',
                                                'taxon_lat_name', (sLatName,))

        if bTaxonName:
            warning_this_exist(_('taxon name'), sLatName)

        dSynonyms = self.check_synonyms(sLatName, sSynonyms, sAuthors)
        if sLatName and not bTaxonName:
            tTaxValues = (iTaxLevel, iMainTax, sLatName, sLocalName,)
            self.save_(tTaxValues, sLatName, sAuthor, dSynonyms['listsyn'],
                       dSynonyms['listauth'])

            self.clean_field()
            self.fill_combobox()

    def save_(self, tTaxonValues, sLatName, sAuthor, lSynonyms, lAuthors):
        sColumns = 'id_level, id_main_taxon, taxon_lat_name, taxon_name'
        iTaxonName = self.oConnector.insert_row('Taxon', sColumns,
                                                tTaxonValues)
        self.oConnector.insert_row('TaxonOtherNames',
                                   'id_taxon, taxon_name, authors',
                                   (iTaxonName, sLatName, sAuthor))
        if lSynonyms:
            self.save_synonyms(iTaxonName, lSynonyms, lAuthors)


class EditSubstrate(ADialog):
    def __init__(self, oParent=None):
        super(EditSubstrate, self).__init__(oParent)

    def init_UI(self):
        self.setWindowTitle(_('Edit new substrate...'))
        self.setModal(Qt.ApplicationModal)

        oVLayout = QVBoxLayout()
        self.oComboSubstrateLevel = HComboBox(_('Substrate:'))
        self.oComboSubstrateLevel.set_combo_list(
            sorted(self.create_substrate_list('Substrate')))
        self.oLineEditSubstrate = HLineEdit(_('Substrate name:'))

        oVLayout.addLayout(self.oComboSubstrateLevel)
        oVLayout.addLayout(self.oLineEditSubstrate)
        oVLayout.addLayout(self.oHLayoutButtons)
        self.setLayout(oVLayout)

    def create_substrate_list(self, sDB):
        oCursor = self.oConnector.sql_get_all(sDB)
        lValues = []
        for tRow in oCursor:
            lValues.append(tRow[1])
        return lValues

    def onClickApply(self):
        sSubstrate = self.oLineEditSubstrate.get_text()
        bSubstrate = self.oConnector.sql_get_id('Substrate', 'id_substrate',
                                                'substrate_name',
                                                (sSubstrate,))

        if not bSubstrate:
            tValues = (sSubstrate,)
            self.save_(tValues)
            self.oLineEditSubstrate.set_text('')

    def save_(self, tValues):
        sColumns = 'substrate_name'
        self.oConnector.insert_row('Substrate', sColumns, tValues)


class NewSubstrate(ADialog):
    def __init__(self, oParent=None):
        super(NewSubstrate, self).__init__(oParent)

    def init_UI(self):
        self.setWindowTitle(_('Add new substrate...'))
        self.setModal(Qt.ApplicationModal)

        oVLayout = QVBoxLayout()
        self.oLineEditSubstrate = HLineEdit(_('Substrate name:'))

        oVLayout.addLayout(self.oLineEditSubstrate)
        oVLayout.addLayout(self.oHLayoutButtons)
        self.setLayout(oVLayout)

    def onClickApply(self):
        sSubstrate = self.oLineEditSubstrate.get_text()
        bSubstrate = self.oConnector.sql_get_id('Substrate', 'id_substrate',
                                                'substrate_name',
                                                (sSubstrate,))

        if not bSubstrate:
            tValues = (sSubstrate,)
            self.save_(tValues)
            self.oLineEditSubstrate.set_text('')

    def save_(self, tValues):
        sColumns = 'substrate_name'
        self.oConnector.insert_row('Substrate', sColumns, tValues)


if __name__ == '__main__':
    pass
