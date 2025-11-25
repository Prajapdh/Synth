# Synth

Install uv:
```
pip install --upgrade uv
```

Creating a virtual environment
uv supports creating virtual environments, e.g., to create a virtual environment at .venv:
```
uv venv
```

A specific name or path can be specified, e.g., to create a virtual environment at my-name:
```
uv venv my-name
```

Activate virtual environment:
```
.venv\Scripts\activate
```

Install all dependencies:
```
uv pip install -r requirements.txt
```

To run the main file:
```
uv run main.py
```
