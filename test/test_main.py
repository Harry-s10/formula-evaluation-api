import pytest
from httpx import ASGITransport, AsyncClient
from ..apps.main import app
from fastapi import status


@pytest.mark.asyncio
async def test_valid_formula_execution():
    request_data = {
        "data"    : [
            {
                "id"    : 1,
                "fieldA": 10
            },
            {
                "id"    : 2,
                "fieldA": 20
            }
        ],
        "formulas": [
            {
                "outputVar" : "result",
                "expression": "fieldA + 10",
                "inputs"    : [
                    {
                        "varName": "fieldA",
                        "varType": "number"
                    }
                ]
            }
        ]
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/execute-formula", json=request_data)
    assert response.status_code == 200

    json_response = response.json()
    assert json_response["status"] == "success"
    assert "results" in json_response
    assert json_response["results"]['result'] == [20, 30]
    assert json_response["message"] == "The formulas were executed successfully with variable-based chaining."


@pytest.mark.asyncio
async def test_missing_variable_in_data():
    request_data = {
        "data"    : [
            {
                "id"    : 1,
                "fieldA": 10,
                "fieldB": 30,
            },
            {
                "id"    : 2,
                "fieldA": 20
            }
        ],
        "formulas": [
            {
                "outputVar" : "result",
                "expression": "fieldA + fieldB",
                "inputs"    : [
                    {
                        "varName": "fieldA",
                        "varType": "number"
                    },
                    {
                        "varName": "fieldB",
                        "varType": "number"
                    }
                ]
            }
        ]
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/execute-formula", json=request_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    json_response = response.json()
    assert f"Variable 'fieldB' not found in {json_response['detail']}"


@pytest.mark.asyncio
async def test_invalid_variable_type():
    request_data = {
        "data"    : [
            {
                "id"    : 1,
                "fieldA": "Ten",
                "fieldB": 30,
            }
        ],
        "formulas": [
            {
                "outputVar" : "result",
                "expression": "fieldA + fieldB",
                "inputs"    : [
                    {
                        "varName": "fieldA",
                        "varType": "number"
                    },
                    {
                        "varName": "fieldB",
                        "varType": "number"
                    }
                ]
            }
        ]
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/execute-formula", json=request_data)
    assert response.status_code == 400
    json_response = response.json()
    assert "Error while converting variable" in json_response["detail"]


@pytest.mark.asyncio
async def test_formula_syntax_error():
    request_data = {
        "data"    : [
            {
                "id"    : 1,
                "fieldA": 10,
                "fieldB": 30
            }
        ],
        "formulas": [
            {
                "outputVar" : "result",
                "expression": "fieldA +",
                "inputs"    : [
                    {
                        "varName": "fieldA",
                        "varType": "number"
                    },
                    {
                        "varName": "fieldB",
                        "varType": "number"
                    }
                ]
            }
        ]
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/execute-formula", json=request_data)
    assert response.status_code == 400
    json_response = response.json()
    assert "Error evaluating expression" in json_response["detail"]


@pytest.mark.asyncio
async def test_empty_data_or_formula():
    request_data = {
        "data"    : [],  # No data points
        "formulas": [
            {
                "expression": "var1 + var2",
                "inputs"    : [
                    {"varName": "var1", "varType": "int"},
                    {"varName": "var2", "varType": "int"}
                ],
                "outputVar" : "result1"
            }
        ]
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/execute-formula", json=request_data)
    assert response.status_code == 400
    json_response = response.json()
    assert "Empty data" in json_response["detail"]  # This can be adjusted based on how your app handles empty data

    # Test case for empty formulas
    request_data = {
        "data"    : [
            {
                "id"  : 1,
                "var1": 10,
                "var2": 5
            }
        ],
        "formulas": []  # No formulas
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/execute-formula", json=request_data)
    assert response.status_code == 400
    json_response = response.json()
    assert "Empty formulas" == json_response["detail"]
