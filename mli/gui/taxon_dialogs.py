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
from PyQt5.QtWidgets import QComboBox, QDialog, QHBoxLayout, QLabel, \
    QLineEdit, QMessageBox, QPushButton, QTextEdit, QVBoxLayout

from mli.gui.file_dialogs import OpenFileDialog
from mli.gui.dialog_elements import HComboBox, HTextEdit, HLineEdit
from mli.lib.config import ConfigProgram
from mli.lib.sql import SQL
from mli.lib.str import text_to_list


def zip_taxon_lists(iTaxName, lSynonyms, lAuthors):
    lTaxName = []
    iNum = len(lSynonyms)
    while iNum:
        lTaxName.append(iTaxName)
        iNum -= 1

    return list(zip_longest(lTaxName, lSynonyms, lAuthors, fillvalue=''))


def warning_taxon_exist(sTaxName):
    oMsgBox = QMessageBox()
    oMsgBox.setIcon(QMessageBox.Information)
    oMsgBox.setText(_(f'Such the taxon name <i>{sTaxName}</i> already exists. '
                      f'Do write data?'))
    oMsgBox.setWindowTitle(_('Save Confirmation'))
    oMsgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    oMsgBoxButton = oMsgBox.exec()
    if oMsgBoxButton == QMessageBox.Ok:
        return True


def warning_synonym_more():
    oMsgBox = QMessageBox()
    oMsgBox.setText(_('There are fewer synonyms than authors!'
                      ' Try to fix it!'))
    oMsgBox.exec()
    return False


class TaxonDialog(QDialog):
    def __init__(self, oParent=None):
        super(TaxonDialog, self).__init__(oParent)
        oConfigProgram = ConfigProgram()
        sDBFile = oConfigProgram.get_config_value('DB', 'filepath')
        self.oConnector = SQL(sDBFile)
        self.init_UI_button_block()
        self.init_UI()
        self.connect_actions()

    def init_UI(self):
        pass

    def init_UI_button_block(self):
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

    def connect_actions(self):
        self.oButtonApply.clicked.connect(self.onClickApply)
        self.oButtonOk.clicked.connect(self.onClickOk)
        self.oButtonCancel.clicked.connect(self.onCancel)

    def onCancel(self):
        self.close()

    def onClickApply(self):
        pass

    def onClickOk(self):
        self.onClickApply()
        self.close()

    def onCreateTaxonList(self):
        sSQL = 'SELECT TaxonLevel.level_name, TaxonStructure.taxon_name ' \
               'FROM TaxonStructure JOIN TaxonLevel ' \
               'ON TaxonStructure.taxon_level=TaxonLevel.id_taxon_level;'
        oCursor = self.oConnector.execute_query(sSQL)
        lValues = []
        for tRow in oCursor:
            lValues.append(f'({tRow[0]}) {tRow[1]}')
        return lValues

    def save_synonyms(self, iTaxName, lSynonyms, lAuthors):
        if lSynonyms:
            lValues = zip_taxon_lists(iTaxName, lSynonyms, lAuthors)
            for tValues in lValues:
                self.oConnector.insert_row('TaxonOtherNames',
                                           'id_taxon, taxon_name, authors',
                                           tValues)


class AddSynonymsDialog(TaxonDialog):
    def __init__(self, oParent=None):
        super(AddSynonymsDialog, self).__init__(oParent)

    def init_UI(self):
        self.setWindowTitle(_('Add new synonyms to taxon name'))
        self.setModal(Qt.ApplicationModal)

        oVLayout = QVBoxLayout()
        self.oComboTaxNames = HComboBox()
        self.oComboTaxNames.set_label(_('Taxon name'))
        self.oComboTaxNames.set_combo_list(self.onCreateTaxonList())
        self.oTextEditSynonyms = HTextEdit()
        self.oTextEditSynonyms.set_label(_('Synonyms'))
        self.oTextEditAuthors = HTextEdit()
        self.oTextEditAuthors.set_label(_('Authors'))

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
        self.oComboTaxNames.set_combo_list(self.onCreateTaxonList())
        self.oComboTaxNames.set_text(sTaxName)
        self.oTextEditSynonyms.set_text('')
        self.oTextEditAuthors.set_text('')

    def check_synonyms(self, sTaxName, sSynonyms, sAuthors):
        iTaxName = self.oConnector.sql_get_id('TaxonStructure', 'id_taxon',
                                              'taxon_name', (sTaxName,))
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
                    bOk = warning_taxon_exist(sTaxName)

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


class EditTaxonDialog(TaxonDialog):
    def __init__(self, oParent=None):
        super(EditTaxonDialog, self).__init__(oParent)

    def init_UI(self):
        self.setWindowTitle(_('Add new taxon to tree'))
        self.setModal(Qt.ApplicationModal)

        oVLayout = QVBoxLayout()
        oHLayoutTaxLevel = QHBoxLayout()
        oHLayoutMainTax = QHBoxLayout()
        oHLayoutLatName = QHBoxLayout()
        oHLayoutAuthor = QHBoxLayout()
        oHLayoutEnName = QHBoxLayout()
        oHLayoutLocalName = QHBoxLayout()
        oHLayoutSynonyms = QHBoxLayout()
        oHLayoutAuthors = QHBoxLayout()

        self.oLabelTaxLevel = QLabel()
        self.oLabelTaxLevel.setText(_('Taxon level'))
        self.oLineEditTaxLevel = QLineEdit()
        self.oComboTaxLevel = QComboBox()
        self.oComboTaxLevel.setFixedWidth(300)
        self.oComboTaxLevel.setLineEdit(self.oLineEditTaxLevel)
        self.oComboTaxLevel.addItems(self.onCreateTaxonList())
        self.oLabelMainTax = QLabel()
        self.oLineEditMainTax = QLineEdit()
        self.oLabelMainTax.setText(_('Main Taxon'))
        self.oComboMainTax = QComboBox()
        self.oComboMainTax.setFixedWidth(300)
        self.oComboMainTax.setLineEdit(self.oLineEditMainTax)
        self.oComboMainTax.addItems(self.onCreateTaxonList())
        self.oLabelLatName = QLabel()
        self.oLabelLatName.setText(_('Latin name'))
        self.oLineEditLatName = QLineEdit()
        self.oLineEditLatName.setFixedWidth(300)
        self.oLabelAuthor = QLabel()
        self.oLabelAuthor.setText(_('Author & year'))
        self.oLineEditAuthor = QLineEdit()
        self.oLineEditAuthor.setFixedWidth(300)
        self.oLabelEnName = QLabel()
        self.oLabelEnName.setText(_('English name'))
        self.oLineEditEnName = QLineEdit()
        self.oLineEditEnName.setFixedWidth(300)
        self.oLabelLocalName = QLabel()
        self.oLabelLocalName.setText(_('Local name'))
        self.oLineEditLocaleName = QLineEdit()
        self.oLineEditLocaleName.setFixedWidth(300)
        self.oLabelSynonyms = QLabel()
        self.oLabelSynonyms.setText(_('Synonyms'))
        self.oTextEditSynonyms = QTextEdit()
        self.oTextEditSynonyms.setFixedSize(300, 100)
        self.oLabelAuthors = QLabel()
        self.oLabelAuthors.setText(_('Authors'))
        self.oTextEditAuthors = QTextEdit()
        self.oTextEditAuthors.setFixedSize(300, 100)

        oHLayoutTaxLevel.addWidget(self.oLabelTaxLevel)
        oHLayoutTaxLevel.addWidget(self.oComboTaxLevel)
        oHLayoutMainTax.addWidget(self.oLabelMainTax)
        oHLayoutMainTax.addWidget(self.oComboMainTax)
        oHLayoutLatName.addWidget(self.oLabelLatName)
        oHLayoutLatName.addWidget(self.oLineEditLatName)
        oHLayoutAuthor.addWidget(self.oLabelAuthor)
        oHLayoutAuthor.addWidget(self.oLineEditAuthor)
        oHLayoutEnName.addWidget(self.oLabelEnName)
        oHLayoutEnName.addWidget(self.oLineEditEnName)
        oHLayoutLocalName.addWidget(self.oLabelLocalName)
        oHLayoutLocalName.addWidget(self.oLineEditLocaleName)
        oHLayoutSynonyms.addWidget(self.oLabelSynonyms)
        oHLayoutSynonyms.addWidget(self.oTextEditSynonyms)
        oHLayoutAuthors.addWidget(self.oLabelAuthors)
        oHLayoutAuthors.addWidget(self.oTextEditAuthors)
        oVLayout.addLayout(oHLayoutTaxLevel)
        oVLayout.addLayout(oHLayoutMainTax)
        oVLayout.addLayout(oHLayoutLatName)
        oVLayout.addLayout(oHLayoutAuthor)
        oVLayout.addLayout(oHLayoutEnName)
        oVLayout.addLayout(oHLayoutLocalName)
        oVLayout.addLayout(oHLayoutSynonyms)
        oVLayout.addLayout(oHLayoutAuthors)
        oVLayout.addLayout(self.oHLayoutButtons)
        self.setLayout(oVLayout)

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
        sFileName = self.oTextFiled.text()
        self.oConfigProgram.set_config_value('DB', 'filepath', sFileName)


class NewTaxonDialog(TaxonDialog):
    def __init__(self, oParent=None):
        super(NewTaxonDialog, self).__init__(oParent)

    def init_UI(self):
        self.setWindowTitle(_('Add new taxon to tree'))
        self.setModal(Qt.ApplicationModal)

        oVLayout = QVBoxLayout()
        self.oComboTaxLevel = HComboBox()
        self.oComboTaxLevel.set_label(_('Taxon level'))
        self.oComboTaxLevel.set_combo_list(
            self.create_tax_level_list('TaxonLevel'))
        self.oComboMainTax = HComboBox()
        self.oComboMainTax.set_label(_('Main Taxon'))
        self.oComboMainTax.set_combo_list(self.onCreateTaxonList())
        self.oLineEditLatName = HLineEdit()
        self.oLineEditLatName.set_text(_('Latin name'))
        self.oLineEditAuthor = HLineEdit()
        self.oLineEditAuthor.set_text(_('Author & year'))
        self.oLineEditEnName = HLineEdit()
        self.oLineEditEnName.set_text(_('English name'))
        self.oLineEditLocaleName = HLineEdit()
        self.oLineEditLocaleName.set_text(_('Local name'))
        self.oTextEditSynonyms = HTextEdit()
        self.oTextEditSynonyms.set_text(_('Synonyms'))
        self.oTextEditAuthors = HTextEdit()
        self.oTextEditAuthors.set_text(_('Authors'))

        oVLayout.addLayout(self.oComboTaxLevel)
        oVLayout.addLayout(self.oComboMainTax)
        oVLayout.addLayout(self.oLineEditLatName)
        oVLayout.addLayout(self.oLineEditAuthor)
        oVLayout.addLayout(self.oLineEditEnName)
        oVLayout.addLayout(self.oLineEditLocaleName)
        oVLayout.addLayout(self.oTextEditSynonyms)
        oVLayout.addLayout(self.oTextEditAuthors)
        oVLayout.addLayout(self.oHLayoutButtons)
        self.setLayout(oVLayout)

    def create_tax_level_list(self, sDB):
        oCursor = self.oConnector.sql_get_all(sDB)
        lValues = []
        for tRow in oCursor:
            lValues.append(tRow[2])
        return lValues

    def onClickApply(self):
        sTaxLevel = self.oComboTaxLevel.get_text()
        sMainTax = self.oComboMainTax.get_text().split()[1]
        sLatName = self.oLineEditLatName.get_text()
        sAuthor = self.oLineEditAuthor.get_text()
        sEnName = self.oLineEditEnName.get_text()
        sLocalName = self.oLineEditLocaleName.get_text()
        sSynonyms = self.oTextEditSynonyms.get_text()
        sAuthors = self.oTextEditAuthors.get_text()

        iTaxLevel = self.oConnector.sql_get_id('TaxonLevel', 'id_taxon_level',
                                               'level_name', (sTaxLevel,))
        iMainTax = self.oConnector.sql_get_id('TaxonStructure', 'id_taxon',
                                              'taxon_name', (sMainTax,))
        bTaxonName = self.oConnector.sql_get_id('TaxonStructure', 'id_taxon',
                                                'taxon_name', (sLatName,))

        bOk = False
        if bTaxonName:
            bOk = warning_taxon_exist(sLatName)

        lSynonyms = []
        lAuthors = []
        if sSynonyms:
            lSynonyms.extend(text_to_list(sSynonyms))
        if sAuthors:
            lAuthors.extend(text_to_list(sAuthor))
        if len(lSynonyms) < len(lAuthors):
            bOk = warning_synonym_more()

        if not bTaxonName or bOk:
            tTaxValues = (iTaxLevel, iMainTax, sLatName, sEnName, sLocalName,)
            self.save_taxon(tTaxValues, sLatName, sAuthor, lSynonyms, lAuthors)

            self.oComboTaxLevel.set_text('')
            self.oComboMainTax.set_text('')
            self.oLineEditLatName.set_text('')
            self.oLineEditAuthor.set_text('')
            self.oLineEditEnName.set_text('')
            self.oLineEditLocaleName.set_text('')
            self.oTextEditSynonyms.set_text('')
            self.oTextEditAuthors.set_text('')

    def save_taxon(self, tTaxonValues, sLatName, sAuthor, lSynonyms, lAuthors):
        sColumns = 'taxon_level, id_main_taxon, taxon_name, taxon_name_en, ' \
                   'taxon_name_ru'

        iTaxName = self.oConnector.insert_row('TaxonStructure',
                                              sColumns, tTaxonValues)
        self.oConnector.insert_row('TaxonOtherNames',
                                   'id_taxon, taxon_name, authors',
                                   (iTaxName, sLatName, sAuthor))

        if lSynonyms:
            lValues = zip_taxon_lists(iTaxName, lSynonyms, lAuthors)
            for tValues in lValues:
                self.oConnector.insert_row('TaxonOtherNames',
                                           'id_taxon, taxon_name, authors',
                                           tValues)
        self.oComboMainTax.clear()
        self.oComboMainTax.addItems(self.onCreateTaxonList())


if __name__ == '__main__':
    pass
