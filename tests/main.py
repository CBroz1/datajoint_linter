import astroid
import pylint.testutils

from datajoint_linter.main import DataJointLinter  # noqa: #401

raise NotImplementedError


class TestUniqueReturnChecker(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = DataJointLinter

    def test_finds_non_unique_ints(self):
        func_node, return_node_a, return_node_b = astroid.extract_node(
            """
            def test(): #@
                if True:
                    return 5 #@
                return 5 #@
            """
        )

        self.checker.visit_functiondef(func_node)
        self.checker.visit_return(return_node_a)
        with self.assertAddsMessages(
            pylint.testutils.MessageTest(
                msg_id="non-unique-returns",
                node=return_node_b,
            ),
        ):
            self.checker.visit_return(return_node_b)
