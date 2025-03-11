import pygame
import random
import time
import colors
from collections import deque

pygame.init()

h_display = 450
v_display = 601

screen = pygame.display.set_mode((h_display, v_display))

pygame.display.set_caption("Snake")
pygame.mixer.init()

clock = pygame.time.Clock()
# Font
font = pygame.font.Font(None, 25)  # Use default font

running = True

shape_colors = [
    (0, 255, 255),   # Cyan (I piece)
    (255, 165, 0),   # Orange (L piece)
    (255, 255, 0),   # Yellow (O piece)
    (0, 255, 0),     # Green (S piece)
    (255, 0, 0),     # Red (Z piece)
    (0, 0, 255),     # Blue (J piece)
    (128, 0, 128),   # Purple (T piece)
]

class Tetris:
    def __init__(self):
        self.shapes = [
            [9, 15, 21, 27],  # I
            [9, 15, 21, 22],  # L
            [15, 16, 21, 22], # O
            [15, 16, 20, 21], # S
            [14, 15, 21, 22], # Z
            [9, 15, 21, 20],  # J
            [14, 15, 16, 21], # T
        ]

        self.row = 20
        self.column = 10
        self.blockSize = 30

        self.board = [[0 for _ in range(self.column)] for _ in range(self.row)]

        self.blockPos = [(self.column // 2)-3, 0]
        shape_index = random.randrange(0, len(self.shapes))
        next_shape_index = random.randrange(0, len(self.shapes))

        self.currentShape = self.shapes[shape_index]
        self.nextShape = self.shapes[next_shape_index]
        self.currentShapeColor = shape_index
        self.nextShapeColor = next_shape_index

        self.delay = 500 # in ms
        self.start_time = time.time()
        self.started_playing = self.start_time
    
    def __addTheShapeIntoBoard(self):
        for i in range(4):
            pos = self.currentShape[i]

            y = (pos // 6) + self.blockPos[1]
            x = (pos % 6) + self.blockPos[0]

            self.board[y][x] = self.currentShapeColor+1
        
        self.__initiateNewBlock()
    
    def __initiateNewBlock(self):
        shape_index = random.randrange(0, len(self.shapes))

        self.currentShape = self.nextShape
        self.currentShapeColor = self.nextShapeColor
        
        self.nextShape = self.shapes[shape_index]
        self.nextShapeColor = shape_index

        self.blockPos = [(self.column // 2)-3, 0]

        if self.__checkShapeCollision():
            self.board = [[0 for _ in range(self.column)] for _ in range(self.row)]
        else:
            self.__checkForRowsFill()
    
    def __checkShapeCollision(self, x=0, y=0):
        for i in range(4):
            pos = self.currentShape[i]

            _y = (pos // 6) + self.blockPos[1] + y
            _x = (pos % 6) + self.blockPos[0] + x

            if _y >= self.row or _x >= self.column or _x < 0 or self.board[_y][_x] != 0: return True
        
        return False
    
    def __drawBoard(self):
        pygame.draw.line(screen, colors.white, (0, 0), (0, self.row*self.blockSize))
        pygame.draw.line(screen, colors.white, (self.column*self.blockSize, 0), (self.column*self.blockSize, self.row*self.blockSize))
        
        for i in range(self.row):
            for j in range(self.column):
                x = j * self.blockSize
                y = i * self.blockSize

                if self.board[i][j] != 0:
                    self.__drawBlock(x, y, shape_colors[self.board[i][j]-1])
        
        pygame.draw.line(screen, colors.white, (0, self.row*self.blockSize), (self.column*self.blockSize, self.row*self.blockSize))
    
    def __drawBlock(self, x, y, color_1=colors.green, color_2=colors.black):
        pygame.draw.rect(screen, color_1, pygame.Rect(x, y, self.blockSize, self.blockSize))
        pygame.draw.rect(screen, color_2, pygame.Rect(x, y, self.blockSize, self.blockSize), 1)
    
    def __drawGhost(self):
        ghost_y = 1
        while not self.__checkShapeCollision(y=ghost_y):
            ghost_y += 1
        ghost_y -= 1

        for i in range(4):
            pos = self.currentShape[i]

            y = pos // 6
            x = pos % 6

            self.__drawBlock((x+self.blockPos[0])*self.blockSize, (y+self.blockPos[1]+ghost_y)*self.blockSize, colors.black, colors.white)

    def __drawShape(self):
        for i in range(4):
            pos = self.currentShape[i]

            y = pos // 6
            x = pos % 6

            self.__drawBlock((x+self.blockPos[0])*self.blockSize, (y+self.blockPos[1])*self.blockSize, shape_colors[self.currentShapeColor])
    
    def rotate(self):
        rotatedShape = []
        for i in range(4):
            pos = self.currentShape[i]
            y = pos // 6
            x = pos % 6

            # y = 6-(y+1)
            x = 6-(x+1)

            # interchange x and y
            x, y = y, x
            rotatedShape.append(y*6 + x)

            y += self.blockPos[1]
            x += self.blockPos[0]

            if y < 0 or y >= self.row or x >= self.column or x < 0 or self.board[y][x] != 0: return False
        
        self.currentShape = rotatedShape
        self.start_time = time.time()
    
    def move(self, x=0):
        if not self.__checkShapeCollision(x):
            self.blockPos[0] += x
            self.start_time = time.time()
    
    def moveDown(self):
        y = 1
        while not self.__checkShapeCollision(y=y):
            y += 1
        
        self.blockPos[1] += y-1  
    
    def __checkForRowsFill(self):
        to_remove = []
        for i in range(self.row):
            _match = True
            for j in range(self.column):
                if self.board[i][j] == 0:
                    _match = False
                    break
            
            if _match: to_remove.append(i)
        
        if len(to_remove):
            for i in to_remove[::-1]:
                del self.board[i]
            
            self.board = [[0] * self.column for _ in range(len(to_remove))] + self.board
    
    def __addPadding(self, st):
        st = str(st)
        if len(st) == 1: return '0' + st
        return st
    
    def __secondsToReadableTime(self, seconds):
        minutes = seconds // 60
        seconds = seconds % 60

        return f'{self.__addPadding(minutes)}:{self.__addPadding(seconds)}'

    def __drawText(self, text, x, y, color=colors.white):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))

        screen.blit(text_surface, text_rect)

    def __drawNextBlock(self):
        self.__drawText('Next block', h_display-75, 190)

        for i in range(4):
            pos = self.nextShape[i]

            y = pos // 6
            x = pos % 6

            self.__drawBlock((x+9)*self.blockSize, (y+6)*self.blockSize, shape_colors[self.nextShapeColor])

    def render(self):
        self.__drawBoard()
        self.__drawGhost()
        self.__drawShape()

        left = h_display-75

        self.__drawText('Play time', left, 100)
        self.__drawText(self.__secondsToReadableTime(int(time.time() - self.started_playing)), left, 125)

        self.__drawNextBlock()
    
    def run(self):
        self.render()

        curr_time = time.time()

        if (curr_time - self.start_time) * 1000 >= self.delay:
            if self.__checkShapeCollision(y=1):
                self.__addTheShapeIntoBoard()
            else:
                self.blockPos[1] += 1
            
            self.start_time = time.time()

tetris = Tetris()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:  # Key pressed
            if event.key == pygame.K_UP:
                tetris.rotate()
            if event.key == pygame.K_DOWN:
                tetris.moveDown()
            if event.key == pygame.K_LEFT:
                tetris.move(-1)
            if event.key == pygame.K_RIGHT:
                tetris.move(1)
    
    screen.fill( colors.black )

    tetris.run()

    pygame.display.flip()
    clock.tick(60)