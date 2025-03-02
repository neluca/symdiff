"""
A very simple implementation of symbolic differentiation
"""
import math


class Expr(object):
    _operand_name = None

    def __init__(self, *args):
        self._args = args

    def __add__(self, other):
        return Add(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def __sub__(self, other):
        return Sub(self, other)

    def __rsub__(self, other):
        return Sub(other, self)

    def __mul__(self, other):
        return Mul(self, other)

    def __rmul__(self, other):
        return Mul(other, self)

    def __truediv__(self, other):
        return Div(self, other)

    def __rtruediv__(self, other):
        return Div(other, self)

    def __pow__(self, other):
        return Pow(self, other)

    def __rpow__(self, other):
        return Pow(other, self)

    def __str__(self):
        terms = [str(item) for item in self._args]
        operand = self._operand_name
        return "({})".format(operand.join(terms))


class Variable(Expr):
    _operand_name = "Variable"
    __slots__ = ("name",)

    def __init__(self, name: str, *args):
        super().__init__(*args)
        try:
            assert isinstance(name, str)
        except:
            raise TypeError("name parameters should be string, get type {} instead".format(type(name)))
        finally:
            self.name = name

    def __str__(self):
        return self.name

    def diff(self, var):
        if self.name == var.name:
            return One()
        else:
            return Zero()


class Zero(Expr):
    _instance = None

    def __new__(cls, *args):
        if Zero._instance is None:
            obj = object.__new__(cls)
            obj.name = "0"
            return obj
        else:
            return Zero._instance

    def __str__(self):
        return "0"


class One(Expr):
    _instance = None

    def __new__(cls, *args):
        if One._instance is None:
            obj = object.__new__(cls)
            obj.name = "1"
            return obj
        else:
            return One._instance

    def __str__(self):
        return "1"


class Add(Expr):
    _operand_name = " + "

    def diff(self, var):
        terms = self._args
        terms_after_diff = [item.diff(var) for item in terms]
        return Add(*terms_after_diff)


class Sub(Expr):
    _operand_name = " - "

    def diff(self, var):
        terms = self._args
        terms_after_diff = [item.diff(var) for item in terms]
        return Sub(*terms_after_diff)


class Mul(Expr):
    _operand_name = " * "

    def diff(self, var):
        terms = self._args
        if len(terms) != 2:
            raise ValueError("Mul operation takes only 2 parameters")
        terms_after_diff = [item.diff(var) for item in terms]

        return Add(*terms_after_diff)


class Pow(Expr):
    _operand_name = " ** "

    def diff(self, var):
        base = self._args[0]  # Base
        pow = self._args[1]  # Exponent
        dbase = base.diff(var)
        dpow = pow.diff(var)
        if isinstance(base, (int, float)):
            return self * dpow * Log(base)
        elif isinstance(pow, (int, float)):
            return self * dbase * pow / base
        else:
            return self * (dpow * Log(base) + dbase * pow / base)


class Div(Expr):
    _operand_name = " / "

    def diff(self, var):
        numerator = self._args[0]  # Numerator
        denominator = self._args[1]  # Denominator
        d_numerator = numerator.diff(var)
        d_denominator = denominator.diff(var)
        if isinstance(numerator, (int, float)):
            # If the numerator is a constant
            return Zero() - d_denominator * numerator / denominator ** 2
        elif isinstance(denominator, (int, float)):
            # If the denominator is a constant
            return d_numerator / denominator
        else:
            return d_numerator / denominator - d_denominator * numerator / denominator ** 2


class Log(Expr):
    def __str__(self):
        return f"log({str(self._args[0])})"

    def diff(self, var):
        return self._args[0].diff(var) / self._args[0]


def diff(function, var):
    return function.diff(var)


log = math.log


def grad(fun, arg_i=0):
    """
    Construct a function that computes the gradient of the input function.
        fun: The function to be differentiated. The position of the variable to be differentiated is specified by arg_i.
             The function must return a single value (not an array).
        arg_i: Optional parameter, must be an integer, specifying the variable to be differentiated. Default is
        the first parameter.

    Returns:
       A function with the same input structure as fun, which computes the gradient of fun.
    """

    def df(*args):
        namespace = []
        for i in range(len(args)):
            namespace.append("arg" + str(i))
        var_list = [Variable(name) for name in namespace]
        expr = str(diff(fun(*var_list), var_list[arg_i]))
        for i in range(len(args)):
            exec("{} = {}".format(namespace[i], args[i]))
        return eval(expr)

    return df
