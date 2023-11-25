""" Sample schema with realistic tables for testing """

import datajoint as dj

from . import CONN_INFO, PREFIX
from . import schema as _  # make sure that the other tables are defined

schema = dj.Schema(PREFIX + "_test1", locals(), connection=dj.conn(**CONN_INFO))


@schema
class Ephys(dj.Imported):
    """Docstring for Ephys."""

    definition = """  # This is already declare in ./schema.py
    """

    def make(self, key):
        pass


schema.spawn_missing_classes()  # load the rest of the classes
