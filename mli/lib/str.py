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

"""
The module contains a collection of functions for solving routine tasks with
strings.
"""
from os.path import join, normcase, split
from gettext import gettext as _


def str_get_file_patch(sDir, sFile):
    """ Concatenates file path and file name based on OS rules.

        :param sDir: String with a patch to a file.
        :param sFile: String with a filename.
        :return: Patch to file based on OS rules.
        """
    return normcase(join(sDir, sFile))


def str_get_html_name(sCanonicalName, sAuthor=''):
    """ Inserts html tags into the taxon scientific name so that the canonical
     name is written in italics.

    :param sCanonicalName: A canonical name of the taxon.
    :type sCanonicalName: str
    :param sAuthor: Author(s) of the taxon.
    :type sAuthor: str
    :return: Formatted string.
    :rtype: str
    """
    if sAuthor:
        return f'<i>{sCanonicalName}</i>, {sAuthor}'
    else:
        return f'<i>{sCanonicalName}</i>'


def str_get_path(sFullFile):
    """ Splits a path to path and file name.

    :param sFullFile: Path with filename.
    :type sFullFile: str
    :return: The path to file.
    :rtype: str
    """
    return split(sFullFile)[0]


def str_sep_comma(sString):
    """ Separates a string by comma to list.

    :param sString: A string that needs to separate.
    :type sString: str
    :return: A separated string by comma.
    :rtype: list or None
    """
    if sString:
        return sString.split(', ')
    return


def str_sep_dot(sString):
    """ Separates a string by dot to list.

    :param sString: A string that needs to separate.
    :type sString: str
    :return: A separated string by dot.
    :rtype: list or None
    """
    if sString:
        return sString.split('.')
    return


def str_text_to_list(sString):
    if sString:
        return sString.split('\n')
    return


def str_sep_name_taxon(sString):
    """ Splits the string into taxon name and author, taking a string of the
        form '(rank) Taxon_name, authors'. It is permissible to indicate
        authors separated by commas, in brackets, using the '&' symbol.

    :param sString: A string that needed to separate.
    :type sString: str
    :return: A canonical form of taxon name and a string with the authors.
             Returns empty instead of author if no author was specified in
             the string.
    :rtype: list[str, str|None]
    """
    if sString.find('(') == 0:
        sString = ' '.join(sString.split(' ')[1:])
    return sString


class HTMLDoc:
    def __init__(self):
        """ Класс содержит методы разбора и оставления строк для формирования
        документа 'карточка таксона'

        **Члены класса**

        *lDoc*: Список строк для документа

        *dLinks*: словарь возможных ссылок на сторонние ресурсы
        """
        self.lDoc = []
        self.dLinks = {}

    def set_title_doc(self, sRank, sName, sAuthor):
        """ Форматирует заголовок документа из составляющих имени и ранга
         таксона.

        :param sRank: Ранг таксона
        :type sRank: str
        :param sName: Имя таксона без автора и года
        :type sName: str
        :param sAuthor: Авторство таксона
        :type sAuthor: str
        :return: none
        """
        self.lDoc.append(f'<h2>({sRank}) '
                         f'{str_get_html_name(sName, sAuthor)}</h2>')

    def set_title_chart(self, sTitle):
        if self.dLinks:
            self.lDoc.extend([item[1] for item in sorted(self.dLinks.items())])

        self.lDoc.append(f'<h3>{sTitle}</h3>')

    def set_is_synonym(self, sName, sAuthor, sMainName, sMainAuthor):
        sIS = _(" является синонимом ")
        self.lDoc.append(f'{str_get_html_name(sName, sAuthor)} {sIS}'
                         f'{str_get_html_name(sMainName, sMainAuthor)}')

    def set_rang_name(self, sRank, sName, sAuthor):
        self.set_string(f'({sRank}) {str_get_html_name(sName, sAuthor)}')

    def set_string(self, String):
        """ Устанавливает строку и переводит каретку в формате HTML

        :param String: Строка для добавления в список
        :type String: str
        :return: None
        """
        self.lDoc.append(f'{String}<br>')

    def set_no_data(self, sNoData):
        self.lDoc.append(f'({sNoData})')

    def set_link(self, sSource, sLink, sIndex,):
        if sSource == 'Plantarium':
            self.dLinks[sSource.upper()] = \
                f'{sSource}: <a href="{sLink}{sIndex}.html">{sIndex}</a> '
        else:
            self.dLinks[sSource.upper()] = \
                f'{sSource}: <a href="{sLink}{sIndex}">{sIndex}</a> '

    def get_doc(self):
        return ''.join(self.lDoc)


if __name__ == '__main__':
    pass
