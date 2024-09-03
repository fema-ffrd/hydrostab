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

Install dev dependencies:
```
(venv-hydrostab) $ pip install ".[dev]"
```

Install git hook scripts (used for automatic liniting/formatting)
```
(venv-hydrostab) $ pre-commit install
```

With the virtual environment activated, run the tests:
```
(venv-hydrostab) $ pytest
```