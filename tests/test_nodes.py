import pytest
import math

from coreceptus.core.nodes import (
    CoreNumber,
    CoreSymbol,
    CoreExpression,
    CoreFunction,
)


def test_core_number_evaluation():
    num = CoreNumber(42)
    assert num.evaluate() == 42
    assert str(num) == "42"
    print(f"CoreNumber: {num} evaluates to {num.evaluate()}", flush=True)


def test_core_symbol_with_context():
    sym = CoreSymbol("x")
    context = {"x": 10}
    assert sym.evaluate(context) == 10
    assert str(sym) == "x"
    print(f"CoreSymbol: {sym} with context {context} evaluates to {sym.evaluate(context)}", flush=True)


def test_core_symbol_without_context():
    sym = CoreSymbol("y")
    with pytest.raises(ValueError, match="Symbol 'y' has no value in context"):
        sym.evaluate()


def test_core_expression_addition():
    expr = CoreExpression(CoreNumber(5), "+", CoreNumber(3))
    assert expr.evaluate() == 8
    assert str(expr) == "(5 + 3)"
    print(f"CoreExpression number addition: {expr} evaluates to {expr.evaluate()}", flush=True)


def test_core_expression_mixed():
    expr = CoreExpression(CoreSymbol("a"), "*", CoreNumber(2))
    context = {"a": 4}
    assert expr.evaluate(context) == 8
    assert str(expr) == "(a * 2)"
    print(f"CoreExpression mixed: {expr} with context {context} evaluates to {expr.evaluate(context)}", flush=True)


@pytest.mark.parametrize("op, expected", [
    ("+", 15),
    ("-", 5),
    ("*", 50),
    ("/", 2),
    ("^", 100000),
])
def test_core_expression_operations(op, expected):
    left = CoreNumber(10)
    right = CoreNumber(5)
    expr = CoreExpression(left, op, right)
    assert expr.evaluate() == expected
    print(f"CoreExpression operation {left} {op} {right} evaluates to {expr.evaluate()}", flush=True)


def test_core_expression_unary_minus():
    expr = CoreExpression(CoreNumber(5), "-", None)
    assert expr.evaluate() == -5
    assert str(expr) == "(-5)"
    print(f"CoreExpression unary minus: {expr} evaluates to {expr.evaluate()}", flush=True)


def test_core_function_sum():
    fn = CoreFunction("sum", [CoreNumber(1), CoreNumber(2), CoreNumber(3)])
    assert fn.evaluate() == 6
    assert str(fn) == "sum(1, 2, 3)"
    print(f"CoreFunction sum: {fn} evaluates to {fn.evaluate()}", flush=True)


def test_core_function_sum_with_symbol():
    fn = CoreFunction("sum", [CoreNumber(2), CoreSymbol("x")])
    context = {"x": 5}
    result = fn.evaluate(context)
    assert result == 7
    print(f"CoreFunction sum with symbol: {fn} with context {context} evaluates to {result}", flush=True)


def test_core_function_unknown():
    with pytest.raises(ValueError, match="Unknown function: unknown"):
        CoreFunction("unknown", [CoreNumber(1)]).evaluate()


@pytest.mark.parametrize("func_name, arg_value, expected_value", [
    ("sin", math.pi / 2, 1),
    ("cos", 0, 1),
    ("tan", 0, 0),
    ("exp", 1, math.exp(1)),
    ("ln", math.e, 1),
    ("log", 100, math.log(100)),
    ("log", (8, 2), 3),  # log base 2 of 8 = 3
    ("sqrt", 16, 4),
])
def test_core_function_math_functions(func_name, arg_value, expected_value):
    from math import isclose
    if func_name == "log" and isinstance(arg_value, tuple):
        args = [CoreNumber(arg_value[0]), CoreNumber(arg_value[1])]
    else:
        args = [CoreNumber(arg_value)]
    fn = CoreFunction(func_name, args)
    result = fn.evaluate()
    assert isclose(result, expected_value, rel_tol=1e-9)
    print(f"CoreFunction {func_name}: {fn} evaluates to {result}", flush=True)


def test_unification_of_numbers_and_symbols():
    n1 = CoreNumber(3)
    s1 = CoreSymbol("y")
    expr = CoreExpression(n1, "+", s1)
    context = {"y": 7}
    val = expr.evaluate(context)
    assert val == 10
    assert isinstance(expr.left, CoreNumber)
    assert isinstance(expr.right, CoreSymbol)
    print(f"Unified Expression: {expr} with context {context} evaluates to {val}", flush=True)


def test_nested_expression_mixed():
    expr1 = CoreExpression(CoreSymbol("x"), "*", CoreNumber(2))
    expr2 = CoreExpression(CoreNumber(5), "+", expr1)
    context = {"x": 4}
    val = expr2.evaluate(context)
    assert val == 13  # 5 + (4*2)
    print(f"Nested Expression: {expr2} with context {context} evaluates to {val}", flush=True)


def test_simplification():
    # 0 + x -> x
    expr = CoreExpression(CoreNumber(0), "+", CoreSymbol("x"))
    simplified = expr.simplify()
    assert str(simplified) == "x"

    # x * 1 -> x
    expr = CoreExpression(CoreSymbol("x"), "*", CoreNumber(1))
    simplified = expr.simplify()
    assert str(simplified) == "x"

    # x ^ 0 -> 1
    expr = CoreExpression(CoreSymbol("x"), "^", CoreNumber(0))
    simplified = expr.simplify()
    assert isinstance(simplified, CoreNumber)
    assert simplified.value == 1

    # 0 * x -> 0
    expr = CoreExpression(CoreNumber(0), "*", CoreSymbol("x"))
    simplified = expr.simplify()
    assert isinstance(simplified, CoreNumber)
    assert simplified.value == 0
    print("Simplification tests passed", flush=True)


def test_differentiation_basic():
    x = CoreSymbol("x")
    c = CoreNumber(5)

    # derivative of constant = 0
    assert c.diff(x).evaluate() == 0

    # derivative of symbol w.r.t itself = 1
    assert x.diff(x).evaluate() == 1

    # derivative of symbol w.r.t different symbol = 0
    y = CoreSymbol("y")
    assert y.diff(x).evaluate() == 0

    # derivative of sum: d/dx(x + 5) = 1 + 0 = 1
    expr = CoreExpression(x, "+", c)
    diff_expr = expr.diff(x).simplify()
    assert diff_expr.evaluate() == 1

    # derivative of product: d/dx(x * x) = x*1 + x*1 = 2x
    expr = CoreExpression(x, "*", x)
    diff_expr = expr.diff(x).simplify()
    # expect string with 2 and x in it
    assert "2" in str(diff_expr) and "x" in str(diff_expr)
    print(f"Differentiated expression: {diff_expr}", flush=True)


def test_differentiation_function():
    x = CoreSymbol("x")

    expr = CoreFunction("sin", [x])
    diff_expr = expr.diff(x)
    assert "cos(x)" in str(diff_expr)

    expr = CoreFunction("ln", [x])
    diff_expr = expr.diff(x)
    assert "1 / x" in str(diff_expr) or "(1 / x)" in str(diff_expr)

    expr = CoreFunction("exp", [x])
    diff_expr = expr.diff(x)
    assert "exp(x)" in str(diff_expr)
    print("Differentiation of functions tests passed", flush=True)


def test_differentiation_power():
    x = CoreSymbol("x")
    c2 = CoreNumber(2)

    # d/dx x^2 = 2*x
    expr = CoreExpression(x, "^", c2)
    diff_expr = expr.diff(x).simplify()
    assert "2" in str(diff_expr) and "x" in str(diff_expr)
    print(f"Differentiated power expression: {diff_expr}", flush=True)


def test_core_function_simplify_evaluate():
    # sum of numbers simplifies to CoreNumber with value 6
    fn = CoreFunction("sum", [CoreNumber(1), CoreNumber(2), CoreNumber(3)])
    simplified = fn.simplify()
    assert isinstance(simplified, CoreNumber)
    assert simplified.value == 6

    # sin(pi/2) simplifies to CoreNumber(1)
    fn = CoreFunction("sin", [CoreNumber(math.pi / 2)])
    simplified = fn.simplify()
    assert isinstance(simplified, CoreNumber)
    assert abs(simplified.value - 1) < 1e-9
    print("Function simplification and evaluation tests passed", flush=True)
