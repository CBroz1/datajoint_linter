from typing import TYPE_CHECKING, Optional

import astroid  # noqa: #401
from astroid import nodes
from datajoint.declare import foreign_key_parser, prepare_declare
from datajoint.errors import DataJointError
from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker

if TYPE_CHECKING:
    from pylint.lint import PyLinter


class DataJointLinter(BaseChecker):
    name = "unique-returns"
    msgs = {  # CWEFR = Custom Warning Error Fatal Refactor
        "C0001": (
            "`%s` err: %s",
            "definition-error",
            "DataJoint was unable to parse the definition of the table.",
        ),
        "C0002": (
            "DataJoint linter does not support `*` import",
            "dj-wildcard-import",
            "Linter won't recognize foreign keys with star imports",
        ),
        "C0003": (
            "`%s` err: Table must have a primary key.",
            "no-pk",
            "Tables must mave primary keys.",
        ),
        "C0004": (
            "`%s` err: Table references the same foreign key multiple times",
            "mult-fk",
            "Tables should not repeat references",
        ),
        "C0005": (
            "`%s` err: Primary dependencies cannot be nullable",
            "null-pk-ref",
            "Primary key foreign key references cannot be nullable",
        ),
        "C0006": (
            "`%s` err: Invalid foreign key option %s",
            "bad-opt",
            "Supported foreign key options: nullable and unique",
        ),
    }

    options = (
        (
            "ignore-ints",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y or n>",
                "help": "Allow returning non-unique integers",
            },
        ),
    )

    __implements__ = IAstroidChecker

    CHECKED_CLASSES = (
        "dj.Manual",
        "dj.Table",
        "dj.Lookup",
        "dj.Imported",
        "dj.Computed",
        "dj.Part",
        "_Merge",
    )

    def __init__(self, linter: Optional["PyLinter"] = None) -> None:
        super().__init__(linter)
        self._class_namespace = set()
        self._module_namespace = set()

    def visit_classdef(self, node: nodes.ClassDef) -> None:
        if node.basenames[0] not in self.CHECKED_CLASSES:
            return
        self._class_namespace.add(node.name)

        def_attr, definition = self._get_def(node)

        if not isinstance(def_attr, nodes.node_classes.Const):
            return

        self._prepare_declare(node, definition)

    def _get_def(self, node):
        def_attr = next(node.getattr("definition")[0].assigned_stmts())
        return def_attr, def_attr.value

    def _prepare_declare(self, node, definition):
        try:
            (
                _,
                primary_key,
                _,
                _,
                _,
                _,
            ) = prepare_declare(definition, {})
            # TODO: Refactor to include context, dynamic analysis
        except DataJointError as error:
            if self._fk_check(node, error, definition):
                return
            self.add_message(
                "definition-error", node=node, args=(node.name, error)
            )
        else:
            if not primary_key:
                self.add_message("no-pk", node=node, args=node.name)

    def _get_fk_from_err(self, error):
        return (
            error.args[0]
            .split("reference ")[1]  # After reference
            .split("]")[-1]  # after options
            .split(" could ")[0]  # Before could
            .split(".proj")[0]  # Before any projections
            .strip()  # remove spaces
        )

    def _fk_check(self, node, error, definition):
        # TODO: PR to DJ to refactor subsets into private methods this can use?
        if not error.args[0].startswith("Foreign"):
            return False  # return if not fk

        fk = self._get_fk_from_err(error)
        in_pk = fk in definition.split("---")[0].split("___")[0]
        fk_ref = [line for line in definition.split("\n") if fk in line]
        # import pdb
        #
        # pdb.set_trace()

        if len(fk_ref) > 1:
            self.add_message("mult-ref", node=node, args=node.name)

        options = [
            opt.upper()
            for opt in foreign_key_parser.parseString(fk_ref[0]).options
        ]

        for opt in options:  # check for invalid options
            if opt not in {"NULLABLE", "UNIQUE"}:
                self.add_message("bad-opt", node=node, args=(node.name, opt))
        is_nullable = "NULLABLE" in options
        if is_nullable and in_pk:
            self.add_message("null-pk-ref", node=node, args=node.name)

        if (
            (node.basenames[0] == "dj.Part" and fk == "master")  # master ref
            or fk in self._class_namespace  # Table imported or in schema
            or fk.split(".")[0] in self._module_namespace  # module imported
        ):
            return True

        return False

    def visit_import(self, node):
        """Captures module import statements, retains for fk check"""
        for names in node.names:
            self._module_namespace.add(names[1] or names[0])

    def visit_importfrom(self, node):
        """Captures table names from import statements, retains for fk check"""
        for names in node.names:
            if names[0] == "*":
                self.add_message("dj-wildcard-import", node=node)
                return
            self._class_namespace.add(names[1] or names[0])


def register(linter: "PyLinter") -> None:
    """This required method auto registers the checker during initialization.

    :param linter: The linter to register the checker to.
    """
    linter.register_checker(DataJointLinter(linter))
