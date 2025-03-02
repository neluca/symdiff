"""
A very simple implementation of symbolic differentiation
"""
import math
from typing import TypeVar, Callable, Union

# Define a type variable for expressions
T = TypeVar("T", bound="Expr")
Num = Union[int, float]
ExprType = Union["Expr", Num]


class Expr(object):
    _operand_name: str = None

    def __init__(self, *args: ExprType):
        self._args = args

    def __add__(self, other: ExprType) -> "Add":
        return Add(self, other)

    def __radd__(self, other: ExprType) -> "Add":
        return Add(other, self)

    def __sub__(self, other: ExprType) -> "Sub":
        return Sub(self, other)

    def __rsub__(self, other: ExprType) -> "Sub":
        return Sub(other, self)

    def __mul__(self, other: ExprType) -> "Mul":
        return Mul(self, other)

    def __rmul__(self, other: ExprType) -> "Mul":
        return Mul(other, self)

    def __truediv__(self, other: ExprType) -> "Div":
        return Div(self, other)

    def __rtruediv__(self, other: ExprType) -> "Div":
        return Div(other, self)

    def __pow__(self, other: ExprType) -> "Pow":
        return Pow(self, other)

    def __rpow__(self, other: ExprType) -> "Pow":
        return Pow(other, self)

    def __str__(self) -> str:
        terms = [str(item) for item in self._args]
        operand = self._operand_name
        return "({})".format(operand.join(terms))

    def diff(self, var: "Variable") -> ExprType:
        raise NotImplementedError("Subclasses should implement this method")


class Variable(Expr):
    _operand_name: str = "Variable"
    __slots__ = ("name",)

    def __init__(self, name: str, *args: ExprType):
        super().__init__(*args)
        if not isinstance(name, str):
            raise TypeError("name parameter should be a string, got type {} instead".format(type(name)))
        self.name = name

    def __str__(self) -> str:
        return self.name

    def diff(self, var: "Variable") -> ExprType:
        if self.name == var.name:
            return One()
        else:
            return Zero()


class Zero(Expr):
    _instance: "Zero" = None

    def __new__(cls, *args: ExprType) -> "Zero":
        if cls._instance is None:
            obj = object.__new__(cls)
            obj.name = "0"
            cls._instance = obj
        return cls._instance

    def __str__(self) -> str:
        return "0"

    def diff(self, var: "Variable") -> "Zero":
        return self


class One(Expr):
    _instance: "One" = None

    def __new__(cls, *args: ExprType) -> "One":
        if cls._instance is None:
            obj = object.__new__(cls)
            obj.name = "1"
            cls._instance = obj
        return cls._instance

    def __str__(self) -> str:
        return "1"

    def diff(self, var: "Variable") -> "Zero":
        return Zero()


class Add(Expr):
    _operand_name: str = " + "

    def diff(self, var: "Variable") -> ExprType:
        terms = self._args
        terms_after_diff = [item.diff(var) for item in terms]
        return Add(*terms_after_diff)


class Sub(Expr):
    _operand_name: str = " - "

    def diff(self, var: "Variable") -> ExprType:
        terms = self._args
        terms_after_diff = [item.diff(var) for item in terms]
        return Sub(*terms_after_diff)


class Mul(Expr):
    _operand_name: str = " * "

    def diff(self, var: "Variable") -> ExprType:
        terms = self._args
        if len(terms) != 2:
            raise ValueError("Mul operation takes only 2 parameters")
        a, b = terms
        return Add(a.diff(var) * b, a * b.diff(var))


class Pow(Expr):
    _operand_name: str = " ** "

    def diff(self, var: "Variable") -> ExprType:
        base, exponent = self._args
        dbase = base.diff(var)
        dpow = exponent.diff(var)
        if isinstance(base, (int, float)):
            return self * dpow * Log(base)
        elif isinstance(exponent, (int, float)):
            return self * dbase * exponent / base
        else:
            return self * (dpow * Log(base) + dbase * exponent / base)


class Div(Expr):
    _operand_name: str = " / "

    def diff(self, var: "Variable") -> ExprType:
        numerator, denominator = self._args
        d_numerator = numerator.diff(var)
        d_denominator = denominator.diff(var)
        return (d_numerator * denominator - numerator * d_denominator) / (denominator ** 2)


class Log(Expr):
    def __str__(self) -> str:
        return f"log({str(self._args[0])})"

    def diff(self, var: "Variable") -> ExprType:
        return self._args[0].diff(var) / self._args[0]


def diff(function: Expr, var: Variable) -> ExprType:
    return function.diff(var)


log = math.log


def grad(fun: Callable[..., ExprType], arg_i: int = 0) -> Callable[..., ExprType]:
    """
    Construct a function that computes the gradient of the input function.
        fun: The function to be differentiated. The position of the variable to be differentiated is specified by arg_i.
             The function must return a single value (not an array).
        arg_i: Optional parameter, must be an integer, specifying the variable to be differentiated. Default is
        the first parameter.

    Returns:
       A function with the same input structure as fun, which computes the gradient of fun.
    """

    def df(*args: ExprType):
        namespace = [f"arg{i}" for i in range(len(args))]
        var_list = [Variable(name) for name in namespace]
        expr = str(diff(fun(*var_list), var_list[arg_i]))
        for i in range(len(args)):
            exec("{} = {}".format(namespace[i], args[i]))
        return eval(expr)

    return df
