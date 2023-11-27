"""
Sample schema with realistic tables for testing
"""

import datajoint as dj
from datajoint import Manual as _Merge  # Testing Spyglass custom table type

schema = dj.Schema("lint_good")


# TEST 00
@schema
class GoodTable1(dj.Lookup):
    """Docstring"""

    definition = """ # Table comment
    key     :  int        # key
    ---
    value   :  int        # value
    varchar :  varchar(1) # test very long verbose comment
    """
    contents = [(k, 2 * k, "a") for k in range(10)]


# TEST 01
@schema
class GoodTable2(dj.Computed):
    """Docstring"""

    definition = """ # Table docstring
    new_key       : int auto_increment # key
    ---
    new_value     : int                # value
    -> [nullable] GoodTable1
    evalue = null : enum('a', 'b')     # enum
    fvalue = null : float              # float
    dvalue = null : double             # double
    ivalue = null : int                # int
    uvalue = null : uuid               # uuid
    notes = ""    : varchar(1)         # varchar
    entry_time=CURRENT_TIMESTAMP :timestamp   # automatic timestamp
    index(new_value, evalue)
    """

    def make(self, key):
        self.insert1({**key, "new_value": 2 * key.get("value", 0)})


# TEST 02
@schema
class GoodTable3(_Merge):
    """Docstring"""

    definition = """
    alt_key          : int auto_increment # key
    ----
    alt_value = null : decimal(7,3)
    -> [unique, nullable] GoodTable1.proj(new="key")
    -> dj.UncaughtBadType
    """

    class GoodPart3(dj.Part):
        """Docstring"""

        definition = """
        -> master
        part_key       : tinyint unsigned
        ----
        current = null : longblob
        """


# TEST 03
@schema
class UncaughtBadFK(dj.Manual):
    """Docstring"""

    definition = """
    alt_key          : int auto_increment # key
    ----
    -> dj.UncaughtBadType
    """
