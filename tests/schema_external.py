""" a schema for testing external attributes """

import tempfile

import datajoint as dj
import numpy as np

from . import CONN_INFO, PREFIX, S3_CONN_INFO

schema = dj.Schema(PREFIX + "_extern", connection=dj.conn(**CONN_INFO))


stores_config = {
    "raw": {"protocol": "file", "location": tempfile.mkdtemp()},
    "repo": {
        "stage": tempfile.mkdtemp(),
        "protocol": "file",
        "location": tempfile.mkdtemp(),
    },
    "repo-s3": {
        **S3_CONN_INFO,
        "protocol": "s3",
        "location": "dj/repo",
        "stage": tempfile.mkdtemp(),
    },
    "local": {
        "protocol": "file",
        "location": tempfile.mkdtemp(),
        "subfolding": (1, 1),
    },
    "share": {
        **S3_CONN_INFO,
        "protocol": "s3",
        "location": "dj/store/repo",
        "subfolding": (2, 4),
    },
}

dj.config["stores"] = stores_config

dj.config["cache"] = tempfile.mkdtemp()


@schema
class Simple(dj.Manual):

    """Docstring for Simple"""

    definition = """
    simple  : int
    ---
    item  : blob@local
    """


@schema
class SimpleRemote(dj.Manual):

    """Docstring for SimpleRemote"""

    definition = """
    simple  : int
    ---
    item  : blob@share
    """


@schema
class Seed(dj.Lookup):

    """Docstring for Seed"""

    definition = """
    seed :  int
    """
    contents = zip(range(4))


@schema
class Dimension(dj.Lookup):

    """Docstring for Dimension"""

    definition = """
    dim  : int
    ---
    dimensions  : blob
    """
    contents = ([0, [100, 50]], [1, [3, 4, 8, 6]])


@schema
class Image(dj.Computed):

    """Docstring for Image"""

    definition = """
    # table for storing
    -> Seed
    -> Dimension
    ----
    img : blob@share     #  objects are stored as specified by dj.config['stores']['share']
    neg : blob@local   # objects are stored as specified by dj.config['stores']['local']
    """

    def make(self, key):
        np.random.seed(key["seed"])
        img = np.random.rand(*(Dimension() & key).fetch1("dimensions"))
        self.insert1(dict(key, img=img, neg=-img.astype(np.float32)))


@schema
class Attach(dj.Manual):

    """Docstring for Attach"""

    definition = """
    # table for storing attachments
    attach : int
    ----
    img : attach@share    #  attachments are stored as specified by: dj.config['stores']['raw']
    txt : attach      #  attachments are stored directly in the database
    """


dj.errors._switch_filepath_types(True)  # pylint: disable=protected-access


@schema
class Filepath(dj.Manual):

    """Docstring for Filepath"""

    definition = """
    # table for file management
    fnum : int # test comment containing :
    ---
    img : filepath@repo  # managed files
    """


@schema
class FilepathS3(dj.Manual):

    """Docstring for FilepathS3"""

    definition = """
    # table for file management
    fnum : int
    ---
    img : filepath@repo-s3  # managed files
    """


dj.errors._switch_filepath_types(False)  # pylint: disable=protected-access
