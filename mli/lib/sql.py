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
#   Copyright (C) 2021  Valerii Goncharuk (aka tagezi)
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

""" The module provides an API for working with the database. It creates a
    multi-level API that can be used in other modules to create requests using
    a minimum of transmitted data.

    :function: get_columns(sColumns, sConj='AND')
    :class: SQLmain

    Using:
    Foo = SQLmain(_DataBaseFile_)
    """

import logging
import sqlite3
from sqlite3 import DatabaseError

from mli.lib.log import start_logging


def get_columns(sColumns, sConj='AND'):
    """ The function of parsing a string, accepts a list of table columns
    separated by commas and returns this list with '=? AND' or '=? OR'
    as separator.

    :param sColumns: A string with a list of table columns separated by commas.
    :type sColumns: str
    :param sConj: The one from 'AND' or 'OR' operator condition.
        By default, is used 'AND'.
    :type sConj: str or None
    :return: The string with a list of table columns separated
        by '=? AND' or '=? OR'.
    :rtype: str
    """
    return sColumns.replace(', ', '=? ' + sConj + ' ') + "=?"


def get_increase_value(sColumns, tValues):
    """ Checks counting elements of values, and if them fewer,
     then makes them equal.

     :Note: In the rison that tuple can't be multiplied on flot, the process
     of increasing the tuple becomes somewhat resource-intensive. So,
     tValues should be consisting of one element.

    :param sColumns: Colum(s) in query.
    :type sColumns: str
    :param tValues: Values should be specified in the request.
    :type tValues: tuple
    :return: A tuple with values, which equal to sColumns.
    :rtype: tuple
    """
    if len(sColumns.split(',')) > len(tValues) == 1:
        return tValues * len(sColumns.split(', '))

    logging.error('The tuple must be filled or consist of one element.'
                  f'The columns: {sColumns}\n The tuple: {tValues}')
    return


class SQL:
    # TODO: PyCharm does not want to define standard reStructureText
    #  designation. I don't how it can fix now. So, I use available methods
    #  to structure text.
    """
    Provides interface for working with database from others scripts.

    *Methods*
      # Standard methods.
        * __init__ -- Method initializes a cursor of sqlite database.
        * __del__ -- Method closes the cursor of sqlite database.
      # Low level methods.
        * export_db -- Method exports from db to sql script.
        * execute_script -- Method imports from slq script to db.
        * execute_query -- Method execute sql_search query.
        * insert_row -- Method inserts a record in the database table.
        * delete_row -- Method deletes a row from the table.
        * update -- Method updates value(s) in record of the database table.
        * select -- Method does selection from the table.
      # Average level API.
        * sql_get_id: Finds id of the row by value(s) of table column(s).
        * sql_get_all: Method gets all records in database table.
        * sql_count: Method counts number of records in database table.
        * sql_table_clean: Method cleans up the table.
    """

    # Standard methods
    def __init__(self, sFileDB):
        """ Initializes connect with database.

        :param sFileDB: Path to database as string.
        :type sFileDB: str
        """
        try:
            self.oConnector = sqlite3.connect(sFileDB)
        except DatabaseError as e:
            logging.exception(f'An error has occurred: {e}.\n'
                              f'String of query: {sFileDB}\n')
        self.logging = start_logging()

    def __del__(self):
        """ Closes connection with the database. """
        self.oConnector.close()

    # Low methods level
    def export_db(self):
        """ Method exports from db to sql script. """
        return self.oConnector.iterdump()

    def execute_script(self, SQL):
        """ Method executes sql script.

        The main difference from the method is the ability to execute
        several commands at the same time. For example, using this method,
        you can restore the database from sql dump.

        :param SQL: SQL Script as string.
        :type SQL: str
        :return: True if script execution is successful, otherwise False.
        :rtype: bool
        """
        oCursor = self.oConnector.cursor()
        try:
            oCursor.executescript(SQL)
        except DatabaseError as e:
            logging.exception(f'An error has occurred: {e}.\n'
                              f'String of query: {SQL}\n')
            return False

        return True

    def execute_query(self, sqlString, tValues=None):
        """ Method executes sql script.

        :param sqlString: SQL query.
        :type sqlString: str
        :param tValues: value(s) that need to safe inserting into query
            (by default, None).
        :type tValues: tuple or None
        :return: Cursor or bool -- True if script execution is successful,
            otherwise False.
        """
        oCursor = self.oConnector.cursor()
        try:
            if tValues is None:
                oCursor.execute(sqlString)
            else:
                oCursor.execute(sqlString, tValues)
        except DatabaseError as e:
            logging.exception(f'An error has occurred: {e}.\n'
                              f'String of query: {sqlString}\n'
                              f'Parameters: {tValues}')
            return False

        return oCursor

    def insert_row(self, sTable, sColumns, tValues):
        """ Inserts a record in the database table.

        :param sTable: Table name as string.
        :type sTable: str
        :param sColumns: Columns names of the table by where needs inserting.
        :type sColumns: str
        :param tValues: Value(s) as tuple for inserting.
        :type tValues: tuple
        :return: ID of an inserted row  if the insert was successful.
            Otherwise, False.
        :rtype: str or bool
        """
        sSQL = ("?, " * len(sColumns.split(", ")))[:-2]
        sqlString = f'INSERT INTO {sTable} ({sColumns}) VALUES ({sSQL})'
        oCursor = self.execute_query(sqlString, tValues)
        if not oCursor:
            return False

        self.oConnector.commit()
        return oCursor.lastrowid

    def delete_row(self, sTable, sColumns=None, tValues=None):
        """ Deletes row in the database table by value(s).

        :param sTable: A table as string in where need to delete row.
        :type sTable: str or None
        :param sColumns: Column(s) where the value(s) will be found.
            (by default, None).
        :type sColumns: str or None
        :param tValues: value(s) as tuple for search of rows.
            (by default, None).
        :type tValues: tuple
        :return: True if the deletion is successful, otherwise False.
        :rtype: bool
        """
        if sColumns is not None:
            sqlString = f'DELETE FROM {sTable} WHERE {get_columns(sColumns)}'
            oCursor = self.execute_query(sqlString, tValues)
        else:
            sqlString = f'DELETE FROM {sTable}'
            oCursor = self.execute_query(sqlString)

        if not oCursor:
            return False

        self.oConnector.commit()
        return True

    def update(self, sTable, sSetUpdate, sWhereUpdate, tValues):
        """ Updates value(s) in the record of the database table.

        :param sTable: A Table as string where update is need to do.
        :type sTable: str
        :param sSetUpdate: Column(s) where the value are writen.
        :type sSetUpdate: str
        :param sWhereUpdate: A column where values correspond to the required.
        :type sWhereUpdate: str
        :param tValues: value(s) as tuple for search corresponding rows.
        :type tValues: tuple
        :return: True if the insert was successful, otherwise False.
        :rtype: bool
        """
        sSetUpdate = sSetUpdate + "=?"
        sWhereUpdate = get_columns(sWhereUpdate)
        sqlString = f'UPDATE {sTable} SET {sSetUpdate} WHERE {sWhereUpdate}'
        oCursor = self.execute_query(sqlString, tValues)
        if not oCursor:
            return False

        self.oConnector.commit()
        return True

    def select(self, sTable, sGet, sWhere='', tValues='', sConj='', sFunc=''):
        """ Looks for row by value(s) in table column(s).

        :param sTable: Table name as string.
        :type sTable: str
        :param sGet: Name of the column of the table, which will be returned.
        :type sGet: str
        :param sWhere: Names of columns of the table, by which to search
            (by default, empty).
        :type sWhere: str or None
        :param sConj: The one from 'AND' or 'OR' operator condition.
            By default, is used 'AND'.
        :type sConj: str or None
        :param tValues: Value(s) as tuple for search
            (by default, empty).
        :type tValues: tuple or None
        :param sFunc: Function name of sqlite, which need to apply
            (by default, empty). Note: Now, you can use only two sqlite
            functions: Count and DISTINCT.
        :type sFunc: str or None
        :return: Cursor or bool -- Cursor object within rows that was found,
            or False, if the row not found.
        """
        if sFunc == 'Count':
            sGet = f'Count({sGet})'
        elif sFunc == 'DISTINCT':
            sGet = f'{sFunc} {sGet}'

        if sWhere:
            if sConj:
                sCol = get_columns(sWhere, sConj)
            else:
                sCol = get_columns(sWhere)

            sqlString = f'SELECT {sGet} FROM {sTable} WHERE {sCol}'
            oCursor = self.execute_query(sqlString, tValues)
        else:
            oCursor = self.execute_query(f'SELECT {sGet} FROM {sTable}')

        if not oCursor:
            return False

        return oCursor

    # Average API level
    def sql_get_values(self, sTable, sID, sWhere, tValues, sConj=''):
        """ Looks for ID of the row by value(s) of table column(s).

        :param sTable: Table name as string.
        :type sTable: str
        :param sID: Name of the column of the table by which to search.
        :type sID: str
        :param sWhere: Names of columns of the table by which to search.
        :type sWhere: str
        :param tValues: Value(s) as tuple for search.
        :type tValues: tuple
        :param sConj: The one from 'AND' or 'OR' operator condition.
            By default, is used 'AND'.
        :type sConj: str or None
        :return: ID as Number in the row cell, or 0, if the row not found.
        :rtype: list or bool
        """
        if sWhere:
            if sConj:
                tValues = get_increase_value(sWhere, tValues)
                sWhere = get_columns(sWhere, sConj)
            else:
                sWhere = get_columns(sWhere)
        sqlString = f'SELECT {sID} FROM {sTable} WHERE {sWhere}'
        oCursor = self.execute_query(sqlString, tValues)
        if not oCursor:
            return False
        else:
            lRows = oCursor.fetchall()

            if not lRows:
                return 0
            else:
                return lRows

    def sql_get_id(self, sTable, sID, sWhere, tValues, sConj=''):
        lRows = self.sql_get_values(sTable, sID, sWhere, tValues, sConj)
        if not lRows:
            return 0
        else:
            return lRows[0][0]

    def sql_get_all(self, sTable):
        """ Gets all records in database table.

        :param sTable: Table name as string where records should be received.
        :type sTable: str
        :return: Tuple of all rows of table.
        :rtype: tuple or bool
        """
        oCursor = self.execute_query(f'SELECT * FROM {sTable}')
        if not oCursor:
            return False

        return oCursor.fetchall()

    def sql_count(self, sTable):
        """ Counts number of records in database table.

        :param sTable: Table name as string where records should be count.
        :type sTable: str
        :return: Number of found records.
        :rtype: int or bool
        """
        # sTable, sGet, sWhere, tValues, sFunc=None
        oCursor = self.select(sTable, sGet='*', sFunc='Count')
        if not oCursor:
            return False

        row = oCursor.fetchall()
        return row[0][0]

    def sql_table_clean(self, lTable):
        """ Cleans up the table.

        :param lTable: Table names as list or tuple of string, or table name
            as string where cleaning is need to do.
        :type lTable: tuple
        :return: True, if execution is successful. Otherwise, False.
            Note: False is returned even if cleaning the last table in
            the tuple was not successful.
        :rtype: bool
        """
        if type(lTable) == str:
            lTable = [lTable]

        for sTable in lTable:
            bDel = self.delete_row(str(sTable))
            if not bDel:
                return False

        return True
