import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import math


class PiecewiseLinearInterpolation:
    def __init__(self, x_points, y_points):
        self.x_points = np.array(x_points)
        self.y_points = np.array(y_points)
        self.segments = []
        self.calculate_segments()
    
    def calculate_segments(self):
        self.segments = []
        for i in range(len(self.x_points) - 1):
            x1, x2 = self.x_points[i], self.x_points[i + 1]
            y1, y2 = self.y_points[i], self.y_points[i + 1]
            
            k = (y2 - y1) / (x2 - x1) if x2 != x1 else 0
            b = y1 - k * x1
            
            self.segments.append({
                'interval': (x1, x2),
                'k': k,
                'b': b,
                'equation': f'y = {k:.6f}x + {b:.6f}'
            })
    
    def interpolate(self, x):
        if x < self.x_points[0] or x > self.x_points[-1]:
            raise ValueError("Точка вне диапазона интерполяции")
        
        for i, segment in enumerate(self.segments):
            x1, x2 = segment['interval']
            if x1 <= x <= x2:
                return segment['k'] * x + segment['b']
        
        return None
    
    def get_segment_by_index(self, index):
        if 0 <= index < len(self.segments):
            return self.segments[index]
        return None


class InterpolationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Кусочно-линейная интерполяция")
        self.root.geometry("1200x800")
        
        self.x_min = 0
        self.x_max = 5
        self.num_points = 10
        
        self.interpolator = None
        self.test_point_x = None
        self.test_point_y = None
        self.current_function = "(x-1.5)*sqrt(x+4)+sin(pi*x)"
        
        self.create_widgets()
        self.generate_points()
    
    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Левая панель управления
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Ввод функции
        ttk.Label(control_frame, text="Функция f(x):").grid(row=0, column=0, sticky=tk.W)
        self.function_var = tk.StringVar(value="(x-1.5)*sqrt(x+4)+sin(pi*x)")
        function_entry = ttk.Entry(control_frame, textvariable=self.function_var, width=35)
        function_entry.grid(row=1, column=0, columnspan=2, pady=(0, 5))
        
        # Подсказка
        hint_text = "Примеры: sin(x), (x-1.5)*sqrt(x+4)+sin(pi*x)\nДоступно: sin, cos, tan, sqrt, exp, log, pi, e"
        hint_label = ttk.Label(control_frame, text=hint_text, font=('Arial', 8), foreground='gray')
        hint_label.grid(row=2, column=0, columnspan=2, sticky=tk.W)
        
        # Интервал
        ttk.Label(control_frame, text="Интервал [a, b]:").grid(row=3, column=0, sticky=tk.W, pady=(10,0))
        interval_frame = ttk.Frame(control_frame)
        interval_frame.grid(row=4, column=0, columnspan=2, sticky=tk.W)
        
        self.x_min_var = tk.StringVar(value="0")
        self.x_max_var = tk.StringVar(value="5")
        ttk.Entry(interval_frame, textvariable=self.x_min_var, width=10).pack(side=tk.LEFT)
        ttk.Label(interval_frame, text=" до ").pack(side=tk.LEFT)
        ttk.Entry(interval_frame, textvariable=self.x_max_var, width=10).pack(side=tk.LEFT)
        
        # Настройки
        ttk.Label(control_frame, text="Количество точек:").grid(row=5, column=0, sticky=tk.W, pady=(10,0))
        self.points_var = tk.StringVar(value="10")
        ttk.Entry(control_frame, textvariable=self.points_var, width=15).grid(row=6, column=0, columnspan=2)
        
        ttk.Button(control_frame, text="Сгенерировать точки", 
                  command=self.generate_points).grid(row=7, column=0, columnspan=2, pady=5)
        
        # Выбор промежутка
        ttk.Label(control_frame, text="Выбрать промежуток:").grid(row=8, column=0, sticky=tk.W, pady=(10,0))
        self.segment_var = tk.StringVar()
        self.segment_combo = ttk.Combobox(control_frame, textvariable=self.segment_var, 
                                         width=30, state='readonly')
        self.segment_combo.grid(row=9, column=0, columnspan=2)
        self.segment_combo.bind('<<ComboboxSelected>>', self.show_segment_info)
        
        # Информация о промежутке
        ttk.Label(control_frame, text="Информация о промежутке:").grid(row=10, column=0, 
                                                                       sticky=tk.W, pady=(10,0))
        self.segment_info = tk.Text(control_frame, height=6, width=35)
        self.segment_info.grid(row=11, column=0, columnspan=2, pady=5)
        
        # Вычисление значения в точке
        ttk.Label(control_frame, text="Точка для вычисления:").grid(row=12, column=0, 
                                                                    sticky=tk.W, pady=(10,0))
        self.point_var = tk.StringVar(value="2.5")
        ttk.Entry(control_frame, textvariable=self.point_var, width=15).grid(row=13, column=0, columnspan=2)
        
        ttk.Button(control_frame, text="Вычислить значение", 
                  command=self.calculate_point).grid(row=14, column=0, columnspan=2, pady=5)
        
        self.result_label = ttk.Label(control_frame, text="", foreground="blue")
        self.result_label.grid(row=15, column=0, columnspan=2)
        
        # График
        self.figure = plt.Figure(figsize=(9, 7), dpi=100)
        self.ax = self.figure.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(self.figure, self.root)
        self.canvas.get_tk_widget().grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def evaluate_function(self, x_values, func_str):
        safe_dict = {
            'x': x_values,
            'sin': np.sin,
            'cos': np.cos,
            'tan': np.tan,
            'sqrt': np.sqrt,
            'exp': np.exp,
            'log': np.log,
            'log10': np.log10,
            'abs': np.abs,
            'pi': np.pi,
            'e': np.e,
            'arcsin': np.arcsin,
            'arccos': np.arccos,
            'arctan': np.arctan,
            'sinh': np.sinh,
            'cosh': np.cosh,
            'tanh': np.tanh,
            'power': np.power,
            'np': np,
        }
        
        try:
            result = eval(func_str, {"__builtins__": {}}, safe_dict)
            return result
        except Exception as e:
            raise ValueError(f"Ошибка в функции: {str(e)}")
    
    def generate_points(self):
        try:
            self.num_points = int(self.points_var.get())
            if self.num_points < 2:
                messagebox.showerror("Ошибка", "Количество точек должно быть >= 2")
                return
            
            self.x_min = float(self.x_min_var.get())
            self.x_max = float(self.x_max_var.get())
            
            if self.x_min >= self.x_max:
                messagebox.showerror("Ошибка", "Начало интервала должно быть меньше конца")
                return
            
            func_str = self.function_var.get().strip()
            if not func_str:
                messagebox.showerror("Ошибка", "Введите функцию")
                return
            
            self.current_function = func_str
            
            x_points = np.linspace(self.x_min, self.x_max, self.num_points)
            y_points = self.evaluate_function(x_points, func_str)
            
            self.interpolator = PiecewiseLinearInterpolation(x_points, y_points)
            
            segment_list = [f"Промежуток {i+1}: [{seg['interval'][0]:.3f}, {seg['interval'][1]:.3f}]" 
                          for i, seg in enumerate(self.interpolator.segments)]
            self.segment_combo['values'] = segment_list
            if segment_list:
                self.segment_combo.current(0)
                self.show_segment_info()
            
            self.plot_graph()
            
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def show_segment_info(self, event=None):
        if not self.interpolator:
            return
        
        index = self.segment_combo.current()
        segment = self.interpolator.get_segment_by_index(index)
        
        if segment:
            info = f"Интервал: [{segment['interval'][0]:.6f}, {segment['interval'][1]:.6f}]\n"
            info += f"Коэффициент k: {segment['k']:.6f}\n"
            info += f"Коэффициент b: {segment['b']:.6f}\n"
            info += f"Уравнение: {segment['equation']}"
            
            self.segment_info.delete(1.0, tk.END)
            self.segment_info.insert(1.0, info)
    
    def calculate_point(self):
        if not self.interpolator:
            messagebox.showerror("Ошибка", "Сначала сгенерируйте точки")
            return
        
        try:
            x = float(self.point_var.get())
            y = self.interpolator.interpolate(x)
            
            self.test_point_x = x
            self.test_point_y = y
            
            self.result_label.config(text=f"f({x:.4f}) = {y:.6f}")
            self.plot_graph()
            
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def plot_graph(self):
        if not self.interpolator:
            return
        
        self.ax.clear()
        
        try:
            x_fine = np.linspace(self.x_min, self.x_max, 1000)
            y_fine = self.evaluate_function(x_fine, self.current_function)
            self.ax.plot(x_fine, y_fine, 'b-', label=f'Исходная функция: {self.current_function}', linewidth=1.5)
        except:
            pass
        
        x_interp = np.linspace(self.x_min, self.x_max, 500)
        y_interp = [self.interpolator.interpolate(x) for x in x_interp]
        self.ax.plot(x_interp, y_interp, 'r--', label='Интерполяция', linewidth=2)
        
        self.ax.plot(self.interpolator.x_points, self.interpolator.y_points, 
                    'go', label='Опорные точки', markersize=8)
        
        if self.test_point_x is not None and self.test_point_y is not None:
            self.ax.plot(self.test_point_x, self.test_point_y, 
                        'y*', markersize=15, label=f'Точка ({self.test_point_x:.3f}, {self.test_point_y:.3f})')
        
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.ax.set_title('Кусочно-линейная интерполяция')
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)
        
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = InterpolationApp(root)
    root.mainloop()
