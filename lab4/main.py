import tkinter as tk
from tkinter import ttk, messagebox


class LUSolver:    
    #разложение LU
    @staticmethod
    def lu_decomposition(A):
        n = len(A)
        L = [[0.0] * n for _ in range(n)]
        U = [[0.0] * n for _ in range(n)]
        
        for i in range(n):
            # матрица U
            for k in range(i, n):
                sum_val = sum(L[i][j] * U[j][k] for j in range(i))
                U[i][k] = A[i][k] - sum_val
            
            # матрица L
            for k in range(i, n):
                if i == k:
                    L[i][i] = 1.0
                else:
                    sum_val = sum(L[k][j] * U[j][i] for j in range(i))
                    if abs(U[i][i]) < 1e-10:
                        raise ValueError("Деление на ноль. Матрица вырождена.")
                    L[k][i] = (A[k][i] - sum_val) / U[i][i]
        
        return L, U
    
    #прямая подстановка
    @staticmethod
    def forward_substitution(L, b):
        n = len(L)
        y = [0.0] * n
        
        for i in range(n):
            sum_val = sum(L[i][j] * y[j] for j in range(i))
            y[i] = b[i] - sum_val
        
        return y
    
    #обратная подстановка
    @staticmethod
    def backward_substitution(U, y):
        n = len(U)
        x = [0.0] * n
        
        for i in range(n - 1, -1, -1):
            sum_val = sum(U[i][j] * x[j] for j in range(i + 1, n))
            if abs(U[i][i]) < 1e-10:
                raise ValueError("Деление на ноль. Матрица вырождена.")
            x[i] = (y[i] - sum_val) / U[i][i]
        
        return x
    
    #решение системы
    @staticmethod
    def solve(A, b):
        L, U = LUSolver.lu_decomposition(A)
        y = LUSolver.forward_substitution(L, b)
        x = LUSolver.backward_substitution(U, y)
        return x, L, U
    
    #выч невязки
    @staticmethod
    def calculate_residual(A, x, b):
        n = len(A)
        residual = []
        
        for i in range(n):
            sum_val = sum(A[i][j] * x[j] for j in range(n))
            residual.append(sum_val - b[i])
        
        return residual
    
    #норма невязки
    @staticmethod
    def residual_norm(residual):
        return sum(r ** 2 for r in residual) ** 0.5


class SeidelSolver:
    """Класс для решения СЛАУ методом Зейделя"""
    
    @staticmethod
    def check_convergence(A):
        """Проверка диагонального преобладания для сходимости"""
        n = len(A)
        for i in range(n):
            diagonal = abs(A[i][i])
            sum_row = sum(abs(A[i][j]) for j in range(n) if j != i)
            if diagonal <= sum_row:
                return False
        return True
    
    @staticmethod
    def solve(A, b, epsilon=1e-4, max_iterations=1000):
        """
        Решение СЛАУ методом Зейделя
        epsilon - точность
        max_iterations - максимальное число итераций
        """
        n = len(A)
        x = [0.0] * n  # начальное приближение
        x_prev = [0.0] * n
        iterations = 0
        history = []  # история итераций
        
        for iteration in range(max_iterations):
            iterations += 1
            x_prev = x.copy()
            
            # Метод Зейделя: используем уже вычисленные значения на текущей итерации
            for i in range(n):
                sum_val = 0.0
                for j in range(n):
                    if j != i:
                        sum_val += A[i][j] * x[j]
                
                if abs(A[i][i]) < 1e-10:
                    raise ValueError("Деление на ноль. Проверьте матрицу.")
                
                x[i] = (b[i] - sum_val) / A[i][i]
            
            # Вычисляем максимальную разницу компонент
            max_diff = max(abs(x[i] - x_prev[i]) for i in range(n))
            
            # Сохраняем историю
            history.append({
                'iteration': iteration + 1,
                'x': x.copy(),
                'max_diff': max_diff
            })
            
            # Проверка точности
            if max_diff < epsilon:
                break
        
        return x, iterations, history
    
    @staticmethod
    def calculate_residual(A, x, b):
        """Вычисление невязки r = Ax - b"""
        n = len(A)
        residual = []
        
        for i in range(n):
            sum_val = sum(A[i][j] * x[j] for j in range(n))
            residual.append(sum_val - b[i])
        
        return residual
    
    @staticmethod
    def residual_norm(residual):
        """Вычисление нормы невязки"""
        return sum(r ** 2 for r in residual) ** 0.5


class LUTab(ttk.Frame):    
    def __init__(self, parent, default_A, default_b):
        super().__init__(parent)
        self.default_A = default_A
        self.default_b = default_b
        self.n = len(default_A)
        self.create_widgets()
    
    def create_widgets(self):
        dim_frame = ttk.LabelFrame(self, text="Размерность системы", padding=10)
        dim_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(dim_frame, text="n =").pack(side="left")
        self.n_var = tk.IntVar(value=self.n)
        ttk.Spinbox(dim_frame, from_=2, to=10, textvariable=self.n_var, width=5).pack(side="left", padx=5)
        ttk.Button(dim_frame, text="Изменить размер", command=self.change_dimension).pack(side="left", padx=5)
        
        matrix_frame = ttk.LabelFrame(self, text="Матрица коэффициентов A", padding=10)
        matrix_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.matrix_entries_frame = ttk.Frame(matrix_frame)
        self.matrix_entries_frame.pack()
        
        vector_frame = ttk.LabelFrame(self, text="Вектор правой части b", padding=10)
        vector_frame.pack(fill="x", padx=10, pady=5)
        
        self.vector_entries_frame = ttk.Frame(vector_frame)
        self.vector_entries_frame.pack()
        
        ttk.Button(self, text="Решить СЛАУ", command=self.solve_system).pack(pady=10)
        
        result_frame = ttk.LabelFrame(self, text="Результаты", padding=10)
        result_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.result_text = tk.Text(result_frame, height=15, width=100)
        scrollbar = ttk.Scrollbar(result_frame, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        self.result_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.create_input_fields()
    
    def change_dimension(self):
        self.n = self.n_var.get()
        
        if self.n > len(self.default_A):
            for row in self.default_A:
                while len(row) < self.n:
                    row.append(0)
            while len(self.default_A) < self.n:
                self.default_A.append([0] * self.n)
            while len(self.default_b) < self.n:
                self.default_b.append(0)
        
        self.create_input_fields()
    
    def create_input_fields(self):
        for widget in self.matrix_entries_frame.winfo_children():
            widget.destroy()
        for widget in self.vector_entries_frame.winfo_children():
            widget.destroy()
        
        self.matrix_entries = []
        self.vector_entries = []
        
        for i in range(self.n):
            row_entries = []
            for j in range(self.n):
                entry = ttk.Entry(self.matrix_entries_frame, width=10)
                entry.grid(row=i, column=j, padx=2, pady=2)
                default_val = self.default_A[i][j] if i < len(self.default_A) and j < len(self.default_A[i]) else 0
                entry.insert(0, str(default_val))
                row_entries.append(entry)
            self.matrix_entries.append(row_entries)
        
        for i in range(self.n):
            entry = ttk.Entry(self.vector_entries_frame, width=10)
            entry.grid(row=i, column=0, padx=2, pady=2)
            default_val = self.default_b[i] if i < len(self.default_b) else 0
            entry.insert(0, str(default_val))
            self.vector_entries.append(entry)
    
    def get_matrix_and_vector(self):
        try:
            A = []
            for i in range(self.n):
                row = []
                for j in range(self.n):
                    val = float(self.matrix_entries[i][j].get())
                    row.append(val)
                A.append(row)
            
            b = []
            for i in range(self.n):
                val = float(self.vector_entries[i].get())
                b.append(val)
            
            return A, b
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения!")
            return None, None
    
    def solve_system(self):
        A, b = self.get_matrix_and_vector()
        
        if A is None or b is None:
            return
        
        try:
            x, L, U = LUSolver.solve(A, b)
            
            residual = LUSolver.calculate_residual(A, x, b)
            residual_norm = LUSolver.residual_norm(residual)
            
            self.result_text.delete(1.0, tk.END)
            
            self.result_text.insert(tk.END, "=" * 80 + "\n")
            self.result_text.insert(tk.END, "РЕШЕНИЕ СЛАУ МЕТОДОМ LU-РАЗЛОЖЕНИЯ\n")
            self.result_text.insert(tk.END, "=" * 80 + "\n\n")
            
            self.result_text.insert(tk.END, "Нижнетреугольная матрица L:\n")
            for row in L:
                self.result_text.insert(tk.END, "  " + "  ".join(f"{val:10.6f}" for val in row) + "\n")
            
            self.result_text.insert(tk.END, "\nВерхнетреугольная матрица U:\n")
            for row in U:
                self.result_text.insert(tk.END, "  " + "  ".join(f"{val:10.6f}" for val in row) + "\n")
            
            self.result_text.insert(tk.END, "\n" + "=" * 80 + "\n")
            self.result_text.insert(tk.END, "РЕШЕНИЕ (вектор x):\n")
            self.result_text.insert(tk.END, "=" * 80 + "\n")
            for i, val in enumerate(x):
                self.result_text.insert(tk.END, f"  x[{i}] = {val:12.8f}\n")
            
            self.result_text.insert(tk.END, "\n" + "=" * 80 + "\n")
            self.result_text.insert(tk.END, "ПРОВЕРКА (невязка r = Ax - b):\n")
            self.result_text.insert(tk.END, "=" * 80 + "\n")
            for i, val in enumerate(residual):
                self.result_text.insert(tk.END, f"  r[{i}] = {val:12.8e}\n")
            
            self.result_text.insert(tk.END, f"\nНорма невязки: {residual_norm:12.8e}\n")
            
            if residual_norm < 1e-8:
                self.result_text.insert(tk.END, "\n✓ Решение найдено с высокой точностью!\n")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при решении СЛАУ:\n{str(e)}")


class SeidelTab(ttk.Frame):
    def __init__(self, parent, default_A, default_b):
        super().__init__(parent)
        self.default_A = default_A
        self.default_b = default_b
        self.n = len(default_A)
        self.create_widgets()
    
    def create_widgets(self):
        dim_frame = ttk.LabelFrame(self, text="Размерность системы", padding=10)
        dim_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(dim_frame, text="n =").pack(side="left")
        self.n_var = tk.IntVar(value=self.n)
        ttk.Spinbox(dim_frame, from_=2, to=10, textvariable=self.n_var, width=5).pack(side="left", padx=5)
        ttk.Button(dim_frame, text="Изменить размер", command=self.change_dimension).pack(side="left", padx=5)
        
        params_frame = ttk.LabelFrame(self, text="Параметры метода", padding=10)
        params_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(params_frame, text="Точность ε =").pack(side="left")
        self.epsilon_var = tk.StringVar(value="1e-4")
        ttk.Entry(params_frame, textvariable=self.epsilon_var, width=10).pack(side="left", padx=5)
        
        ttk.Label(params_frame, text="Макс. итераций =").pack(side="left", padx=(20, 0))
        self.max_iter_var = tk.IntVar(value=1000)
        ttk.Entry(params_frame, textvariable=self.max_iter_var, width=10).pack(side="left", padx=5)
        
        matrix_frame = ttk.LabelFrame(self, text="Матрица коэффициентов A", padding=10)
        matrix_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.matrix_entries_frame = ttk.Frame(matrix_frame)
        self.matrix_entries_frame.pack()
        
        vector_frame = ttk.LabelFrame(self, text="Вектор правой части b", padding=10)
        vector_frame.pack(fill="x", padx=10, pady=5)
        
        self.vector_entries_frame = ttk.Frame(vector_frame)
        self.vector_entries_frame.pack()
        
        ttk.Button(self, text="Решить СЛАУ методом Зейделя", command=self.solve_system).pack(pady=10)
        
        result_frame = ttk.LabelFrame(self, text="Результаты", padding=10)
        result_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.result_text = tk.Text(result_frame, height=15, width=100)
        scrollbar = ttk.Scrollbar(result_frame, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        self.result_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.create_input_fields()
    
    def change_dimension(self):
        self.n = self.n_var.get()
        
        if self.n > len(self.default_A):
            for row in self.default_A:
                while len(row) < self.n:
                    row.append(0)
            while len(self.default_A) < self.n:
                self.default_A.append([0] * self.n)
            while len(self.default_b) < self.n:
                self.default_b.append(0)
        
        self.create_input_fields()
    
    def create_input_fields(self):
        for widget in self.matrix_entries_frame.winfo_children():
            widget.destroy()
        for widget in self.vector_entries_frame.winfo_children():
            widget.destroy()
        
        self.matrix_entries = []
        self.vector_entries = []
        
        for i in range(self.n):
            row_entries = []
            for j in range(self.n):
                entry = ttk.Entry(self.matrix_entries_frame, width=10)
                entry.grid(row=i, column=j, padx=2, pady=2)
                default_val = self.default_A[i][j] if i < len(self.default_A) and j < len(self.default_A[i]) else 0
                entry.insert(0, str(default_val))
                row_entries.append(entry)
            self.matrix_entries.append(row_entries)
        
        for i in range(self.n):
            entry = ttk.Entry(self.vector_entries_frame, width=10)
            entry.grid(row=i, column=0, padx=2, pady=2)
            default_val = self.default_b[i] if i < len(self.default_b) else 0
            entry.insert(0, str(default_val))
            self.vector_entries.append(entry)
    
    def get_matrix_and_vector(self):
        try:
            A = []
            for i in range(self.n):
                row = []
                for j in range(self.n):
                    val = float(self.matrix_entries[i][j].get())
                    row.append(val)
                A.append(row)
            
            b = []
            for i in range(self.n):
                val = float(self.vector_entries[i].get())
                b.append(val)
            
            return A, b
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения!")
            return None, None
    
    def solve_system(self):
        A, b = self.get_matrix_and_vector()
        
        if A is None or b is None:
            return
        
        try:
            epsilon = float(self.epsilon_var.get())
            max_iter = self.max_iter_var.get()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное значение точности!")
            return
        
        try:
            # Проверка сходимости
            if not SeidelSolver.check_convergence(A):
                messagebox.showwarning("Предупреждение", 
                    "Матрица не имеет диагонального преобладания.\n" +
                    "Метод Зейделя может не сойтись!")
            
            # Решаем СЛАУ
            x, iterations, history = SeidelSolver.solve(A, b, epsilon, max_iter)
            
            # Вычисляем невязку
            residual = SeidelSolver.calculate_residual(A, x, b)
            residual_norm = SeidelSolver.residual_norm(residual)
            
            # Выводим результаты
            self.result_text.delete(1.0, tk.END)
            
            self.result_text.insert(tk.END, "=" * 80 + "\n")
            self.result_text.insert(tk.END, "РЕШЕНИЕ СЛАУ МЕТОДОМ ЗЕЙДЕЛЯ\n")
            self.result_text.insert(tk.END, "=" * 80 + "\n\n")
            
            self.result_text.insert(tk.END, f"Точность: ε = {epsilon}\n")
            self.result_text.insert(tk.END, f"Количество итераций: {iterations}\n\n")
            
            # Показываем последние 10 итераций
            self.result_text.insert(tk.END, "Последние итерации:\n")
            self.result_text.insert(tk.END, "-" * 80 + "\n")
            start_idx = max(0, len(history) - 10)
            for item in history[start_idx:]:
                self.result_text.insert(tk.END, 
                    f"Итерация {item['iteration']:3d}: max_diff = {item['max_diff']:12.8e}\n")
            
            self.result_text.insert(tk.END, "\n" + "=" * 80 + "\n")
            self.result_text.insert(tk.END, "РЕШЕНИЕ (вектор x):\n")
            self.result_text.insert(tk.END, "=" * 80 + "\n")
            for i, val in enumerate(x):
                self.result_text.insert(tk.END, f"  x[{i}] = {val:12.8f}\n")
            
            self.result_text.insert(tk.END, "\n" + "=" * 80 + "\n")
            self.result_text.insert(tk.END, "ПРОВЕРКА (невязка r = Ax - b):\n")
            self.result_text.insert(tk.END, "=" * 80 + "\n")
            for i, val in enumerate(residual):
                self.result_text.insert(tk.END, f"  r[{i}] = {val:12.8e}\n")
            
            self.result_text.insert(tk.END, f"\nНорма невязки: {residual_norm:12.8e}\n")
            
            if iterations >= max_iter:
                self.result_text.insert(tk.END, 
                    f"\n⚠ Достигнуто максимальное число итераций ({max_iter})\n")
            else:
                self.result_text.insert(tk.END, 
                    f"\n✓ Решение найдено за {iterations} итераций с точностью {epsilon}\n")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при решении СЛАУ:\n{str(e)}")


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Решение СЛАУ")
        self.root.geometry("950x750")
        
        self.default_A = [
            [-35.15, 2.83, -1.96, 4.69],
            [7.92, -21.41, 3.24, -8.76],
            [2.68, 4.75, -18.82, 1.54],
            [0.93, -3.16, -2.05, -31.11]
        ]
        self.default_b = [0.39, 5.12, -2.37, 4.88]
        
        self.create_widgets()
    
    def create_widgets(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        lu_tab = LUTab(notebook, self.default_A.copy(), self.default_b.copy())
        notebook.add(lu_tab, text="LU-разложение")
        
        seidel_tab = SeidelTab(notebook, self.default_A.copy(), self.default_b.copy())
        notebook.add(seidel_tab, text="Метод Зейделя")


def main():
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
