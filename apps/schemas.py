from typing import Any, Dict, List

from pydantic import BaseModel


class InputVar(BaseModel):
    varName: str
    varType: str  # Can be "number", "boolean", "datetime", "currency", "percentage"


class Formula(BaseModel):
    outputVar: str
    expression: str
    inputs: List[InputVar]


class FormulaRequest(BaseModel):
    data: List[Dict[str, Any]]  # Data items with arbitrary fields
    formulas: List[Formula]
