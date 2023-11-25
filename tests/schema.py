"""
Sample schema with realistic tables for testing
"""

import inspect
import random
from datetime import date, timedelta

import datajoint as dj
import numpy as np

# from . import CONN_INFO, PREFIX

# schema = dj.Schema(PREFIX + "_test1", connection=dj.conn(**CONN_INFO))
schema = dj.Schema("lint_test1")


@schema
class TTest(dj.Lookup):
    """Docstring"""

    definition = """
    key   :   int     # key
    ---
    value   :   int     # value
    """
    contents = [(k, 2 * k) for k in range(10)]


@schema
class TTest2(dj.Manual):
    """Docstring for TTest2"""

    definition = """
    key   :   int     # key
    ---
    value   :   int     # value
    """


@schema
class TTest3(dj.Manual):
    """Docstring"""

    definition = """
    key : int
    ---
    value : varchar(300)
    """


@schema
class NullableNumbers(dj.Manual):
    """Docstring"""

    definition = """
    key : int
    ---
    fvalue = null : float
    dvalue = null : double
    ivalue = null : int
    uvalue = null : uuid
    """


@schema
class TTestExtra(dj.Manual):
    """clone of Test but with an extra field"""

    definition = TTest.definition + "\nextra : int # extra int\n"


@schema
class TTestNoExtra(dj.Manual):
    """
    clone of Test but with no extra fields
    """

    definition = TTest.definition


@schema
class Auto(dj.Lookup):
    """Docstring"""

    definition = """
    id  :int auto_increment
    ---
    name :varchar(12)
    """

    def fill(self):
        """Docstring"""
        if not self:
            self.insert(
                [{"name": name} for name in ["Godel", "Escher", "Bach"]]
            )


@schema
class User(dj.Lookup):
    """Docstring"""

    definition = """      # lab members
    username: varchar(12)
    """
    contents = [
        ["Jake"],
        ["Cathryn"],
        ["Shan"],
        ["Fabian"],
        ["Edgar"],
        ["George"],
        ["Dimitri"],
    ]


@schema
class Subject(dj.Lookup):
    """Docstring"""

    definition = """  # Basic information about animal subjects used in experiments
    subject_id   :int  #  unique subject id
    ---
    real_id            :varchar(40)  # real-world name. Omit if the same as subject_id
    species = "mouse"  :enum('mouse', 'monkey', 'human')
    date_of_birth      :date
    subject_notes      :varchar(4000)
    unique index (real_id, species)
    """

    contents = [
        [
            1551,
            "1551",
            "mouse",
            "2015-04-01",
            "genetically engineered super mouse",
        ],
        [10, "Curious George", "monkey", "2008-06-30", ""],
        [1552, "1552", "mouse", "2015-06-15", ""],
        [1553, "1553", "mouse", "2016-07-01", ""],
    ]


@schema
class Language(dj.Lookup):
    """Docstring"""

    definition = """
    # languages spoken by some of the developers
    # additional comments are ignored
    name        : varchar(40) # name of the developer
    language    : varchar(40) # language
    """
    contents = [
        ("Fabian", "English"),
        ("Edgar", "English"),
        ("Dimitri", "English"),
        ("Dimitri", "Ukrainian"),
        ("Fabian", "German"),
        ("Edgar", "Japanese"),
    ]


@schema
class Experiment(dj.Imported):
    """Docstring"""

    definition = """  # information about experiments
    -> Subject
    experiment_id  :smallint  # experiment number for this subject
    ---
    experiment_date  :date   # date when experiment was started
    -> [nullable] User
    data_path=""     :varchar(255)  # file path to recorded data
    notes=""         :varchar(2048) # e.g. purpose of experiment
    entry_time=CURRENT_TIMESTAMP :timestamp   # automatic timestamp
    """

    fake_experiments_per_subject = 5

    def make(self, key):
        """
        populate with random data
        """

        users = [None, None] + list(User().fetch()["username"])
        random.seed("Amazing Seed")
        self.insert(
            dict(
                key,
                experiment_id=experiment_id,
                experiment_date=(
                    date.today() - timedelta(random.expovariate(1 / 30))
                ).isoformat(),
                username=random.choice(users),
            )
            for experiment_id in range(self.fake_experiments_per_subject)
        )


@schema
class Trial(dj.Imported):
    """Docstring"""

    definition = """   # a trial within an experiment
    -> Experiment.proj(animal='subject_id')
    trial_id  :smallint   # trial number
    ---
    start_time                 :double      # (s)
    """

    class Condition(dj.Part):
        """Docstring"""

        definition = """   # trial conditions
        -> Trial
        cond_idx : smallint   # condition number
        ----
        orientation :  float   # degrees
        """

    def make(self, key):
        """populate with random data (pretend reading from raw files)"""
        random.seed("Amazing Seed")
        trial = self.Condition()
        for trial_id in range(10):
            key["trial_id"] = trial_id
            self.insert1(dict(key, start_time=random.random() * 1e9))
            trial.insert(
                dict(key, cond_idx=cond_idx, orientation=random.random() * 360)
                for cond_idx in range(30)
            )


@schema
class Ephys(dj.Imported):
    """Docstring"""

    definition = """    # some kind of electrophysiological recording
    -> Trial
    ----
    sampling_frequency :double  # (Hz)
    duration           :decimal(7,3)  # (s)
    """

    class Channel(dj.Part):
        """Docstring"""

        definition = """     # subtable containing individual channels
        -> master
        channel    :tinyint unsigned   # channel number within Ephys
        ----
        voltage    : longblob
        current = null : longblob   # optional current to test null handling
        """

    def make(self, key):
        """
        populate with random data
        """
        random.seed(str(key))
        row = dict(
            key,
            sampling_frequency=6000,
            duration=np.minimum(2, random.expovariate(1)),
        )
        self.insert1(row)
        number_samples = int(row["duration"] * row["sampling_frequency"] + 0.5)
        sub = self.Channel()
        sub.insert(
            dict(
                key,
                channel=channel,
                voltage=np.float32(np.random.randn(number_samples)),
            )
            for channel in range(2)
        )


@schema
class Image(dj.Manual):
    """Docstring"""

    definition = """
    # table for testing blob inserts
    id           : int # image identifier
    ---
    img             : longblob # image
    """


@schema
class UberTrash(dj.Lookup):
    """Docstring"""

    definition = """
    id : int
    ---
    """
    contents = [(1,)]


@schema
class UnterTrash(dj.Lookup):
    """Docstring"""

    definition = """
    -> UberTrash
    my_id   : int
    ---
    """
    contents = [(1, 1), (1, 2)]


@schema
class SimpleSource(dj.Lookup):
    """Docstring"""

    definition = """
    id : int  # id
    """
    contents = ((x,) for x in range(10))


@schema
class SigIntTable(dj.Computed):
    """Docstring"""

    definition = """
    -> SimpleSource
    """

    def make(self, key):
        raise KeyboardInterrupt


@schema
class SigTermTable(dj.Computed):
    """Docstring"""

    definition = """
    -> SimpleSource
    """

    def make(self, key):
        raise SystemExit("SIGTERM received")


@schema
class DjExceptionName(dj.Lookup):
    """Docstring"""

    definition = """
    dj_exception_name:    char(64)
    """

    @property
    def contents(self):
        """Docstring"""
        return [
            [member_name]
            for member_name, member_type in inspect.getmembers(dj.errors)
            if inspect.isclass(member_type)
            and issubclass(member_type, Exception)
        ]


@schema
class ErrorClass(dj.Computed):
    """Docstring"""

    definition = """
    -> DjExceptionName
    """

    def make(self, key):
        exception_name = key["dj_exception_name"]
        raise getattr(dj.errors, exception_name)


@schema
class DecimalPrimaryKey(dj.Lookup):
    """Docstring"""

    definition = """
    id  :  decimal(4,3)
    """
    contents = zip((0.1, 0.25, 3.99))


@schema
class IndexRich(dj.Manual):
    """Docstring"""

    definition = """
    -> Subject
    ---
    -> [unique, nullable] User.proj(first="username")
    first_date : date
    value : int
    index (first_date, value)
    """


#  Schema for issue 656
@schema
class ThingA(dj.Manual):
    """Docstring"""

    definition = """
    a: int
    """


@schema
class ThingB(dj.Manual):
    """Docstring"""

    definition = """
    b1: int
    b2: int
    ---
    b3: int
    """


@schema
class ThingC(dj.Manual):
    """Docstring"""

    definition = """
    -> ThingA
    ---
    -> [unique, nullable] ThingB
    """


@schema
class Parent(dj.Lookup):
    """Docstring"""

    definition = """
    parent_id: int
    ---
    name: varchar(30)
    """

    contents = [(1, "Joe")]


@schema
class Child(dj.Lookup):
    """Docstring"""

    definition = """
    -> Parent
    child_id: int
    ---
    name: varchar(30)
    """
    contents = [(1, 12, "Dan")]


# Related to issue #886 (8), #883 (5)
@schema
class ComplexParent(dj.Lookup):
    """Docstring"""

    definition = "\n".join([f"parent_id_{i+1}: int" for i in range(8)])
    contents = [tuple(i for i in range(8))]


@schema
class ComplexChild(dj.Lookup):
    """Docstring"""

    definition = "\n".join(
        ["-> ComplexParent"] + [f"child_id_{i+1}: int" for i in range(1)]
    )
    contents = [tuple(i for i in range(9))]


@schema
class SubjectA(dj.Lookup):
    """Docstring"""

    definition = """
    subject_id: varchar(32)
    ---
    dob : date
    sex : enum('M', 'F', 'U')
    """
    contents = [
        ("mouse1", "2020-09-01", "M"),
        ("mouse2", "2020-03-19", "F"),
        ("mouse3", "2020-08-23", "F"),
    ]


@schema
class SessionA(dj.Lookup):
    """Docstring"""

    definition = """
    -> SubjectA
    session_start_time: datetime
    ---
    session_dir=''  : varchar(32)
    """
    contents = [
        ("mouse1", "2020-12-01 12:32:34", ""),
        ("mouse1", "2020-12-02 12:32:34", ""),
        ("mouse1", "2020-12-03 12:32:34", ""),
        ("mouse1", "2020-12-04 12:32:34", ""),
    ]


@schema
class SessionStatusA(dj.Lookup):
    """Docstring"""

    definition = """
    -> SessionA
    ---
    status: enum('in_training', 'trained_1a', 'trained_1b', 'ready4ephys')
    """
    contents = [
        ("mouse1", "2020-12-01 12:32:34", "in_training"),
        ("mouse1", "2020-12-02 12:32:34", "trained_1a"),
        ("mouse1", "2020-12-03 12:32:34", "trained_1b"),
        ("mouse1", "2020-12-04 12:32:34", "ready4ephys"),
    ]


@schema
class SessionDateA(dj.Lookup):
    """Docstring"""

    definition = """
    -> SubjectA
    session_date:  date
    """
    contents = [
        ("mouse1", "2020-12-01"),
        ("mouse1", "2020-12-02"),
        ("mouse1", "2020-12-03"),
        ("mouse1", "2020-12-04"),
    ]


@schema
class Stimulus(dj.Lookup):
    """Docstring"""

    definition = """
    id: int
    ---
    contrast: int
    brightness: int
    """


@schema
class Longblob(dj.Manual):
    """Docstring"""

    definition = """
    id: int
    ---
    data: longblob
    """
