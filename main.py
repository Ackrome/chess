from models import *
import numpy as np
from tkinter import *
from collections import Counter
### !!!ВАЖНО: 1 - белая фигура; 2 - чёрная фигура; 0 - нет фигуры
###################################################################################################
### Необходимые переменные
###################################################################################################

# Состояние игры: берём фигуру или ставим
is_pick = 1

# Количество ходов
n_moves = 1

# Разделитель принимаемых функцией xod координат
separator_coords = ' '

# Список букв для отображения вокруг шахматной доски
Alpha = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

# Список цифр для отображения вокруг шахматной доски
Beta = ['1', '2', '3', '4', '5', '6', '7', '8']

# Словарь перехода из строчного названия в строчное отображение фигуры unicode
coder = {
    'pawn_1': '\u2659', 'pawn_2': '\u265F',
    'rook_1': '\u2656', 'rook_2': '\u265C',
    'knight_1': '\u2658', 'knight_2': '\u265E',
    'bishop_1': '\u2657', 'bishop_2': '\u265D',
    'king_1': '\u2654', 'king_2': '\u265A',
    'queen_1': '\u2655', 'queen_2': '\u265B',
    '0_0': ''
}

# Двумерный кортеж начальных позиций
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

# Словарь классов фигур 
figure_classes = {
    'pawn': pawn,
    'rook': rook,
    'knight': knight,
    'bishop': bishop,
    'king': king,
    'queen': queen,
}

selected_buttons = [] # История нажатых кнопок
buttons = [] # Матрица 8 х 8 всех кнопок поля
eaten_figures = [[],[]] # двумерный список съеденных фигур, вида [e1,e2]
eat_init = 0 # Показатель инициализации визуализации съеденных фигур

cell_size=40 # Размер стороны клетки
rows=8 # Количество рядов
plus=2 # Смещение всего поля (НЕ МЕНЯТЬ)
mult=1.7 # Мультипликатор размера
created_eaten = [] # Объекты выведенных съеденных фигур


logic = [[0 for i in range(8)] for j in range(8)] # <=== Логическое представление игрового поля, его модель
for i in range(8):
    for j in range(8):
        cell = start_positions[i][j]

        if cell[-1]!='0':
            logic[i][j] = figure_classes[cell[:-2]](color=int(cell[-1]), x=i, y=j)

# ID объектов canvas, где содержатся отображаемые имена игроков
p1 = ''
p2 = ''

x_offset = 0
y_offset = 0
window_width = 0
window_height = 0

canvas = []
root = []
###################################################################################################
### Необходимые функции
###################################################################################################
    
def get_poses(inpt):
    """
    Converts user input into chessboard coordinates.

    :param inpt: Input string in the format "letter number" (e.g., "A 1").
    :return: A tuple (x, y) where x is the row index and y is the column index.
    :raises Exception: If the input format is invalid.
    """
    y, x = [t for t in inpt.split() if t]

    if len(y)!=1 or len(x)!=1:
        raise Exception

    y = y.upper()
    x = int(x)-1
    y = 'ABCDEFGH'.find(y)

    return (x, y)


def is_check_or_checkmate(logic) -> tuple:
    """
    Determines if a player is in check or checkmate.

    :param logic: The logical representation of the chessboard.
    :return: A tuple (color, state, danger_positions):
        - color: 1 for white, 2 for black, 0 for no checkmate.
        - state: 1 for check, 2 for checkmate, 0 for no danger.
        - danger_positions: List of positions threatening the king, if applicable.
    """
    # Поиск королей
    kings = [0]*3
    for x in range(8):
        for y in range(8):
            if logic[x][y] and logic[x][y].name()=='King':
                kings[logic[x][y].color] = (x, y)

    # ШАХ
    kings_state = (
        0,
        danger_poses_check(kings[1][0], kings[1][1], logic),
        danger_poses_check(kings[2][0], kings[2][1], logic),
    )   

    # ШАХ И МАТ
    delta = (-1, 0, 1)
    kings_state_2 = [[] for i in range(3)]
    for color in range(1, 3):

        for delta_x in delta:
            for delta_y in delta:
                cell = (kings[color][0]+delta_x, kings[color][1]+delta_y)
                danger_cell = danger_poses_check(cell[0], cell[1], logic)
                kings_state_2[color].append(danger_cell)

    if all(kings_state_2[1]):
        return (1, 2, 0)

    if all(kings_state_2[2]):
        return (2, 2, 0)
    
    if kings_state[1]:
        return (1, 1, kings_state[1])
    
    if kings_state[2]:
        return (2, 1, kings_state[2])

    return (0, 0, 0)
    
picked = ''
# Если берем фигуру
def pick(inpt):
    """
    Handles the logic for selecting a chess piece to move.

    :param inpt: Input string with the coordinates of the piece to pick.
    """
    global n_moves
    global logic
    global is_pick
    global picked
    global root
    global canvas
    
    x, y = get_poses(inpt)
    
    if logic[x][y] and logic[x][y].color%2!=n_moves%2:
        return
    
    checkmate = is_check_or_checkmate(logic)
    figure = logic[x][y]
    try:
        possible_poses = figure.probable_poses_check(logic)
        if not len(possible_poses):
            return
        danger_poses = danger_poses_check(x, y, logic)
    except:
        return

    if checkmate[1]==1 and n_moves%2!=checkmate[0]%2:


        danger_poses = list(checkmate[2])
        render(danger=danger_poses)
    
    elif checkmate[1]==2 and n_moves%2!=checkmate[0]%2:
        return

    is_pick = 0
    picked = inpt
    render(possible_poses, danger_poses)
            
            
# Если ставим уже взятую фигуру:
def place(inpt):
    """
    Handles the logic for placing a selected chess piece on the board.

    :param inpt: Input string with the coordinates where the piece will be placed.
    """
    global n_moves
    global logic
    global is_pick
    global picked
    global canvas
    global root
    x, y = get_poses(picked)
    new_x, new_y = get_poses(inpt)
    possible_poses = logic[x][y].probable_poses_check(logic)
            
    if (new_x, new_y) not in possible_poses:
        return

    result = logic[x][y].move(logic, new_x, new_y, possible_poses)

    if result[0]==1:
        new_logic = result[1]

        if is_check_or_checkmate(new_logic)[0]%2!=n_moves%2 and is_check_or_checkmate(new_logic)[1]==1:
            return
            
        logic = new_logic
        n_moves += 1
        is_pick = 1
        show_player_who(canvas,n_moves)
        render()
        
    
    elif result[0]==2:
        new_logic = result[1]
        
        if is_check_or_checkmate(new_logic)[0]%2!=n_moves%2 and is_check_or_checkmate(new_logic)[1]==1:
            return

        eaten_figures[n_moves%2].append(f'{result[2].name().lower()}_{result[2].color}')
    
        logic = new_logic
        n_moves += 1
        is_pick = 1
        show_player_who(canvas,n_moves)
        render()
    
    else:
        return
###################################################################################################
### Отображение
###################################################################################################
def button_click(button, position):
    """
    Handles the button click event for the chessboard.

    :param button: The button object that was clicked.
    :param position: The position on the board associated with the button.
    """
    global is_pick
    global eat_init
    if len(selected_buttons):
        if selected_buttons[-1]:
            selected_buttons[-1].configure(bg=selected_buttons[-1].default_color)
    
    button.configure(bg="yellow")
    selected_buttons.append(button)
    
    if is_pick:
        pick(position)
    else:
        place(position)
        
    if eaten_figures != [[],[]] and eat_init == 0:
           canvas.create_text(
           3* ((cell_size) * (rows + 1 + plus) * mult) / 4, int(cell_size*1.03),
           text=f"Съеденные фигуры:", font=('Times New Roman', int((cell_size) ** 0.75)), fill="black"
           )
           show_eaten_figures(canvas)
           eat_init = 1
           
    elif eat_init == 1:
        show_eaten_figures(canvas)

    
def show_eaten_figures(canvas):
    """
    Displays the pieces that have been captured on the canvas.

    :param canvas: The canvas object where captured pieces are shown.
    """
    for i in created_eaten:
        canvas.delete(i)
        
    for i in range(len(eaten_figures)):
        count = dict(Counter(eaten_figures[i]))
        for j in range(len(count.keys())):
            
            created_eaten.append(canvas.create_text(
                (5+2*i)*((cell_size) * (rows + 1 + plus) * mult)//8,(1.3*j+3)*cell_size // 2,
                text=f"{get_code(list(count.keys())[j])} x {count[list(count.keys())[j]]}", font=('Times New Roman', int((cell_size) ** 0.8)), fill="black"
            ))
    

def show_player_who(canvas,n_moves):
    """
    Highlights the current player's turn on the canvas.

    :param canvas: The canvas object where player information is displayed.
    :param n_moves: The number of moves made so far.
    """
    if n_moves%2:
        canvas.itemconfig(1, fill="green")
        canvas.itemconfig(3, fill="black")
    else:
        canvas.itemconfig(3, fill="green")
        canvas.itemconfig(1, fill="black")

def show_notification(root, message, width=window_width, height=100, font=('Times New Roman', 14), delay=3000, color = 'black', x_shift = x_offset+9, y_shift = y_offset-100):
    """
    Creates a notification popup with a given message.

    :param root: The root Tkinter object.
    :param message: The notification text.
    :param width: Width of the notification window.
    :param height: Height of the notification window.
    :param font: Font of the notification text.
    :param delay: Duration (in milliseconds) before the notification disappears.
    :param color: Text color.
    :param x_shift: X-coordinate offset for positioning the window.
    :param y_shift: Y-coordinate offset for positioning the window.
    """
    
    # Для всех уведомлений width=window_width,x_shift=x_offset+9,y_shift = y_offset-100
    notification = Toplevel(root)
    notification.title("Уведомление")
    notification.geometry(f"{width}x{height}+{x_shift}+{y_shift}")
    notification.overrideredirect(True)  # Убираем рамки окна
    
    # Добавляем текст уведомления
    label = Label(notification, text=message, font=font, wraplength=width - 20, justify="center", fg = color)
    label.pack(expand=True, fill="both", padx=10, pady=10)
    
    # Автоматическое закрытие уведомления через delay миллисекунд
    notification.after(delay, notification.destroy)


def get_code(arg):
    """
    Maps chess piece codes to their Unicode representation.

    :param arg: The piece code.
    :return: The Unicode character representing the chess piece.
    """
    return np.vectorize(coder.get)(arg)

def get_adeq_fig(arg):
    """
    Maps logical representations of pieces to their Unicode representation.

    :param arg: The logical representation of a chess piece.
    :return: The Unicode character representing the chess piece.
    """
    name_lower = np.vectorize(lambda x: x.name().lower() +'_'+ x.color())
    return np.vectorize(coder.get)(name_lower(arg))


def get_player_names():
    """
    Opens a window to input the names of the players.

    :return: A list containing the names of the players [white_player, black_player].
    """
    names = []

    def save_names():
        names.append(entry_white.get())
        names.append(entry_black.get())
        input_window.destroy()

    input_window = Tk()
    input_window.title("Введите имена игроков")
    
    # Размер окна
    window_width = int(250)
    window_height = int(100)

    # Получение размера экрана
    screen_width = input_window.winfo_screenwidth()
    screen_height = input_window.winfo_screenheight()

    # Расчет координат для центрирования окна
    x_offset = (screen_width - window_width) // 2
    y_offset = (screen_height - window_height) // 2

    # Установка размера и позиции окна
    input_window.geometry(f"{window_width}x{window_height}+{x_offset}+{y_offset}")  

    Label(input_window, text="Игрок 1 (белые):").grid(row=0, column=0, padx=5, pady=5)
    entry_white = Entry(input_window, width=20)
    entry_white.grid(row=0, column=1, padx=5, pady=5)

    Label(input_window, text="Игрок 2 (чёрные):").grid(row=1, column=0, padx=5, pady=5)
    entry_black = Entry(input_window, width=20)
    entry_black.grid(row=1, column=1, padx=5, pady=5)

    Button(input_window, text="Сохранить", command=save_names).grid(row=2, column=0, columnspan=2, pady=10)

    input_window.mainloop()
    
    return names

def create_chess_board(cell_size=cell_size, rows=rows, cols=rows, plus=plus, mult=mult, font=None, x_shift=100):
    """
    Creates and displays a graphical chessboard using Tkinter.

    :param cell_size: The size of each cell in pixels.
    :param rows: Number of rows on the chessboard.
    :param cols: Number of columns on the chessboard.
    :param plus: Padding for the chessboard.
    :param mult: Multiplier for scaling the board size.
    :param font: Font for displaying text on the board.
    :param x_shift: Horizontal offset for the board's position.
    """
    global x_offset
    global y_offset
    global window_width
    global window_height
    
    if font is None:
        font = ('Times New Roman', int((cell_size) ** 0.8))

    # Добавляем имена игроков
    player_names = get_player_names()
    
    canvas_width = (cell_size) * (rows + 1 + plus) * mult
    canvas_height = (cell_size) * (rows + 1 + plus)
    
    root = Tk()
    root.title("Шахматная доска из кнопок")
    
    # Размер окна
    window_width = int(canvas_width)
    window_height = int(canvas_height)

    # Получение размера экрана
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Расчет координат для центрирования окна
    x_offset = (screen_width - window_width) // 2
    y_offset = (screen_height - window_height) // 2

    # Установка размера и позиции окна
    root.geometry(f"{window_width}x{window_height}+{x_offset}+{y_offset}")    

    canvas = Canvas(root, width=canvas_width, height=canvas_height )
    canvas.pack()
    
    # Для всех уведомлений width=window_width,x_shift=x_offset+9,y_shift = y_offset-100
    
    # Приветствие
    show_notification(root,f"Добро пожаловать, {player_names[0]}(белые) и {player_names[1]}(черные) ! Игра начинается.", delay=5000,width=window_width,x_shift=x_offset+9,y_shift = y_offset-100)

    p1 = canvas.create_text(
        canvas_width / 3, cell_size / 3,
        text=f"{player_names[0]} (белые)", font=('Times New Roman', int((cell_size) ** 0.75)), fill="black"
    )
    canvas.create_text(
        canvas_width / 2, cell_size /3,
        text='vs', font=('Times New Roman', int((cell_size) ** 0.75)), fill="black"
    )
    p2 = canvas.create_text(
        2* canvas_width / 3, cell_size /3,
        text=f"{player_names[1]} (чёрные)", font=('Times New Roman', int((cell_size) ** 0.75)), fill="black"
    )

    show_player_who(canvas, n_moves)

    # Создаем шахматную доску
    for row in range(rows):
        buttons.append([])
        for col in range(cols):
            color = "white" if (row + col) % 2 == 0 else "black"
            position = f"{Alpha[col]}{separator_coords}{Beta[row]}"

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


    return root, canvas, buttons, player_names

def render(possible=(), danger=()):
    global logic
    global buttons
    
    for x in range(len(logic)):
        for y in range(len(logic[x])):
            cell = logic[x][y]
            new_text = f'{cell.name().lower()}_{cell.color}' if cell else '0_0'
            buttons[x][y].configure(text=coder[new_text])
            if (x, y) in possible:
                if cell:
                    buttons[x][y].configure(bg='yellow')
                else:
                    buttons[x][y].configure(bg='green')
            
            elif (x, y) in danger:
                buttons[x][y].configure(bg='red')
                
            else:
                buttons[x][y].configure(bg=buttons[x][y].default_color)

root, canvas, buttons, player_names = create_chess_board()

root.mainloop()
