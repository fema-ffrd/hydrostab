# hydrostab
Hydrograph stability

## Developer Setup
Create a virtual environment in the project directory:
```
$ python -m venv venv-hydrostab
```

Activate the virtual environment:
```
$ source ./venv-hydrostab/bin/activate
(venv-hydrostab) $
```

Install the package in editable mode:
```
(venv-hydrostab) $ pip install -e .
```

Install dev dependencies:
```
(venv-hydrostab) $ pip install ".[dev]"

```

Install dependencies for notebooks (note that we're using 
[jupytext](https://jupytext.readthedocs.io/en/latest/) 
to sync notebooks as Markdown documents):
```
(venv-hydrostab) $ pip install ".[nb]"
```

Install git hook scripts (used for automatic liniting/formatting)
```
(venv-hydrostab) $ pre-commit install
```

With the virtual environment activated, run the tests:
```
(venv-hydrostab) $ pytest
```