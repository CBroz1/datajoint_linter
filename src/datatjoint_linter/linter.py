import inspect
import json

import datajoint as dj


class DataJointLinter:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def lint(self):
        # Find all subclasses of dj.Table
        for name, obj in inspect.getmembers(dj):
            if inspect.isclass(obj) and issubclass(obj, dj.Table):
                self.check_definition(obj)

    def check_definition(self, table_class):
        # Check the definition attribute of the table class
        if hasattr(table_class, "definition"):
            definition = getattr(table_class, "definition")
            if not isinstance(definition, dj.schema._definition.Definition):
                self.errors.append(
                    {"message": f"Invalid definition in {table_class.__name__}"}
                )
            else:
                self.check_data_types(definition)

    def demo_line_no(self, definition):
        definition_lines = definition.split("\n")

        # Iterate through the lines of the definition
        for line_number, line in enumerate(definition_lines, start=1):
            # Check for issues in the line (you can replace this with your own logic)
            if "varchar" in line.lower():
                # If an issue is found, add it to the linting_results list
                self.errors.append(
                    {
                        "message": "Use of 'varchar' detected in the definition",
                        "line": line_number,  # Line number where the issue was found
                        "column": line.find("varchar")
                        + 1,  # Column number where 'varchar' starts
                    }
                )

    def check_data_types(self, definition):
        for field_name, field_type in definition.describe():
            if not self.is_valid_data_type(field_type):
                self.errors.append(
                    {
                        "message": f"Invalid data type '{field_type}' in definition"
                    }
                )

    def is_valid_data_type(self, data_type):
        # Define a list of valid MySQL data types
        valid_data_types = [
            "int",
            "smallint",
            "tinyint",
            "mediumint",
            "bigint",
            "float",
            "double",
            "decimal",
            "char",
            "varchar",
            "text",
            "longtext",
            "binary",
            "varbinary",
            "blob",
            "longblob",
            # Add more valid data types as needed
        ]
        # Check if the data_type is valid
        return data_type.lower() in valid_data_types


if __name__ == "__main__":
    linter = DataJointLinter()
    linter.lint()
    if linter.errors:
        print(json.dumps(linter.errors, indent=4))
    else:
        print("No linting errors found.")
