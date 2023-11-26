"""Each table raises the error in the class docstring"""

import datajoint as dj

from datajoint_linter import *

from .schema_good import GoodTable1

schema = dj.Schema("lint_bad")


@schema
class DataTypeErr(dj.Lookup):
    """Unsupported attribute type {type}"""

    definition = """
    key     :  int        # key
    ---
    value   :  badtype    # value
    varchar :  varchar(1) # comment
    """
    contents = [(k, 2 * k, "a") for k in range(10)]


@schema
class BadFKRef(dj.Manual):
    """Foreign key reference %s could not be resolved"""

    definition = """ # Table docstring
    new_key       : int auto_increment # key
    ---
    -> [nullable] FakeTable
    """


@schema
class NoPK(dj.Manual):
    """Table must have a primary key"""

    definition = """ # Table docstring
    ---
    value : int
    """


@schema
class NullablePK(dj.Manual):
    """Primary key attributes cannot be nullable in line %s"""

    definition = """
    key=null :  int        # key
    ---
    value    :  int        # value
    """


@schema
class NullableFKRef(dj.Manual):
    """Primary dependencies cannot be nullable in line {line}"""

    definition = """ # Table docstring
    -> [nullable] GoodTable1
    new_key       : int auto_increment # key
    """


@schema
class BadFKOpt(dj.Imported):
    """Invalid foreign key option {opt}"""

    definition = """ # Table docstring
    new_key       : int auto_increment # key
    ---
    -> [nonoption] GoodTable1
    """

    def make(self, key):
        pass


@schema
class NotSupportFilepath(dj.Computed):
    """The filepath data type is disabled until complete validation."""

    definition = """ # Table docstring
    new_key       : int auto_increment # key
    ---
    this_path     : filepath@data
    """

    def make(self, key):
        pass


@schema
class GoodMaster(dj.Manual):
    """Docstring"""

    definition = """
    alt_key          : int auto_increment # key
    ----
    alt_value = null : decimal(7,3)
    -> [unique, nullable] GoodTable1.proj(new="uncaught_bad_key")
    """

    class BadPart(dj.Part):
        """Table comment must not start with a colon :"""

        definition = """ # : Bad Comment
        -> master
        part_key       : tinyint unsigned
        """


@schema
class ColonComment(dj.Manual):
    """An attribute comment must not start with a colon in comment {comment}"""

    definition = """ # Table docstring
    key       : int auto_increment # : key
    """


@schema
class DeclarationErr(dj.Manual):
    """Declaration error in position {pos} in line:\n  {line}\n{msg}"""

    definition = """ # Table docstring
    new&key       : int auto_increment # key
    """


@schema
class BlobDefault(dj.Manual):
    """The default value for a blob ... can only be NULL in:\n{line}"""

    definition = """ # Table docstring
    key       : int auto_increment # key
    ---
    thing="bad default" : blob
    """


@schema
class ParseErr(dj.Manual):
    """Parsing error in line %s. %s."""

    definition = """ # Table docstring
    new_key       : int auto_increment # key
    ---
    [ParseErr] -> BadFKRef
    """
