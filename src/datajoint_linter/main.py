from typing import TYPE_CHECKING, Optional

import astroid  # noqa: #401
from astroid import nodes
from pylint.checkers import BaseChecker

if TYPE_CHECKING:
    from pylint.lint import PyLinter


class DataJointLinter(BaseChecker):
    name = "unique-returns"
    msgs = {  # CWEFR = Custom Warning Error Fatal Refactor
        "C0001": (
            "Custom message.",
            "custom-message",
            "none",
        ),
        "W0001": (
            "Table `%s` uses varchar.",
            "use-varchar",
            "Found use of varchar in a table definition.",
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

    CHECKED_CLASSES = (
        "dj.Table",
        "dj.Lookup",
        "dj.Imported",
        "dj.Computed",
        "dj.Part",
        "_Merge",
    )

    def __init__(self, linter: Optional["PyLinter"] = None) -> None:
        super().__init__(linter)
        self._class_stack = []

    def visit_classdef(self, node: nodes.ClassDef) -> None:
        # from IPython import embed
        #
        # embed()

        if node.basenames[0] not in self.CHECKED_CLASSES:
            return
        def_attr = next(node.getattr("definition")[0].assigned_stmts())
        if isinstance(def_attr, nodes.node_classes.Call):
            return
        definition = def_attr.value
        from IPython import embed

        embed()
        if "varchar" in definition:
            self.add_message("use-varchar", node=node, args=node.name)
        self._class_stack.append([])

    def leave_classdef(self, node: nodes.ClassDef) -> None:
        if node.name not in self.CHECKED_CLASSES:
            return
        self._class_stack.pop()

    # def visit_name(self, node):
    #     # captures @schema, and class X
    #     print(f"visit name {node.tolineno}")
    #
    # def visit_call(self, node):
    #     # can capture dj.Schema
    #     print(f"visit call {node.tolineno}")
    #
    # def visit_attribute(self, node):
    #     # captures class X
    #     print(f"visit attribute {node.tolineno}")
    #
    # def visit_assign(self, node):
    #     # captures definition
    #     print(f"visit assign {node.tolineno}")


def register(linter: "PyLinter") -> None:
    """This required method auto registers the checker during initialization.

    :param linter: The linter to register the checker to.
    """
    linter.register_checker(DataJointLinter(linter))
