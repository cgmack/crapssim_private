# Technical Context

## Technologies Used
- **Primary Language**: Python 3.x
- **Type Safety**: `pydantic` for runtime type enforcement and `mypy` for static type checking
- **Testing Framework**: `pytest` for unit and integration testing.
- **Documentation**: `Sphinx` (likely, given `docs/conf.py` and `docs/Makefile`).
- **Dependency Management**: `pip` and `requirements.txt` 
- **Data Persistance**: `postgresql`
- **API**: Fastapi and Uvicorn
- **Front End**: `React` with `Vite`

## Development Setup
- **Virtual Environment**: Development containers will be used. Therefore addiitonl  Python virtual environment  `venv` is not required.
- **Installation**: Dependencies are listed in `requirements.txt`. Installation typically involves `pip install -r requirements.txt`.
- **Running Tests**: Tests can be executed using `pytest` from the project root.

## Technical Constraints
- **Accuracy**: The simulation must accurately reflect the rules and probabilities of craps.
- **Performance**: Simulations, especially for a large number of iterations, need to be reasonably performant. 
- **Maintainability**: Code should be clean, well-documented, and follow Python best practices to ensure long-term maintainability.

## Tool Usage Patterns
- **Code Editing**: VSCode with Roo Code
- **Version Control**: `git` for source code management.
- **Testing**: Frequent execution of `pytest` during development.
- **Documentation Generation**: `Sphinx` commands for building documentation.