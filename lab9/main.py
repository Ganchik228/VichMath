import math


def vec_add(a, b):
    return [a[i] + b[i] for i in range(len(a))]

def vec_sub(a, b):
    return [a[i] - b[i] for i in range(len(a))]

def vec_mul_scalar(a, s):
    return [a[i] * s for i in range(len(a))]

def dot(a, b):
    return sum(a[i] * b[i] for i in range(len(a)))

def vec_norm(a):
    return math.sqrt(dot(a, a))


def mat_vec_mul(A, x):
    return [sum(A[i][j]*x[j] for j in range(len(x))) for i in range(len(A))]

def mat_inv_2x2(A):
    det = A[0][0]*A[1][1] - A[0][1]*A[1][0]
    return [
        [ A[1][1]/det, -A[0][1]/det ],
        [-A[1][0]/det,  A[0][0]/det ]
    ]

def F(x):
    x1, x2 = x

    f1 = math.cos(math.log(0.5 + x1**2)) \
         - math.sin(math.log(0.4 + (x2/2)**2)) - 0.025

    denom = x1**2 + 2*x2**2 + 4 - math.cos(0.01*x1*x2)
    f2 = 4/denom - 0.3

    return [f1, f2]



def J(x):
    x1, x2 = x

    d11 = -math.sin(math.log(0.5 + x1*x1)) * (2*x1)/(0.5 + x1*x1)
    d12 = -math.cos(math.log(0.4 + (x2/2)**2)) * ((x2/2)/(0.4 + (x2/2)**2))

    denom = x1*x1 + 2*x2*x2 + 4 - math.cos(0.01*x1*x2)

    d_denom_dx1 = 2*x1 + math.sin(0.01*x1*x2) * (0.01*x2)
    d_denom_dx2 = 4*x2 + math.sin(0.01*x1*x2) * (0.01*x1)

    d21 = -4 * d_denom_dx1 / (denom*denom)
    d22 = -4 * d_denom_dx2 / (denom*denom)

    return [
        [d11, d12],
        [d21, d22]
    ]


def newton_method(x0, eps=1e-6, max_iter=50):
    x = x0

    for k in range(max_iter):
        Fx = F(x)
        Jx = J(x)
        J_inv = mat_inv_2x2(Jx)

        step = mat_vec_mul(J_inv, Fx)
        x_new = vec_sub(x, step)

        if vec_norm(step) < eps:
            return x_new, k+1, F(x_new), vec_norm(F(x_new))

        x = x_new

    return x, max_iter, F(x), vec_norm(F(x))


x0 = [0.5, 0.5]

x_star, k, F_val, eps_val = newton_method(x0)

print("\n===== РЕЗУЛЬТАТЫ РАБОТЫ ПРОГРАММЫ =====")
print(f"Решение x^(k) = [{x_star[0]:.8f}, {x_star[1]:.8f}]")
print(f"Количество итераций k = {k}")
print(f"Вектор F(x^(k)) = [{F_val[0]:.8e}, {F_val[1]:.8e}]")
print(f"Точность ε = {eps_val:.8e}")
