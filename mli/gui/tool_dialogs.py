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
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QPushButton, QVBoxLayout

from mli.gui.dialog_elements import HComboBox, VComboBox, HLineEdit, \
    VLineEdit, VTextEdit
from mli.gui.message_box import warning_lat_name, warning_synonym_exist, \
    warning_synonym_more, warning_this_exist
from mli.lib.config import ConfigProgram
from mli.lib.sql import SQL
from mli.lib.str import text_to_list


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


class AToolDialogButtons(QDialog):
    """An abstract class that creates a block of Apply, OK, Cancel buttons and
    reserves action methods for them."""

    def __init__(self, oParent=None):
        """ Initiating a class. """
        super(AToolDialogButtons, self).__init__(oParent)
        oConfigProgram = ConfigProgram()
        sDBFile = oConfigProgram.get_config_value('DB', 'filepath')
        self.oConnector = SQL(sDBFile)
        self.init_UI_button_block()
        self.connect_actions_button()

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

    def connect_actions_button(self):
        """ The method of linking signals and button slots. """
        self.oButtonApply.clicked.connect(self.onClickApply)
        self.oButtonOk.clicked.connect(self.onClickOk)
        self.oButtonCancel.clicked.connect(self.onCancel)

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


class ASubstrateDialog(AToolDialogButtons):
    """An abstract class that creates fields and functionality common to all
    dialogs of the substrate. """

    def __init__(self, oParent=None):
        """ Initiating a class. """
        super(ASubstrateDialog, self).__init__(oParent)
        self.init_UI_failed()

    def init_UI_failed(self):
        """ initiating a dialog view """
        self.oComboSubstrateLevel = HComboBox(_('Old substrate name:'))
        self.oLineEditSubstrate = HLineEdit(_('New substrate name:'))

    def onClickApply(self):
        """ Realization of the abstract method of the parent class. """
        sSubstrate = self.oLineEditSubstrate.get_text()
        bSubstrate = self.oConnector.sql_get_id('Substrate',
                                                'id_substrate',
                                                'substrate_name',
                                                (sSubstrate,))

        if not bSubstrate:
            self.save_((sSubstrate,))
            self.oLineEditSubstrate.set_text('')

    def save_(self, tValues):
        """ Method for saving information about the substrate in the database.

        :param tValues: Type of substrate to be entered into the database.
        :type tValues: tuple
        """
        self.oConnector.insert_row('Substrate', 'substrate_name', tValues)


class ATaxonDialog(AToolDialogButtons):
    """ Creates abstract class that contain common elements for Dialogs of
        taxon."""

    def __init__(self, oParent=None):
        """ Initiating a class. """
        super(ATaxonDialog, self).__init__(oParent)
        self.init_UI_failed()
        self.fill_combobox()
        self.connect_actions()

    def init_UI_failed(self):
        """ initiating a dialog view """
        self.oComboMainTax = VComboBox(_('Main Taxon:'))
        self.oComboTaxLevel = VComboBox(_('Taxon level:'), 150)
        self.oLineEditLatName = VLineEdit(_('Latin name:'))
        self.oLineEditAuthor = HLineEdit(_('Author:'), 145)
        self.oLineEditYear = HLineEdit(_('Year:'), 50)
        self.oLineEditLocaleName = VLineEdit(_('Local name:'))
        self.oTextEditSynonyms = VTextEdit(_('Synonyms:'), 250)
        self.oTextEditAuthors = VTextEdit(_('Authors:'), 145)
        self.oTextEditYears = VTextEdit(_('Years:'), 50)
        self.oComboTaxNames = VComboBox(_('Taxon name: '))
        self.oComboBoxSynonym = VComboBox(_('Synonym:'))

        self.oHLayoutAuthor = QHBoxLayout()
        self.oHLayoutAuthor.addLayout(self.oLineEditAuthor)
        self.oHLayoutAuthor.addStretch(5)
        self.oHLayoutAuthor.addLayout(self.oLineEditYear)

        oVLayoutLevel = QVBoxLayout()
        oVLayoutLevel.addLayout(self.oComboTaxLevel)
        oVLayoutLevel.addStretch(1)

        oVLayoutTaxon = QVBoxLayout()
        oVLayoutTaxon.addLayout(self.oLineEditLatName)
        oVLayoutTaxon.addLayout(self.oHLayoutAuthor)
        oVLayoutTaxon.addLayout(self.oLineEditLocaleName)

        self.oHLayoutTaxon = QHBoxLayout()
        self.oHLayoutTaxon.addLayout(oVLayoutLevel)
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
                   f'WHERE TaxonLevel.level_name="{sTaxonLevel}" ' \
                   f'AND id_status=1 ' \
                   'ORDER BY Taxon.taxon_lat_name ASC;'
            oCursor = self.oConnector.execute_query(sSQL)

            for tRow in oCursor:
                lValues.append(f'({tRow[0]}) {tRow[1]}')
        return lValues

    def fill_combobox(self):
        """ Fills the fields with the drop-down list during the first
        initialization and after applying the Apply button."""
        lTaxonLevel = self.create_level_list(bGetAll=True)
        self.oComboMainTax.set_combo_list(self.create_taxon_list(lTaxonLevel))
        self.oComboTaxLevel.set_combo_list(lTaxonLevel)
        self.oComboTaxLevel.set_text(lTaxonLevel[1])
        self.oComboTaxNames.set_combo_list(self.create_taxon_list(lTaxonLevel))

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

    def check_synonyms(self, sTaxName, sSynonyms, sAuthors, sYears):
        """ Checks if there are such synonyms in the list of taxon and if the
        number of synonyms matches the number of authors.

        :param sTaxName: Latin name of taxon.
        :type sTaxName: str
        :param sSynonyms: A list of synonyms.
        :type sSynonyms: str
        :param sAuthors: A author list of synonyms.
        :type sAuthors: str
        :param sYears: A list when the author named the taxon.
        :type sYears: str
        :return:Returns a dictionary in the form of a taxon name, a list of
         synonyms, and a list of authors, or False
        :rtype: dict[int, list[str], list[str], list[str]] | bool
        """
        iTaxName = self.oConnector.sql_get_id('Taxon', 'id_taxon',
                                              'taxon_lat_name', (sTaxName,))
        bOk = True
        lSynonyms = []
        if sSynonyms:
            lSynonyms.extend(text_to_list(sSynonyms))
            for sSynonym in lSynonyms:
                bExist = self.oConnector.sql_get_id('Taxon',
                                                    'id_taxon',
                                                    'taxon_lat_name',
                                                    (sSynonym,))
                if bExist:
                    bOk = warning_synonym_exist(sTaxName)

        lAuthors, lYears = [], []
        if sAuthors:
            lAuthors.extend(text_to_list(sAuthors))
        if sYears:
            lYears.extend(text_to_list(sYears))
        if len(lSynonyms) < len(lAuthors):
            bOk = warning_synonym_more()

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
            iStatus = self.oConnector.sql_get_id('TaxonStatus',
                                                 'id_status',
                                                 'status_name',
                                                 ('ACCEPTED',))
            lValues = zip_taxon_lists(iTaxName, lSynonyms,
                                      lAuthors, lYears, iStatus)
            self.oConnector.insert_row('Taxon',
                                       'id_level, id_main_taxon, '
                                       'taxon_lat_name, author, year'
                                       'id_status',
                                       lValues)


class AddSynonymsDialog(ATaxonDialog):
    def __init__(self, oParent=None):
        """ Initiating a class. """
        super(AddSynonymsDialog, self).__init__(oParent)
        self.init_UI()

    def init_UI(self):
        """ Creating a dialog window. """
        self.setWindowTitle(_('Add new synonyms to taxon name'))
        self.setModal(Qt.ApplicationModal)

        oVLayout = QVBoxLayout()
        oVLayout.addLayout(self.oComboTaxNames)
        oVLayout.addLayout(self.oHLayoutSynonyms)
        oVLayout.addLayout(self.oHLayoutButtons)
        self.setLayout(oVLayout)

    def onClickApply(self):
        """ Actions to be taken when adding a new taxon synonyms. """
        sTaxName = self.oComboTaxNames.get_text().split(') ')[1]
        sSynonyms = self.oTextEditSynonyms.get_text()
        sAuthors = self.oTextEditAuthors.get_text()
        sYears = self.oTextEditYears.get_text()
        dSynonyms = self.check_synonyms(sTaxName, sSynonyms, sAuthors, sYears)
        if not dSynonyms:
            return

        self.save_synonyms(dSynonyms['tax_name'],
                           dSynonyms['list_syn'],
                           dSynonyms['list_auth'],
                           dSynonyms['list_year'])

        self.oTextEditSynonyms.clear_text()
        self.oTextEditAuthors.clear_text()
        self.oTextEditYears.clear_text()


class EditSynonymDialog(ATaxonDialog):
    def __init__(self, oParent=None):
        """ Initiating a class. """
        super(EditSynonymDialog, self).__init__(oParent)

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
        oCursor = self.oConnector.select('TaxonSynonym',
                                         'id_other_names, taxon_name,'
                                         ' author, year',
                                         'id_taxon, taxon_name',
                                         (self.iTaxonID, sSynonym,))
        self.lSynonym = oCursor.fetchone()

    def onCurrentTaxonNamesChanged(self, sTaxonName):
        sValue = sTaxonName.split(') ')[1]
        self.iTaxonID = self.oConnector.sql_get_id('Taxon', 'id_taxon',
                                                   'taxon_lat_name',
                                                   (sValue,))
        oCursor = self.oConnector.get_synonym_id(self.iTaxonID)
        tSynonyms = oCursor.fetchall()
        lSynonyms = []
        for lRow in tSynonyms:
            lSynonyms.append(lRow[0])

        self.oComboBoxSynonym.set_combo_list(lSynonyms)

    def save_(self):
        pass


class EditTaxonDialog(ATaxonDialog):
    def __init__(self, oParent=None):
        """ Initiating a class. """
        super(EditTaxonDialog, self).__init__(oParent)

        self.iOldMainTaxonID = None
        self.sOldMainTaxonName = None
        self.iOldTaxonLevelID = None
        self.sOldTaxonLevelName = None
        self.iOldTaxonID = None
        self.sOldAuthor = None
        self.sOldYear = None
        self.sOldTaxonLocalName = None
        self.iOldOtherNameID = None
        self.iOldOtherName = None
        self.iOldOtherNameAuthor = None
        self.iOldOtherNameYear = None

        self.init_UI()

    def init_UI(self):
        """ Creating a dialog window. """
        self.setWindowTitle(_('Editing synonyms of a taxon'))
        self.setModal(Qt.ApplicationModal)

        oVLayout = QVBoxLayout()
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
        sOldTaxonName = self.oComboTaxNames.get_text()
        sMainTaxon = self.oComboMainTax.get_text()
        sTaxonLevel = self.oComboTaxLevel.get_text()
        sLatName = self.oLineEditLatName.get_text()
        sAuthor = self.oLineEditAuthor.get_text()
        sYear = self.oLineEditYear.get_text()
        sLocaleName = self.oLineEditLocaleName.get_text()

        if not sLatName and not sLatName.isalpha() and not sLatName.isascii():
            warning_lat_name()
            return

        if sOldTaxonName != sLatName:
            self.save_('taxon_lat_name', sLatName, self.iOldTaxonID)
        sMainTaxon = sMainTaxon.split()[1]

        if sMainTaxon != self.sOldMainTaxonName:
            iMainTaxonID = self.oConnector.sql_get_id('Taxon', 'id_taxon',
                                                      'taxon_lat_name',
                                                      (sMainTaxon,))
            self.save_('id_main_taxon', iMainTaxonID, self.iOldTaxonID)

        if sTaxonLevel != self.sOldTaxonLevelName:
            iLevelID = self.oConnector.sql_get_id('TaxonLevel', 'id_level',
                                                  'level_name', (sTaxonLevel,))
            self.save_('id_level', iLevelID, self.iOldTaxonID)

        if sAuthor != self.sOldAuthor:
            self.save_('author', sAuthor, self.iOldTaxonID)

        if sYear != self.sOldYear:
            self.save_('year', sYear, self.iOldTaxonID)

        if sLocaleName != self.sOldTaxonLocalName:
            self.save_('taxon_local_name', sLocaleName, self.iOldTaxonID)

    def onCurrentTaxonNamesChanged(self, sTaxonName):
        sName = sTaxonName.split(') ')[1]
        sSQL = "SELECT Taxon.id_main_taxon, MTaxonLevel.level_name, " \
               "MainTaxon.taxon_lat_name AS Main_Taxon_name, " \
               "Taxon.id_level, TaxonLevel.level_name, Taxon.id_taxon, " \
               "Taxon.taxon_lat_name, Taxon.author, Taxon.year, " \
               "Taxon.taxon_local_name " \
               "FROM Taxon " \
               "JOIN Taxon MainTaxon " \
               "ON MainTaxon.id_taxon=Taxon.id_main_taxon " \
               "JOIN TaxonLevel ON Taxon.id_level=TaxonLevel.id_level " \
               "JOIN TaxonLevel MTaxonLevel " \
               "ON MTaxonLevel.id_level=MainTaxon.id_level " \
               f"WHERE Taxon.taxon_lat_name='{sName}'"
        oCursor = self.oConnector.execute_query(sSQL)

        tRow = oCursor.fetchone()
        self.iOldMainTaxonID = tRow[0]
        sOldMainTaxonLevelName = tRow[1]
        self.sOldMainTaxonName = tRow[2]
        self.iOldTaxonLevelID = tRow[3]
        self.sOldTaxonLevelName = tRow[4]
        self.iOldTaxonID = tRow[5]
        sOldTaxonLatName = tRow[6]
        self.sOldAuthor = tRow[7]
        self.sOldYear = tRow[8]
        self.sOldTaxonLocalName = tRow[9]

        sMainTaxon = f'({sOldMainTaxonLevelName}) {self.sOldMainTaxonName}'
        self.oComboMainTax.set_text(sMainTaxon)
        self.oComboTaxLevel.set_text(self.sOldTaxonLevelName)
        self.oLineEditLatName.set_text(sOldTaxonLatName)
        self.oLineEditAuthor.set_text(self.sOldAuthor)
        self.oLineEditLocaleName.set_text(self.sOldTaxonLocalName)

    def save_(self, sSetCol, sUpdate, sWhere,
              sTable='Taxon', sWhereCol='id_taxon'):

        tValues = (sUpdate, sWhere,)
        self.oConnector.update(sTable, sSetCol, sWhereCol, tValues)


class NewTaxonDialog(ATaxonDialog):
    """ Dialog window which adds information on new taxon. """

    def __init__(self, oParent=None):
        """ Initiating a class. """
        super(NewTaxonDialog, self).__init__(oParent)
        self.init_UI()

    def init_UI(self):
        """ Creating a dialog window. """
        self.setWindowTitle(_('Add new taxon to tree'))
        self.setModal(Qt.ApplicationModal)

        oVLayout = QVBoxLayout()
        oVLayout.addLayout(self.oComboMainTax)
        oVLayout.addLayout(self.oHLayoutTaxon)
        oVLayout.addLayout(self.oHLayoutSynonyms)
        oVLayout.addLayout(self.oHLayoutButtons)
        self.setLayout(oVLayout)

    def onClickApply(self):
        """ Actions to be taken when adding a new taxon. """
        sTaxLevel = self.oComboTaxLevel.get_text()
        sMainTax = self.oComboMainTax.get_text().split()[1]
        sLatName = self.oLineEditLatName.get_text()
        sAuthor = self.oLineEditAuthor.get_text()
        iYear = self.oLineEditYear.get_text()
        sLocalName = self.oLineEditLocaleName.get_text()
        sSynonyms = self.oTextEditSynonyms.get_text()
        sAuthors = self.oTextEditAuthors.get_text()
        sYears = self.oTextEditYears.get_text()

        if not sLatName and sLatName.isalpha() and sLatName.isascii():
            warning_lat_name()
            return

        bTaxonName = self.oConnector.sql_get_id('Taxon', 'id_taxon',
                                                'taxon_lat_name', (sLatName,))

        if sLatName and bTaxonName:
            warning_this_exist(_('taxon name'), sLatName)
            return

        if sLatName and not bTaxonName:
            iTaxLevel = self.oConnector.sql_get_id('TaxonLevel', 'id_level',
                                                   'level_name', (sTaxLevel,))
            iMainTax = self.oConnector.sql_get_id('Taxon', 'id_taxon',
                                                  'taxon_lat_name',
                                                  (sMainTax,))
            tTaxValues = (iTaxLevel, iMainTax, sLatName,
                          sAuthor, iYear, sLocalName,)
            dSynonyms = self.check_synonyms(sLatName, sSynonyms, sAuthors,
                                            sYears)
            self.save_(tTaxValues, dSynonyms['list_syn'],
                       dSynonyms['list_auth'], dSynonyms['list_year'])

            self.clean_field()
            self.fill_combobox()

    def save_(self, tTaxonValues, lSynonyms, lAuthors, lYears):
        """ Saving information about the taxon in the database.

        :param tTaxonValues: Information on taxon in view: index of a Taxon
            level, a Main taxon, a Latin name, an Author, a Year, a Local name.
        :type tTaxonValues: tuple[str]
        :param lSynonyms: A list of taxon synonyms.
        :type lSynonyms: list[str]
        :param lAuthors: A list of authors of taxon synonyms.
        :type lAuthors: list[str]
        :param lYears:A list of years when the author named the taxon.
        :type lYears: list[str]
        """
        sColumns = 'id_level, id_main_taxon, taxon_lat_name, ' \
                   'author, year, taxon_local_name'
        iTaxonName = self.oConnector.insert_row('Taxon', sColumns,
                                                tTaxonValues)
        if lSynonyms:
            self.save_synonyms(iTaxonName, lSynonyms, lAuthors, lYears)


class EditSubstrateDialog(ASubstrateDialog):
    """ Dialog window which allows user to change substrate type. """

    def __init__(self, oParent=None):
        """ Initiating a class. """
        super(EditSubstrateDialog, self).__init__(oParent)
        self.init_UI()

    def init_UI(self):
        """ Creating a dialog window. """
        self.setWindowTitle(_('Edit substrate...'))
        self.setModal(Qt.ApplicationModal)

        self.oComboSubstrateLevel.set_combo_list(
            sorted(self.create_substrate_list('Substrate')))

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
        lValues = []
        for tRow in oCursor:
            lValues.append(tRow[1])
        return lValues


class NewSubstrateDialog(ASubstrateDialog):
    """ Dialog window which adds new substrate type. """

    def __init__(self, oParent=None):
        """ Initiating a class. """
        super(NewSubstrateDialog, self).__init__(oParent)
        self.init_UI()

    def init_UI(self):
        """ Creating a dialog window. """
        self.setWindowTitle(_('Add new substrate...'))
        self.setModal(Qt.ApplicationModal)

        oVLayout = QVBoxLayout()
        oVLayout.addLayout(self.oLineEditSubstrate)
        oVLayout.addLayout(self.oHLayoutButtons)
        self.setLayout(oVLayout)


if __name__ == '__main__':
    pass
