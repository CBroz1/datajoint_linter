"""Module for advanced schema definition."""
import datajoint as dj

from . import CONN_INFO, PREFIX

schema = dj.Schema(
    PREFIX + "_advanced", locals(), connection=dj.conn(**CONN_INFO)
)


@schema
class Person(dj.Manual):
    """Docstring for Person."""

    definition = """
    person_id : int
    ----
    full_name : varchar(60)
    sex : enum('M','F')
    """

    def fill(self):
        """
        fill fake names from www.fakenamegenerator.com
        """
        self.insert(
            (
                (0, "May K. Hall", "F"),
                (1, "Jeffrey E. Gillen", "M"),
                (2, "Hanna R. Walters", "F"),
                (3, "Russel S. James", "M"),
                (4, "Robbin J. Fletcher", "F"),
                (5, "Wade J. Sullivan", "M"),
                (6, "Dorothy J. Chen", "F"),
                (7, "Michael L. Kowalewski", "M"),
                (8, "Kimberly J. Stringer", "F"),
                (9, "Mark G. Hair", "M"),
                (10, "Mary R. Thompson", "F"),
                (11, "Graham C. Gilpin", "M"),
                (12, "Nelda T. Ruggeri", "F"),
                (13, "Bryan M. Cummings", "M"),
                (14, "Sara C. Le", "F"),
                (15, "Myron S. Jaramillo", "M"),
            )
        )


@schema
class Parent(dj.Manual):
    """docstring for Parent."""

    definition = """
    -> Person
    parent_sex  : enum('M','F')
    ---
    -> Person.proj(parent='person_id')
    """

    def fill(self):
        """Fill fake parent data."""

        def make_parent(pid, parent):
            return {
                "person_id": pid,
                "parent": parent,
                "parent_sex": (Person & {"person_id": parent}).fetch1("sex"),
            }

        self.insert(
            make_parent(*r)
            for r in (
                (0, 2),
                (0, 3),
                (1, 4),
                (1, 5),
                (2, 4),
                (2, 5),
                (3, 4),
                (3, 7),
                (4, 7),
                (4, 8),
                (5, 9),
                (5, 10),
                (6, 9),
                (6, 10),
                (7, 11),
                (7, 12),
                (8, 11),
                (8, 14),
                (9, 11),
                (9, 12),
                (10, 13),
                (10, 14),
                (11, 14),
                (11, 15),
                (12, 14),
                (12, 15),
            )
        )


@schema
class Subject(dj.Manual):
    """Docstring for Subject."""

    definition = """
    subject : int
    ---
    -> [unique, nullable] Person
    """


@schema
class Prep(dj.Manual):
    """Docstring for Prep."""

    definition = """
    prep   : int
    """


@schema
class Slice(dj.Manual):
    """Docstring for Slice."""

    definition = """
    -> Prep
    slice  : int
    """


@schema
class Cell(dj.Manual):
    """Docstring for Cell."""

    definition = """
    -> Slice
    cell  : int
    """


@schema
class InputCell(dj.Manual):
    """Docstring for InputCell."""

    definition = """  # a synapse within the slice
    -> Cell
    -> Cell.proj(input="cell")
    """


@schema
class LocalSynapse(dj.Manual):
    """Docstring for LocalSynapse."""

    definition = """  # a synapse within the slice
    -> Cell.proj(presynaptic='cell')
    -> Cell.proj(postsynaptic='cell')
    """


@schema
class GlobalSynapse(dj.Manual):
    """Docstring for GlobalSynapse."""

    # Mix old-style and new-style projected foreign keys
    definition = """
    # a synapse within the slice
    -> Cell.proj(pre_slice="slice", pre_cell="cell")
    -> Cell.proj(post_slice="slice", post_cell="cell")
    """
