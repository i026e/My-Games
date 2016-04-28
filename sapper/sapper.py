#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Created on Wed Apr 27 16:08:07 2016

@author: pavel
"""
import tkinter
import random
import time
import datetime

from sys import argv

SOUND_FILE = "95078__sandyrb__the-crash.wav" #"http://www.freesound.org/people/sandyrb/sounds/95078/"

DEFAULT_SIZE = 10
DEFAULT_BOMBS = 10
DEFAULT_SOUND = True
DEFAULT_CANONADE = True


class sound:    
    import sys 
    from threading import Thread
    from os import system
    from subprocess import call
    
    DELAY = 0.6
    
    def __init__(self, sound_file, enabled=True, canonade = False):
        self.sound_file = sound_file
        self.enabled = enabled
        
        self.canonade = canonade
        
        
        #print(sound.sys.platform)
        if sound.sys.platform == 'linux':
            self._play = self._play_linux
        elif sound.sys.platform == 'darwin':
            self._play = self._play_darwin
        else:
            self._play = self._play_windows
        
        
    def play(self, times):
        if self.enabled:
            times = times if self.canonade else 1
            
            for i in range(times):
                delay = random.uniform(i*sound.DELAY, (i+1)*sound.DELAY)
                sound.Thread(group=None, \
                             target = self._play_delayed, \
                             args=(delay,)).start()
            
                
    def _play_delayed(self, delay):
        time.sleep(delay)
        self._play()
    def _play_windows(self):
        self.system("start " + self.sound_file)
    def _play_linux(self):
        sound.call(["aplay",self.sound_file])
    def _play_darwin(self):
        sound.call(["afplay",self.sound_file])
        
class game:
    def __init__(self, grid_size, num_bombs):
        self.grid_size = grid_size
        self.num_cells = self.grid_size * self.grid_size        
        self.total_bombs = min(num_bombs, self.grid_size * self.grid_size -1)
        
        self.opened = [[False]*self.grid_size for i in range(self.grid_size)]        
        self.flagged = [[False]*self.grid_size for i in range(self.grid_size)]
        self.num_opened = 0
        self.num_flags = 0
        
        self.initialized = False
    def _init_grid(self, free_row, free_col):
        cells = [(r, c) for r in range(self.grid_size) 
                        for c in range(self.grid_size) 
                        if not (r == free_row and c == free_col)]
        random.shuffle(cells)
        
        self.bombs = set(cells[0:self.total_bombs])
        
        self.grid = [[0]*self.grid_size for i in range(self.grid_size)]
        
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                for neighb in self._neighbors(row, col):
                    if neighb in self.bombs:
                        self.grid[row][col] += 1
                        
    def open_cell(self, row, col): 
        if self.is_flagged(row, col):
            return False, []
            
        if not self.initialized:
            self._init_grid(row, col)
            self.initialized = True
        return self._is_bomb(row, col), self._bfs_0(row, col)
        
    def num_bombs(self, row, col):
        return self.grid[row][col]         
        
    
    def switch_flag(self, row, col):
        if not self._is_open(row, col):
            self.flagged[row][col] = not self.flagged[row][col]
            
            if self.flagged[row][col]:
                self.num_flags += 1
            else:
                self.num_flags -= 1
                
            return self.flagged[row][col]
        return None
    
    def _neighbors(self, row, col):
        neighbs = []
        for r in range(max(0, row-1), min(row+2, self.grid_size)):
            for c in range(max(0, col-1), min(col+2, self.grid_size)):
                neighbs.append((r, c))
        return neighbs
    
        
            
    def is_flagged(self, row, col):
        return self.flagged[row][col]
    def _open(self, row, col):
        self.opened[row][col] = True
    def _is_open(self, row, col):
        return self.opened[row][col]
    def _is_bomb(self, row, col) :
        return (row, col) in self.bombs
    
    def _bfs_0(self, row, col):
        queue = [(row, col)]
        cleared = []
        
        while len(queue) > 0:
            r, c = queue.pop(0)
            
            if not self._is_open(r, c):
                self._open(r, c)
                self.num_opened += 1
            
                cleared.append((r, c))            
                for neighb_r, neighb_c in self._neighbors(r, c): 
                    #not open, not marked, is zero or current iz zero
                    if ( not self._is_open(neighb_r, neighb_c) \
                        and not self.is_flagged(neighb_r, neighb_c) \
                        and ( self.num_bombs(r, c) == 0 \
                            or self.num_bombs(neighb_r, neighb_c) == 0)): 
                                queue.append((neighb_r, neighb_c))
        #print(cleared)
        return cleared
    
    @property
    def solved(self):
        #print(self.num_cells - self.num_opened, self.total_bombs)
        return (self.num_cells - self.num_opened) == self.total_bombs
    @property
    def bombs_left(self):
        return self.total_bombs - self.num_flags
                
class window:
    TITLE = "sapper"
    TITLE_WIN = "sapper :)"
    TITLE_LOOSE = "sapper :("
    
    REFRESH = 1000 #ms
    
    BTN_WIDTH = 1
    BTN_HEIGHT = 1
    
    BOMB_LBL =  u"\u2688"
    NO_FLAG_LBL = u' '
    FLAG_LBL = u"\u2691"
    
    BOMBS_LEFT_TXT = "Bombs left: {num_bombs}"
    TIMER_TXT = "Elapsed time: {time}"
    
    NUM_BOMB_TXT = {0:(u' ', "black"),
                    1:(u'1', "dark blue"),
                    2:(u'2', "dark green"),
                    3:(u'3', "dark violet"),
                    4:(u'4', "dark grey"),
                    5:(u'5', "dark salmon"),
                    6:(u'6', "dark goldenrod"),
                    7:(u'7', "dark orange"),
                    8:(u'8', "dark red"),
                    9:(u'9', "black")}
    def __init__(self, game, sound):
        self.root = tkinter.Tk()
        self.sound = sound
        
        self.game = game
        self.grid_size = self.game.grid_size    
        
        
        self._init_game_frame()
        self._init_info_frame() 
        
        self.user_actions_allowed = True
        
        self.set_title(window.TITLE)
    
    
    def _init_game_frame(self):
        #game_frame_side = window.BUTTON_SIZE*self.grid_size
        
        self.game_frame = tkinter.Frame(self.root)
         
        self._init_bomb_buttons(self.game_frame)                
        self.game_frame.pack()
        
    def _init_info_frame(self):
        self.info_frame = tkinter.Frame(self.root, width=780, relief=tkinter.SUNKEN)
        
        self.bombs_left = tkinter.Label(self.info_frame, text = "bombs")
        self.bombs_left.pack(side=tkinter.LEFT)
        
        
        #separator = tkinter.Frame(self.info_frame, relief=tkinter.SUNKEN)
        #separator.pack(fill = tkinter.X, padx=5)
        
        self.time = tkinter.Label(self.info_frame, text = window.TIMER_TXT.format(time=""))
        self.time.pack(side=tkinter.RIGHT)
        
        self.info_frame.pack(fill = tkinter.X) 
        
        self.left_bombs_upd()
    def _init_bomb_buttons(self, game_frame):
        self.buttons = [[None]*self.grid_size for i in range(self.grid_size)]
        self.buttons_dict = {}
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                button = tkinter.Button(game_frame,width = window.BTN_WIDTH,
                                        height = window.BTN_HEIGHT,
                                        text=window.NO_FLAG_LBL,
                                        command=self.on_btn_left_click)
                button.grid(row = row, column = col)
                button.bind("<Button-1>", self.on_btn_left_press)
                button.bind("<Button-3>", self.on_btn_right_press)
                self.buttons[row][col] = button
                self.buttons_dict[button] = (row, col)
    
            
    def on_btn_left_click(self):
        if self.user_actions_allowed:
            button = self.pressed_button
            
            row, col = self.buttons_dict[button]
            
            explode, to_open = self.game.open_cell(row, col)
            #print(to_open)
            if not explode:
                for (row, col) in to_open:
                    self.open_btn(row, col)
                print("win:", self.game.solved)  
                if self.game.solved:
                    self.win()
                
            else:
                self.loose()
          
    def on_btn_left_press(self, event):
        if self.user_actions_allowed:
            button = event.widget        
            button.config(relief=tkinter.SUNKEN)  
            self.pressed_button = button
            
            self.timer_start()
        
    def on_btn_right_press(self, event):
        if self.user_actions_allowed:
            button = event.widget
            row, col = self.buttons_dict[button]
            
            flagged = self.game.switch_flag(row, col)
            
            if flagged is not None:
                if flagged:
                    button.config(text = window.FLAG_LBL)
                else:            
                    button.config(text = window.NO_FLAG_LBL)
            self.left_bombs_upd()
            
            self.timer_start()
        
    
    def win(self):
        self.user_actions_allowed = False
        self.timer_stop()
        
        self.show_bombs(exploded = False)  
        self.set_title(window.TITLE_WIN)
        
        self.bombs_left.config(text = window.BOMBS_LEFT_TXT.format(num_bombs=0))
    def loose(self):
        self.user_actions_allowed = False
        self.timer_stop()
        
        # light is faster than sound   
        self.show_bombs(exploded = True)        
        self.sound.play(len(self.game.bombs))  
        self.set_title(window.TITLE_LOOSE)
            
    def open_btn(self, row, col):
        button = self.buttons[row][col]
        near_bombs = self.game.num_bombs(row, col)
        text, color = window.NUM_BOMB_TXT[near_bombs]
        button.config(relief=tkinter.SUNKEN, text = text, fg = color)
    
    def show_bombs(self, exploded=False):
        lbl =  window.BOMB_LBL if exploded else window.FLAG_LBL       
        for row, col in self.game.bombs:
            button = self.buttons[row][col]
            button.config(text = lbl)
            
    def left_bombs_upd(self) :       
        num_bombs = self.game.bombs_left
        self.bombs_left.config(text = window.BOMBS_LEFT_TXT.format(num_bombs=num_bombs))
    
    
    def timer_start(self):
        self.timer_enabled = True
        self.start_time = datetime.datetime.now()   
        self.time_refresher()
    def timer_stop(self):
        self.timer_enabled = False
    
    def time_refresher(self):               
        period = datetime.datetime.now() - self.start_time            
        self.time.config(text= window.TIMER_TXT.format(time=str(period)))
        
        if self.timer_enabled:
            self.root.after(window.REFRESH, self.time_refresher)
    def set_title(self, title):
        self.root.title(title)
    
    def show(self):
        self.root.mainloop()
    

if __name__ == "__main__":
    # execute only if run as a script
    
    params = {'size': DEFAULT_SIZE,
              'bombs':DEFAULT_BOMBS,
              'sound_enabled':DEFAULT_SOUND,
              'canonade':DEFAULT_CANONADE }

    for arg in argv:
        for p in params:
            if arg.startswith(p):
                try:
                    val = int(arg[len(p)+1:])
                    params[p] = val
                    print("set", p, "to", val)
                except:
                    pass
                
    s = sound(SOUND_FILE, params['sound_enabled'], params['canonade'])
    g = game(params['size'], params['bombs'])
    
    w = window(g, s)
    w.show()