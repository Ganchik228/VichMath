import matplotlib.pyplot as plt
import csv

def plot_function_from_file(filename):
    x_values = []
    y_values = []

    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 2:
                try:
                    x = float(row[0])
                    y = float(row[1])
                    x_values.append(x)
                    y_values.append(y)
                except ValueError:
                    print(f"Пропуск некорректной строки: {row}")

    if not x_values or not y_values:
        print("Нет данных для построения графика.")
        return

    fig, ax = plt.subplots()
    ax.plot(x_values, y_values)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    plt.grid(True)
    plt.show()

plot_function_from_file('test.csv')
