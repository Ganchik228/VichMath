import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from scipy.optimize import minimize


def f_fun(xy):
    x, y = xy
    # cos(ln(0.5 + x1^2)) - sin(ln(0.4 + (x2/2)^2)) - 0.025 = 0
    return math.cos(math.log(0.5 + x*x)) - math.sin(math.log(0.4 + (y/2.0)**2)) - 0.025

def g_fun(xy):
    x, y = xy
    # 4/(x1^2 + 2 x2^2 + 4 - cos(0.01 x1 x2)) - 0.3 = 0
    denom = x*x + 2.0*y*y + 4.0 - math.cos(0.01 * x * y)
    return 4.0/denom - 0.3

def Phi(xy):
    a = f_fun(xy)
    b = g_fun(xy)
    return a*a + b*b


def numerical_grad(func, xy, h=1e-6):
    x, y = xy
    xp = (x + h, y)
    xm = (x - h, y)
    dpx = (func(xp) - func(xm)) / (2*h)
    yp = (x, y + h)
    ym = (x, y - h)
    dpy = (func(yp) - func(ym)) / (2*h)
    return np.array([dpx, dpy])


def bracket_minimum(phi_1d, x0=0.0, step=0.1, expand=2.0, max_iter=50):
    a = x0
    fa = phi_1d(a)
    b = x0 + step
    fb = phi_1d(b)
    if fb > fa:
        b = x0 - step
        fb = phi_1d(b)
        if fb > fa:
            return (min(a,b), max(a,b))
    iter_count = 0
    while True:
        iter_count += 1
        step *= expand
        c = b + step if b > a else b - step
        fc = phi_1d(c)
        if fc > fb or iter_count > max_iter:
            return (min(a,c), max(a,c))
        a, fa = b, fb
        b, fb = c, fc


def golden_section(phi_1d, a, b, tol=1e-6, max_iter=200):
    gr = (math.sqrt(5) - 1) / 2.0  # ~0.618
    c = b - gr * (b - a)
    d = a + gr * (b - a)
    fc = phi_1d(c)
    fd = phi_1d(d)
    it = 0
    while (b - a) > tol and it < max_iter:
        it += 1
        if fc < fd:
            b, d, fd = d, c, fc
            c = b - gr * (b - a)
            fc = phi_1d(c)
        else:
            a, c, fc = c, d, fd
            d = a + gr * (b - a)
            fd = phi_1d(d)
    return (a + b) / 2.0

def coordinate_descent_2d(xy0, eps=1e-4, max_iter=500, plotting=True):
    x = float(xy0[0])
    y = float(xy0[1])
    xy = np.array([x, y], dtype=float)

    if plotting:
        xs = np.linspace(x - 1.0, x + 1.0, 201)
        ys = np.linspace(y - 1.0, y + 1.0, 201)
        X, Y = np.meshgrid(xs, ys)
        Z = np.zeros_like(X)
        for i in range(X.shape[0]):
            for j in range(X.shape[1]):
                Z[i,j] = Phi((float(X[i,j]), float(Y[i,j])))
        plt.figure(figsize=(6,5))
        levels = np.logspace(-6, 2, 25)
        plt.contour(X, Y, Z, levels=levels, norm=LogNorm(), linewidths=0.7)
        plt.plot(x, y, "ro", label="start")
        plt.title("Локализация: контуры Phi вокруг начального приближения")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.legend()
        plt.show()

    k = 0
    while k < max_iter:
        k += 1
        prev_xy = xy.copy()

        def phi_x(t):
            return Phi((t, float(xy[1])))

        a, b = bracket_minimum(phi_x, x0=float(xy[0]), step=0.1, expand=1.8, max_iter=80)
        x_opt = golden_section(phi_x, a, b, tol=1e-8, max_iter=200)
        xy[0] = x_opt

        def phi_y(t):
            return Phi((float(xy[0]), t))

        a, b = bracket_minimum(phi_y, x0=float(xy[1]), step=0.1, expand=1.8, max_iter=80)
        y_opt = golden_section(phi_y, a, b, tol=1e-8, max_iter=200)
        xy[1] = y_opt

        delta = np.linalg.norm(xy - prev_xy)
        if delta < eps:
            break

    Phi_val = Phi((xy[0], xy[1]))
    grad = numerical_grad(lambda zz: Phi((zz[0], zz[1])), (xy[0], xy[1]))
    return {
        "xk": xy,
        "k": k,
        "Phi": Phi_val,
        "grad": grad,
        "delta": delta
    }



def Phi_vec(p):
    return Phi(p)




if __name__ == "__main__":
    
    res = minimize(Phi_vec, x0=[0.5, 0.5])
    print(res)  
    
    x0 = (0.5, 0.5)

    res = coordinate_descent_2d(x0, eps=1e-4, max_iter=500, plotting=True)

    print("\nРЕЗУЛЬТАТ МЕТОДА ПОКООРДИНАТНОГО СПУСКА")
    print(f"Найденное решение x^(k) = [{res['xk'][0]:.8f}, {res['xk'][1]:.8f}]")
    print(f"Количество итераций k = {res['k']}")
    print(f"Значение Phi(x^(k)) = {res['Phi']:.10e}")
    print(f"Градиент (∇Phi) в точке = [{res['grad'][0]:.6e}, {res['grad'][1]:.6e}]")
    print(f"Точность (||x^(k) - x^(k-1)||) = {res['delta']:.6e}")
