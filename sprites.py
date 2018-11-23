# Sprite classes
import settings as stg
import pygame as pg
import random as rnd

vec = pg.math.Vector2

class Spritesheet:
    # utility class for loading and parsing spritesheets
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height,scale):
        # grab an image out of a larger spritesheet
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (width//scale, height//scale))
        return image

class Player(pg.sprite.Sprite):
    
    def __init__(self,game):
        self._layer = stg.PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self,self.groups)
        self.game = game # player is given reference to game class
        self.orientation = "R"
        self.invincible = False
        self.invincible_timer = 0
        self.walking = False
        self.jumping = False
        self.ducking = False
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.game.spritesheet_player.get_image(67, 196, 66, 92,2)
        self.image.set_colorkey(stg.BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (stg.WIDTH / 2, stg.HEIGHT / 1.2)
        self.pos = vec(stg.WIDTH / 2, stg.HEIGHT / 2)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
    
    def load_images(self):
        
        self.standing_frames_r = [self.game.spritesheet_player.get_image(73, 0, 72, 97,2),
                                  self.game.spritesheet_player.get_image(365, 0, 72, 97,2)]
        self.standing_frames_l = []
        for frame in self.standing_frames_r:
            frame.set_colorkey(stg.BLACK)
            self.standing_frames_l.append( pg.transform.flip(frame,True,False))
       
        self.walking_frames_r = [self.game.spritesheet_player.get_image(0, 0, 72, 97,2),
                                 self.game.spritesheet_player.get_image(73, 0, 72, 97,2),
                                 self.game.spritesheet_player.get_image(146, 0, 72, 97,2),
                                 #self.game.spritesheet_player.get_image(0, 98, 72, 97,1),
                                 self.game.spritesheet_player.get_image(73, 98, 72, 97,2),
                                 self.game.spritesheet_player.get_image(146, 98, 72, 97,2),
                                 self.game.spritesheet_player.get_image(219, 0, 72, 97,2),
                                 #self.game.spritesheet_player.get_image(292, 0, 72, 97,1),
                                 self.game.spritesheet_player.get_image(219, 98, 72, 97,2),
                                 self.game.spritesheet_player.get_image(365, 0, 72, 97,2),
                                 self.game.spritesheet_player.get_image(292, 0, 72, 97,2),
                                 self.game.spritesheet_player.get_image(292, 98, 72, 97,2)]
        self.walking_frames_l = []
        for frame in self.walking_frames_r:
            frame.convert()
            frame.set_colorkey(stg.BLACK)
            self.walking_frames_l.append(pg.transform.flip(frame,True,False)) #flips horizontally not vertically
            
        self.jumping_frame_r = self.game.spritesheet_player.get_image(438, 93, 67, 94,2).convert()
        self.jumping_frame_r.set_colorkey(stg.BLACK)
        self.jumping_frame_l = pg.transform.flip(self.jumping_frame_r,True,False)
            
        self.hurt_frame_r = self.game.spritesheet_player.get_image(438, 0, 69, 92,2).convert()
        self.hurt_frame_r.set_colorkey(stg.BLACK)
        self.hurt_frame_l = pg.transform.flip(self.hurt_frame_r,True,False)
            
        self.ducking_frame_r = self.game.spritesheet_player.get_image(365, 98, 69, 71,2).convert()
        self.ducking_frame_r.set_colorkey(stg.BLACK)
        self.ducking_frame_l = pg.transform.flip(self.ducking_frame_r,True,False)
        
        #for frame in self.standing_frames_r + self.standing_frames_l + self.walking_frames_l + self.walking_frames_r:
        #    pg.transform.scale(frame, (frame.get_width()//2 , frame.get_height()//2) )

    def jump(self):
        
        #jump only if standing on platform
        self.rect.y += 1
        hits = pg.sprite.spritecollide(self,self.game.platforms,False)
        self.rect.y -= 1
        if hits and not self.jumping:
            self.game.jump_sound.play()
            self.jumping = True
            #self.standing = False
            self.vel.y -= -stg.PLAYER_BASE_JUMP
            
    def jump_cut(self):
        if self.jumping:
            if self.vel.y < -6:
                self.vel.y = -6

    def update(self):
        
        self.animate()
        
        if pg.time.get_ticks() - self.invincible_timer < 1000:
            self.invincible = True
        else:
            self.invincible = False
        
        self.acc = vec(0, stg.PLAYER_GRAVITY)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.orientation = "L"
            if self.ducking == False:
                self.acc.x = -stg.PLAYER_ACC
        if keys[pg.K_RIGHT]:
            self.orientation = "R"
            if self.ducking == False:
                self.acc.x = stg.PLAYER_ACC
            

        # apply friction
        self.acc.x += self.vel.x * stg.PLAYER_FRICTION
        # equations of motion
        self.vel += self.acc
        if abs(self.vel.x) < stg.PLAYER_THRESHOLD_VELOCITYX:
            self.vel.x = 0
        self.pos += self.vel + 0.5 * self.acc
        # wrap around the sides of the screen
        if self.pos.x > stg.WIDTH + self.rect.width/2:
            self.pos.x = 0 - self.rect.width/2
        if self.pos.x < 0 - self.rect.width/2 :
            self.pos.x = stg.WIDTH + self.rect.width/2

        self.rect.midbottom = self.pos
        
        if stg.INVINCIBLE == "ON":
            self.invincible = True
    
    def animate(self):
        current_time = pg.time.get_ticks()
        
        if self.vel.x != 0 and self.vel.y == 0:
            self.walking = True
            
        if self.vel.y != 0 or self.vel.x == 0:
            self.walking = False
        
        if not self.walking and not self.jumping and not self.ducking:
            if current_time - self.last_update > 400:
                self.last_update = current_time
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames_r)
                bottom = self.rect.bottom
                if self.orientation == "R":
                    self.image = self.standing_frames_r[self.current_frame]
                elif self.orientation == "L":
                    self.image = self.standing_frames_l[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        elif self.walking:
            if current_time - self.last_update > 50:
                self.last_update = current_time
                self.current_frame = (self.current_frame + 1) % len(self.walking_frames_r)
                bottom = self.rect.bottom
                if self.orientation == "R":
                    self.image = self.walking_frames_r[self.current_frame]
                else:
                    self.image = self.walking_frames_l[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
                
        if self.jumping:
            if self.orientation == "R":
                self.image = self.jumping_frame_r             
            elif self.orientation == "L":
                self.image = self.jumping_frame_l
            self.rect = self.image.get_rect()
        
        elif self.ducking:
            if self.orientation == "R":
                self.image = self.ducking_frame_r             
            elif self.orientation == "L":
                self.image = self.ducking_frame_l
            self.rect = self.image.get_rect()
        
        self.mask = pg.mask.from_surface(self.image)

class Bubble(pg.sprite.Sprite):
    def __init__(self,game,plat):
        self._layer = stg.BUBBLE_LAYER
        self.groups = game.all_sprites, game.bubbles
        pg.sprite.Sprite.__init__(self,self.groups)
        self.game = game # platform is given reference to game class
        self.plat = plat
        self.empty = True
        self.image = self.game.spritesheet_jumper.get_image(0,1662,211,215,3).convert()
        self.image.set_colorkey(stg.BLACK) 
        self.image.set_alpha(100)
        self.rect = self.image.get_rect()
        
        self.rect.centerx = rnd.choice([-100,stg.WIDTH+100])
        self.vel = vec(2, 0)
        if self.rect.centerx > stg.WIDTH:
            self.vel.x *= -1
        self.acc = vec(0, 0.05)
        
    def update(self):
        if self.empty == True:
            self.vel.y += self.acc.y
            if self.vel.y > 3 or self.vel.y < -3:
                self.acc.y *= -1
                
            self.rect.y += self.vel.y
            self.rect.x += self.vel.x    
            if self.rect.left > stg.WIDTH+300 or self.rect.right < -300:
                self.kill()
            


        
class Platform(pg.sprite.Sprite):
    def __init__(self,game,x,y,sheet_pos):
        self._layer = stg.PLATFORM_LAYER
        self.groups = game.all_sprites, game.platforms
        pg.sprite.Sprite.__init__(self,self.groups)
        self.has_object = False
        self.type = sheet_pos
        self.game = game # platform is given reference to game class
        self.platform_images = [self.game.spritesheet_jumper.get_image(*sheet_pos,2),
                                pg.transform.flip(self.game.spritesheet_jumper.get_image(*sheet_pos,2),True,False)
                                ]
        for image in self.platform_images:
            image.convert()
        self.image = rnd.choice(self.platform_images)
        self.image.set_colorkey(stg.BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
"""
class Moving_Platform(pg.sprite.Sprite):
    def __init__(self,game,x,y,sheet_pos):
        self._layer = stg.PLATFORM_LAYER
        self.groups = game.all_sprites, game.platforms
        pg.sprite.Sprite.__init__(self,self.groups)
        self.has_object = False
        self.type = sheet_pos
        self.game = game # platform is given reference to game class
        self.image = rnd.choice([self.game.spritesheet_jumper.get_image(*sheet_pos,2),
                                pg.transform.flip(self.game.spritesheet_jumper.get_image(*sheet_pos,2),True,False)])
        self.image.set_colorkey(stg.BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
"""        
 
class Spring(pg.sprite.Sprite):
    def __init__(self,game,plat):
        self._layer = stg.SPRING_LAYER
        self.groups = game.all_sprites, game.springs
        pg.sprite.Sprite.__init__(self,self.groups)
        self.game = game # platform is given reference to game class
        self.plat = plat
        self.sprung = False
        self.frames = [ self.game.spritesheet_items.get_image(432,288,70,70,1),
                        self.game.spritesheet_items.get_image(432,216,70,70,1)]
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top
        
        
        
        for frame in self.frames:
            frame.convert()
            frame.set_colorkey(stg.BLACK)
                           
          
    def update(self):
        self.rect.bottom = self.plat.rect.top
        if not self.game.platforms.has(self.plat):
            self.kill()
            
        if self.sprung == False:
            self.image = self.frames[0]
        else:
            self.image = self.frames[1]
    
"""       
class Mob(pg.sprite.Sprite):
    def __init__(self,game,plat):
        self._layer = stg.MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.stompable = True
        self.game = game
        self.plat = plat
        self.orientation = "R"
        self.alive = True

        self.frames_l = [ self.game.spritesheet_enemies.get_image(71,235,70,47,1),
                          self.game.spritesheet_enemies.get_image(0,0,88,37,1),
                          self.game.spritesheet_enemies.get_image(571,406,38,43,1),#bat dead
                        ]    
        for frame in self.frames_l:
            frame.set_colorkey(stg.BLACK) 
        
        self.frames_r = []
        for frame in self.frames_l:
            frame.set_colorkey(stg.BLACK)
            self.frames_r.append(pg.transform.flip(frame,True,False)) #flips horizontally not vertically
        
        self.current_frame = 0
        self.last_update = 0
        self.image = self.frames_r[0]
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top
        
        self.vel = vec(5, 0)
        self.acc = vec(0, 0.5)
        
    def update(self):
        
        self.animate()
        if self.alive == True:
            self.vel.y += self.acc.y
            if abs(self.vel.y) < 3:
                self.acc.y *= -1
            if self.rect.x < 0 or self.rect.x > stg.WIDTH:
                self.vel.x *= - 1    
        else:
            self.vel.y += 0.8
            self.vel.x = 0

            
        self.rect.y += self.vel.y
        self.rect.x += self.vel.x
        
        if self.vel.x < 0:
            self.orientation = "L"
        else:
            self.orientation = "R"
        
    def animate(self):
        current_time = pg.time.get_ticks()
        if self.alive:
            if current_time - self.last_update > 200:
                self.last_update = current_time
                self.current_frame = (self.current_frame + 1) % 2
                center = self.rect.center
                if self.orientation == "R":
                    self.image = self.frames_r[self.current_frame]
                elif self.orientation == "L":
                    self.image = self.frames_l[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.center = center
        else:
            if self.orientation == "R":
                self.image = self.frames_r[2]
            elif self.orientation == "L":
                self.image = self.frames_l[2]
        self.mask = pg.mask.from_surface(self.image) 
"""        
class Mob(pg.sprite.Sprite):
    def __init__(self,game,plat,enemy_type):
        self._layer = stg.MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.type = enemy_type
        self.game = game
        self.plat = plat
        self.orientation = "R"
        self.stompable = True
        self.alive = True
        self.load_images()
        self.current_frame = 0
        self.last_update = 0
        self.image = self.frames_r[0]
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top
        
        if self.type == "bat":
            self.vel = vec(4, 0)
            self.acc = vec(0, 0.5)
            self.game.bat_sound.play()
            self.frame_rate = 100
        elif self.type == "spider":
            self.vel = vec(2, 0)
            self.acc = vec(0, 0.5)
            self.game.spider_sound.play()
            self.frame_rate = 100
        elif self.type == "bee":
            self.rect.centerx = rnd.choice([-100,stg.WIDTH+100])
            self.vel = vec(rnd.randrange(1,6), 0)
            if self.rect.centerx > stg.WIDTH:
                self.vel.x *= -1
            self.acc = vec(0, 0.2)
            self.game.bee_sound.play()
            self.frame_rate = 50
      
    def load_images(self):
        if self.type == "bat":
            self.frames_l = [ self.game.spritesheet_enemies.get_image(71,235,70,47,1),
                              self.game.spritesheet_enemies.get_image(0,0,88,37,1),
                              self.game.spritesheet_enemies.get_image(571,406,38,43,1),# dead
                            ]     
        elif self.type == "spider":
            self.frames_l = [ self.game.spritesheet_enemies.get_image(0,90,72,51,1),
                              self.game.spritesheet_enemies.get_image(0,37,77,53,1),
                              self.game.spritesheet_enemies.get_image(71,282,69,51,1),# dead
                            ]  
        elif self.type == "bee":
            self.frames_l = [ self.game.spritesheet_enemies.get_image(315,353,56,48,1),
                              self.game.spritesheet_enemies.get_image(140,23,61,42,1),
                              pg.transform.flip(self.game.spritesheet_enemies.get_image(315,305,56,48,1),False,True),# dead
                            ]      
        for frame in self.frames_l:
            frame.convert()
            frame.set_colorkey(stg.BLACK) 
        self.frames_r = []
        for frame in self.frames_l:
            self.frames_r.append(pg.transform.flip(frame,True,False)) #flips horizontally not vertically 
        
        
        
    def update(self):
        
        self.animate()
        if self.alive == True:
            if self.type == "bat":
                if self.rect.x < 0 or self.rect.x > stg.WIDTH:
                    self.vel.x *= - 1 
            elif self.type == "spider":
                if self.rect.left < self.plat.rect.left or self.rect.right > self.plat.rect.right:
                    self.vel.x *= - 1 
            elif self.type == "bee":
                self.vel.y += self.acc.y
                if self.vel.y > 3 or self.vel.y < -3:
                    self.acc.y *= -1
        else:
            self.vel.y += 0.8
            self.vel.x = 0

            
        self.rect.y += self.vel.y
        self.rect.x += self.vel.x
        
        if self.vel.x < 0:
            self.orientation = "L"
        else:
            self.orientation = "R"
        
        if self.rect.left > stg.WIDTH+100 or self.rect.right < -100:
            self.kill()
        
    def animate(self):
        current_time = pg.time.get_ticks()
        if self.alive:
            if current_time - self.last_update > self.frame_rate:
                self.last_update = current_time
                self.current_frame = (self.current_frame + 1) % (len(self.frames_r)-1)
                center = self.rect.center
                if self.orientation == "R":
                    self.image = self.frames_r[self.current_frame]
                elif self.orientation == "L":
                    self.image = self.frames_l[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.center = center
        else:
            if self.orientation == "R":
                self.image = self.frames_r[len(self.frames_r)-1]
            elif self.orientation == "L":
                self.image = self.frames_l[len(self.frames_r)-1]
        self.mask = pg.mask.from_surface(self.image)         
      
class Decoration(pg.sprite.Sprite):
    def __init__(self,game,plat,dec_type):
        self._layer = stg.DEC_LAYER
        self.groups = game.all_sprites, game.decorations
        pg.sprite.Sprite.__init__(self, self.groups)
        self.type = dec_type
        self.game = game
        self.plat = plat
        self.load_images()
        self.current_frame = 0
        self.last_update = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = rnd.randrange(self.plat.rect.x,self.plat.rect.right-self.rect.width)
        self.rect.bottom = self.plat.rect.top

      
    def load_images(self):
        if self.type == "grass":
            self.frames = [ self.game.spritesheet_items.get_image(0,363,70,70,1),#bat dead
                            ]      
        elif self.type == "mushroom1":
            self.frames = [ self.game.spritesheet_items.get_image(72,291,70,70,1),#bat dead
                            ]   
        elif self.type == "mushroom2":
            self.frames = [ self.game.spritesheet_items.get_image(72,219,70,70,1),#bat dead
                            ] 
        elif self.type == "cactus":
            self.frames = [ self.game.spritesheet_items.get_image(360,216,70,70,1),#bat dead
                            ] 
        for frame in self.frames:
            frame.convert()
            frame.set_colorkey(stg.BLACK) 

    def update(self):
        
        self.animate()
       
        self.rect.bottom = self.plat.rect.top
        if not self.game.platforms.has(self.plat):
            self.kill()

        
    def animate(self):
        current_time = pg.time.get_ticks()

        if current_time - self.last_update > 1000000:
            self.last_update = current_time
            self.current_frame = (self.current_frame + 1) % (len(self.frames))
            center = self.rect.center
            self.image = self.frames[self.current_frame]
            self.rect = self.image.get_rect()
            self.rect.center = center       
        
class Cloud(pg.sprite.Sprite):
    def __init__(self,game):
        self._layer = stg.CLOUD_LAYER
        self.groups = game.all_sprites, game.decorations
        self.type = "cloud"
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.load_images()
        self.rect.x = rnd.randrange(stg.WIDTH-self.rect.width)
        self.rect.y = rnd.randrange(-500,-50)
    

      
    def load_images(self):
        self.cloud_images = [ self.game.spritesheet_items.get_image(0,147,128,71,1),
                       self.game.spritesheet_items.get_image(0,73,129,71,1),
                       self.game.spritesheet_items.get_image(0,0,129,71,1)
                            ] 
        for image in self.cloud_images:
            image.convert()
            image.set_colorkey(stg.BLACK) 
        self.image = rnd.choice(self.cloud_images)
        self.rect = self.image.get_rect()
        scale = rnd.randrange(50,120)/100
        self.image = pg.transform.scale(self.image,(int(self.rect.width*scale),int(self.rect.height*scale)))
        self.rect = self.image.get_rect()

    def update(self):
        if self.rect.top > stg.HEIGHT*2:
            self.kill()
            
class Star(pg.sprite.Sprite):
    def __init__(self,game):
        self._layer = stg.STAR_LAYER
        self.groups = game.all_sprites, game.decorations
        self.type = "star"
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.load_images()
        self.rect.x = rnd.randrange(stg.WIDTH-self.rect.width)
        self.rect.y = rnd.randrange(-500,-50)
    
    def load_images(self):

        self.image = self.game.spritesheet_items.get_image(504,288,70,70,3).convert()
        self.image.set_colorkey(stg.BLACK) 
        self.rect = self.image.get_rect()

    def update(self):
        if self.rect.top > stg.HEIGHT*2:
            self.kill()

        

        
        
        
        
        