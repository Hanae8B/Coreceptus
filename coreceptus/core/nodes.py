import math
from typing import Optional, Dict, Union, List

Context = Optional[Dict[str, Union[int, float]]]


class CoreNumber:
    def __init__(self, value: Union[int, float]):
        self.value = value

    def evaluate(self, context: Context = None) -> Union[int, float]:
        return self.value

    def __str__(self):
        return str(self.value)

    def simplify(self):
        return self

    def diff(self, var):
        return CoreNumber(0)


class CoreSymbol:
    def __init__(self, name: str):
        self.name = name

    def evaluate(self, context: Context = None) -> Union[int, float]:
        if context and self.name in context:
            return context[self.name]
        raise ValueError(f"Symbol '{self.name}' has no value in context")

    def __str__(self):
        return self.name

    def simplify(self):
        return self

    def diff(self, var):
        if self.name == var.name:
            return CoreNumber(1)
        else:
            return CoreNumber(0)


class CoreExpression:
    def __init__(self, left, operator: str, right=None):
        self.left = left
        self.operator = operator
        self.right = right

    def evaluate(self, context: Context = None) -> Union[int, float]:
        if self.operator == '-' and self.right is None:
            # Unary minus
            return -self.left.evaluate(context)

        left_val = self.left.evaluate(context)
        right_val = self.right.evaluate(context) if self.right else None

        if self.operator == '+':
            return left_val + right_val
        elif self.operator == '-':
            return left_val - right_val
        elif self.operator == '*':
            return left_val * right_val
        elif self.operator == '/':
            return left_val / right_val
        elif self.operator == '^':
            return left_val ** right_val
        else:
            raise ValueError(f"Unknown operator: {self.operator}")

    def __str__(self):
        if self.operator == '-' and self.right is None:
            return f"(-{self.left})"
        return f"({self.left} {self.operator} {self.right})"

    def simplify(self):
        left = self.left.simplify()
        right = self.right.simplify() if self.right else None

        # Unary minus simplification
        if self.operator == '-' and right is None:
            if isinstance(left, CoreNumber):
                return CoreNumber(-left.value)
            return CoreExpression(left, '-', None)

        # Simplify known operations with numbers
        if right is not None:
            if isinstance(left, CoreNumber) and isinstance(right, CoreNumber):
                value = self.evaluate()
                return CoreNumber(value)

            # Simplify 0 + x = x, x + 0 = x
            if self.operator == '+':
                if isinstance(left, CoreNumber) and left.value == 0:
                    return right
                if isinstance(right, CoreNumber) and right.value == 0:
                    return left

                # Special case: x + x = 2 * x
                if str(left) == str(right):
                    return CoreExpression(CoreNumber(2), '*', left).simplify()

            # Simplify x - 0 = x
            if self.operator == '-':
                if isinstance(right, CoreNumber) and right.value == 0:
                    return left

                # Special case: x - x = 0
                if str(left) == str(right):
                    return CoreNumber(0)

            # Simplify x * 1 = x, 1 * x = x
            if self.operator == '*':
                if isinstance(left, CoreNumber):
                    if left.value == 1:
                        return right
                    if left.value == 0:
                        return CoreNumber(0)
                if isinstance(right, CoreNumber):
                    if right.value == 1:
                        return left
                    if right.value == 0:
                        return CoreNumber(0)

            # Simplify x / 1 = x
            if self.operator == '/':
                if isinstance(right, CoreNumber) and right.value == 1:
                    return left

            # Simplify x ^ 0 = 1
            if self.operator == '^':
                if isinstance(right, CoreNumber) and right.value == 0:
                    return CoreNumber(1)
                if isinstance(right, CoreNumber) and right.value == 1:
                    return left

        return CoreExpression(left, self.operator, right)

    def diff(self, var):
        # Derivative of unary minus
        if self.operator == '-' and self.right is None:
            return CoreExpression(self.left.diff(var), '-', None)

        # Use product, sum, power rules
        if self.operator == '+':
            return CoreExpression(self.left.diff(var), '+', self.right.diff(var))
        elif self.operator == '-':
            return CoreExpression(self.left.diff(var), '-', self.right.diff(var))
        elif self.operator == '*':
            # Product rule: (f*g)' = f'*g + f*g'
            left_diff = CoreExpression(self.left.diff(var), '*', self.right)
            right_diff = CoreExpression(self.left, '*', self.right.diff(var))
            return CoreExpression(left_diff, '+', right_diff)
        elif self.operator == '/':
            # Quotient rule: (f/g)' = (f'*g - f*g')/g^2
            numerator = CoreExpression(
                CoreExpression(self.left.diff(var), '*', self.right),
                '-',
                CoreExpression(self.left, '*', self.right.diff(var)),
            )
            denominator = CoreExpression(self.right, '^', CoreNumber(2))
            return CoreExpression(numerator, '/', denominator)
        elif self.operator == '^':
            # Handle power rule if exponent is a number
            if isinstance(self.right, CoreNumber):
                n = self.right.value
                new_exp = CoreNumber(n - 1)
                base_diff = self.left.diff(var)
                coef = CoreNumber(n)
                return CoreExpression(
                    CoreExpression(coef, '*', CoreExpression(self.left, '^', new_exp)),
                    '*',
                    base_diff,
                )
            else:
                # Generalized power differentiation (f^g)'
                # f^g * (g' * ln(f) + g * f'/f)
                f = self.left
                g = self.right
                f_diff = f.diff(var)
                g_diff = g.diff(var)
                ln_f = CoreFunction("ln", [f])
                term1 = CoreExpression(g_diff, '*', ln_f)
                term2 = CoreExpression(g, '*', CoreExpression(f_diff, '/', f))
                return CoreExpression(self, '*', CoreExpression(term1, '+', term2))
        else:
            raise ValueError(f"Unknown operator: {self.operator}")


class CoreFunction:
    def __init__(self, name: str, args: List):
        self.name = name
        self.args = args

    def evaluate(self, context: Context = None) -> Union[int, float]:
        evaluated_args = [arg.evaluate(context) for arg in self.args]

        if self.name == "sum":
            return sum(evaluated_args)
        elif self.name == "sin":
            return math.sin(evaluated_args[0])
        elif self.name == "cos":
            return math.cos(evaluated_args[0])
        elif self.name == "tan":
            return math.tan(evaluated_args[0])
        elif self.name == "exp":
            return math.exp(evaluated_args[0])
        elif self.name == "ln":
            return math.log(evaluated_args[0])
        elif self.name == "log":
            if len(evaluated_args) == 1:
                return math.log(evaluated_args[0])
            elif len(evaluated_args) == 2:
                return math.log(evaluated_args[0], evaluated_args[1])
            else:
                raise ValueError(f"Invalid number of arguments for log: {len(evaluated_args)}")
        elif self.name == "sqrt":
            return math.sqrt(evaluated_args[0])
        else:
            raise ValueError(f"Unknown function: {self.name}")

    def __str__(self):
        args_str = ", ".join(str(arg) for arg in self.args)
        return f"{self.name}({args_str})"

    def simplify(self):
        simplified_args = [arg.simplify() for arg in self.args]
        # If all args are numbers, evaluate
        if all(isinstance(arg, CoreNumber) for arg in simplified_args):
            value = self.evaluate()
            return CoreNumber(value)
        else:
            return CoreFunction(self.name, simplified_args)

    def diff(self, var):
        # Differentiation rules for some functions
        arg = self.args[0]
        d_arg = arg.diff(var)

        if self.name == "sin":
            return CoreExpression(CoreFunction("cos", [arg]), "*", d_arg)
        elif self.name == "cos":
            return CoreExpression(
                CoreExpression(CoreNumber(-1), "*", CoreFunction("sin", [arg])),
                "*",
                d_arg,
            )
        elif self.name == "tan":
            sec2 = CoreExpression(CoreFunction("sec", [arg]), "^", CoreNumber(2))
            # We'll define sec(x) = 1/cos(x) if needed, but for now not implemented
            # So just use (1 / cos(x))^2
            # For simplicity, we'll return derivative as (1 / cos(x))^2 * d_arg
            return CoreExpression(
                CoreExpression(CoreNumber(1), "/", CoreExpression(CoreFunction("cos", [arg]), "^", CoreNumber(2))),
                "*",
                d_arg,
            )
        elif self.name == "exp":
            return CoreExpression(CoreFunction("exp", [arg]), "*", d_arg)
        elif self.name == "ln":
            return CoreExpression(CoreExpression(CoreNumber(1), "/", arg), "*", d_arg)
        elif self.name == "sqrt":
            # d/dx sqrt(x) = 1 / (2*sqrt(x))
            denominator = CoreExpression(CoreNumber(2), "*", CoreFunction("sqrt", [arg]))
            return CoreExpression(CoreExpression(CoreNumber(1), "/", denominator), "*", d_arg)
        else:
            raise NotImplementedError(f"Derivative of function '{self.name}' not implemented.")
