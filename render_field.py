import numpy as np
from tkinter import *

Alpha = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
Beta = ['1', '2', '3', '4', '5', '6', '7', '8']

coder = {
    'pawn_1': '\u2659', 'pawn_2': '\u265F',
    'rook_1': '\u2656', 'rook_2': '\u265C',
    'knight_1': '\u2658', 'knight_2': '\u265E',
    'bishop_1': '\u2657', 'bishop_2': '\u265D',
    'king_1': '\u2654', 'king_2': '\u265A',
    'queen_1': '\u2655', 'queen_2': '\u265B',
    '0_0': ''
}
start_positions = tuple([
    tuple(['rook_2', 'knight_2', 'bishop_2', 'queen_2', 'king_2', 'bishop_2', 'knight_2', 'rook_2']),
    tuple(['pawn_2' for i in range(8)]),
    tuple(['0_0' for i in range(8)]),
    tuple(['0_0' for i in range(8)]),
    tuple(['0_0' for i in range(8)]),
    tuple(['0_0' for i in range(8)]),
    tuple(['pawn_1' for i in range(8)]),
    tuple(['rook_1', 'knight_1', 'bishop_1', 'queen_1', 'king_1', 'bishop_1', 'knight_1', 'rook_1']),
])

selected_buttons = []
buttons = []
eaten_figures = [[],[]]


def button_click(button, position):
    """Обработчик нажатия кнопки."""
    if len(selected_buttons):
        if selected_buttons[-1]:
            selected_buttons[-1].configure(bg=selected_buttons[-1].default_color)

    button.configure(bg="yellow")
    selected_buttons.append(button)
    
    #xod(f"{position}")


def get_code(arg):
    return np.vectorize(coder.get)(arg)


def get_player_names():
    """Открывает окно для ввода имён игроков."""
    names = []

    def save_names():
        names.append(entry_white.get())
        names.append(entry_black.get())
        input_window.destroy()

    input_window = Toplevel()
    input_window.title("Введите имена игроков")

    Label(input_window, text="Игрок 1 (белые):").grid(row=0, column=0, padx=5, pady=5)
    entry_white = Entry(input_window, width=20)
    entry_white.grid(row=0, column=1, padx=5, pady=5)

    Label(input_window, text="Игрок 2 (чёрные):").grid(row=1, column=0, padx=5, pady=5)
    entry_black = Entry(input_window, width=20)
    entry_black.grid(row=1, column=1, padx=5, pady=5)

    Button(input_window, text="Сохранить", command=save_names).grid(row=2, column=0, columnspan=2, pady=10)

    input_window.wait_window()
    
    return names


def create_chess_board(cell_size, rows=8, cols=8, plus=2, mult=1.7, font=None):
    root = Tk()
    root.title("Шахматная доска из кнопок")

    canvas_width = (cell_size) * (rows + 1 + plus) * mult
    canvas_height = (cell_size) * (rows + 1 + plus)

    canvas = Canvas(root, width=canvas_width, height=canvas_height)
    canvas.pack()

    if font is None:
        font = ('Times New Roman', int((cell_size) ** 0.8))

    # Добавляем имена игроков
    player_names = get_player_names()
    

    canvas.create_text(
        canvas_width / 3, cell_size / 3,
        text=f"{player_names[0]} (белые)", font=('Times New Roman', int((cell_size) ** 0.75)), fill="black"
    )
    canvas.create_text(
        canvas_width / 2, cell_size /3,
        text='vs', font=('Times New Roman', int((cell_size) ** 0.75)), fill="black"
    )
    canvas.create_text(
        2* canvas_width / 3, cell_size /3,
        text=f"{player_names[1]} (чёрные)", font=('Times New Roman', int((cell_size) ** 0.75)), fill="black"
    )
    

    # Создаем шахматную доску
    for row in range(rows):
        buttons.append([])
        for col in range(cols):
            color = "white" if (row + col) % 2 == 0 else "black"
            position = f"{Alpha[col]}{Beta[row]}"

            btn = Button(
                canvas,
                text=get_code(start_positions)[row][col],
                font=font,
                fg="black" if color == "white" else "white",
                bg=color,
                activebackground=color,
            )
            btn.configure(command=lambda b=btn, pos=position: button_click(b, pos))
            btn.default_color = color

            canvas.create_window(
                (col + plus) * cell_size, (row + plus) * cell_size,
                window=btn, width=cell_size, height=cell_size
            )
            buttons[row].append(btn)

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


    return root, canvas, buttons


root, canvas, buttons = create_chess_board(
    cell_size=40,
    rows=8,
    plus=2,
    mult=1.7
)
root.mainloop()