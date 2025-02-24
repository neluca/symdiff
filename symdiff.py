import math


class Expr(object):
    _operand_name = None

    def __init__(self, *args):
        for arg in args:
            if isinstance(arg, (int, float)):
                arg = Variable(str(arg))
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

    def __init__(self, name: str):
        try:
            assert (isinstance(name, str))
        except:
            raise TypeError("name parameters should be string, \
                  get type {} instead".format(type(name)))
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
        base = self._args[0]  # 底数
        pow = self._args[1]   # 幂
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
        numer = self._args[0]  # 分子（被除数） numerator
        denom = self._args[1]  # 分母（除数）  denominator
        d_numer = numer.diff(var)
        d_denom = denom.diff(var)
        if isinstance(numer, (int, float)):
            # 如果分子是常数
            return Zero() - d_denom * numer / denom ** 2
        elif isinstance(denom, (int, float)):
            # 如果分母是常数
            return d_numer / denom
        else:
            return d_numer / denom - d_denom * numer / denom ** 2


class Log(Expr):
    def __str__(self):
        return f"log({str(self._args[0])})"

    def diff(self, var):
        return self._args[0].diff(var) / self._args[0]


def diff(function, var):
    return function.diff(var)


log = math.log


def grad(fun, argnum=0):
    """
    构造一个方程，它仅计算函数 fun 的梯度
        fun: 被微分的函数。需要被微分的位置由参数 argnum 指定, 函数的返回只能为一个数（不能为数组）
        argnums: 可选参数，只能为整数, 用于指定微分的对象；不指定则默认对第一个参数求导

    返回:
       一个和fun具有相同输入结构的函数，这个函数能够计算函数fun的梯度
    """

    def df(*args):
        namespace = []
        for i in range(len(args)):
            namespace.append("arg" + str(i))
        var_list = [Variable(name) for name in namespace]
        expr = str(diff(fun(*var_list), var_list[argnum]))
        for i in range(len(args)):
            exec("{} = {}".format(namespace[i], args[i]))
        return eval(expr)

    return df
