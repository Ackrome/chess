from tkinter import *
import numpy as np  
from models_orig import *

get_code = np.vectorize(coder.get)

selected_buttons = []
changed_for_move = []

def button_click(button, position):
    """Обработчик нажатия кнопки."""
    global selected_buttons

    # Сбрасываем цвет предыдущей кнопки
    if len(selected_buttons):
        if selected_buttons[-1]:
            selected_buttons[-1].configure(bg=selected_buttons[-1].default_color)
            
    if len(changed_for_move):
        for i in changed_for_move:
            i.configure(i.default_color)
    
    # Устанавливаем цвет текущей кнопки
    button.configure(bg="yellow")
    
    selected_buttons.append(button)
    
    #for i in predict_list(position)

    
    
    
    print(f"{position}")

def create_chess_board(canvas,cell_size,rows=8, cols=8,plus=2,font=None):
    
    if font==None:
        font = ('Times New Roman', int((cell_size)**0.8))


    for row in range(rows):

        for col in range(cols):
            # Определяем цвет клетки
            color = "white" if (row + col) % 2 == 0 else "black"
            
            position = f"{Alpha[col]}{Beta[row]}"
            
            
            # Создаем кнопку
            btn = Button(
                canvas, 
                text = get_code(start_positions)[row][col],
                font=font,
                fg="black" if color == "white" else "white",
                bg=color, 
                activebackground=color,
                 # Захват кнопки и координат
            )
            btn.configure(command=lambda b=btn, pos=position: button_click(b, pos))
            # Сохраняем исходный цвет кнопки
            btn.default_color = color
            
            # Размещаем кнопку на Canvas
            canvas.create_window((col+plus) * cell_size, (row+plus) * cell_size, 
                                 window=btn, width=cell_size, height=cell_size)
            

            
    # Добавляем буквенные обозначения (сверху и снизу)
    for col in range(cols):
        letter = Alpha[col]
        canvas.create_text(
            (col + plus) * cell_size, 1 * cell_size, 
            text=letter, font=font
        )
        canvas.create_text(
            (col + plus) * cell_size, (rows + plus) * cell_size, 
            text=letter, font=font
        )
    
    # Добавляем числовые обозначения (слева и справа)
    for row in range(rows):
        number = Beta[row]
        canvas.create_text(
            1 * cell_size, (row + plus) * cell_size, 
            text=number, font=font
        )
        canvas.create_text(
            (cols + plus) * cell_size, (row + plus) * cell_size, 
            text=number, font=font
        )
    

    return 

# Создаем главное окно
root = Tk()
root.title("Шахматная доска из кнопок")

cell_size=40
rows = 8
plus = 2
mult = 1.7
# Задаем размеры Canvas
canvas_width = (cell_size)*(rows+1+plus) *mult # Шахматная доска 8x8 с размерами клетки 50x50 пикселей
canvas_height = (cell_size)*(rows+1+plus)

canvas = Canvas(root, width=canvas_width, height=canvas_height)
canvas.pack()

# Создаем шахматную доску
create_chess_board(canvas,cell_size,plus=plus)

# Запускаем главное окно
root.mainloop()
