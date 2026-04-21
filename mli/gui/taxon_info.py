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
from PyQt6.QtWidgets import QTextBrowser

from mli.lib.str import HTMLDoc


class TaxonBrowser(QTextBrowser):
    def __init__(self, oConnector, sSciName):
        super().__init__()

        self.oConnector = oConnector
        self.sSciName = sSciName
        self.sNoData = _('Нет данных.')
        self.oHTML = HTMLDoc()

        self.initUI()

    def initUI(self):
        self.setOpenExternalLinks(True)
        self.setText(self.get_page_taxon_info())

    def get_page_taxon_info(self):
        iStatusID, sStatusName = \
            self.oConnector.get_status_taxon(self.sSciName)
        iLevelID, sRankName = self.oConnector.get_taxon_rank(self.sSciName)
        iTaxonID = self.oConnector.get_taxon_id(self.sSciName)
        sName, sAuthor = self.oConnector.get_name_author(iTaxonID)[0]
        self.oHTML.set_title_doc(sRankName, sName, sAuthor)

        if iStatusID != 1:
            sMainName, sMainAuthor = self.oConnector.get_main_taxon(iTaxonID)
            self.oHTML.set_is_synonym(sName, sAuthor, sMainName, sMainAuthor)

        self.oHTML.set_title_chart(_('Статус:'))
        self.oHTML.set_string(sStatusName)

        if iStatusID == 1:
            self.get_accepted_taxon_info(iTaxonID, sStatusName)

        self.get_taxon_db_links(iTaxonID, iLevelID, sName)
        self.get_taxon_ref_links(iTaxonID)

        return self.oHTML.get_doc()

    def get_accepted_taxon_info(self, iTaxonID, sStatusName):
        self.oHTML.set_title_chart(_('Синонимы:'))
        tSynonyms = self.oConnector.get_synonyms(iTaxonID)
        self.get_name(tSynonyms)

        self.oHTML.set_title_chart(_("Описание:"))
        self.oHTML.set_no_data(self.sNoData)

        self.oHTML.set_title_chart(_('Дочерние таксоны:'))
        tChildren = \
            self.oConnector.get_taxon_children(iTaxonID, sStatusName)
        self.get_name(tChildren)

    def get_name(self, tValues):
        if tValues:
            for sRank, sNameSyn, sAuthor in tValues:
                self.oHTML.set_rang_name(sRank, sNameSyn, sAuthor)
        else:
            self.oHTML.set_no_data(self.sNoData)

    def get_taxon_db_links(self, iTaxonID, iLevelID, sName):
        tTaxonDB = self.oConnector.get_taxon_db_link(iTaxonID)
        self.oHTML.set_title_chart(_("Ссылки в других базах данных:"))
        if tTaxonDB:
            for sSource, sLink, sIndex in tTaxonDB:
                self.oHTML.set_link(sSource, sLink, sIndex)
        else:
            self.oHTML.set_no_data(self.sNoData)

        if iLevelID <= 21:
            sLink = r'https://lichenportal.org/cnalh/taxa/index.php?taxon='
            self.oHTML.set_link('LichenPortal', sLink, sName)

    def get_taxon_ref_links(self, iTaxonID):
        self.oHTML.set_title_chart(_('Ссылки на источники:'))
        self.oHTML.set_no_data(self.sNoData)


if __name__ == '__main__':
    pass
