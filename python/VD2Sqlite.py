# -*- coding: iso-8859-15 -*-
# Copyright (C) 2013-2015 Martin Glueck All rights reserved
# Langstrasse 4, A--2244 Spannberg, Austria. martin@mangari.org
# #*** <License> ************************************************************#
# This module is part of the library selfbus.
#
# This module is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this module. If not, see <http://www.gnu.org/licenses/>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    VD2Sqlite
#
# Purpose
#    Convert an vd file into a sqlite database
#
# Revision Dates
#    07-Dec-2013 (MG) Creation
#    ��revision-date�����
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals
from   collections import OrderedDict as OD

#from     sqlalchemy import create_engine, Table, Column
#import   sqlalchemy

def no_to_col (i) :
    result = ""
    if i > 26 :
        result += chr (ord ("A") + (i // 26) - 1)
        i -= (i // 26) * 26
    result += chr (ord ("A") + i - 1)
    return result
# end def no_to_col

class Column (object) :
    """A column of a table"""

    def __init__ (self, name, type, size, null) :
        self.name    = name
        self.type    = type
        self.size    = size
        self.null    = null
    # end def __init__

    def create (self) :
        type_fct = getattr (self, "_sql_type_%d" % (self.type, ))
        return sqlalchemy.Column (self.name, type_fct (), nullable = self.null)
    # end def create

    def python_value (self, string) :
        type_fct = getattr (self, "_python_value_%d" % (self.type, ))
        return type_fct (string)
    # end def python_value

    def _python_value_1 (self, string) :
        if string :
            return int (string)
    # end def _python_value_1

    def _python_value_2 (self, string) :
        if string :
            return int (string)
    # end def _python_value_3

    def _python_value_3 (self, string) :
        return string
    # end def _python_value_3

    def _python_value_5 (self, string) :
        if string :
            return float (string)
    # end def _python_value_5

    def _python_value_8 (self, string) :
        return string
    # end def _python_value_8

    def _sql_type_1 (self) :
        return sqlalchemy.Integer
    # end def _sql_type_1

    def _sql_type_2 (self) :
        return sqlalchemy.SmallInteger
    # end def _sql_type_2

    def _sql_type_3 (self) :
        return sqlalchemy.Unicode (self.size)
    # end def _sql_type_3

    def _sql_type_5 (self) :
        return sqlalchemy.Float
    # end def _sql_type_5

    def _sql_type_8 (self) :
        return sqlalchemy.Unicode (self.size)
    # end def _sql_type_8

# end class Column

class Table (object) :
    """A table in the VD file"""

    def __init__ (self, name, number) :
        self.name    = name
        self.number  = number
        self.columns = []
        self.data    = []
    # end def __init__

    def add_row (self, file) :
        result = dict ()
        for c in self.columns :
            line = file.readline ()
            result [c.name] = c.python_value (line)
        self.data.append (result)
    # end def add_row

    def create (self, metadata) :
        columns   = [c.create () for c in self.columns]
        self._sql = sqlalchemy.Table ("%03d_%s" % (int (self.number), self.name), metadata, * columns)
    # end def create

    def create_excel (self, doc, i) :
        try :
            sheet = doc.Sheets [i]
        except :
            sheet = doc.Sheets.Add (After = doc.Sheets [doc.Sheets.Count - 1])
        sheet.Name = self.name
        headers = [c.name for c in self.columns]
        sheet.Range ("A1:%s1" % no_to_col (len (headers))).Value = headers
        max = len (self.data)
        for rn, row in enumerate (self.data) :
            if not (rn % 100) :
                print ("%6d/%6d" % (rn + 1, max))
            data = [row [c.name] for c in self.columns]
            sheet.Range ("A%d:%s%d" % (rn + 2, no_to_col (len (data)), rn + 2)).Value = data
    # end def create_excel

    def create_joined_execl (self, name, doc, i, joins, C) :
        try :
            sheet  = doc.Sheets [i]
        except :
            sheet  = doc.Sheets.Add (After = doc.Sheets [doc.Sheets.Count - 1])
        try :
            sheet.Name = name
        except :
            pass
        headers    = [c.name for c in self.columns]
        sep_cols   = [no_to_col (len (headers))]
        max = len (self.data)
        jdata = dict ()
        for ji in joins.values () :
            table = ji ["target"]
            key   = ji ["key"]
            data  = jdata [table.name] = dict ()
            headers.extend (c.name for c in table.columns)
            for row in table.data :
                data [row [key]] = row
            sep_cols.append (no_to_col (len (headers)))
        sheet.Range    ("A1:%s1" % no_to_col (len (headers))).Value = headers
        for rn, row in enumerate (self.data) :
            if not (rn % 100) :
                print ("%6d/%6d" % (rn + 1, max))
            data  = [row [c.name] for c in self.columns]
            jrows = {self : row}
            for src, ji in joins.items () :
                table             = ji ["target"]
                key               = ji ["key"]
                jrow              = jdata [table.name] [jrows [src] [key]]
                jrows [table]     = jrow
                data.extend (jrow [c.name] for c in table.columns)
            row_spec = "A%d:%s%d" % (rn + 2, no_to_col (len (data)), rn + 2)
            sheet.Range (row_spec).Value = data
        for col  in sep_cols [:-1] :
            srange = sheet.Range    ("%s1:%s%d" % (col, col, rn))
            border = srange.Borders (C.xlEdgeRight)
            border.LineStyle = C.xlContinuous
            border.Weight    = C.xlMedium
    # end def create_joined_execl

    def fill (self, engine) :
        ins = self._sql.insert ()
        con = engine.connect   ()
        for row in self.data :
            con.execute (ins, ** row)
        con.close       ()
    # end def fill

    def __str__ (self) :
        result = ["Table<%s>" % (self.name, )]
        for c in self.columns :
            result.append ("  %-30s<%s>" % (c.name, c.type))
        return "\n".join (result)
    # end def __str__

    @classmethod
    def From_File (cls, file) :
        line               = file.readline ()
        kind, number, name = line.split    (" ", 2)
        if kind != "T" :
            raise ValueError \
                ("Expected kind `T`, found `%s`" % (kind, ))
        result             = cls (name, number)
        line = file.readline ()
        while (   (line != "-------------------------------------" )
              and (line != "XXX")
              ) :
            parts = line.split (" ")
            if parts [0] [0] == "C" :
                ### add a new column
                if parts [1] [1:] != result.number :
                    raise ValueError ("Table header error")
                result.columns.append \
                    ( Column
                        ( parts [5]
                        , int (parts [2])
                        , int (parts [3])
                        , parts [4] == "Y"
                        )
                    )
            if parts [0] [0] == "R" :
                ### add a new data row
                result.add_row (file)
            line = file.readline ()
        return result
    # end def From_File

# end class Table

class VD_File (object) :
    """A VD File"""

    class File (object) :

        def __init__ (self, file) :
            self.file  = file
            self._line = None
            self.eof   = False
        # end def __init__

        def _read (self) :
            line = self.file.readline ()
            if not line :
                self.eof = True
            return line.strip ()
        # end def _read

        def readline (self) :
            if self._line is not None :
                result     = self._line
            else :
                result     = self._read ()
            self._line     = self._read ()
            while self._line [:2] == r"\\" :
                result    += self._line [2:]
                self._line = self._read ()
            return result
        # end def readline

        def __bool__ (self) :
            return not self.eof
        # end def __bool__

    # end class File

    def __init__ (self, vd_name) :
        self.file_name = vd_name
        self.tables    = OD                 ()
        self.file      = self.File          (open (vd_name, "r"))
        line           = self.file.readline ()
        if line != "EX-IM" :
            raise ValueError ("Magic marker `EX_IM` not found!")
        while line != "-------------------------------------" :
            line = self.file.readline ().strip ()
        while self.file :
            table = Table.From_File (self.file)
            self.tables [table.name] = table
    # end def __init__

    def create_database (self, engine) :
        metadata = sqlalchemy.MetaData ()
        for t in self.tables.values () :
            t.create        (metadata)
        metadata.create_all (engine)
    # end def create_database

    def create_excel (self, file_name, create_joined = False) :
        import win32com.client
        e         = win32com.client.gencache.EnsureDispatch \
                        ("Excel.Application")
        from win32com.client import constants as C
        e.Visible = True
        doc       = e.Workbooks.Add ()
        for i, table in enumerate (self.tables.values ()) :
            print ("Dump %s" % (table.name, ))
            table.create_excel (doc, i + 1)
        if create_joined :
            atom  = self.tables ["parameter_atomic_type"]
            par_t = self.tables ["parameter_type"]
            para  = self.tables ["parameter"]
            dpara = self.tables ["device_parameter"]
            obj   = self.tables ["communication_object"]
            dobj  = self.tables ["device_object"]
            joins = OD ()
            joins [dpara] = dict (target = para,  key    = "PARAMETER_ID")
            joins [para]  = dict (target = par_t, key    = "PARAMETER_TYPE_ID")
            joins [par_t] = dict (target = atom,  key    = "ATOMIC_TYPE_NUMBER")
            print ("Created joined table for parameters")
            dpara.create_joined_execl ("Parameter Full", doc, i + 2, joins, C)
            joins = OD ()
            joins [dobj] = dict (target = obj, key = "OBJECT_ID")
            print ("Created joined table for objects")
            dobj.create_joined_execl ("Object Full", doc, i + 3, joins, C)
        doc.SaveAs             (file_name)
    # end def create_excel

    def fill (self, engine) :
        for t in self.tables.values () :
            t.fill (engine)
    # end def fill

# end class VD_File

if __name__ == "__main__" :
    import sys

    def info(type, value, tb):
       if hasattr(sys, 'ps1') or not sys.stderr.isatty():
          # we are in interactive mode or we don't have a tty-like
          # device, so we call the default hook
          sys.__excepthook__(type, value, tb)
       else:
          import traceback, pdb
          # we are NOT in interactive mode, print the exception...
          traceback.print_exception(type, value, tb)
          print
          # ...then start the debugger in post-mortem mode.
          pdb.pm()

    sys.excepthook = info
    vd_file = VD_File (sys.argv [1])
    #engine  = sqlalchemy.create_engine \
    #    ( "sqlite:///%s.sqlite" % (sys.argv [2], )
    #    #, echo=True
    #    )
    #vd_file.create_database (engine)
    #vd_file.fill            (engine)
    vd_file.create_excel     (sys.argv [2], True)
### __END__ VD2Sqlite
