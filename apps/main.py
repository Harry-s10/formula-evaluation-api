import re
import numexpr
import uvicorn

from fastapi import FastAPI, HTTPException, status
from dateutil.parser import parse as parse_date
from typing import Any, Dict, List
from . import schemas

app = FastAPI()


def parse_currency(value: str) -> float:
    """
    Parses a string representing currency into a float.

    Args:
        value (str): string representing currency

    Returns:
        float representing currency value

    Raises:
        ValueError: invalid currency format

    """
    # Regular expression to match different currency formats (ISO, symbols, etc.)
    currency_pattern = r'([A-Za-z]{3})?\s?\$?\s?([0-9,.]+)'
    match = re.match(currency_pattern, value.replace(',', ''))
    if match:
        return float(match.group(2))
    raise ValueError(f"Invalid currency format: {value}")


def convert_variable(value: Any, var_type: str) -> Any:
    """
    Convert the input variable to the appropriate type based on var_type.
    Args:
        value (Any): input variable value
        var_type (str): input variable type

    Returns:
        Converted input variable value
    """
    try:
        if var_type == "number":
            return float(value)
        elif var_type == "boolean":
            return bool(value)
        elif var_type == "datetime":
            return parse_date(value) if isinstance(value, str) else value
        elif var_type == "percentage":
            if isinstance(value, str) and value.endswith('%'):
                return float(value.strip('%'))
            return float(value)
        elif var_type == "currency":
            if isinstance(value, str):
                return parse_currency(value)
            return float(value)
    except ValueError as e:
        raise ValueError(e)
    raise ValueError(f"Unsupported variable type: {var_type}")


def validate_formulas(data: List[Dict[str, Any]], formulas: List[schemas.Formula]):
    """
    Validate that the submitted expression is both syntactically correctly and feasible based on provided inputs.

    The functions perform syntax checks on the expression and ensures that all variable literals used within the formula
    are defined in the provided input dictionary. If any variable in the expression is not present in the input data,
    an error is raised.

    Args:
        data (List[Dict[str, Any]]: Input data variables
        formulas (List[schemas.Formula]): List of formulas need to validate

    Raises:
        ValueError: If the expression contains undefined variable or has syntax errors.
    """
    available_vars = set(data[0].keys())  # All keys from the first data item
    evaluated_vars = set()

    for formula in formulas:
        # Check if all input variables exist either in available_vars or evaluated_vars
        for input_var in formula.inputs:
            if input_var.varName not in available_vars and input_var.varName not in evaluated_vars:
                raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Variable '{input_var.varName}' used in formula '{formula.outputVar}' is not "
                               f"available in data or prior formulas."
                )

        # Prevent circular references (outputVar cannot be an input of its own formula)
        if formula.outputVar in [input_var.varName for input_var in formula.inputs]:
            raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Formula '{formula.outputVar}' cannot reference itself in its inputs."
            )

        # Check for valid expression syntax using numexpr's parsing
        try:
            numexpr.evaluate(formula.expression, local_dict={var.varName: 1 for var in formula.inputs})
        except Exception as e:
            raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error evaluating expression: syntax error in formula '{formula.outputVar}' with expression '{formula.expression}': {str(e)}"
            )

        # Add the formula's output variable to the list of evaluated variables
        evaluated_vars.add(formula.outputVar)


@app.post("/api/execute-formula")
async def evaluate_formulas(request: schemas.FormulaRequest):
    """
    Receives the request to evaluate formulas.

    This function will validate the formulas and then evaluate the formulas to generate the result.
    Args:
        request (schemas.FormulaRequest): Request body

    Returns:
        Response with results

    Raises:
        HTTPException: Situation where input variable is not present in the data. Error while evaluating the expression. Or any internal serval error.

    """
    try:
        data_items = request.data
        formulas = request.formulas
        if len(data_items) == 0:
            raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Empty data"
            )
        if len(formulas) == 0:
            raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Empty formulas"
            )
        # Validate the formulas
        validate_formulas(data_items, formulas)

        # Dictionary to store results per outputVar
        results = {formula.outputVar: [] for formula in formulas}

        # Process each data item
        for item in data_items:
            # Clone the item dictionary to keep track of dynamic changes for each data point
            local_item = item.copy()

            # For each formula
            for formula in formulas:
                # Prepare variables for the expression
                variables = {}
                for input_var in formula.inputs:
                    var_name = input_var.varName
                    if var_name in local_item:
                        try:
                            variables[var_name] = convert_variable(local_item[var_name], input_var.varType)
                        except Exception as e:
                            raise HTTPException(
                                    status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"Error while converting variable: {e}"
                            )
                    else:
                        raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Variable '{var_name}' not found in data item with id {item.get('id', 'unknown')}"
                        )

                # Evaluate the expression using the variables
                try:
                    result = numexpr.evaluate(formula.expression, local_dict=variables)
                    # Convert result to a native Python type (if necessary)
                    result_value = result.item() if hasattr(result, 'item') else result
                    # Store the result in the results dictionary under the formula's outputVar
                    results[formula.outputVar].append(result_value)
                    # Update local_item so the result can be used in subsequent formulas
                    local_item[formula.outputVar] = result_value
                except Exception as e:
                    raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error evaluating expression '{formula.expression}': {str(e)}"
                    )

        # Return the results in the specified format
        return {
            "results": results,
            "status" : "success",
            "message": "The formulas were executed successfully with variable-based chaining."
        }
    except HTTPException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.detail))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


if __name__ == '__main__':
    uvicorn.run('main:app')
