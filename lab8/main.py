import numpy as np
import matplotlib.pyplot as plt
import math

# исходная функция y'
def f(x, y):
    return math.asin(1 - 1/(math.exp(x) + y**2))

# Метод Эйлера-Коши
def euler_cauchy(x0, y0, x_end, h):
    xs = [x0]
    ys = [y0]

    while xs[-1] < x_end:
        x = xs[-1]
        y = ys[-1]

        # шаг Эйлера
        y_euler = y + h * f(x, y)

        # шаг Эйлера-Коши
        y_new = y + h * 0.5 * (f(x, y) + f(x + h, y_euler))

        xs.append(x + h)
        ys.append(y_new)

    return np.array(xs), np.array(ys)

# параметры задачи
x0 = 0
y0 = 1
x_end = 1
h = 0.01

# решение
xs, ys = euler_cauchy(x0, y0, x_end, h)

# ---- Проверка уравнения в трех точках ----
check_points = [0.2, 0.5, 0.9]
print("Проверка выполнения ОДУ (y' ≈ вычисленно):\n")
print("  x      y'(числ.)       f(x,y)           ошибка")
print("-----------------------------------------------")

# численная производная: (y(x+h) - y(x))/h
for xp in check_points:
    idx = np.argmin(np.abs(xs - xp))
    if idx < len(xs) - 1:
        y_prime_num = (ys[idx+1] - ys[idx]) / h
    else:
        y_prime_num = (ys[idx] - ys[idx-1]) / h

    y_prime_true = f(xs[idx], ys[idx])
    err = abs(y_prime_true - y_prime_num)

    print(f"{xs[idx]:.2f}    {y_prime_num:.6f}    {y_prime_true:.6f}    {err:.6e}")

# ---- График решения ----
plt.figure(figsize=(8,5))
plt.plot(xs, ys, label="Решение методом Эйлера-Коши")
plt.scatter([x0], [y0], color="red", label="Начальное условие y(0)=1")
plt.xlabel("x")
plt.ylabel("y")
plt.title("Численное решение ОДУ методом Эйлера-Коши")
plt.grid(True)
plt.legend()
plt.show()
