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

""" The module provides message boxes that give hints about incorrect user
actions.

*Function*:
    | warning_no_synonyms(sName)
    | warning_lat_name()
    | warning_restart_app()
    | warning_this_exist(sThis, sThisName)

*Using*:
    As an example, let's show that the name of the taxon Cladonia, P. Browne
    already exists.

    .. code-block::

        warning_this_exist('taxon name', 'Cladonia, P.Browne')

"""

from gettext import gettext as _
from PyQt6.QtWidgets import QMessageBox


def warning_no_synonyms(sName):
    oMsgBox = QMessageBox()
    oMsgBox.setWindowTitle(_('Не существует синонима!'))
    sString = _('Не существует синонима для')
    oMsgBox.setText(f'{sString} {sName}')
    oMsgBox.exec()


def warning_lat_name():
    """ Create a message dialog window with warning that a Latin name of taxon
    isn't specified.
    """
    oMsgBox = QMessageBox()
    oMsgBox.setWindowTitle(_('Это не латинское имя!'))
    oMsgBox.setText(_('Укажите латинское имя для таксона!'))
    oMsgBox.exec()


def warning_restart_app():
    """ Create a message dialog window with warning that app should be
    restarted.
    """
    oMsgBox = QMessageBox()
    oMsgBox.setWindowTitle(_('Перезагрузить приложение!'))
    oMsgBox.setText(_('Приложение должно быть перезапущено, чтобы изменения '
                      'вступили в силу!'))
    oMsgBox.exec()


def warning_this_exist(sThis, sThisName):
    """ Create a dialog window of the message with warning that this exists.

    :param sThis: A stuff which trying to add.
    :type sThis: str
    :param sThisName: The name of stuff which trying to add.
    :type sThisName: str
    """
    oMsgBox = QMessageBox()
    oMsgBox.setWindowTitle(_('Это имя уже существует!'))

    sThe = _('Имя')
    sExist = _("уже существует.")
    oMsgBox.setText(f'{sThe} {sThis} {sThisName} {sExist}')
    oMsgBox.exec()


if __name__ == '__main__':
    pass
