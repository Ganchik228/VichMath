import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

import csv
import numpy as np

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        
        # Создаем канвас и скроллбар
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Биндим колесико мыши
        self.bind_mousewheel()

    def bind_mousewheel(self):
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")

        self.canvas.bind('<Enter>', _bind_to_mousewheel)
        self.canvas.bind('<Leave>', _unbind_from_mousewheel)

class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("График функций")
        self.root.geometry("1200x800")  # Устанавливаем начальный размер
        
        # Вкладки
        self.notebook = ttk.Notebook(root)
        
        # Создаем скроллируемые фреймы для каждой вкладки
        self.analytical_scroll = ScrollableFrame(self.notebook)
        self.tabular_scroll = ScrollableFrame(self.notebook)
        self.dichotomy_scroll = ScrollableFrame(self.notebook)
        self.extrema_scroll = ScrollableFrame(self.notebook)
        
        self.notebook.add(self.analytical_scroll, text="Аналитическая функция")
        self.notebook.add(self.tabular_scroll, text="Табличная функция")
        self.notebook.add(self.dichotomy_scroll, text="Метод дихотомии")
        self.notebook.add(self.extrema_scroll, text="Поиск экстремума")
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Получаем ссылки на внутренние фреймы
        self.analytical_tab = self.analytical_scroll.scrollable_frame
        self.tabular_tab = self.tabular_scroll.scrollable_frame
        self.dichotomy_tab = self.dichotomy_scroll.scrollable_frame
        self.extrema_tab = self.extrema_scroll.scrollable_frame
        
        self.create_analytical_tab()
        self.create_tabular_tab()
        self.create_dichotomy_tab()
        self.create_extrema_tab()
        
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
        
        # Кнопки 
        button_frame = ttk.Frame(self.analytical_tab)
        button_frame.grid(row=2, column=1, padx=5, pady=10)
        
        plot_btn = ttk.Button(button_frame, text="Построить", command=self.plot_analytical)
        plot_btn.pack(side=tk.LEFT, padx=5)
        
        extrema_btn = ttk.Button(button_frame, text="Найти экстремумы", command=self.find_extrema_points)
        extrema_btn.pack(side=tk.LEFT, padx=5)
        
        # График (уменьшенный размер)
        self.fig_analytical = plt.Figure(figsize=(8, 5))
        self.ax_analytical = self.fig_analytical.add_subplot(111)
        self.canvas_analytical = FigureCanvasTkAgg(self.fig_analytical, self.analytical_tab)
        self.canvas_analytical.get_tk_widget().grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        
        # Масштаб
        toolbar_frame = ttk.Frame(self.analytical_tab)
        toolbar_frame.grid(row=4, column=0, columnspan=2)

        self.toolbar_analytical = NavigationToolbar2Tk(self.canvas_analytical, toolbar_frame)
        self.toolbar_analytical.update()

        # Результаты экстремумов (с ограниченной высотой)
        results_frame = ttk.LabelFrame(self.analytical_tab, text="Результаты поиска экстремумов", padding=10)
        results_frame.grid(row=5, column=0, columnspan=2, padx=5, pady=10, sticky="ew")
        
        self.extrema_results_text = tk.Text(results_frame, height=6, width=80, wrap=tk.WORD)
        extrema_scroll = ttk.Scrollbar(results_frame, orient="vertical", command=self.extrema_results_text.yview)
        self.extrema_results_text.configure(yscrollcommand=extrema_scroll.set)
        self.extrema_results_text.grid(row=0, column=0, sticky="ew")
        extrema_scroll.grid(row=0, column=1, sticky="ns")

    def create_tabular_tab(self):
        ttk.Label(self.tabular_tab, text="Выберите файл:").grid(row=0, column=0, padx=5, pady=5)
        self.file_path_label = ttk.Label(self.tabular_tab, text="Нет файла", width=50, wraplength=300)
        self.file_path_label.grid(row=1, column=0, padx=5, pady=5)
        
        plot_btn = ttk.Button(self.tabular_tab, text="Построить", command=self.plot_tabular)
        plot_btn.grid(row=1, column=1, padx=5, pady=10)

        # График (уменьшенный размер)
        self.fig_tabular = plt.Figure(figsize=(8, 5))
        self.ax_tabular = self.fig_tabular.add_subplot(111)
        self.canvas_tabular = FigureCanvasTkAgg(self.fig_tabular, self.tabular_tab)
        self.canvas_tabular.get_tk_widget().grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # Масштаб
        toolbar_frame = ttk.Frame(self.tabular_tab)
        toolbar_frame.grid(row=3, column=0, columnspan=2)
        
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
        
        # График (уменьшенный размер)
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
        
        # Текстовое поле для итераций (уменьшенная высота)
        ttk.Label(results_frame, text="Итерационная последовательность:").grid(row=0, column=0, sticky=tk.W)
        self.iterations_text = tk.Text(results_frame, height=8, width=80)
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.iterations_text.yview)
        self.iterations_text.configure(yscrollcommand=scrollbar.set)
        self.iterations_text.grid(row=1, column=0, columnspan=2, sticky="ew")
        scrollbar.grid(row=1, column=2, sticky="ns")
        
        # Результат
        self.result_label = ttk.Label(results_frame, text="", wraplength=600)
        self.result_label.grid(row=2, column=0, columnspan=2, pady=10, sticky=tk.W)
        
    def create_extrema_tab(self):
        # Функция
        ttk.Label(self.extrema_tab, text="f(x):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.extrema_formula_entry = ttk.Entry(self.extrema_tab, width=40)
        self.extrema_formula_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5)
        
        # Интервал поиска
        ttk.Label(self.extrema_tab, text="Интервал поиска [a, b]:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.extrema_a_entry = ttk.Entry(self.extrema_tab, width=15)
        self.extrema_a_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Label(self.extrema_tab, text=",").grid(row=1, column=1, padx=5, pady=5)
        self.extrema_b_entry = ttk.Entry(self.extrema_tab, width=15)
        self.extrema_b_entry.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        
        # Точность
        ttk.Label(self.extrema_tab, text="Точность ε:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.extrema_epsilon_entry = ttk.Entry(self.extrema_tab, width=15)
        self.extrema_epsilon_entry.insert(0, "0.0001")
        self.extrema_epsilon_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Кнопка решения
        solve_extrema_btn = ttk.Button(self.extrema_tab, text="Найти экстремум", command=self.solve_extrema_parabolic)
        solve_extrema_btn.grid(row=3, column=1, padx=5, pady=10)
        
        # График (уменьшенный размер)
        self.fig_extrema = plt.Figure(figsize=(8, 5))
        self.ax_extrema = self.fig_extrema.add_subplot(111)
        self.canvas_extrema = FigureCanvasTkAgg(self.fig_extrema, self.extrema_tab)
        self.canvas_extrema.get_tk_widget().grid(row=4, column=0, columnspan=3, padx=5, pady=5)
        
        # Масштаб
        toolbar_frame_extrema = ttk.Frame(self.extrema_tab)
        toolbar_frame_extrema.grid(row=5, column=0, columnspan=3)
        self.toolbar_extrema = NavigationToolbar2Tk(self.canvas_extrema, toolbar_frame_extrema)
        self.toolbar_extrema.update()
        
        # Результаты
        results_frame_extrema = ttk.LabelFrame(self.extrema_tab, text="Результаты", padding=10)
        results_frame_extrema.grid(row=6, column=0, columnspan=3, padx=5, pady=10, sticky="ew")
        
        # Текстовое поле для итераций (уменьшенная высота)
        ttk.Label(results_frame_extrema, text="Итерационная последовательность:").grid(row=0, column=0, sticky=tk.W)
        self.extrema_iterations_text = tk.Text(results_frame_extrema, height=8, width=80)
        extrema_scrollbar = ttk.Scrollbar(results_frame_extrema, orient="vertical", command=self.extrema_iterations_text.yview)
        self.extrema_iterations_text.configure(yscrollcommand=extrema_scrollbar.set)
        self.extrema_iterations_text.grid(row=1, column=0, columnspan=2, sticky="ew")
        extrema_scrollbar.grid(row=1, column=2, sticky="ns")
        
        # Результат
        self.extrema_result_label = ttk.Label(results_frame_extrema, text="", wraplength=600)
        self.extrema_result_label.grid(row=2, column=0, columnspan=2, pady=10, sticky=tk.W)

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
        
    def find_extrema_points(self):
        """Локализация экстремумов на графике"""
        try:
            formula = self.formula_entry.get().strip()
            x_min_str = self.x_min.get().strip()
            x_max_str = self.x_max.get().strip()

            if not formula or not x_min_str or not x_max_str:
                raise ValueError("Заполните все поля")

            x_min = float(x_min_str)
            x_max = float(x_max_str)
            
            # Поиск локальных экстремумов
            x_vals = np.linspace(x_min, x_max, 1000)
            y_vals = []
            
            for x in x_vals:
                try:
                    y = self.evaluate_function(formula, x)
                    y_vals.append(y)
                except:
                    y_vals.append(np.nan)
            
            y_vals = np.array(y_vals)
            
            # Поиск локальных минимумов и максимумов
            extrema_points = []
            for i in range(1, len(y_vals) - 1):
                if not (np.isnan(y_vals[i-1]) or np.isnan(y_vals[i]) or np.isnan(y_vals[i+1])):
                    # Локальный минимум
                    if y_vals[i] < y_vals[i-1] and y_vals[i] < y_vals[i+1]:
                        extrema_points.append((x_vals[i], y_vals[i], 'minimum'))
                    # Локальный максимум
                    elif y_vals[i] > y_vals[i-1] and y_vals[i] > y_vals[i+1]:
                        extrema_points.append((x_vals[i], y_vals[i], 'maximum'))
            
            # Перестроение графика с отмеченными экстремумами
            self.ax_analytical.clear()
            self.ax_analytical.plot(x_vals, y_vals, label=formula)
            
            # Отметка экстремумов
            for x_ext, y_ext, ext_type in extrema_points:
                color = 'red' if ext_type == 'maximum' else 'blue'
                marker = '^' if ext_type == 'maximum' else 'v'
                self.ax_analytical.plot(x_ext, y_ext, marker=marker, color=color, markersize=10, 
                                      label=f'{ext_type}: ({x_ext:.3f}, {y_ext:.3f})')
            
            self.ax_analytical.set_title("График с локализованными экстремумами")
            self.ax_analytical.set_xlabel("X")
            self.ax_analytical.set_ylabel("Y")
            self.ax_analytical.grid(True)
            self.ax_analytical.legend()
            self.canvas_analytical.draw()
            
            # Вывод результатов в текстовое поле
            self.extrema_results_text.delete(1.0, tk.END)
            if extrema_points:
                result_text = f"Найдено экстремумов: {len(extrema_points)}\n\n"
                for i, (x_ext, y_ext, ext_type) in enumerate(extrema_points):
                    ext_name = "Максимум" if ext_type == 'maximum' else "Минимум"
                    result_text += f"{i+1}. {ext_name}: x = {x_ext:.6f}, f(x) = {y_ext:.6f}\n"
            else:
                result_text = "Экстремумы не найдены в заданном диапазоне"
            
            self.extrema_results_text.insert(1.0, result_text)
            
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def numerical_derivative(self, formula, x, h=1e-8):
        """Численное дифференцирование"""
        try:
            f_x_plus_h = self.evaluate_function(formula, x + h)
            f_x_minus_h = self.evaluate_function(formula, x - h)
            return (f_x_plus_h - f_x_minus_h) / (2 * h)
        except:
            return None

    def numerical_second_derivative(self, formula, x, h=1e-6):
        """Численная вторая производная"""
        try:
            f_x_plus_h = self.evaluate_function(formula, x + h)
            f_x = self.evaluate_function(formula, x)
            f_x_minus_h = self.evaluate_function(formula, x - h)
            return (f_x_plus_h - 2*f_x + f_x_minus_h) / (h**2)
        except:
            return None

    def solve_extrema_parabolic(self):
        """Метод парабол для поиска экстремума"""
        try:
            formula = self.extrema_formula_entry.get().strip()
            a_str = self.extrema_a_entry.get().strip()
            b_str = self.extrema_b_entry.get().strip()
            epsilon_str = self.extrema_epsilon_entry.get().strip()
            
            if not formula or not a_str or not b_str or not epsilon_str:
                raise ValueError("Заполните все поля")
        
            a = float(a_str)
            b = float(b_str)
            epsilon = float(epsilon_str)
            
            if a >= b:
                raise ValueError("a должно быть меньше b")
            
            # Начальные точки для метода парабол
            x1 = a
            x2 = (a + b) / 2
            x3 = b
            
            iterations = []
            iteration_count = 0
            max_iterations = 1000
            
            while iteration_count < max_iterations:
                iteration_count += 1
                
                # Вычисляем значения функции
                f1 = self.evaluate_function(formula, x1)
                f2 = self.evaluate_function(formula, x2)
                f3 = self.evaluate_function(formula, x3)
                
                # Проверяем условие унимодальности
                if not (x1 < x2 < x3):
                    raise ValueError("Нарушен порядок точек")
                
                # Вычисляем коэффициенты параболы
                a0 = f1
                a1 = (f2 - f1) / (x2 - x1)
                a2 = ((f3 - f1) / (x3 - x1) - (f2 - f1) / (x2 - x1)) / (x3 - x2)
                
                # Новая точка (вершина параболы)
                if abs(a2) < 1e-12:
                    raise ValueError("Вторая производная близка к нулю")
                
                x_new = (x1 + x2) / 2 - a1 / (2 * a2)
                f_new = self.evaluate_function(formula, x_new)
                
                iterations.append({
                    'iteration': iteration_count,
                    'x1': x1, 'x2': x2, 'x3': x3, 'x_new': x_new,
                    'f1': f1, 'f2': f2, 'f3': f3, 'f_new': f_new,
                    'interval_length': x3 - x1
                })
                
                # Проверка точности
                if x3 - x1 < epsilon:
                    break
                
                # Обновление интервала
                if x_new < x2:
                    if f_new < f2:
                        x3, x2 = x2, x_new
                    else:
                        x1 = x_new
                else:
                    if f_new < f2:
                        x1, x2 = x2, x_new
                    else:
                        x3 = x_new
            
            # Результат
            extremum_x = (x1 + x3) / 2
            extremum_f = self.evaluate_function(formula, extremum_x)
            
            # Определение типа экстремума
            first_derivative = self.numerical_derivative(formula, extremum_x)
            second_derivative = self.numerical_second_derivative(formula, extremum_x)
            
            if second_derivative is not None:
                if second_derivative > 0:
                    extremum_type = "Минимум"
                elif second_derivative < 0:
                    extremum_type = "Максимум"
                else:
                    extremum_type = "Неопределенный"
            else:
                extremum_type = "Неопределенный"
            
            # Отображение результатов
            self.display_extrema_iterations(iterations, extremum_x, extremum_f, 
                                          first_derivative, second_derivative, 
                                          extremum_type, iteration_count)
            
            # Построение графика
            self.plot_extrema_graph(formula, extremum_x, a, b)
            
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def display_extrema_iterations(self, iterations, extremum_x, extremum_f, 
                                 first_deriv, second_deriv, extremum_type, iteration_count):
        """Отображает результаты итераций поиска экстремума"""
        self.extrema_iterations_text.delete(1.0, tk.END)
        
        header = f"{'№':<3} {'x1':<10} {'x2':<10} {'x3':<10} {'x_new':<10} {'f_new':<12} {'|x3-x1|':<12}\n"
        self.extrema_iterations_text.insert(tk.END, header)
        self.extrema_iterations_text.insert(tk.END, "-" * 80 + "\n")
        
        for iter_data in iterations:
            line = (f"{iter_data['iteration']:<3} "
                   f"{iter_data['x1']:<10.6f} "
                   f"{iter_data['x2']:<10.6f} "
                   f"{iter_data['x3']:<10.6f} "
                   f"{iter_data['x_new']:<10.6f} "
                   f"{iter_data['f_new']:<12.6f} "
                   f"{iter_data['interval_length']:<12.6e}\n")
            self.extrema_iterations_text.insert(tk.END, line)
        
        result_text = (f"\nРезультат:\n"
                      f"Точка экстремума: x = {extremum_x:.6f}\n"
                      f"Значение функции: f(x) = {extremum_f:.6f}\n"
                      f"Тип экстремума: {extremum_type}\n"
                      f"Количество итераций: {iteration_count}")
        
        if first_deriv is not None:
            result_text += f"\nПервая производная: f'(x) = {first_deriv:.6e}"
        if second_deriv is not None:
            result_text += f"\nВторая производная: f''(x) = {second_deriv:.6e}"
        
        self.extrema_result_label.config(text=result_text)

    def plot_extrema_graph(self, formula, extremum_x, original_a, original_b):
        """Строит график функции с найденным экстремумом"""
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
            
            self.ax_extrema.clear()
            
            # График функции
            self.ax_extrema.plot(x_vals, y_vals, 'b-', label=f'f(x) = {formula}', linewidth=2)
            
            # Найденный экстремум
            f_extremum = self.evaluate_function(formula, extremum_x)
            second_deriv = self.numerical_second_derivative(formula, extremum_x)
            
            if second_deriv is not None and second_deriv > 0:
                color, marker, label_type = 'red', 'v', 'Минимум'
            elif second_deriv is not None and second_deriv < 0:
                color, marker, label_type = 'green', '^', 'Максимум'
            else:
                color, marker, label_type = 'orange', 'o', 'Экстремум'
                
            self.ax_extrema.plot(extremum_x, f_extremum, marker=marker, color=color, 
                               markersize=10, label=f'{label_type}: x = {extremum_x:.6f}')
            
            # Исходный интервал
            self.ax_extrema.axvline(x=original_a, color='gray', linestyle='--', alpha=0.7, 
                                  label=f'Интервал [{original_a:.2f}, {original_b:.2f}]')
            self.ax_extrema.axvline(x=original_b, color='gray', linestyle='--', alpha=0.7)
            
            self.ax_extrema.set_title(f"Поиск экстремума функции {formula} методом парабол")
            self.ax_extrema.set_xlabel("x")
            self.ax_extrema.set_ylabel("f(x)")
            self.ax_extrema.grid(True, alpha=0.3)
            self.ax_extrema.legend()
            
            self.canvas_extrema.draw()
            
        except Exception as e:
            messagebox.showerror("Ошибка построения графика", str(e))
        

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
