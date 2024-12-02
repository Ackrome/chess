import os
import time
from sys import exit
CONST=' '
os.system('cls')
while type(CONST)!=int:      
    try:
        CONST=int(input('Which game you want to play: EXTENDED CHESS(TYPE 0)  or ORIGINAL CHESS(TYPE 1) or CHECKERS(TYPE 2)? \nSelect the type of chess you wish to play by pressing the appropriate key: '))
    except:
        pass

if CONST==1:
    from models_orig import *
elif CONST==0:
    from models_plus import *
elif CONST==2:
    from models_checkers import *
### ВАЖНО: 1 - белая фигура; 2 - чёрная фигура; 0 - нет фигуры
###################################################################################################
### Необходимые переменные
###################################################################################################
Transdict= {'A':0,'B':1,'C':2,'D':3,'E':4,'F':5,'G':6,'H':7}
###################################################################################################
### Класс игры
###################################################################################################

class Game(): 
    def __init__(self, eaten ,success):
        self.field = Field()
        self.player_1 = input('Enter the first player: ')
        self.player_2 = input('Enter the second player: ')
        self.success = success
        self.eaten=eaten
        self.check_yes = 0
        self.play = 0
        self.previous_logics=[]
        self.previous_eaten=[]
        self.previous_eaten.append(self.eaten[:])
    
    def __move(self,data):       
        return self.field.logic[data[0]][data[1]].move(data)
    
    def __predict(self,data,eat=0):
        return self.field.logic[data[0]][data[1]].predict(data,eat)
        

    def xod(self,data):
        self.xod_data = self.__move(data)
        
        self.eaten.extend(self.xod_data[2])
        self.previous_eaten.append(self.eaten[:])
        self.success = self.xod_data[0]
        self.field.logic=self.xod_data[1] if self.xod_data[1] else self.field.logic
        self.previous_logics.append(self.field.logic)

    def check_given_xod(self):
        old_logic=self.field.logic
        
        if self.check_yes >=2 or (len(self.field.predict_danger(old_logic,(self.play)%2+1,1))==8):
            return 1
        
        os.system('cls')
        
    
        long_live_the_king=[]
        vortex_dict=dict()
        

        for i in self.field.predict_danger(old_logic,(self.play)%2+1):
            if self.field.logic[i[0]][i[1]].figure=='king':
                
                self.check_yes =1
                break
            else:
                self.check_yes =0

        print(('\033[1m'+self.player_1+' \033[31mvs\033[0m\033[1m '+self.player_2+'\033[0m\n').center(70))

        self.field.render(self.play, self.eaten,[[8,8]],[],self.field.predict_danger(old_logic,(self.play)%2+1),vortex_dict.keys(),long_live_the_king)

        print('\nThe moves should be entered as the \033[1mcoordinates\033[0m of the piece you want to go to, \033[1mEnter\033[0m,\nthe \033[1mcoordinates\033[0m you want to place that piece on, \033[1mEnter\033[0m.\n\nCoordinates should be given as \033[1m<letter><digit>\033[0m\n')
        if self.check_yes :
            print('\033[5m\033[31mCHECK\n\033[0m')
            
        xodik = input('Enter your move: ')
        xodik = xodik.split()
        xodik=''.join(xodik)
        
        if xodik=='endgame':
            return exit()
        if len(xodik)!=2:
            return 0
        try:
            int(xodik[1])
        except ValueError:
            return 0
        try:
            Transdict[xodik[0].capitalize()]
        except KeyError:
            return 0
        
        if old_logic[8-int(xodik[1])][Transdict[xodik[0].capitalize()]].figure_color!=(self.play)%2+1:
            return 0
        
        try_xod=tuple([8-int(xodik[1]),Transdict[xodik[0].capitalize()],old_logic,(self.play)%2+1])


        os.system('cls')
        
        
        print(('\033[1m'+self.player_1+' \033[31mvs\033[0m\033[1m '+self.player_2+'\033[0m\n').center(70))
        if self.check_yes :
            self.field.render(self.play, self.eaten, self.__predict(try_xod),self.__predict(try_xod,1),self.field.predict_danger(try_xod[2],(self.play)%2+1),vortex_dict.keys(),long_live_the_king)
        else:
            self.field.render(self.play, self.eaten, self.__predict(try_xod),self.__predict(try_xod,1),self.field.predict_danger(try_xod[2],(self.play)%2+1),vortex_dict.keys())


        print('\nThe moves should be entered as the \033[1mcoordinates\033[0m of the piece you want to go to, \033[1mEnter\033[0m,\nthe \033[1mcoordinates\033[0m you want to place that piece on, \033[1mEnter\033[0m.\n\nCoordinates should be given as \033[1m<letter><digit>\033[0m\n')
        if self.check_yes :
            print('\033[5m\033[31mCHECK\n\033[0m')

        xodik_p1=xodik
        xodik_p2 = input('Enter your move: '+xodik_p1)
        
        xodik=xodik_p1+xodik_p2
        xodik = xodik.split()
        xodik=''.join(xodik)
        lotr = xodik

        if xodik=='endgame':
            return exit()
        
        if len(xodik)!=4:
            return 0
        
        for i in range(2):
            try:
                int(xodik[2*i+1])
            except ValueError:
                return 0
            try:
                Transdict[xodik[2*i].capitalize()]
            except KeyError:
                return 0
    
        if (self.play)%2+1!=self.field.logic[8-int(xodik[1])][Transdict[xodik[0].capitalize()]].figure_color:
            return 0
        
        xodik = tuple([8-int(xodik[1]),Transdict[xodik[0].capitalize()],8-int(xodik[3]),Transdict[xodik[2].capitalize()],old_logic,(self.play)%2+1])
        
        self.xod(xodik)

        if self.success==0:
            self.field.logic=old_logic
            return 0
        
        for i in self.field.predict_danger(old_logic,(self.play)%2+1):
            if self.field.logic[i[0]][i[1]].figure=='king':
                self.check_yes +=1

        if CONST == 2 and len(self.__predict(tuple([8-int(lotr[3]),Transdict[lotr[2].capitalize()],old_logic,(self.play)%2+1]),1))>=1 and self.success==2:
            return -2
        
        return -1
###################################################################################################
### Сама игра
###################################################################################################
os.system('cls')
new_game = Game([],0)
win=0
logics=[]
logics.append(new_game.field.logic[:])

while win!=True:
    prov=new_game.check_given_xod()
    while prov==0:
        print('\033[31mWrong move. Try again.\033[0m ', end='')
        time.sleep(0.7)
        prov=new_game.check_given_xod() 
    if prov ==-1:
        print('\n\033[32mMove accepted.\033[0m')
        new_game.play+=1
        time.sleep(0.7)
        os.system('cls')
    elif prov ==-2:
        print('\n\033[32mMove accepted.\033[0m')
        time.sleep(0.7)
        os.system('cls')
    elif prov==1:
        os.system('cls')
        if (new_game.play)%2+1==1:
            print(f'{new_game.player_1} won the game!')
        else:
            print(f'{new_game.player_2} won the game!')
        win=True