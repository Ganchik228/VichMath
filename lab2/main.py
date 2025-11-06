import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

import csv
import numpy as np

class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("График функций")
        
        # Вкладки
        self.notebook = ttk.Notebook(root)
        self.analytical_tab = ttk.Frame(self.notebook)
        self.tabular_tab = ttk.Frame(self.notebook)
        self.dichotomy_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.analytical_tab, text="Аналитическая функция")
        self.notebook.add(self.tabular_tab, text="Табличная функция")
        self.notebook.add(self.dichotomy_tab, text="Метод дихотомии")
        self.notebook.pack(padx=10, pady=10)
        
        self.create_analytical_tab()
        self.create_tabular_tab()
        self.create_dichotomy_tab()
        
    def create_analytical_tab(self):
        # Поля
        ttk.Label(self.analytical_tab, text="f(x):").grid(row=0, column=0, padx=5, pady=5)
        self.formula_entry = ttk.Entry(self.analytical_tab, width=40)
        self.formula_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Диапазон
        ttk.Label(self.analytical_tab, text="Диапазон:").grid(row=1, column=0, padx=5, pady=5)
        self.x_min = ttk.Entry(self.analytical_tab, width=10)
        self.x_max = ttk.Entry(self.analytical_tab, width=10)
        self.x_min.grid(row=1, column=1, sticky=tk.W, padx=5)
        self.x_max.grid(row=1, column=1, sticky=tk.E, padx=5)
        
        # Кнопка 
        plot_btn = ttk.Button(self.analytical_tab, text="Построить", command=self.plot_analytical)
        plot_btn.grid(row=2, column=1, padx=5, pady=10)
        
        # График
        self.fig_analytical = plt.Figure(figsize=(5, 4))
        self.ax_analytical = self.fig_analytical.add_subplot(111)
        self.canvas_analytical = FigureCanvasTkAgg(self.fig_analytical, self.analytical_tab)
        self.canvas_analytical.get_tk_widget().grid(row=3, column=0, columnspan=2)
        
        # Масштаб
        toolbar_frame = ttk.Frame(self.analytical_tab)
        toolbar_frame.grid(row=4, column=0, columnspan=2)

        self.toolbar_analytical = NavigationToolbar2Tk(self.canvas_analytical, toolbar_frame)
        self.toolbar_analytical.update()


    def create_tabular_tab(self):
        ttk.Label(self.tabular_tab, text="Выберите файл:").grid(row=0, column=0, padx=5, pady=5)
        self.file_path_label = ttk.Label(self.tabular_tab, text="Нет файла")
        self.file_path_label.grid(row=1, column=0, padx=5, pady=5)
        

        plot_btn = ttk.Button(self.tabular_tab, text="Построить", command=self.plot_tabular)
        plot_btn.grid(row=1, column=1, padx=5, pady=10)

        # График
        self.fig_tabular = plt.Figure(figsize=(5, 4))
        self.ax_tabular = self.fig_tabular.add_subplot(111)
        self.canvas_tabular = FigureCanvasTkAgg(self.fig_tabular, self.tabular_tab)
        self.canvas_tabular.get_tk_widget().grid(row=3, column=0, columnspan=2)

        # Масштаб
        toolbar_frame = ttk.Frame(self.tabular_tab)
        toolbar_frame.grid(row=4, column=0, columnspan=2)
        
        self.toolbar_tabular = NavigationToolbar2Tk(self.canvas_tabular, toolbar_frame)
        self.toolbar_tabular.update()
        
    def create_dichotomy_tab(self):
        # Функция
        ttk.Label(self.dichotomy_tab, text="f(x) = 0:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.dichotomy_formula_entry = ttk.Entry(self.dichotomy_tab, width=40)
        self.dichotomy_formula_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5)
        
        # Интервал
        ttk.Label(self.dichotomy_tab, text="Интервал [a, b]:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.a_entry = ttk.Entry(self.dichotomy_tab, width=15)
        self.a_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Label(self.dichotomy_tab, text=",").grid(row=1, column=1, padx=5, pady=5)
        self.b_entry = ttk.Entry(self.dichotomy_tab, width=15)
        self.b_entry.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        
        # Точность
        ttk.Label(self.dichotomy_tab, text="Точность ε:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.epsilon_entry = ttk.Entry(self.dichotomy_tab, width=15)
        self.epsilon_entry.insert(0, "0.0001")
        self.epsilon_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Кнопка решения
        solve_btn = ttk.Button(self.dichotomy_tab, text="Решить", command=self.solve_dichotomy)
        solve_btn.grid(row=3, column=1, padx=5, pady=10)
        
        # График
        self.fig_dichotomy = plt.Figure(figsize=(8, 5))
        self.ax_dichotomy = self.fig_dichotomy.add_subplot(111)
        self.canvas_dichotomy = FigureCanvasTkAgg(self.fig_dichotomy, self.dichotomy_tab)
        self.canvas_dichotomy.get_tk_widget().grid(row=4, column=0, columnspan=3, padx=5, pady=5)
        
        # Масштаб
        toolbar_frame_dichotomy = ttk.Frame(self.dichotomy_tab)
        toolbar_frame_dichotomy.grid(row=5, column=0, columnspan=3)
        self.toolbar_dichotomy = NavigationToolbar2Tk(self.canvas_dichotomy, toolbar_frame_dichotomy)
        self.toolbar_dichotomy.update()
        
        # Результаты
        results_frame = ttk.LabelFrame(self.dichotomy_tab, text="Результаты", padding=10)
        results_frame.grid(row=6, column=0, columnspan=3, padx=5, pady=10, sticky="ew")
        
        # Текстовое поле для итераций
        ttk.Label(results_frame, text="Итерационная последовательность:").grid(row=0, column=0, sticky=tk.W)
        self.iterations_text = tk.Text(results_frame, height=8, width=90)
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.iterations_text.yview)
        self.iterations_text.configure(yscrollcommand=scrollbar.set)
        self.iterations_text.grid(row=1, column=0, columnspan=2, sticky="ew")
        scrollbar.grid(row=1, column=2, sticky="ns")
        
        # Результат
        self.result_label = ttk.Label(results_frame, text="")
        self.result_label.grid(row=2, column=0, columnspan=2, pady=10, sticky=tk.W)
        
    def plot_analytical(self):
        try:
            formula = self.formula_entry.get().strip()
            x_min_str = self.x_min.get().strip()
            x_max_str = self.x_max.get().strip()

            if not formula:
                raise ValueError("Введите формулу")
            if not x_min_str or not x_max_str:
                raise ValueError("Заполните диапазон X")

            x_min = float(x_min_str)
            x_max = float(x_max_str)

            if x_min >= x_max:
                raise ValueError("X min должно быть меньше X max")

            x_vals = np.linspace(x_min, x_max, 500)

            safe_formula = formula.replace('x', 'x_vals')

            y_vals = eval(safe_formula, {
                'np': np,
                'x_vals': x_vals,
                'sin': np.sin,
                'cos': np.cos,
                'tan': np.tan,
                'exp': np.exp,
                'log': np.log,
                'sqrt': np.sqrt,
                'abs': np.abs,
                'pi': np.pi,
                'e': np.e,
                'pow': np.power
            })

            self.ax_analytical.clear()

            self.ax_analytical.plot(x_vals, y_vals, label=formula)
            self.ax_analytical.set_title("График аналитической функции")
            self.ax_analytical.set_xlabel("X")
            self.ax_analytical.set_ylabel("Y")
            self.ax_analytical.grid(True)
            self.ax_analytical.legend()

            self.canvas_analytical.draw()

        except Exception as e:
            tk.messagebox.showerror("Ошибка", str(e))
            
    def plot_tabular(self):
        try:
            file_path = filedialog.askopenfilename(
                title="Выберите csv файл",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            )

            if not file_path:
                return
            
            x_vals = []
            y_vals = []

            with open(file_path,'r',newline='') as f:
                csv_reader = csv.reader(f)
                for row in csv_reader:
                    if len(row) < 2:
                        raise ValueError("Каждая строка должна иметь два значения")
                    try:
                        x = float(row[0])
                        y = float(row[1])
                    except Exception as e:
                        raise ValueError(f"Неверные данные в строке {csv_reader.line_num}: {e}")
                    
                    x_vals.append(x)
                    y_vals.append(y)

            self.ax_tabular.clear()

            self.ax_tabular.plot(x_vals, y_vals, marker='o', label='Табличная функция')
            self.ax_tabular.set_title("Табличная функция")
            self.ax_tabular.set_xlabel("X")
            self.ax_tabular.set_ylabel("Y")
            self.ax_tabular.grid(True)
            self.ax_tabular.legend()

            self.canvas_tabular.draw()
            
            self.file_path_label.config(text=file_path)
            
        except Exception as e:
            tk.messagebox.showerror("Ошибка", str(e))
    
    def evaluate_function(self, formula, x_val):
        safe_formula = formula.replace('x', str(x_val))
        return eval(safe_formula, {
            'np': np,
            'sin': np.sin,
            'cos': np.cos,
            'tan': np.tan,
            'exp': np.exp,
            'log': np.log,
            'sqrt': np.sqrt,
            'abs': np.abs,
            'pi': np.pi,
            'e': np.e,
            'pow': np.power
        })
    
    def solve_dichotomy(self):
        try:
            formula = self.dichotomy_formula_entry.get().strip()
            a_str = self.a_entry.get().strip()
            b_str = self.b_entry.get().strip()
            epsilon_str = self.epsilon_entry.get().strip()
            
            if not formula:
                raise ValueError("Введите функцию")
            if not a_str or not b_str:
                raise ValueError("Введите границы интервала")
            if not epsilon_str:
                raise ValueError("Введите точность")
        
            a = float(a_str)
            b = float(b_str)
            epsilon = float(epsilon_str)
            
            if a >= b:
                raise ValueError("a должно быть меньше b")
            
            # Проверяем, что функция меняет знак на интервале
            fa = self.evaluate_function(formula, a)
            fb = self.evaluate_function(formula, b)
            
            if fa * fb >= 0:
                raise ValueError("Функция должна менять знак на интервале [a, b]")
            
            # Метод дихотомии
            iterations = []
            iteration_count = 0
            
            while (b - a) / 2 > epsilon:
                iteration_count += 1
                c = (a + b) / 2
                fc = self.evaluate_function(formula, c)
                
                iterations.append({
                    'iteration': iteration_count,
                    'a': a,
                    'b': b,
                    'c': c,
                    'f_c': fc,
                    'interval_length': b - a
                })
                
                if abs(fc) < epsilon:
                    break
                
                if fa * fc < 0:
                    b = c
                    fb = fc
                else:
                    a = c
                    fa = fc
            root = (a + b) / 2
            f_root = self.evaluate_function(formula, root)
            
            # Отображение результатов
            self.display_iterations(iterations, root, f_root, iteration_count)
            
            # Построение графика
            self.plot_dichotomy_graph(formula, root, iterations[0]['a'], iterations[0]['b'])
            
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    
    def display_iterations(self, iterations, root, f_root, iteration_count):
        """Отображает результаты итераций"""
        self.iterations_text.delete(1.0, tk.END)
        
        header = f"{'№':<3} {'a':<12} {'b':<12} {'c':<12} {'f(c)':<12} {'|b-a|':<12}\n"
        self.iterations_text.insert(tk.END, header)
        self.iterations_text.insert(tk.END, "-" * 75 + "\n")
        
        for iter_data in iterations:
            line = (f"{iter_data['iteration']:<3} "
                   f"{iter_data['a']:<12.6f} "
                   f"{iter_data['b']:<12.6f} "
                   f"{iter_data['c']:<12.6f} "
                   f"{iter_data['f_c']:<12.6e} "
                   f"{iter_data['interval_length']:<12.6e}\n")
            self.iterations_text.insert(tk.END, line)
        
        result_text = (f"\nРезультат:\n"
                      f"Корень: x = {root:.6f}\n"
                      f"Значение функции в корне: f(x) = {f_root:.6e}\n"
                      f"Количество итераций: {iteration_count}")
        
        self.result_label.config(text=result_text)
    
    def plot_dichotomy_graph(self, formula, root, original_a, original_b):
        """Строит график функции с найденным корнем"""
        try:
            # Расширяем интервал для лучшей визуализации
            margin = abs(original_b - original_a) * 0.2
            x_min = original_a - margin
            x_max = original_b + margin
            
            x_vals = np.linspace(x_min, x_max, 1000)
            y_vals = []
            
            for x in x_vals:
                try:
                    y = self.evaluate_function(formula, x)
                    y_vals.append(y)
                except:
                    y_vals.append(np.nan)
            
            y_vals = np.array(y_vals)
            
            self.ax_dichotomy.clear()
            
            # График функции
            self.ax_dichotomy.plot(x_vals, y_vals, 'b-', label=f'f(x) = {formula}', linewidth=2)
            
            # Ось x
            self.ax_dichotomy.axhline(y=0, color='k', linestyle='-', alpha=0.3)
            
            # Найденный корень
            f_root = self.evaluate_function(formula, root)
            self.ax_dichotomy.plot(root, f_root, 'ro', markersize=8, label=f'Корень: x = {root:.6f}')
            
            # Исходный интервал
            self.ax_dichotomy.axvline(x=original_a, color='g', linestyle='--', alpha=0.7, label=f'Интервал [{original_a:.2f}, {original_b:.2f}]')
            self.ax_dichotomy.axvline(x=original_b, color='g', linestyle='--', alpha=0.7)
            
            self.ax_dichotomy.set_title(f"Решение уравнения {formula} = 0 методом дихотомии")
            self.ax_dichotomy.set_xlabel("x")
            self.ax_dichotomy.set_ylabel("f(x)")
            self.ax_dichotomy.grid(True, alpha=0.3)
            self.ax_dichotomy.legend()
            
            self.canvas_dichotomy.draw()
            
        except Exception as e:
            messagebox.showerror("Ошибка построения графика", str(e))
        

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
