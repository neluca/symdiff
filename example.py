from symdiff import Variable, diff, grad

x = Variable("x")
y = Variable("y")


def f(x, y):
    return x - y ** x


expr_df_dx = str(diff(f(x, y), x))
expr_df_dy = str(diff(f(x, y), y))
print(expr_df_dx)
print(expr_df_dy)

df_dx = grad(f, 0)
df_dy = grad(f, 1)
print(df_dx(1.0, 2.0), df_dy(1.0, 2.0))
