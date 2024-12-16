from models import Field, danger_poses_check
import os
import random


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
    
