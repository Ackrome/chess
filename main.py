from models import Field, danger_poses_check
import os
import random
import numpy as np
from tkinter import *


### !!!ВАЖНО: 1 - белая фигура; 2 - чёрная фигура; 0 - нет фигуры




###################################################################################################
### Необходимые переменные
###################################################################################################

xods = [] # <= Сюда будут сохраняться все ходы в виде копий объекта Game для возможности отката

start_message = '\nВыберите фигуру для хода, введя координаты в фомате *буква* *пробел* *цифра*.\nОтмените предыдущий ход, введя /back.\nПроверьте угрозы, введя /check *координаты фигуры*\nСдайтесь, введи /endgame\n'
start_message_2 = '\nВыберите одну из подсвеченных клеток для хода, введя координаты в фомате *буква* *пробел* *цифра*.\nОтмените выбор фигуры, введя /back.\n'


###################################################################################################
### Класс игры
###################################################################################################

class Game(): 
    def __init__(self, field=None, c=None, player_1=-100, player_2=-100, eaten_1=None, eaten_2=None):
        self.field = field if field else Field()
        self.c = c if c else 0 # число ходов
        self.eaten_1 = eaten_1 if eaten_1 else []
        self.eaten_2 = eaten_2 if eaten_2 else []


        (self.player_1, self.player_2) = (self.player_1, self.player_2) if random.randint(0, 1) else (self.player_2, self.player_1)

    def save(self):
        return Game(self.field.save(), self.c, self.player_1, self.player_2, self.eaten_1.copy(), self.eaten_2.copy())
    
###################################################################################################
### Класс поля
###################################################################################################

class Field():
    def __init__(self, logic=None):
        if logic:
            self.logic = logic
        else:
            self.logic = self.first_generation()

    
    def first_generation(self):
        logic = [[0 for i in range(8)] for j in range(8)] # <=== Логическое представление игрового поля, его модель

        for i in range(8):
            for j in range(8):
                cell = start_positions[i][j]

                if cell:
                    logic[i][j] = figure_classes[cell[:-2]](color=int(cell[-1]), x=i, y=j)              
                
        return logic
                
                
    def render(self, c: int, p1: str, p2: str, e1: str, e2: str, possible_poses: tuple=(), danger_poses: tuple=()):
        result = []

        for i in range(8):
            row = f'|\033[1;36;40m{8-i}  \033[0;37;40m'

            for j in range(8):
                cll = self.logic[i][j]

                if (i, j) in possible_poses:
                    cll = possible_to_eat(str(cll).center(2)) if cll else possible('.'.center(2))

                elif (i, j) in danger_poses:
                    cll = danger(str(cll).center(2))
                
                else:
                    cll = str(cll).center(2) if cll else '.'.center(2)

                row += cll
            
            row += f'\033[1;36;40m {8-i}\033[0;37;40m|'

            field.append(row)
        
        field.extend(['|' + ' '*21 + '|',
                    '|\033[1;36;40m   A B C D E F G H   \033[0;37;40m|',
                    "'"*23])
        
        # Статистика
        stats = ['' for i in range(2)]

        stats.append(f'')
        stats.append(f'{" "*5}\033[30;2;47m{p1}\033[0;37;40m: {", ".join(e1)}')
        stats.extend([
            '',
            '',
            '',
            f'{" "*5}Было сделано ходов: {c}',
            '',
            '',
            '',
        ])
        stats.append(f'{" "*5}\033[0;2;40m{p2}\033[0;37;40m: {", ".join(e2)}')

        stats.extend(['' for i in range(len(field)-len(stats))])

        result = [x + y for x, y in zip(field, stats)]


        return '\n'.join(result)
    

    def save(self):
        return Field([x[::] for x in self.logic][::])

###################################################################################################
### Необходимые функции
###################################################################################################
    
def get_poses(inpt):
    y, x = [t for t in inpt.split() if t]

    if len(y)!=1 or len(x)!=1:
        raise Exception

    y = y.upper()
    x = 8-int(x)
    y = 'ABCDEFGH'.find(y)

    return (x, y)


def is_check_or_checkmate(logic) -> tuple:
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
    

def xod(game: Game, message: str=start_message, message_2: str=start_message_2, special: str='', danger_poses: tuple=()):
    checkmate = is_check_or_checkmate(game.field.logic)

    if checkmate[1]==1 and game.c%2!=checkmate[0]%2:
        message = f'\n{[0, game.player_1, game.player_2][checkmate[0]]}, ваш король находится под шахом!\n' + message

        danger_poses = tuple(list(danger_poses) + list(checkmate[2]))
    
    elif checkmate[1]==2 and game.c%2!=checkmate[0]%2:
        message = f'\n{[game.player_1, game.player_2][checkmate[0]]}, ваш король находится под матом!\n' + message

    os.system('cls')

    print(f'{game.player_1 if not game.c%2 else game.player_2} - ваш ход!\n')

    print(game.field.render(game.c, game.player_1, game.player_2, game.eaten_1, game.eaten_2, danger_poses=danger_poses))
          
    print(message)

    inpt = special if special else input('Ваше действие: ')

    # Сдаться
    if inpt=='/end game':
        print(f'Игрок {game.player_2 if game.c%2 else game.player_1} выиграл!')
    
    # Откат хода
    if inpt=='/back':
        confirmation = input('Вы уверены (Yes/No)?: ')

        if confirmation=='Yes':
            if xods:
                xod(xods[-1], start_message)

            else:
                msg = '\nВы уже на ходе 0!\n' + start_message
                xod(game, msg)
        
        else:
            xod(game, start_message)

    # Проверка угроз
    if inpt[:6]=='/check': 
        msg = '\nВы неправильно ввели координаты!\n' + start_message
        try:
            x_d, y_d = get_poses(inpt[7:])

            if game.field.logic[x_d][y_d].color%2==game.c%2:
                msg = '\nВыберите фигуру своего цвета!\n' + start_message
                xod(game, msg)

        except Exception:
            xod(game, msg)

        danger_poses = danger_poses_check(x_d, y_d, game.field.logic)

        xod(game, danger_poses=danger_poses)

    # Обычный ход
    else:
        msg = '\nВы неправильно ввели координаты!\n' + start_message
        try:
            x, y = get_poses(inpt)

            if game.field.logic[x][y].color%2==game.c%2:
                msg = '\nВыберите фигуру своего цвета!\n' + start_message
                xod(game, msg)

        except Exception:
            xod(game, msg)
        
        figure = game.field.logic[x][y]

        possible_poses = figure.probable_poses_check(game.field.logic)

        os.system('cls')
        print(f'{game.player_1 if not game.c%2 else game.player_2} - ваш ход!\n')
        game.field.render(game.c, game.player_1, game.player_2, game.eaten_1, game.eaten_2, possible_poses)
        print(message_2)

        inpt_ = input('Ваше действие: ')

        # Отмена выбора фигуры
        if inpt_=='/back':
            xod(game)

        # Обычный ход
        else:
            msg_2 = '\nВы неправильно ввели координаты!\n' + start_message_2
            try:
                new_x, new_y = get_poses(inpt_)
            except Exception:
                xod(game, message_2=msg_2, special=inpt)

            msg_2 = '\nВы выбрали невозможную для хода клетку!\n' + start_message_2
            if (new_x, new_y) not in possible_poses:
                xod(game, message_2=msg_2, special=inpt)
        
            result = game.field.logic[x][y].move(game.field.logic, new_x, new_y, possible_poses)

            if result[0]==1:
                xods.append(game.save())

                new_logic = result[1]

                if is_check_or_checkmate(new_logic)[0]%2!=game.c%2 and is_check_or_checkmate(new_logic)[1]==1:
                    msg_2 = '\nВы не можете поставить своего короля под угрозу!\n' + start_message
                    xod(game, message_2=msg_2, special=inpt)

                game.field.logic = new_logic
                game.c += 1
                xod(game)
            
            elif result[0]==2:
                xods.append(game.save())

                new_logic = result[1]
                
                if is_check_or_checkmate(new_logic)[0]%2!=game.c%2 and is_check_or_checkmate(new_logic)[1]==1:
                    msg_2 = '\nВы не можете поставить своего короля под угрозу!\n' + start_message
                    xod(game, message_2=msg_2, special=inpt)

                if game.c%2:
                    game.eaten_2.append(result[2].name())

                else:
                    game.eaten_1.append(result[2].name())
                game.field.logic = new_logic
                game.c += 1
                xod(game)
            
            else:
                msg = '\nНевозможно сделать такой ход\n' + start_message
                xod(game, message=msg)
        

###################################################################################################
### Игровой процесс
###################################################################################################

this_game = Game()

xod(this_game, start_message)




# c = 1
# wr_fl = 0
# while True:
#     os.system('cls')

#     print(f'{this_game.player_1 if c%2 else this_game.player_2} - ваш ход!')

#     print(this_game.field.render())

#     positions = [x for x in input(f'{this_game.player_1 if c%2 else this_game.player_2}, {"Вы неправильно ввели координаты, попробуйте ещё раз" if wr_fl else "Введите координаты хода"}: ').split() if x]
    
#     if len(positions)!=4:
#         wr_fl = 1
#         continue

#     positions[0], positions[2] = positions[0].lower(), positions[2].lower()

#     if ord(positions[0]) in range(97, 123) and ord(positions[1]) in range(48, 58) and ord(positions[2]) in range(97, 123) and ord(positions[3]) in range(48, 58):
#         # Перевод в логическое понимание для работы с координатами
#         positions = [
#             8 - int(positions[1]),
#             ord(positions[0])-97,
#             8 - int(positions[3]),
#             ord(positions[2])-97,
#         ]

#         cll = this_game.field.logic[positions[0]][positions[1]]

#         if cll.figure_color!=c%2+2*(not c%2):
#             wr_fl = 1
#             continue
        
#         new_x = positions[2]
#         new_y = positions[3]

#         if cll.figure=='pawn':
#             result = figure_move['pawn_'+str(cll.figure_color)](this_game.field.logic, cll, new_x, new_y)
#         else:
#             result = figure_move[cll.figure](this_game.field.logic, cll, new_x, new_y)

#         if result[0]==1:
#             this_game.field.logic = result[1]
#             c += 1
#             wr_fl = 0
#         elif result[0]==2:
#           this_game.field.logic = result[1]
#           if c%1:
#               this_game.eaten_1.append(result[2])
#           else:
#               this_game.eaten_2.append(result[2])
#           c += 1
#           wr_fl = 0
#         
#           else:
#             wr_fl = 1
#             continue

    
#     else:
#         wr_fl = 1
#         continue


import numpy as np
from tkinter import *

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

selected_buttons = [] # История нажатых кнопок
buttons = [] # Матрица 8 х 8 всех кнопок поля
eaten_figures = [[],[]] # двумерный список съеденных фигур, вида [e1,e2]
eat_init = 0 # Показатель инициализации визуализации съеденных фигур


def button_click(button, position):
    """Обработчик нажатия кнопки."""
    if len(selected_buttons):
        if selected_buttons[-1]:
            selected_buttons[-1].configure(bg=selected_buttons[-1].default_color)

    button.configure(bg="yellow")
    selected_buttons.append(button)
    
    ######################################################
    #
    #
    #
    #xod_data = xod(f"{position}")
    #
    #
    #
    # if eaten_figures == None and eat_init == 0:
    #       canvas.create_text(
    #       3* canvas_width / 4, cell_size,
    #       text=f"eaten figures:", font=('Times New Roman', int((cell_size) ** 0.75)), fill="black"
    #       )
    #       eat_init = 1
    
    ######################################################
    

def get_code(arg):
    return np.vectorize(coder.get)(arg)

def get_adeq_fig(arg):
    name_lower = np.vectorize(lambda x: x.name().lower() +'_'+ x.color())
    return np.vectorize(coder.get)(name_lower(arg))


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


root, canvas, buttons, player_names = create_chess_board(
    cell_size=40,
    rows=8,
    plus=2,
    mult=1.7
)

##########################################################################################
#
#
#
# Init Game
#
#
#

##########################################################################################

root.mainloop()
