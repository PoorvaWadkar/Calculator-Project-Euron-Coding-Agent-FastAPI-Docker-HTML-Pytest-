"""Simple calculator service built with FastAPI."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Simple Calculator")


class Calculation(BaseModel):
    a: float
    b: float
    operation: str


@app.get("/")
def root():
    return {"message": "Calculator API. POST /calculate with {a, b, operation}."}


@app.post("/calculate")
def calculate(calc: Calculation) -> dict:
    op = calc.operation.strip().lower()
    if op == "+":
        result = calc.a + calc.b
    elif op == "-":
        result = calc.a - calc.b
    elif op == "*":
        result = calc.a * calc.b
    elif op == "/":
        if calc.b == 0:
            raise HTTPException(400, "Division by zero")
        result = calc.a / calc.b
    else:
        raise HTTPException(400, f"Unknown operation: {op}")
    return {"a": calc.a, "b": calc.b, "operation": op, "result": result}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
