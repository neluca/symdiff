from symdiff import Variable, diff, grad

x = Variable("x")
y = Variable("y")


def f(x, y):
    return x - y ** x


expr = str(diff(f(x, y), x))
print(expr)

df = grad(f)
print(df(1.0, 2.0))
