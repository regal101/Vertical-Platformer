import pygame as pg
import random as rnd
import settings as stg
from sprites import Player, Platform, Spritesheet, Spring, Mob, Decoration, Cloud, Star, Bubble
from os import path

class Game:
    def __init__(self):
        # initialize game window, etc
        pg.init()
        pg.mixer.pre_init(44100,-16,4,2048)
        pg.mixer.init()#
        
    
        #print(pg.mixer.get_init())
        self.screen = pg.display.set_mode((stg.WIDTH, stg.HEIGHT))
        pg.display.set_caption(stg.TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font(stg.FONT_NAME)
        self.load_date()
     
    def load_date(self):
        # load highscore
        self.dir = path.dirname(__file__)
        with open(path.join(self.dir,stg.HS_FILE), 'r') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0
        # load spritesheets
        img_dir = path.join(self.dir,'img')
        self.spritesheet_items = Spritesheet(path.join(img_dir,stg.SPRITESHEET_ITEMS))
        self.spritesheet_player = Spritesheet(path.join(img_dir,stg.SPRITESHEET_PLAYER))
        self.spritesheet_tiles = Spritesheet(path.join(img_dir,stg.SPRITESHEET_TILES))
        self.spritesheet_enemies = Spritesheet(path.join(img_dir,stg.SPRITESHEET_ENEMIES))
        self.spritesheet_jumper = Spritesheet(path.join(img_dir,stg.SPRITESHEET_JUMPER))
        # load sounds
        self.snd_dir = path.join(self.dir,'snd')
        self.jump_sound = pg.mixer.Sound(path.join(self.snd_dir,'jump_sound1.wav'))
        self.stomp_sound = pg.mixer.Sound(path.join(self.snd_dir,'smb_stomp.wav'))
        self.spring_sound = pg.mixer.Sound(path.join(self.snd_dir,'spring_sound.wav'))
        self.stomp_sound = pg.mixer.Sound(path.join(self.snd_dir,'smb_stomp.wav'))
        self.spring_sound = pg.mixer.Sound(path.join(self.snd_dir,'spring_sound.wav'))
        self.spider_sound = pg.mixer.Sound(path.join(self.snd_dir,'spider_sound.wav'))
        self.bat_sound = pg.mixer.Sound(path.join(self.snd_dir,'bat_sound.wav'))
        self.wind_sound = pg.mixer.Sound(path.join(self.snd_dir,'wind_sound.wav'))
        self.bee_sound = pg.mixer.Sound(path.join(self.snd_dir,'bee_sound.wav'))

    def new(self):
        # start a new game
        self.score = 10000
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.platforms = pg.sprite.LayeredUpdates()
        self.items = pg.sprite.LayeredUpdates()
        self.springs = pg.sprite.LayeredUpdates()
        self.mobs = pg.sprite.LayeredUpdates()  
        self.decorations = pg.sprite.LayeredUpdates()
        self.bubbles = pg.sprite.LayeredUpdates() 
        self.player = Player(self) # player is given reference to game class
        
        for plat in stg.PLATFORM_LIST:
            Platform(self,plat[0],plat[1],plat[2])
        if self.score > 7000:
            for i in range(20):
                s = Star(self)
                s.rect.x = rnd.randrange(0, stg.WIDTH)
                s.rect.y = rnd.randrange(0, stg.HEIGHT)
    
        pg.mixer.music.load(path.join(self.snd_dir,'music.mp3'))
        self.run()

    def run(self):
        # Game Loop
        self.playing = True
        pg.mixer.music.play(-1)
        while self.playing:
            self.clock.tick(stg.FPS)
            self.events()
            self.update()
            self.draw()
        pg.mixer.music.fadeout(1000)

    def update(self):
        # Game Loop - Update
        self.all_sprites.update()

        # check if player hits platform - only if falling
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player,self.platforms,False)
            if hits:
                # find the (one of the) lowest platforms being touched
                lowest_plat = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest_plat.rect.bottom:
                        lowest_plat = hit
                # creates list of equally low lowest platform
                lowest_plats = []
                for hit in hits:
                    if hit.rect.bottom == lowest_plat.rect.bottom:
                        lowest_plats.append(hit)   
                # stops player from falling through platform, takes into account edge effect
                for lowest_plat in lowest_plats:
                    if self.player.pos.x < lowest_plat.rect.right + self.player.rect.width/4 and \
                       self.player.pos.x > lowest_plat.rect.left - self.player.rect.width/4:
                        if self.player.pos.y < lowest_plat.rect.centery:
                            self.player.pos.y = lowest_plat.rect.top
                            self.player.vel.y = 0
                            self.player.jumping = False
         
        # collisions with mobs
        mob_hits = pg.sprite.spritecollide(self.player,self.mobs,False)
        for mob in mob_hits:
            if mob.alive == True:
                if self.player.invincible == False:
                    if mob.stompable == True:
                        if self.player.vel.y > 0 or mob.rect.top < self.player.rect.bottom < mob.rect.top + mob.rect.height/2:
                            self.stomp_sound.play()
                            mob.alive = False
                            self.player.jumping = False
                            self.player.vel.y = -10
                        else:
                            self.playing = False
                    else:
                        self.playing = False
                else:
                    self.stomp_sound.play()
                    mob.alive = False
                   
        #if player 1/4 from top of screen move shift everything
        if self.player.rect.top <= stg.HEIGHT/4:
            if self.score < 7000 and rnd.randrange(30+int(self.score/40)) < 1:
                Cloud(self)
            if self.score > 5000 and rnd.randrange(max(250-int((self.score/100)),150)) < 1:
                Star(self)
            self.shift_screen()
    
        # checks if a spring collision occurs
        spring_collisions = pg.sprite.spritecollide(self.player,self.springs,False, False)
        for sprg in spring_collisions:
            if sprg.rect.centery < self.player.rect.bottom < sprg.rect.centery + sprg.rect.height/2:
                if self.player.vel.y > 0:
                    if sprg.sprung == False:
                        self.spring_sound.play()
                        sprg.sprung = True
                        self.player.jumping = False
                        self.player.rect.bottom = sprg.rect.top
                        self.player.vel.y = stg.SPRING_POWER
                        # make player invincible while spring jumping
                        self.player.invincible_timer = pg.time.get_ticks()
            

        # fall to death
        if self.player.rect.bottom > stg.HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y,10)
                if sprite.rect.bottom < 0:
                    sprite.kill()
        if len(self.decorations) == 0 and len(self.platforms) == 0:
            self.playing = False
        
        # spwn new platforms
        while(len(self.platforms) < 8 and self.player.rect.top < stg.HEIGHT):
            plat_length = rnd.choice([1,1,1,1,2])
            xpos = rnd.randrange(0,stg.WIDTH-70*plat_length)
            ypos = rnd.randrange(-40,-30)
            if plat_length == 1:
                p = Platform(self,xpos,ypos,stg.GRASS_SHORT)
            elif plat_length == 2:
                p = Platform(self,xpos,ypos,stg.GRASS_LONG)
            p.kill()
            collisions = pg.sprite.spritecollide(p,self.platforms,False,False)
            while len(collisions) != 0:
                p.rect.x = rnd.randrange(0,stg.WIDTH-70*plat_length)
                p.rect.y = rnd.randrange(-50,-35)
                collisions = pg.sprite.spritecollide(p,self.platforms,False,False)
            self.all_sprites.add(p)
            self.platforms.add(p)
            
            # spawns spring
            if rnd.random() < stg.SPRING_SPWN_RATE:
                Spring(self,p)
            # spawns mob
            if p.type == stg.GRASS_LONG:
                if rnd.random() < min(1,stg.LONG_PLAT_MOB_SPAWN_RATE*stg.DIFFICULTY + stg.LONG_PLAT_MOB_SPAWN_RATE*self.score/10000):
                    Mob(self,p,rnd.choice(stg.ENEMY_LIST))
            else:
                if rnd.random() < min(1,stg.SHORT_PLAT_MOB_SPAWN_RATE*stg.DIFFICULTY + stg.SHORT_PLAT_MOB_SPAWN_RATE*self.score/10000):
                    Mob(self,p,rnd.choice(["bat","bee"]))
            # spawns decoration
            if rnd.random() < stg.DEC_SPAWN_RATE:
                Decoration(self,p,rnd.choice(stg.DECORATION_LIST))
            # spawns decoration
            if rnd.random() < 0.02:
                self.wind_sound.play()
            # spawns bubble
            if rnd.random() < 1:
                pass
                #Bubble(self,p)
                #self.wind_sound.play()


    def events(self):
        # Game Loop - events
        for event in pg.event.get():
            # check for closing window
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.player.jump()
                elif event.key == pg.K_DOWN:
                    self.player.ducking = True
                    
            if event.type == pg.KEYUP:
                if event.key == pg.K_UP:
                    self.player.jump_cut() 
                if event.key == pg.K_DOWN:
                    self.player.ducking = False

    def draw(self):
        # Game Loop - draw
        colour = max(int(155-(self.score/10000)*155),0)
        self.screen.fill((0,colour,colour))
        self.all_sprites.draw(self.screen)
        
        #self.screen.blit(self.player.image,self.player.rect )
        self.draw_text(self.screen,str(self.score),22, stg.WHITE, stg.WIDTH/2,15)
        # *after* drawing everything, flip the display
        pg.display.flip()

    def show_start_screen(self):
        # game splash/start screen
        #pg.mixer.music.load(path.join(self.snd_dir,''))
        #pg.mixer.music.play(-1)
        self.screen.fill(stg.LIGHT_BLUE)
        self.draw_text(self.screen,stg.TITLE, 22,stg.WHITE, stg.WIDTH/2,stg.HEIGHT/4)
        self.draw_text(self.screen,"Move (left/right arrows) jump (up arrow)",18,stg.WHITE, stg.WIDTH/2,stg.HEIGHT/2)
        self.draw_text(self.screen,"Press any key to play",18,stg.WHITE, stg.WIDTH/2,stg.HEIGHT* 3/4)
        self.draw_text(self.screen,"High Score: " + str(self.highscore), 22, stg.WHITE, stg.WIDTH/2, 15)
        pg.display.flip()
        self.wait_for_key()

    def show_go_screen(self):
        # game over/continue
        #escapes game over screen if game running is set to false
        #pg.mixer.music.load(path.join(self.snd_dir,''))
        #pg.mixer.music.play(-1)
        if not self.running:
            return
        self.screen.fill(stg.LIGHT_BLUE)
        self.draw_text(self.screen,"GAME OVER", 22,stg.WHITE, stg.WIDTH/2,stg.HEIGHT/4)
        self.draw_text(self.screen,"Score: " + str(self.score),18,stg.WHITE, stg.WIDTH/2,stg.HEIGHT/2)
        self.draw_text(self.screen,"Press any key to play",18,stg.WHITE, stg.WIDTH/2,stg.HEIGHT* 3/4)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text(self.screen,"NEW HIGH SCORE!",22, stg.WHITE,stg.WIDTH/2,stg.HEIGHT/2 + 40)
            with open(path.join(self.dir,stg.HS_FILE), 'w') as f:
                f.write(str(self.score))
        else:
            self.draw_text(self.screen,"High Score: " + str(self.highscore), 22, stg.WHITE, stg.WIDTH/2, stg.HEIGHT/2 + 40)
        pg.display.flip()
        self.wait_for_key()
    
    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(stg.FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP:
                    waiting = False
                    
    def shift_screen(self):
        self.player.pos.y += abs(self.player.vel.y)
        for plat in self.platforms:
             plat.rect.y += abs(self.player.vel.y)
             #kill platforms if they go off screen
             if plat.rect.top >= stg.HEIGHT+100:
                 plat.kill()
                 self.score += 10
        for mob in self.mobs:
            mob.rect.y += abs(self.player.vel.y)
            #kill platforms if they go off screen
            if mob.rect.top >= stg.HEIGHT+100:
                mob.kill()
        for dec in self.decorations:
            if dec.type == "cloud" or dec.type == "star":
                dec.rect.y += abs(self.player.vel.y)/(4*100/dec.rect.width)
            else:
                dec.rect.y += abs(self.player.vel.y)
        for spring in self.springs:
            spring.rect.y += abs(self.player.vel.y)
        for bubble in self.bubbles:
            bubble.rect.y += abs(self.player.vel.y)
            #kill platforms if they go off screen
            if bubble.rect.top >= stg.HEIGHT+100:
                bubble.kill()
    
    def draw_text(self,surf,text,size, color,x,y):
        font = pg.font.Font(self.font_name,size) #sets font
        text_surface = font.render(text,True,color) # creates surface to render text pixels onto
        text_rect = text_surface.get_rect() #  get the rectangle of the surface
        text_rect.midtop = (x,y) # rectangles middle top is the coordinates passed in
        surf.blit(text_surface,text_rect) # blit surface onto screen at the locations of the rectangle

g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pg.quit()