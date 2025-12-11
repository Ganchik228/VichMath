import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def f(x):
    return (x - 1.5) * np.sqrt(x + 4) + np.sin(np.pi * x)


def midpoint_rule(a, b, n):
    h = (b - a) / n
    s = 0.0
    for i in range(n):
        x = a + h * (i + 0.5)
        s += f(x)
    return s * h


def aitken_order(I1, I2, I3):
    return math.log(abs((I1 - I2) / (I2 - I3)), 2)


def solve(a, b):
    print("Метод средних прямоугольников")
    print(f"Интервал интегрирования: [{a}, {b}]")
    print("Функция: (x - 1.5)*sqrt(x+4) + sin(pi*x)")
    print("-----------------------------------------")

    N = 100  # базовый шаг

    I1 = midpoint_rule(a, b, N)
    I2 = midpoint_rule(a, b, 2*N)
    I3 = midpoint_rule(a, b, 4*N)

    p = aitken_order(I1, I2, I3)

    print(f"I(N = {N})   = {I1}")
    print(f"I(N = {2*N}) = {I2}")
    print(f"I(N = {4*N}) = {I3}")
    print(f"Эффективный порядок точности p = {p:.6f}")

    # --------------------------------------------------
    # 5. Построение графика функции на интервале
    # --------------------------------------------------
    X = np.linspace(a, b, 500)
    Y = f(X)

    plt.figure(figsize=(8, 5))
    plt.plot(X, Y)
    plt.xlabel("x")
    plt.ylabel("f(x)")
    plt.title("График функции f(x) = (x - 1.5)*sqrt(x+4) + sin(pi x)")
    plt.grid(True)

    ax = plt.gca()
    h = (b - a) / N
    for i in range(N):
        x_left = a + i * h
        height = f(x_left + h / 2)
        rect_y = min(0, height)
        rect_height = abs(height)
        ax.add_patch(Rectangle((x_left, rect_y), h, rect_height,
                               edgecolor="orange", facecolor="orange", alpha=0.3))

    plt.show()


# --------------------------------------------------
# Запуск программы
# --------------------------------------------------
solve(-4, 4)
