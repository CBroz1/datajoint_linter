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

1. Install the [PyLint Extension](https://marketplace.visualstudio.com/items?itemName=ms-python.pylint)
1. Add the following to your `settings.json` file:

```json
{
    "pylint.args": [
        "--load-plugins=datajoint_linter",
        "--disable=E0401,W0401,W0611,W0621"
    ]
}
```

These disable codes are recommended for any DataJoint project. They disable

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

- `-> m.NonexistentClass` will only be checked before the `.` to test
    for the presence `mm` in the namespace (e.g, `import my_module as m`)
- `-> imported_obj` will only be checked for the persence of
    `imported_obj` in the namespace (e.g.,
    `from my_module import imported_obj`). It will not check that DataJoint
    supports referencing this object type  as foreign keys.
- `-> Table.proj(new='bad_key')` will not be caught as the linter does not check
    the contents of projections
