import contextlib

import astroid
from datajoint.errors import DataJointError
from pylint.testutils import CheckerTestCase, MessageTest

from datajoint_linter.main import DataJointLinter  # noqa: #401


class TestDataJointLinter(CheckerTestCase):
    CHECKER_CLASS = DataJointLinter

    # To add fk refs to namespace for an isolated test:
    #    self.checker._class_namespace.add("goodtable1")
    #    self.checker._module_namespace.add("dj")
    # To adjust config for an isolated test:
    #    self.linter.config.permit_dj_filepath = True

    @contextlib.contextmanager
    def assertAddsMessages(self, *messages: MessageTest):
        """Redefines parent class func to only compare string reprs of args

        Also removes unused positition arg flag
        """
        yield
        got = self.linter.release_messages()
        no_msg = "No message."
        expected = "\n".join(repr(m) for m in messages) or no_msg
        got_str = "\n".join(repr(m) for m in got) or no_msg
        msg = (
            "Expected messages did not match actual.\n"
            f"\nExpected:\n{expected}\n\nGot:\n{got_str}\n"
        )

        assert len(messages) == len(got), msg

        for expected_msg, gotten_msg in zip(messages, got):
            assert expected_msg.msg_id == gotten_msg.msg_id, msg
            assert expected_msg.node == gotten_msg.node, msg
            assert str(expected_msg.args) == str(gotten_msg.args), msg
            assert expected_msg.line == gotten_msg.line, msg
            assert expected_msg.col_offset == gotten_msg.col_offset, msg

    def test_basic(self, test_cases_good):
        my_class = astroid.extract_node(test_cases_good[1])
        with self.assertNoMessages():
            self.checker.visit_classdef(my_class)

    def test_fk_ref(self, test_cases_good):
        my_class = astroid.extract_node(test_cases_good[2])
        self.checker._class_namespace.add("GoodTable1")
        with self.assertNoMessages():
            self.checker.visit_classdef(my_class)

    def test_fk_opts(self, test_cases_good):
        my_class = astroid.extract_node(test_cases_good[3])
        self.checker._class_namespace.add("GoodTable1")
        self.checker._module_namespace.add("dj")
        with self.assertNoMessages():
            self.checker.visit_classdef(my_class)

    def test_fk_module(self, test_cases_good):
        my_class = astroid.extract_node(test_cases_good[4])
        self.checker._module_namespace.add("dj")
        with self.assertNoMessages():
            self.checker.visit_classdef(my_class)

    def test_wildcard_import(self, test_cases_bad):
        my_import = astroid.extract_node("from datajoint import *")
        with self.assertAddsMessages(
            MessageTest(
                msg_id="dj-wildcard-import",
                node=my_import,
                line=1,
                col_offset=0,
                end_line=1,
                end_col_offset=23,
            ),
        ):
            self.checker.visit_importfrom(my_import)

    def test_type_err(self, test_cases_bad):
        my_class = astroid.extract_node(test_cases_bad[1])
        self.checker._module_namespace.add("dj")
        with self.assertAddsMessages(
            MessageTest(
                msg_id="definition-error",
                node=my_class,
                line=2,
                args=(
                    "DataTypeErr",
                    DataJointError("Unsupported attribute type badtype"),
                ),
                col_offset=0,
                end_line=2,
                end_col_offset=17,
            ),
        ):
            self.checker.visit_classdef(my_class)

    def test_bad_fk(self, test_cases_bad):
        my_class = astroid.extract_node(test_cases_bad[2])
        with self.assertAddsMessages(
            MessageTest(
                msg_id="definition-error",
                node=my_class,
                args=(
                    "BadFKRef",
                    DataJointError(
                        "Foreign key reference  FakeTable could not be resolved"
                    ),
                ),
                line=2,
                col_offset=0,
                end_line=2,
                end_col_offset=14,
            ),
        ):
            self.checker.visit_classdef(my_class)

    def test_no_pk(self, test_cases_bad):
        my_class = astroid.extract_node(test_cases_bad[3])
        with self.assertAddsMessages(
            MessageTest(
                msg_id="no-pk",
                node=my_class,
                args="NoPK",
                line=2,
                col_offset=0,
                end_line=2,
                end_col_offset=10,
            ),
        ):
            self.checker.visit_classdef(my_class)

    def test_null_pk(self, test_cases_bad):
        my_class = astroid.extract_node(test_cases_bad[4])
        with self.assertAddsMessages(
            MessageTest(
                msg_id="definition-error",
                line=2,
                node=my_class,
                args=(
                    "NullablePK",
                    DataJointError(
                        "Primary key attributes cannot be nullable in line "
                        + '"key=null :  int        # key"'
                    ),
                ),
                col_offset=0,
                end_line=2,
                end_col_offset=16,
            ),
        ):
            self.checker.visit_classdef(my_class)

    def test_null_fk(self, test_cases_bad):
        my_class = astroid.extract_node(test_cases_bad[5])
        self.checker._class_namespace.add("GoodTable1")
        with self.assertAddsMessages(
            MessageTest(
                msg_id="null-pk-ref",
                line=2,
                node=my_class,
                args="NullableFKRef",
                col_offset=0,
                end_line=2,
                end_col_offset=19,
            ),
        ):
            self.checker.visit_classdef(my_class)

    def test_bad_fk_opt(self, test_cases_bad):
        my_class = astroid.extract_node(test_cases_bad[6])
        self.checker._class_namespace.add("GoodTable1")
        with self.assertAddsMessages(
            MessageTest(
                msg_id="bad-opt",
                node=my_class,
                args=("BadFKOpt", "NONOPTION"),
                line=2,
                col_offset=0,
                end_line=2,
                end_col_offset=16,
            ),
        ):
            self.checker.visit_classdef(my_class)

    def test_nofp(self, test_cases_bad):
        my_class = astroid.extract_node(test_cases_bad[7])
        with self.assertAddsMessages(
            MessageTest(
                msg_id="no-fp",
                node=my_class,
                args="NotSupportFilepath",
                line=2,
                col_offset=0,
                end_line=2,
                end_col_offset=16,
            ),
        ):
            self.checker.visit_classdef(my_class)

    def test_permit_fp(self, test_cases_bad):
        my_class = astroid.extract_node(test_cases_bad[7])
        self.linter.config.permit_dj_filepath = True
        with self.assertNoMessages():
            self.checker.visit_classdef(my_class)

    def test_no_comment_colon(self, test_cases_bad):
        my_class = astroid.extract_node(test_cases_bad[9])
        self.checker._class_namespace.add("GoodTable1")
        with self.assertAddsMessages(
            MessageTest(
                msg_id="definition-error",
                node=my_class,
                args=(
                    "BadPart",
                    DataJointError(
                        'Table comment must not start with a colon ":"'
                    ),
                ),
                line=1,
                col_offset=0,
                end_line=2,
                end_col_offset=16,
            ),
        ):
            self.checker.visit_classdef(my_class)

    def test_no_attrib_colon(self, test_cases_bad):
        my_class = astroid.extract_node(test_cases_bad[10])
        with self.assertAddsMessages(
            MessageTest(
                msg_id="definition-error",
                node=my_class,
                args=(
                    "ColonComment",
                    DataJointError(
                        "An attribute comment must not start with a colon in "
                        + 'comment ": key"'
                    ),
                ),
                line=2,
                col_offset=0,
                end_line=2,
                end_col_offset=16,
            ),
        ):
            self.checker.visit_classdef(my_class)

    def test_declaration_error(self, test_cases_bad):
        my_class = astroid.extract_node(test_cases_bad[11])
        with self.assertAddsMessages(
            MessageTest(
                msg_id="definition-error",
                node=my_class,
                args=(
                    "DeclarationErr",
                    DataJointError(
                        "Declaration error in position 3 in line:\n  "
                        + "new&key       : int auto_increment # key#\nExpected "
                        + '":"'
                    ),
                ),
                line=2,
                col_offset=0,
                end_line=2,
                end_col_offset=16,
            ),
        ):
            self.checker.visit_classdef(my_class)

    def test_blob_default(self, test_cases_bad):
        my_class = astroid.extract_node(test_cases_bad[12])
        with self.assertAddsMessages(
            MessageTest(
                msg_id="definition-error",
                node=my_class,
                args=(
                    "BlobDefault",
                    DataJointError(
                        "The default value for a blob or attachment attributes "
                        + 'can only be NULL in:\nthing="bad default" : blob'
                    ),
                ),
                line=2,
                col_offset=0,
                end_line=2,
                end_col_offset=16,
            ),
        ):
            self.checker.visit_classdef(my_class)

    def test_parse_err(self, test_cases_bad):
        my_class = astroid.extract_node(test_cases_bad[13])
        with self.assertAddsMessages(
            MessageTest(
                msg_id="definition-error",
                node=my_class,
                args=(
                    "ParseErr",
                    DataJointError(
                        'Parsing error in line "[ParseErr] -> BadFKRef". '
                        + "Expected \"->\", found '['  (at char 0), "
                        + "(line:1, col:1)."
                    ),
                ),
                line=2,
                col_offset=0,
                end_line=2,
                end_col_offset=16,
            ),
        ):
            self.checker.visit_classdef(my_class)

    def test_mult_pk_ref(self, test_cases_bad):
        my_class = astroid.extract_node(test_cases_bad[14])
        self.checker._class_namespace.add("GoodTable1")
        with self.assertAddsMessages(
            MessageTest(
                msg_id="mult-fk-ref",
                node=my_class,
                args="MultiplePKRef",
                line=2,
                col_offset=0,
                end_line=2,
                end_col_offset=19,
            ),
        ):
            self.checker.visit_classdef(my_class)

    def test_no_definition(self, test_cases_bad):
        my_class = astroid.extract_node(test_cases_bad[15])
        with self.assertAddsMessages(
            MessageTest(
                msg_id="no-def",
                node=my_class,
                args="NoDefinition",
                line=2,
                col_offset=0,
                end_line=2,
                end_col_offset=13,
            ),
        ):
            self.checker.visit_classdef(my_class)
