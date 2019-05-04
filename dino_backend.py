__author__ = "Shivam Shekhar"
"""Imports all of the necessary packages"""
import os
import sys
import pygame
import random
from pygame import *
import pyautogui as pag
import numpy as np

pygame.init()
# Sets screen dimensions, colors, sounds, and images.
# Also initializes time/score.
scr_size = (width,height) = (600,150)
FPS = 60
gravity = 0.6

pag.PAUSE = 0

black = (0,0,0)
white = (255,255,255)
background_col = (235,235,235)

high_score = 0

screen = pygame.display.set_mode(scr_size)
clock = pygame.time.Clock()
pygame.display.set_caption("T-Rex Rush")

jump_sound = pygame.mixer.Sound('sprites/jump.wav')
die_sound = pygame.mixer.Sound('sprites/die.wav')
checkPoint_sound = pygame.mixer.Sound('sprites/checkPoint.wav')

# Next, it pulls the sprites to be able to construct the image
# we see on screen.

def load_image(
    name,
    sizex=-1,
    sizey=-1,
    colorkey=None,
    ):

    fullname = os.path.join('sprites', name)
    image = pygame.image.load(fullname)
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)

    if sizex != -1 or sizey != -1:
        image = pygame.transform.scale(image, (sizex, sizey))

    return (image, image.get_rect())

def load_sprite_sheet(
        sheetname,
        nx,
        ny,
        scalex = -1,
        scaley = -1,
        colorkey = None,
        ):
    fullname = os.path.join('sprites',sheetname)
    sheet = pygame.image.load(fullname)
    sheet = sheet.convert()

    sheet_rect = sheet.get_rect()

    sprites = []

    sizex = sheet_rect.width/nx
    sizey = sheet_rect.height/ny

    for i in range(0,ny):
        for j in range(0,nx):
            rect = pygame.Rect((j*sizex,i*sizey,sizex,sizey))
            image = pygame.Surface(rect.size)
            image = image.convert()
            image.blit(sheet,(0,0),rect)

            if colorkey is not None:
                if colorkey is -1:
                    colorkey = image.get_at((0,0))
                image.set_colorkey(colorkey,RLEACCEL)

            if scalex != -1 or scaley != -1:
                image = pygame.transform.scale(image,(scalex,scaley))

            sprites.append(image)

    sprite_rect = sprites[0].get_rect()

    return sprites,sprite_rect

# Game over screen
def disp_gameOver_msg(retbutton_image,gameover_image):
    retbutton_rect = retbutton_image.get_rect()
    retbutton_rect.centerx = width / 2
    retbutton_rect.top = height*0.52

    gameover_rect = gameover_image.get_rect()
    gameover_rect.centerx = width / 2
    gameover_rect.centery = height*0.35

    screen.blit(retbutton_image, retbutton_rect)
    screen.blit(gameover_image, gameover_rect)

# I think this is the loading screen
def extractDigits(number):
    if number > -1:
        digits = []
        i = 0
        while(number/10 != 0):
            digits.append(number%10)
            number = int(number/10)

        digits.append(number%10)
        for i in range(len(digits),5):
            digits.append(0)
        digits.reverse()
        return digits

# Our dino dude(ette). Initializes all of his stats such as life, score, movement,
# and jump speed. It also imports the images of the normal dino and the
# ducking dino.

class Dino():
    def __init__(self,sizex=-1,sizey=-1):
        self.images,self.rect = load_sprite_sheet('dino.png',5,1,sizex,sizey,-1)
        self.images1,self.rect1 = load_sprite_sheet('dino_ducking.png',2,1,59,sizey,-1)
        self.rect.bottom = int(0.98*height)
        self.rect.left = width/15
        self.image = self.images[0]
        self.index = 0
        self.counter = 0
        self.score = 0
        self.isJumping = False
        self.isDead = False
        self.isDucking = False
        self.isBlinking = False
        self.movement = [0,0]
        self.jumpSpeed = 11.5

        self.stand_pos_width = self.rect.width
        self.duck_pos_width = self.rect1.width
    
    def jump(self):
        if self.rect.bottom == int(0.98*height):
            self.isJumping = True
            if pygame.mixer.get_init() != None:
                jump_sound.play()
            self.movement[1] = -1*self.jumpSpeed
        

# Next it draws itself, checks its boundary, defines how to jump, and defines
# how to duck. Finally it checks if its dead. If it isn't, it increases the score.

    def draw(self):
        screen.blit(self.image,self.rect)

    def checkbounds(self):
        if self.rect.bottom > int(0.98*height):
            self.rect.bottom = int(0.98*height)
            self.isJumping = False

    def update(self):
        if self.isJumping:
            self.movement[1] = self.movement[1] + gravity

        if self.isJumping:
            self.index = 0
        elif self.isBlinking:
            if self.index == 0:
                if self.counter % 400 == 399:
                    self.index = (self.index + 1)%2
            else:
                if self.counter % 20 == 19:
                    self.index = (self.index + 1)%2

        elif self.isDucking:
            if self.counter % 5 == 0:
                self.index = (self.index + 1)%2
        else:
            if self.counter % 5 == 0:
                self.index = (self.index + 1)%2 + 2

        if self.isDead:
           self.index = 4

        if not self.isDucking:
            self.image = self.images[self.index]
            self.rect.width = self.stand_pos_width
        else:
            self.image = self.images1[(self.index)%2]
            self.rect.width = self.duck_pos_width

        self.rect = self.rect.move(self.movement)
        self.checkbounds()

        if not self.isDead and self.counter % 7 == 6 and self.isBlinking == False:
            self.score += 1
            if self.score % 100 == 0 and self.score != 0:
                if pygame.mixer.get_init() != None:
                    checkPoint_sound.play()

        self.counter = (self.counter + 1)

# This defines the cactus! It puts a cactus randomly between 0 and 3
class Cactus(pygame.sprite.Sprite):
    def __init__(self,speed=5,sizex=-1,sizey=-1):
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.images,self.rect = load_sprite_sheet('cacti-small.png',3,1,sizex,sizey,-1)
        self.rect.bottom = int(0.98*height)
        self.rect.left = width + self.rect.width
        self.image = self.images[random.randrange(0,3)]
        self.movement = [-1*speed,0]

    def draw(self):
        screen.blit(self.image,self.rect)

    def update(self):
        self.rect = self.rect.move(self.movement)
        self.dino_distance = self.rect.left - 84

        if self.rect.right < 0:
            self.kill()
            
# Yo, this defines the ground, image-wise and movement-wise.
class Ground():
    def __init__(self,speed=-5):
        self.image,self.rect = load_image('ground.png',-1,-1,-1)
        self.image1,self.rect1 = load_image('ground.png',-1,-1,-1)
        self.rect.bottom = height
        self.rect1.bottom = height
        self.rect1.left = self.rect.right
        self.speed = speed

    def draw(self):
        screen.blit(self.image,self.rect)
        screen.blit(self.image1,self.rect1)

    def update(self):
        self.rect.left += self.speed
        self.rect1.left += self.speed

        if self.rect.right < 0:
            self.rect.left = self.rect1.right

        if self.rect1.right < 0:
            self.rect1.left = self.rect.right

# Clouds just look pretty. They don't do anything.
class Cloud(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.image,self.rect = load_image('cloud.png',int(90*30/42),30,-1)
        self.speed = 1
        self.rect.left = x
        self.rect.top = y
        self.movement = [-1*self.speed,0]

    def draw(self):
        screen.blit(self.image,self.rect)

    def update(self):
        self.rect = self.rect.move(self.movement)
        if self.rect.right < 0:
            self.kill()

# This defines the scoring? I'm a bit confused on this part
class Scoreboard():
    def __init__(self,x=-1,y=-1):
        self.score = 0
        self.tempimages,self.temprect = load_sprite_sheet('numbers.png',12,1,11,int(11*6/5),-1)
        self.image = pygame.Surface((55,int(11*6/5)))
        self.rect = self.image.get_rect()
        if x == -1:
            self.rect.left = width*0.89
        else:
            self.rect.left = x
        if y == -1:
            self.rect.top = height*0.1
        else:
            self.rect.top = y

    def draw(self):
        screen.blit(self.image,self.rect)

    def update(self,score):
        score_digits = extractDigits(score)
        self.image.fill(background_col)
        for s in score_digits:
            self.image.blit(self.tempimages[s],self.temprect)
            self.temprect.left += self.temprect.width
        self.temprect.left = 0

"""This defines the intro screen. It has some backup messages if the game
won't load. Next, it defines the keys that make the dino jump and duck.
Finally, this part starts the game when you press jump!"""
def introscreen(game_start):
    temp_dino = Dino(44,47)
    temp_dino.isBlinking = True
    gameStart = game_start

    callout,callout_rect = load_image('call_out.png',196,45,-1)
    callout_rect.left = width*0.05
    callout_rect.top = height*0.4

    temp_ground,temp_ground_rect = load_sprite_sheet('ground.png',15,1,-1,-1,-1)
    temp_ground_rect.left = width/20
    temp_ground_rect.bottom = height

    logo,logo_rect = load_image('logo.png',240,40,-1)
    logo_rect.centerx = width*0.6
    logo_rect.centery = height*0.6
    while not gameStart:
        if pygame.display.get_surface() == None:
            print("Couldn't load display surface")
            return True
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        temp_dino.isJumping = True
                        temp_dino.isBlinking = False
                        temp_dino.movement[1] = -1*temp_dino.jumpSpeed

        temp_dino.update()

        if pygame.display.get_surface() != None:
            screen.fill(background_col)
            screen.blit(temp_ground[0],temp_ground_rect)
            if temp_dino.isBlinking:
                screen.blit(logo,logo_rect)
                screen.blit(callout,callout_rect)
            temp_dino.draw()

            pygame.display.update()

        clock.tick(FPS)
        if temp_dino.isJumping == False and temp_dino.isBlinking == False:
            gameStart = True
# Now we get to the meat of the game. It establishes the placement of the Dino,
# the movement of the ground, and all of the obstacles. Next it establishes the
# game screen.

playerDino = Dino(44,47)
gameOver = False
gameQuit = False
cacti = pygame.sprite.Group()
t = 0


def gameplay(agent):
    global high_score
    global playerDino
    global gameOver
    global gameQuit
    global t
    gamespeed = 4
    startMenu = False
    new_ground = Ground(-1*gamespeed)
    scb = Scoreboard()
    highsc = Scoreboard(width*0.78)
    counter = 0
    state = GameState
    cacti_jumped = 0
    is_falling = False
    survived = 0
    state_value = 0

    global cacti
    clouds = pygame.sprite.Group()
    last_obstacle = pygame.sprite.Group()

    Cactus.containers = cacti
    Cloud.containers = clouds

    retbutton_image,retbutton_rect = load_image('replay_button.png',35,31,-1)
    gameover_image,gameover_rect = load_image('game_over.png',190,11,-1)

    temp_images,temp_rect = load_sprite_sheet('numbers.png',12,1,11,int(11*6/5),-1)
    HI_image = pygame.Surface((22,int(11*6/5)))
    HI_rect = HI_image.get_rect()
    HI_image.fill(background_col)
    HI_image.blit(temp_images[10],temp_rect)
    temp_rect.left += temp_rect.width
    HI_image.blit(temp_images[11],temp_rect)
    HI_rect.top = height*0.1
    HI_rect.left = width*0.73

# Here, the code is for establishing jumping and ducking for the dino.
    while not gameQuit:
        while startMenu:
            pass
        while not gameOver:
            if pygame.display.get_surface() == None:
                print("Couldn't load display surface")
                gameQuit = True
                gameOver = True
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        gameQuit = True
                        gameOver = True

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            playerDino.jump()
                            
                        # if event.key == pygame.K_r:
                        #     gameplay(agent)
                        
                        if event.key == pygame.K_ESCAPE:
                            gameOver = True
                            gameQuit = True

# Now we establish the obstacles. If they hit one, the dino's state changes
# to dead. It populates the game with a random amount of cacti and pteras.
            temp = (epsilon/(1+(np.sqrt(t)/100)))
            if temp > epsilon_final:
                agent.take_action(epsilon, state, playerDino.isJumping, state_value, t)
            else: 
                agent.act_with_best_q(state_value)
            # agent.act_with_best_q(state_value)
            # print(temp)
            for c in cacti:
                c.movement[0] = -1*gamespeed
                # if c.dino_distance/gamespeed < 10 and c.dino_distance >0 and playerDino.isJumping != True:
                #     agent.press_jump()
                    
                    
                if pygame.sprite.collide_mask(playerDino,c):
                    playerDino.isDead = True
                    if pygame.mixer.get_init() != None:
                        die_sound.play()
                        
            num_cacti_0 = len(cacti)

            if len(cacti) < 2:
                if len(cacti) == 0:
                    last_obstacle.empty()
                    last_obstacle.add(Cactus(gamespeed,40,40))
                else:
                    for l in last_obstacle:
                        if l.rect.right < width*0.7 and random.randrange(0,50) == 10:
                            last_obstacle.empty()
                            last_obstacle.add(Cactus(gamespeed, 40, 40))
                            
            if len(clouds) < 5 and random.randrange(0,300) == 10:
                Cloud(width,random.randrange(height/5,height/2))
            
             
# After this, it updates all of the states and draws the next screen.
            prev_height = playerDino.rect.bottom
            playerDino.update()
            cur_height = playerDino.rect.bottom
            if prev_height < cur_height: isfalling = True
            else: isfalling = False
            cacti.update()
            # pteras.update()
            clouds.update()
            new_ground.update()
            # scb.update(playerDino.score)
            scb.update(int(1000*epsilon/(1+(t/100))))
            highsc.update(high_score)
            t+=1
            
            ### Cactus jumping
            
            ### Figure out if we have jumped over a cactus previously
            num_cacti_1 = len(cacti)
            # if num_cacti_0 - num_cacti_1 > 0:
            #     survived = True
            survived = num_cacti_0 - num_cacti_1
            cacti_jumped += survived
            
            

            if pygame.display.get_surface() != None:
                screen.fill(background_col)
                new_ground.draw()
                clouds.draw(screen)
                scb.draw()
                if high_score != 0:
                    highsc.draw()
                    screen.blit(HI_image,HI_rect)
                cacti.draw(screen)
                # pteras.draw(screen)
                playerDino.draw()

                pygame.display.update()
            clock.tick(FPS)
# Checks if you died.
            if playerDino.isDead:
                gameOver = True
                agent_scores.append(playerDino.score)
                if playerDino.score > high_score:
                    high_score = playerDino.score
# If you didn't, after a certain point, it increases speed
            if counter%700 == 699:
                new_ground.speed -= 1
                gamespeed += 1

            counter = (counter + 1)
            
            ### Get state for learning on next frame
            state.update(state, playerDino.rect.bottom, cacti, gamespeed, gameOver, isfalling)
            state_value = state.return_bool_state(state, playerDino.isJumping)
            ### IF gameOver then we need to store the current game's information?

        if gameQuit:
            break
# End credit stuff.
# Allows you to quit the game and get back to the start screen
        while gameOver:
            if pygame.display.get_surface() == None:
                print("Couldn't load display surface")
                gameQuit = True
                gameOver = False
            else:
                #here can use game state to update what we need
                #right now just auto restart for more practice
                state.restart()
                playerDino = Dino(44,47)
                gameOver = False
                gameQuit = False
                cacti = pygame.sprite.Group()
                gameplay(agent)
                
            highsc.update(high_score)
            if pygame.display.get_surface() != None:
                disp_gameOver_msg(retbutton_image,gameover_image)
                if high_score != 0:
                    highsc.draw()
                    screen.blit(HI_image,HI_rect)
                pygame.display.update()
            clock.tick(FPS)

    pygame.quit()
    quit()

reward = np.matrix([[1, -1],
                    [1, -1],
                    [-1, 1],
                    [1, -1]])
                    
Q = np.zeros(reward.shape)  

trained_Q = np.array([[ 0.10869565, -0.09130435],
       [ 0.10869565, -0.09130435],
       [-0.09130435,  0.10869565],
       [ 0.10869565, -0.09130435]])

epsilon = .05
epsilon_final = 1.032
alpha = .1
gamma = 0.8
agent_scores = []

class Game:
    def __init__(self):
        self.isGameQuit = None
   
    def main(agent, start):
        isGameQuit = introscreen(start)
        if not isGameQuit:
            gameplay(agent)
            

class GameState:
    def __init__(self, agent):
        self.agent = agent
        self.bottom = 147
        self.isfalling = False
        self.nearest = 600
        self.isdead = False
        
    def restart():
        #may want something more here to dump replay experience or q-table updates
        #can add a bool that says if we are training or not to initiate or not allow restarts
        pag.press("enter")
        
    def update(self, vertical, cacti, gamespeed, gameover, isfalling):
        self.isfalling = isfalling
        self.bottom = vertical
        self.isdead = gameover
        self.nearest = 600
        self.second_cactus = 1200
        for c in cacti:
            if c.dino_distance > 0 and int(c.dino_distance/gamespeed) < self.nearest:
                self.second_cactus = self.nearest
                self.nearest = int(c.dino_distance/gamespeed)
        # print(self.nearest)
        # print(self.s    qecond_cactus)        
                
    def return_bool_state (self, isjumping):
        tracking = 0
        if self.nearest < 17: tracking +=2
        if isjumping == True: tracking +=1
        return tracking
    
    def get_next_state(self, DinoCopy):
        DinoCopy.update()
        tracking = 0
        if self.nearest-1 < 17: tracking +=2
        if DinoCopy.isjumping == True: tracking +=1
        return tracking
          
    
    # def get_state(self, actions):
    #     agent.available actions
        
    # sits inside game updates on each frame, talks to agent to find what to do and
    # maybe can make a similarity case function

class Agent:
    def __init__(self, game):
        self.game = game
        self.actions = [0,1]
        self.action_idx = 0
        self.new_state_value = 0
        
        self.game.main(self, True)
        
        
    def press_jump(self):
        pag.press("space")
        
    def get_actions(self, state):
        if state.bottom == 147: return [0,1]
        else: return [0]
        
    def take_action(self, epsilon, state, isjumping, state_value, t):
        if random.random() <= (epsilon/(1+(np.sqrt(t)/100))):
            self.action_idx = np.random.choice(self.actions)
            if self.action_idx == 1: 
                self.press_jump()
                self.new_state_value = state.return_bool_state(state, isjumping)
            # else: self.new_state_value = state_value
        else:
            self.action_idx = np.where(Q[state_value,] == np.max(Q[state_value,]))[0][0]
            if self.action_idx > 1: 
                self.press_jump()
                self.new_state_value = state.return_bool_state(state, isjumping)
            # else: self.new_state_value = state_value
        
        
        Q[state_value, self.action_idx] += alpha * (reward[state_value, self.action_idx] 
                    + gamma*(np.max(Q[self.new_state_value,:])) 
                    + gamma*0)-Q[state_value, self.action_idx]
        
        
    def act_with_best_q(self, state_value):
        self.action_idx = np.where(trained_Q[state_value,] == np.max(trained_Q[state_value,]))[0][0]
        # self.action_idx = np.where(Q[state_value,] == np.max(Q[state_value,]))[0][0]
        if self.action_idx == 1: self.press_jump()
        
        
#height > cactus then reward if cactus is under
#reward is +num cacti jumped, +.1 for each frame, -100 for dying?

game = Game
agent = Agent(game)
print(agent_scores)  