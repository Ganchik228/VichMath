import numpy as np
import math

# -----------------------------
# Вспомогательные функции
# -----------------------------

def vec_norm(v):
    """Евклидова норма вектора"""
    return math.sqrt(sum(vi**2 for vi in v))

def print_vector(name, v):
    print(f"{name} = [{v[0]:.8f}, {v[1]:.8f}]")

# -----------------------------
# Система уравнений
# -----------------------------
def F(x):
    x1, x2 = x

    eq1 = math.cos(math.log(0.5 + x1**2)) - \
          math.sin(math.log(0.4 + (x2/2)**2)) - 0.025

    eq2 = 4 / (x1**2 + 2*x2**2 + 4 - math.cos(0.01*x1*x2)) - 0.3

    return np.array([eq1, eq2])

# -----------------------------
# Якобиан системы
# -----------------------------
def J(x):
    x1, x2 = x

    # Частные производные (симв. вычисление вручную)
    # Уравнение 1
    df1dx1 = -math.sin(math.log(0.5 + x1**2)) * (2*x1)/(0.5 + x1**2)
    df1dx2 = -math.cos(math.log(0.4 + (x2/2)**2)) * ((x2/2)/(0.4 + (x2/2)**2))

    # Уравнение 2
    denom = (x1**2 + 2*x2**2 + 4 - math.cos(0.01*x1*x2))
    dDen_dx1 = 2*x1 + math.sin(0.01*x1*x2) * 0.01 * x2
    dDen_dx2 = 4*x2 + math.sin(0.01*x1*x2) * 0.01 * x1

    df2dx1 = -4 * dDen_dx1 / (denom**2)
    df2dx2 = -4 * dDen_dx2 / (denom**2)

    return np.array([
        [df1dx1, df1dx2],
        [df2dx1, df2dx2]
    ])

# -----------------------------
# Метод Ньютона
# -----------------------------
def newton_method(x0, eps=1e-6, max_iter=50):
    x = np.array(x0, dtype=float)

    for k in range(max_iter):
        Fx = F(x)
        Jx = J(x)

        # Решаем J * dx = F
        dx = np.linalg.solve(Jx, Fx)

        x_new = x - dx

        if vec_norm(dx) < eps:
            return x_new, k+1, F(x_new)

        x = x_new

    return x, max_iter, F(x)

# -----------------------------
# Запуск решения
# -----------------------------
x0 = [0.5, 0.5]  # начальное приближение — можно менять
solution, iterations, residual = newton_method(x0)

print("\nРЕЗУЛЬТАТ РЕШЕНИЯ СИСТЕМЫ:")
print_vector("r*", solution)
print_vector("F(r*)", residual)
print(f"Количество итераций: {iterations}")
print(f"Точность ε: {vec_norm(residual):.8e}")
