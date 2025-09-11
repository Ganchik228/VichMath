import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

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
        
        self.notebook.add(self.analytical_tab, text="Аналитическая функция")
        self.notebook.add(self.tabular_tab, text="Табличная функция")
        self.notebook.pack(padx=10, pady=10)
        
        self.create_analytical_tab()
        self.create_tabular_tab()
        
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
        

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
