# Formula Evaluation API

This project is a RESTful API built with **FastAPI** that allows users to evaluate mathematicall formulas based on variable inputs. it performs dynamic formula evaluation using the `numexpr` library, supporting chained calculations where outputs from one formula can be used as inputs in another.

## Features

- **Dynamic Formula Evaluation**: Evaluate complex mathematical expressions with variable provided in the request.
- **Chained Calculations**: Use results from one formula as input for subsequent formulas.
- **Error Handlings**: Provides detailed error messages for missing variables and formula evaluation issues.

## Table of Contents

- [Requirements](#requirements)
- [Dependencies](#dependencies)
- [Installation](#installation)
- [Deployment](#deployment)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Error Handling](#error-handling)



## Requirements

Before setting up the project, ensure you have the following installed :

- **Python 3.7+**
- **Pip** (Python package manager)
- **Virtual enviornment** (optional but recommended for dependency isolation)

To check if you have these installed, run:

```bash
python --version
pip --verion
```

## Dependencies

This project relies on the following key dependencies:

- **FastAPI**: A modern, fast (high-performance) web framewordk for building APIs with Python 3.7+ based on standard Python type hints.

    Install FastAPI:
    ```bash
    pip install fastapi
    ```

- **Uvicorn**: A lightning-fast ASGI server for Python web applications, used to run FastAPI applications.

    Install Uvicorn:
    ```bash
    pip install uvicorn
    ```

- **NumExpr**: A fast numerical expression evaluator for array-based calculations, used for evaluating formulas in this API.

    Install NumExpr:
    ```bash
    pip install numexpr
    ```

- **Pydantic** (included with FastAPI): A data validation and settings management library, used to validate input data based on schema definitions.

Other dependencies may be specified in the `requirements.txt` file.

## Installation

1. Unzip the repository.
2. Navigate to the project directory.
    ```bash
    cd formula-evaluation-api
    ```
3. Create a virtual environment (optional but recommended)
    ```bash
    python -m venv venv
    ```
4. Activate the virtual environment.
    - On macOS/Linux
        ```bash
        source venv/bin/activare
        ```
    - On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
5. Install the required dependencies.
    ```bash
    pip install -r requirements.txt
    ```

## Deployment
There are several ways to deploy a FastAPI application. Below are two common methods:
### 1. Running Locally with Uvicorn
The easiest way to start your FastAPI server for local development is by using **Uvicorn**
1. After installation, run the following command to start the application:
    ```bash
    uvicorn main:app --reload
    ```
2. Open your browser and navigate to `http://127.0.0.1:8000/docs` to see the API documentation in **Swagger UI**.

### 2. Deploying to Production with Gunicorn + Uvicorn workers
For production deployment, it's recommended to use a process manager like **Gunicorn** with **Uvicorn** workers:
1. Install Gunicorn:
    ```bash
    pip install gunicorn
    ```
2. Run the application with Gunicorn and Uvicorn workers:
    ```bash
    gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
    ```
This will run your FastAPI application with 4 worker processes for better concurrency and performance.

## Usage
Once the server is running, you can access the API at `http://127.0.0.1:8000`. Use the `/api/execute-formula` endpoint to evaluate formulas based on your provided data.

## API Endpoints
`POST /api/execute-formula`
This endpoint allows you to evaluate multiple formulas based on variable inputs.

## Error Handling
- **400 Bad Reequest**: If a required variable is missing in the data or an error occurs during formula evaluation.

    Example:
    ```json
    {
      "detail": "Variable 'varName' not found in data item with id 'unknown'"
    }
    ```

- **500 Internal Server Error**: For any server-side issues or unexpected errors
