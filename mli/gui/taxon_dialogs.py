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

from gettext import gettext as _
from itertools import zip_longest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout

from mli.gui.abstract_classes import AToolDialogButtons
from mli.gui.dialog_elements import VComboBox, HLineEdit, \
    VLineEdit, VTextEdit
from mli.gui.message_box import warning_no_synonyms, warning_lat_name,\
    warning_this_exist
from mli.lib.str import str_sep_name_taxon, str_text_to_list


def zip_taxon_lists(iTaxName, lSynonyms, lAuthors, lYears, iStatus):
    """ Creates a list of lists from the taxon ID, taxon synonyms, and synonym
    authors.

    :param iTaxName: The ID of the modern taxon name.
    :type iTaxName: int
    :param lSynonyms: A synonym list of the modern taxon name.
    :type lSynonyms: list
    :param lAuthors: An author of the synonym.
    :type lAuthors: list
    :param lYears: An year of publication new taxon name.
    :type lYears: list
    :param iStatus: index of status SYNONYM in database.
    :type iStatus: int
    :return: Return a list with elements of the form - taxon ID, taxon synonym,
     and synonym author.
    :rtype: list[int, str, str, int, int]
    """
    lTaxName, lStatus = [], []
    iNum = len(lSynonyms)
    while iNum:
        lTaxName.append(iTaxName)
        lStatus.append(iStatus)
        iNum -= 1

    return list(zip_longest(lTaxName, lSynonyms,
                            lAuthors, lYears, lStatus, fillvalue=''))


class ATaxonDialog(AToolDialogButtons):
    """ Creates abstract class that contain common elements for Dialogs of
        taxon."""

    def __init__(self, oConnector, oParent=None):
        """ Initiating a class. """
        super(ATaxonDialog, self).__init__(oConnector, oParent)
        self.init_UI_failed()
        self.fill_combobox()
        self.connect_actions()

    def init_UI_failed(self):
        """ initiating a dialog view """
        self.oComboStatus = VComboBox(_('Taxon status:'), 150)
        self.oComboMainTax = VComboBox(_('Main Taxon:'), 450)
        self.oComboTaxLevel = VComboBox(_('Taxon level:'), 150)
        self.oLineEditLatName = VLineEdit(_('Latin name:'))
        self.oLineEditAuthor = HLineEdit(_('Author:'), 145)
        self.oLineEditYear = HLineEdit(_('Year:'), 50)
        self.oLineEditLocaleName = VLineEdit(_('Local name:'))
        self.oTextEditSynonyms = VTextEdit(_('Synonyms:'), 250)
        self.oTextEditAuthors = VTextEdit(_('Authors:'), 145)
        self.oTextEditYears = VTextEdit(_('Years:'), 50)
        self.oComboTaxNames = VComboBox(_('Taxon name:'), 450)
        self.oComboBoxSynonym = VComboBox(_('Synonym:'), 150)

        self.oHLayoutAuthor = QHBoxLayout()
        self.oHLayoutAuthor.addLayout(self.oLineEditAuthor)
        self.oHLayoutAuthor.addStretch(5)
        self.oHLayoutAuthor.addLayout(self.oLineEditYear)

        self.oVLayoutLevel = QVBoxLayout()
        self.oVLayoutLevel.addLayout(self.oComboTaxLevel)
        self.oVLayoutLevel.addStretch(1)

        oVLayoutTaxon = QVBoxLayout()
        oVLayoutTaxon.addLayout(self.oLineEditLatName)
        oVLayoutTaxon.addLayout(self.oHLayoutAuthor)

        self.oHLayoutTaxon = QHBoxLayout()
        self.oHLayoutTaxon.addLayout(self.oVLayoutLevel)
        self.oHLayoutTaxon.addLayout(oVLayoutTaxon)

        self.oHLayoutSynonyms = QHBoxLayout()
        self.oHLayoutSynonyms.addLayout(self.oTextEditSynonyms)
        self.oHLayoutSynonyms.addLayout(self.oTextEditAuthors)
        self.oHLayoutSynonyms.addLayout(self.oTextEditYears)

    def connect_actions(self):
        """ Connects buttons with actions they should perform. """
        (self.oComboMainTax.get_widget()).currentTextChanged.connect(
            self.onCurrentMainTaxonChanged)

    def clean_field(self):
        """ Clears all fields after use. """
        self.oComboMainTax.clear_list()
        self.oComboTaxLevel.clear_list()
        self.oLineEditLatName.set_text('')
        self.oLineEditAuthor.set_text('')
        self.oLineEditYear.set_text('')
        self.oLineEditLocaleName.set_text('')
        self.oTextEditSynonyms.clear_text()
        self.oTextEditAuthors.clear_text()
        self.oTextEditYears.clear_text()
        self.oComboTaxNames.clear_list()

    def create_level_list(self, sTaxon='', bGetAll=None):
        """ Generates a list of taxon levels depending on a condition. At the
        first list initialization and using button Apply, all taxon levels are
        collected, at choosing Main taxon, only those that are below the
        selected taxon name.

        :param sTaxon: A name of main taxon.
        :type sTaxon: str
        :param bGetAll: It is needed to choose all levels.
        :type bGetAll: bool
        :return: list of taxon levels.
        :rtype: list[str]
        """
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

    def create_status_list(self):
        """ Creates a list of statuses.

        :return: list[str]
        """
        tRows = self.oConnector.get_statuses()
        lList = []
        for Row in tRows:
            lList.append(Row[1].lower())

        return lList

    def create_taxon_list(self):
        """ Creates a list of taxon names for further use in dialog elements.

        :return: A list in form - (Taxon Level) Taxon Name
        :type: list[str]
        """
        lValues = []
        tRows = self.oConnector.get_taxon_list('ACCEPTED')

        for tRow in tRows:
            if tRow[3]:
                lValues.append(f'({tRow[1]}) {tRow[2]}, {tRow[3]}')
            else:
                lValues.append(f'({tRow[1]}) {tRow[2]}')
        return lValues

    def fill_combobox(self):
        """ Fills the fields with the drop-down list during the first
        initialization and after applying the Apply button."""
        lTaxonLevel = self.create_level_list(bGetAll=True)
        self.oComboStatus.set_combo_list(self.create_status_list())
        self.oComboMainTax.set_combo_list(self.create_taxon_list())
        self.oComboTaxLevel.set_combo_list(lTaxonLevel)
        self.oComboTaxLevel.set_text(lTaxonLevel[1])
        self.oComboTaxNames.set_combo_list(self.create_taxon_list())

    def onCurrentMainTaxonChanged(self, sTaxon=''):
        """ The slot that should fire after the taxon name in the Main taxon
        drop-down list.

        :param sTaxon: A name of main taxon.
        :type sTaxon: str
        """
        # If the user enters the name by hand, there will be an error.
        if sTaxon.find("(") >= 0 and sTaxon.find(")") > 1:
            lTaxonLevel = self.create_level_list(sTaxon)
            self.oComboTaxLevel.clear_list()
            self.oComboTaxLevel.set_combo_list(lTaxonLevel)
            self.oComboTaxLevel.set_text(lTaxonLevel[0])

    def check_synonyms(self, sTaxName, sAuthor, sSynonyms, sAuthors, sYears):
        """ Checks if there are such synonyms in the list of taxon and if the
        number of synonyms matches the number of authors.

        :param sTaxName: Latin name of taxon.
        :type sTaxName: str
        :param sAuthor: An author of the taxon name.
        :type sAuthor: str
        :param sSynonyms: A list of synonyms.
        :type sSynonyms: str
        :param sAuthors: A author list of synonyms.
        :type sAuthors: str
        :param sYears: A list when the author named the taxon.
        :type sYears: str
        :return: Returns a dictionary in the form of a taxon name, a list of
            synonyms, and a list of authors, or False
        :rtype: dict[int, list[str], list[str], list[str]] | bool
        """
        iTaxName = self.oConnector.get_taxon_id(sTaxName, sAuthor)
        bOk = True
        lSynonyms = []
        if sSynonyms:
            lSynonyms.extend(str_text_to_list(sSynonyms))
            for sSynonym in lSynonyms:
                # TODO: Do search synonym by name and author
                bExist = self.oConnector.get_synonym_id(sSynonym, '')
                if bExist:
                    bOk = warning_this_exist('synonym', sTaxName)

        lAuthors, lYears = [], []
        if sAuthors:
            lAuthors.extend(str_text_to_list(sAuthors))
        if sYears:
            lYears.extend(str_text_to_list(sYears))

        if bOk:
            return {'tax_name': iTaxName,
                    'list_syn': lSynonyms,
                    'list_auth': lAuthors,
                    'list_year': lYears}
        return False

    def save_synonyms(self, iTaxName, lSynonyms, lAuthors, lYears):
        """ Save a list of synonyms.

        :param iTaxName: The ID of the modern taxon name.
        :type iTaxName: int
        :param lSynonyms: A synonym list of the modern taxon name.
        :type lSynonyms: list
        :param lAuthors: An author of the synonym.
        :type lAuthors: list
        :param lYears: A year when the author named taxon.
        :type lYears: list
        """
        if lSynonyms:
            iStatus = self.oConnector.get_status_id('SYNONYM')
            lValues = zip_taxon_lists(iTaxName, lSynonyms,
                                      lAuthors, lYears, iStatus)
            self.oConnector.insert_taxon(lValues)


class EditSynonymDialog(ATaxonDialog):
    def __init__(self, oConnector, oParent=None):
        """ Initiating a class. """
        super(EditSynonymDialog, self).__init__(oConnector, oParent)

        self.lSynonym = None
        self.iTaxonID = None

        self.init_UI()
        self.connect_actions()

    def init_UI(self):
        """ Creating a dialog window. """
        self.setWindowTitle(_('Editing an existing taxon'))
        self.setModal(Qt.ApplicationModal)

        self.oComboMainTaxonNames = VComboBox(_('New main taxon:'))
        self.oEditLineSynonym = VLineEdit(_('New synonym name:'))
        self.oLineEditAuthor = HLineEdit(_('Author:'), 145)
        self.oLineEditYear = HLineEdit(_('Year:'), 50)

        oVLayout = QVBoxLayout()
        oVLayout.addLayout(self.oComboTaxNames)
        oVLayout.addLayout(self.oComboBoxSynonym)
        oVLayout.addLayout(self.oComboMainTaxonNames)
        oVLayout.addLayout(self.oEditLineSynonym)
        oHLayout = QHBoxLayout()
        oHLayout.addLayout(self.oLineEditAuthor)
        oHLayout.addLayout(self.oLineEditYear)
        oVLayout.addLayout(oHLayout)
        oVLayout.addLayout(self.oHLayoutButtons)
        self.setLayout(oVLayout)

    def connect_actions(self):
        super().connect_actions()
        (self.oComboTaxNames.get_widget()).currentTextChanged.connect(
            self.onCurrentTaxonNamesChanged)
        self.oComboBoxSynonym.get_widget().currentTextChanged.connect(
            self.onCurrentSynonymChanged)

    def onClickApply(self):
        pass

    def onCurrentSynonymChanged(self, sSynonym):
        # TODO: Do search synonym
        oCursor = self.oConnector.select('TaxonSynonym',
                                         'id_other_names, taxon_name,'
                                         ' author, year',
                                         'id_taxon, taxon_name',
                                         (self.iTaxonID, sSynonym,))
        self.lSynonym = oCursor.fetchone()

    def onCurrentTaxonNamesChanged(self, sTaxonName):
        sTaxName, sAuthor = str_sep_name_taxon(sTaxonName)
        self.iTaxonID = self.oConnector.get_taxon_id(sTaxName, sAuthor)

        tSynonyms = self.oConnector.get_synonyms(self.iTaxonID)
        if not tSynonyms:
            warning_no_synonyms(f'{sTaxName}, {sAuthor}')
            return

        lSynonyms = []
        for lRow in tSynonyms:
            lSynonyms.append(lRow[0])

        self.oComboBoxSynonym.set_combo_list(lSynonyms)

    def save_(self):
        pass


class EditTaxonDialog(ATaxonDialog):
    def __init__(self, oConnector, oParent=None):
        """ Initiating a class. """
        super(EditTaxonDialog, self).__init__(oConnector, oParent)

        self.iOldMainTaxonID = None
        self.sOldMainTaxonName = None
        self.sOldMainTaxonAuthor = None
        self.iOldTaxonLevelID = None
        self.sOldTaxonLevelName = None
        self.iOldTaxonID = None
        self.sOldTaxonName = None
        self.sOldAuthor = None
        self.sOldYear = None

        self.init_UI()

    def init_UI(self):
        """ Creating a dialog window. """
        self.setWindowTitle(_('Editing of a taxon'))
        self.setModal(Qt.ApplicationModal)

        oVLayout = QVBoxLayout()
        oVLayout.addLayout(self.oComboStatus)
        oVLayout.addLayout(self.oComboTaxNames)
        oVLayout.addLayout(self.oComboMainTax)
        oVLayout.addLayout(self.oHLayoutTaxon)
        oVLayout.addLayout(self.oHLayoutButtons)
        self.setLayout(oVLayout)

    def connect_actions(self):
        super().connect_actions()
        (self.oComboTaxNames.get_widget()).currentTextChanged.connect(
            self.onCurrentTaxonNamesChanged)

    def onClickApply(self):
        sMainTaxon = self.oComboMainTax.get_text()
        sTaxonLevel = self.oComboTaxLevel.get_text()
        sLatName = self.oLineEditLatName.get_text()
        sAuthor = self.oLineEditAuthor.get_text()
        sYear = self.oLineEditYear.get_text()
        sStatus = self.oComboStatus.get_text()

        if not sLatName and not sLatName.isalpha() and not sLatName.isascii():
            warning_lat_name()
            return

        if self.sOldTaxonName != sLatName:
            self.save_('taxon_name', sLatName, self.iOldTaxonID)

        sMainTaxonName, sMainTaxonAuthor = str_sep_name_taxon(sMainTaxon)
        if sMainTaxon != self.sOldMainTaxonName:
            iMainTaxonID = self.oConnector.get_taxon_id(sMainTaxonName,
                                                        sMainTaxonAuthor)
            self.save_('id_main_taxon', iMainTaxonID, self.iOldTaxonID)

        if sTaxonLevel != self.sOldTaxonLevelName:
            iLevelID = self.oConnector.get_level_id('level_name', sTaxonLevel)
            self.save_('id_level', iLevelID, self.iOldTaxonID)

        if sAuthor != self.sOldAuthor:
            self.save_('author', sAuthor, self.iOldTaxonID)

        if sYear != self.sOldYear:
            self.save_('year', sYear, self.iOldTaxonID)

    def onCurrentTaxonNamesChanged(self, sTaxonName):
        sName, sAuthor = str_sep_name_taxon(sTaxonName)
        lRow = self.oConnector.get_taxon_info(sName, sAuthor)

        self.iOldMainTaxonID = lRow[0]
        sOldMainTaxonLevelName = lRow[1]
        self.sOldMainTaxonName = lRow[2]
        self.sOldMainTaxonAuthor = lRow[3]
        self.iOldTaxonLevelID = lRow[4]
        self.sOldTaxonLevelName = lRow[5]
        self.iOldTaxonID = lRow[6]
        self.sOldTaxonName = lRow[7]
        self.sOldAuthor = lRow[8]
        iOldYear = lRow[9]

        if not iOldYear:
            self.sOldYear = ''
        else:
            self.sOldYear = str(iOldYear)

        sMainTaxon = f'({sOldMainTaxonLevelName}) {self.sOldMainTaxonName}'
        if self.sOldMainTaxonAuthor:
            sMainTaxon = f'{sMainTaxon}, {self.sOldMainTaxonAuthor}'

        self.oComboMainTax.set_text(sMainTaxon)
        self.oComboTaxLevel.set_text(self.sOldTaxonLevelName)
        self.oLineEditLatName.set_text(self.sOldTaxonName)
        self.oLineEditAuthor.set_text(self.sOldAuthor)
        self.oLineEditYear.set_text(self.sOldYear)

    def save_(self, sSetCol, sUpdate, sWhere,
              sTable='Taxon', sWhereCol='id_taxon'):

        tValues = (sUpdate, sWhere,)
        self.oConnector.update(sTable, sSetCol, sWhereCol, tValues)


class NewTaxonDialog(ATaxonDialog):
    """ Dialog window which adds information on new taxon. """

    def __init__(self, oConnector, oParent=None):
        """ Initiating a class. """
        super(NewTaxonDialog, self).__init__(oConnector, oParent)
        self.init_UI()

    def init_UI(self):
        """ Creating a dialog window. """
        self.setWindowTitle(_('Add new taxon to tree'))
        self.setModal(Qt.ApplicationModal)

        oVLayout = QVBoxLayout()
        oVLayout.addLayout(self.oComboStatus)
        oVLayout.addLayout(self.oComboMainTax)
        oVLayout.addLayout(self.oHLayoutTaxon)
        oVLayout.addLayout(self.oHLayoutButtons)
        self.setLayout(oVLayout)

    def onClickApply(self):
        """ Actions to be taken when adding a new taxon. """
        sLevel = self.oComboTaxLevel.get_text()
        sMainTax, sMAuthor = str_sep_name_taxon(self.oComboMainTax.get_text())
        sName = self.oLineEditLatName.get_text()
        sAuthor = self.oLineEditAuthor.get_text()
        iYear = self.oLineEditYear.get_text()
        sStatus = self.oComboStatus.get_text().upper()

        if not sName and sName.isalpha() and sName.isascii():
            warning_lat_name()
            return

        bTaxonName = self.oConnector.get_taxon_id(sName, sAuthor)

        if sName and bTaxonName:
            warning_this_exist(_('taxon name'), f'<i>{sName}</i>, {sAuthor}')
            return

        if sName and not bTaxonName:
            iLevel = self.oConnector.get_level_id('level_name', sLevel)
            iStatus = self.oConnector.get_status_id(sStatus)
            iMainTax = self.oConnector.get_taxon_id(sMainTax, sMAuthor)
            tValues = (iLevel, iMainTax, sName, sAuthor, iYear, iStatus,)

            self.oConnector.insert_taxon(tValues)

            self.clean_field()
            self.fill_combobox()


if __name__ == '__main__':
    pass
