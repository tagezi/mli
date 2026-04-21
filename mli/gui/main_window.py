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
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QComboBox, QCompleter, \
    QInputDialog, QMainWindow, QTextBrowser

from mli.gui.color_dialogs import NewColor, EditColor
from mli.gui.file_dialogs import OpenFileDialog
from mli.gui.substract_dialogs import EditSubstrateDialog, NewSubstrateDialog
from mli.gui.help_dialog import About
from mli.gui.setting_dialog import SettingDialog
from mli.gui.tab_widget import CentralTabWidget
from mli.gui.table_widget import TableWidget
from mli.gui.taxon_dialogs import EditTaxonDialog, EditSynonymDialog,\
    NewTaxonDialog
from mli.gui.taxon_info import TaxonBrowser

from mli.lib.config import ConfigProgram
from mli.lib.sql import SQL, check_connect_db
from mli.lib.str import str_get_file_patch, str_get_path


class MainWindow(QMainWindow):
    def __init__(self, sPath):
        super().__init__()

        self.sPathApp = sPath
        oConfigProgram = ConfigProgram(self.sPathApp)
        sBasePath = oConfigProgram.sDir
        sDBPath = oConfigProgram.get_config_value('DB', 'db_path')
        sDBDir = oConfigProgram.get_config_value('DB', 'db_dir')
        if not sDBPath:
            sDBFile = oConfigProgram.get_config_value('DB', 'db_file')
            sDBPath = str_get_file_patch(sBasePath, sDBDir)
            sDBPath = str_get_file_patch(sDBPath, sDBFile)

        self.oConnector = SQL(sDBPath)
        check_connect_db(self.oConnector, sBasePath, sDBDir)

        self.setWindowTitle(_('Manual Lichen identification'))
        self.oCentralWidget = CentralTabWidget(self)

        dKeyTable = {_('Имя'): [''],
                     _('Жизненная форма'): [''],
                     _('Цвет талома'): ['']}
        oTableWidget = TableWidget(dKeyTable,
                                   len(dKeyTable['Имя']), len(dKeyTable))

        self.oCentralWidget.add_tab(oTableWidget, _('Простая идентификация'))
        self.create_actions()
        self.connect_actions()
        self.set_menu_bar()
        self.setCentralWidget(self.oCentralWidget)
        self.onSetStatusBarMessage()

        self.showMaximized()

    def create_actions(self):
        """ Method collect all actions which can do from GUI of program. """
        # File menu
        self.oOpenDB = QAction(_('Открыть базу данных...'), self)
        self.oPrint = QAction(_('Печать...'))
        self.oSetting = QAction(_('Настройки...'))
        self.oExitAct = QAction(QIcon.fromTheme('SP_exit'), _('Выход'), self)
        self.oExitAct.setShortcut('Ctrl+Q')
        self.oExitAct.setStatusTip(_('Закрыть приложение'))

        # Edit
        self.oUndo = QAction(_('Назад'), self)
        self.oUndo.setShortcut('Ctrl+Z')
        self.oRedo = QAction(_('Повтор'), self)
        self.oRedo.setShortcut('Ctrl+Z')
        self.oFind = QAction(_('Найти...'), self)
        self.oFind.setShortcut('Ctrl+F')
        self.oNewTaxon = QAction(_('Новый таксон...'))
        self.oEditTaxon = QAction(_('Редактировать таксон...'))
        self.oEditSynonym = QAction(_('Редактировать синоним таксона...'))
        self.oNewColor = QAction(_('Новый цвет...'))
        self.oNewColorsTaxon = QAction(_('Новый цвет таксона...'))
        self.oEditColor = QAction(_('Редактировать цвет...'))
        self.oEditColorsTaxon = QAction(_('Редактировать цвет таксона...'))
        self.oNewSubstrate = QAction(_('Новый субстрат...'))
        self.oEditSubstrate = QAction(_('Редактировать субстрат...'))

        # Tools
        self.oTaxonInfo = QAction(_('Информация о таксоне...'))

        # Help
        self.oOpenHelp = QAction(_('Помощь'), self)
        self.oAbout = QAction(_('О приложении'), self)

    def set_menu_bar(self):
        """ Method create Menu Bar on main window of program GUI. """
        oMenuBar = self.menuBar()

        # Create file menu
        oFileMenu = oMenuBar.addMenu(_('&Файл'))
        oFileMenu.addAction(self.oOpenDB)
        oFileMenu.addSeparator()
        oFileMenu.addAction(self.oPrint)
        oFileMenu.addSeparator()
        oFileMenu.addAction(self.oSetting)
        oFileMenu.addSeparator()
        oFileMenu.addAction(self.oExitAct)

        # Create Edit menu
        oEdit = oMenuBar.addMenu(_('&Правка'))
        oEdit.addAction(self.oUndo)
        oEdit.addAction(self.oRedo)
        oEdit.addSeparator()
        oTaxa = oEdit.addMenu(_('Таксон'))
        oTaxa.addAction(self.oNewTaxon)
        oTaxa.addAction(self.oEditTaxon)
        oTaxa.addAction(self.oEditSynonym)

        oColor = oEdit.addMenu(_('Цвет'))
        oColor.addAction(self.oNewColor)
        oColor.addAction(self.oEditColor)
        oEdit.addSeparator()
        oColor.addAction(self.oNewColorsTaxon)
        oColor.addAction(self.oEditColorsTaxon)

        oSubstrates = oEdit.addMenu(_('Субстрат'))
        oSubstrates.addAction(self.oNewSubstrate)
        oSubstrates.addAction(self.oEditSubstrate)
        oEdit.addSeparator()
        oEdit.addAction(self.oFind)

        # Create Tool menu
        oTools = oMenuBar.addMenu(_('&Инструменты'))
        oTools.addAction(self.oTaxonInfo)

        # Create Help menu
        oHelpMenu = oMenuBar.addMenu(_('&Помощь'))
        oHelpMenu.addAction(self.oOpenHelp)
        oHelpMenu.addAction(self.oAbout)

    def connect_actions(self):
        """ It is PyQt5 slots or other words is connecting from GUI element to
        method or function in program. """
        # Menu File
        self.oOpenDB.triggered.connect(self.onOpenDB)
        self.oSetting.triggered.connect(self.onOpenSetting)
        self.oExitAct.triggered.connect(QApplication.quit)

        # Menu Edit
        self.oNewTaxon.triggered.connect(self.onNewTaxon)
        self.oEditTaxon.triggered.connect(self.onEditTaxon)
        self.oEditSynonym.triggered.connect(self.onEditSynonym)
        self.oNewColor.triggered.connect(self.onNewColor)
        self.oEditColor.triggered.connect(self.onEditColor)
        self.oNewColorsTaxon.triggered.connect(self.onNewColorTaxon)
        self.oEditColorsTaxon.triggered.connect(self.onEditColorTaxon)
        self.oNewSubstrate.triggered.connect(self.onNewSubstrate)
        self.oEditSubstrate.triggered.connect(self.onEditSubstrate)

        # Tool menu
        self.oTaxonInfo.triggered.connect(self.onTaxonInfo)

        # Menu Help
        self.oAbout.triggered.connect(self.onDisplayAbout)

    def get_page_taxon_info(self, sTaxonName):
        return TaxonBrowser(self.oConnector, sTaxonName)

    def get_taxon_list(self):
        tTaxonList = self.oConnector.get_full_taxon_list()

        return [tRow[0] for tRow in tTaxonList]

    def onDisplayAbout(self):
        """ Method open dialog window with information about the program. """
        oAbout = About(self)
        oAbout.exec()

    def onOpenDB(self):
        pass

    def onOpenSetting(self):
        oSettingDialog = SettingDialog(self.oConnector, self.sPathApp, self)
        oSettingDialog.exec()

    def onEditColor(self):
        oEditColor = EditColor(self.oConnector, self)
        oEditColor.exec()

    def onEditColorTaxon(self):
        pass

    def onEditSubstrate(self):
        oEditSubstrate = EditSubstrateDialog(self.oConnector, self)
        oEditSubstrate.exec()

    def onEditSynonym(self):
        oEditSynonym = EditSynonymDialog(self.oConnector, self)
        oEditSynonym.exec()

    def onEditTaxon(self):
        oEditTaxonDialog = EditTaxonDialog(self.oConnector, self)
        oEditTaxonDialog.exec()

    def onNewColor(self):
        oNewColor = NewColor(self.oConnector, self)
        oNewColor.exec()

    def onNewColorTaxon(self):
        pass

    def onNewSubstrate(self):
        oNewSubstrate = NewSubstrateDialog(self.oConnector, self)
        oNewSubstrate.exec()

    def onNewTaxon(self):
        oNewTaxonDialog = NewTaxonDialog(self.oConnector, self)
        oNewTaxonDialog.exec()

    def onSetStatusBarMessage(self, sMassage='Ready'):
        """ Method create Status Bar on main window of program GUI. """
        self.statusBar().showMessage(sMassage)

    def onTaxonInfo(self):
        lTaxonList = self.get_taxon_list()
        oInputDialog = QInputDialog(self)
        oInputDialog.setWindowTitle('Выбор таксона.')
        oInputDialog.setLabelText(_('Список таксонов:'))
        oInputDialog.setComboBoxItems(lTaxonList)
        oInputDialog.setComboBoxEditable(True)
        oComboBox = oInputDialog.findChild(QComboBox)
        if oComboBox is not None:
            oCompleter = QCompleter(lTaxonList, oComboBox)
            oComboBox.setCompleter(oCompleter)
        ok = oInputDialog.exec()
        if ok:
            sTaxonName = oInputDialog.textValue()
            oTaxonInfo = self.get_page_taxon_info(sTaxonName)
            self.oCentralWidget.add_tab(oTaxonInfo, sTaxonName)
