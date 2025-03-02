# Symbolic Differentiation
A very simple implementation of symbolic differentiation.

### Example usage

```python
from symdiff import Variable, diff, grad

x = Variable("x")
y = Variable("y")

def f(x, y):
    return x - y ** x

expr = str(diff(f(x, y), x))
print(expr)

df_dx = grad(f, 0)
df_dy = grad(f, 1)
print(df_dx(1.0, 2.0), df_dy(1.0, 2.0))

```

output:

```
(1 - ((y ** x) * ((1 * log(y)) + ((0 * x) / y))))
-0.3862943611198906 -1.0
```

