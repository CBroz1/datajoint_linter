# DataJoint Linter

Linting tool for DataJoint table classes. Catching issues in the IDE, before
declaration.

## Installation

```bash
git clone https://github.com/CBroz1/datajoint_linter
pip install datajoint_linter # in default python environment
```

### VSCode

__NOTE__: Work in progress

1. Install the
    [PyLint Extension](https://marketplace.visualstudio.com/items?itemName=ms-python.pylint)

2. Test your installation on the example schema to see example errors.

    ```console
    cd datajoint_linter
    pylint tests/schema_bad.py
    ```

3. Find your pylint path

    ```console
    whereis pylint
    ```

4. Add the following to your `settings.json` file:

    ```json
    {
        "pylint.path": [
            "/your/path/pylint"
        ],
        "pylint.args": [
            "--load-plugins=datajoint_linter",
            "--permit-dj-filepaths=y", 
            "--disable=E0401,W0401,W0611,W0621"
        ]
    }
    ```

`permit-dj-filepath` will quiet warnings about use of filepath datatypes.

The above disable codes are recommended for any DataJoint project. They disable

- E0401: Unable to import - install packages vary by environment
- E0102: Function redefined - for Merge tables
- W0611: Unused import - for foreign key imports
- W0621: Outer scope - false positives on key in make

## Neovim

`null-ls` is now deprecated. Alternative configs (e.g, `efm-langserver`) may
look similar.

```lua
local null_ls = require "null-ls"
local lint = null_ls.builtins.diagnostics
local sources = {
    lint.pylint.with({ extra_args = {
        "--load-plugins=datajoint_linter",
        "--permit-dj-filepaths=y", 
        "--disable=E0401,W0401,W0611,W0621"
    }})
}
```

## How it works

This package is a static analysis tool of the `definition` for standard Tables
(plus `_Merge` tables). It will catch ...

- Bad data types
- Definition syntax errors (e.g., nullable primary key)
- Foreign key references to objects not in the namespace

Without running your code, it won't catch foreign type errors. For example,

- `-> m.NonexistentClass` will only be checked before the `.` to test for the
    presence `mm` in the namespace (e.g, `import my_module as m`)
- `-> imported_obj` will only be checked for the presence of `imported_obj` in
    the namespace (e.g., `from my_module import imported_obj`). It will not
    check that DataJoint supports referencing this object type as foreign keys.
- `-> Table.proj(new='bad_key')` will not be caught as the linter does not check
    the contents of projections

This linter also does not execute checks to see if filepath types have been
enabled in the user's environment. To enable them, use the
`--permit-dj-filepaths` flag.

## Tests

Tests passing as of `datajoint-python` version `0.14.1`.

```console
pytest .
```

## To do

Portions of the linter rely on extracted pieces from DataJoint's
`compile_foreign_key` method syntax because the `prepare_declare` without any
`context`, which prempively hits the first error in this method. This project
could either ...

1. Run dynamic analysis, to fully process foreign key references in context.
2. PR to `datajoint-python` to extract pieces of declaration into private
    methods to be reused here.
