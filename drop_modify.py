import sys
import pygame
from random import randint as rand
import sqlite3

conn = sqlite3.connect('dropDB.sqlite')
cur = conn.cursor()
if  cur.execute('SELECT id FROM User') == None:
    cur.execute('INSERT OR IGNORE INTO User (character_id, stars, best_score) VALUES (1,0,0)')
    print('he')


character_id = cur.execute('SELECT character_id FROM User').fetchone()[0]
character = cur.execute('SELECT name, image, cost FROM Character WHERE id= ?', (character_id,)).fetchone()
character_name = character[0]
character_image = character[1]
character_cost = character[2]

user_stars = cur.execute('SELECT stars FROM User').fetchone()[0]
user_best_score = cur.execute('SELECT best_score FROM User').fetchone()[0]

pygame.init()
#game branding
pygame.display.set_caption("Pix Drop")
icon = pygame.transform.scale(pygame.image.load("pix.png"), (32, 32))
pygame.display.set_icon(icon)
font = pygame.font.Font('Jesus_Heals.ttf',60)
bord = pygame.font.Font('Jesus_Lives.ttf', 60)
star_font = pygame.font.Font('Jesus_Heals.ttf', 28)
best_score_font = pygame.font.Font('Jesus_Heals.ttf', 32)
#frame settings
size = (450, 750)
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
fps = 60
cloud_x = 400
cloud_dx = -1
camera_y = 0

#images
back_img = pygame.image.load("angryimg.png")
cloud_img = pygame.image.load("cloud.png")
opp = pygame.image.load("download.png")
cont = pygame.image.load("cont.png")
cont_btn_img = pygame.image.load("btn100.png")
not_cont_img = pygame.image.load("btn_cancel_1.png")
restart_btn_img = pygame.image.load("restart_btn.png")
best_score_img = pygame.image.load("best_score.png")
star = pygame.image.load("star32.png")
leaf = pygame.image.load("leaf32.png")
mushroom = pygame.image.load("mushroom32.png")
carrot = pygame.image.load("carrot32.png")
trick = {"star":star, "leaf":leaf, "mushroom":mushroom, "carrot":carrot}
home = pygame.image.load("home.png")
platform_images = ["platform_long.png", "platform_short.png"]
enemy_images = ["kill_long.png", "kill_short.png"]
py_platform = [(pygame.image.load(i), i) for i in platform_images]
py_enemy = [(pygame.image.load(i), i) for i in enemy_images]
# dead_pix = pygame.image.load("pix_kill100.png")
# dead_pix = pygame.transform.scale(dead_pix, (32,32))

#platfroms
itn = (0, 200)
dst = 120
data = [
    [itn[0], itn[1],  py_platform[rand(0, len(py_platform)-1)]], 
    [rand(0,itn[1]), itn[1]+dst, py_platform[rand(0, len(py_platform)-1)]], 
    [rand(0,itn[1]), itn[1]+dst*2, py_enemy[rand(0, len(py_enemy)-1)]], 
    [rand(0,itn[1]), itn[1]+dst*3, py_enemy[rand(0, len(py_enemy)-1)]],
    [rand(0,itn[1]), itn[1]+dst*4, py_enemy[rand(0, len(py_enemy)-1)]]
]

#cloud 
cloud_x = 400
cloud_dx = -1

class Pix:
    dy = 7
    dif = 0
    def __init__(self, x, y, image):
        self.image = image
        self.height = image.get_height()
        self.width = image.get_width()
        self.x = x
        self.y = y

    def draw(self, size=None):
        if size == None:
            screen.blit(self.image, (self.x, self.y))
        else:
            screen.blit(pygame.transform.scale(self.image, size), (self.x, self.y))

    def fall(self):
        Pix.dy = 7
        self.y += Pix.dy

    def collide(self, smth):
        if smth.special:
            if smth.x >= size[0]+smth.width or smth.x<=-smth.width:
                self.x = smth.x + Pix.dif
        if self.y+self.height+20 >= smth.y and (smth.x<self.x+self.width//2 and self.x+self.width//2<smth.x+smth.width):
            smth.opacity = 0
            Pix.dif = self.x - smth.x
            Pix.dy = 0
            self.y = smth.y - self.height
            self.x += smth.dx
            return True
        return False


class Platform:
    cnt=0
    sz=0
    def __init__(self, x, y, image, picname, dx=3, special=False, opacity=0, alpha=2, trick=None, trick_name=None, move_sharply=False):
        self.image = image
        self.picname = picname
        self.x = x
        self.y = y
        self.height = image.get_height()
        self.width = image.get_width()
        self.dx = dx
        self.special = special
        self.opacity = opacity
        self.alpha = alpha
        self.trick = trick
        self.trick_name = trick_name
        self.move_sharply = move_sharply

    def move(self):
        if self.special:
            self.x += self.dx
            if self.x > size[0]+self.width:
                self.x = - self.width
        else:
            self.x += self.dx
            if self.x <= 0:
                self.dx *= -1
            elif self.x>= size[0]-self.width+2:
                self.dx *= -1

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def draw_alpha(self):
        s = pygame.Surface((self.width, self.height)).convert()
        self.opacity += self.alpha
        if self.opacity>=254 or self.opacity<=4:
            self.alpha *= -1 
        s.blit(screen, (-self.x, -self.y))
        s.blit(self.image, (0, 0))
        s.set_alpha(self.opacity)
        screen.blit(s, (self.x, self.y))

    def draw_smth(self, smth):
        if smth!=None:
            if self.opacity==0:
                if Platform.sz<smth.get_width():
                    screen.blit(pygame.transform.scale(smth, (Platform.sz,Platform.sz)), (self.x+(self.width//2)-Platform.sz//2, self.y-Platform.sz-10))
                else:
                    screen.blit(smth, (self.x+(self.width//2)-smth.get_width()//2, self.y-smth.get_height()-10))
            else:
                if Platform.sz<smth.get_width():
                    s = pygame.Surface((Platform.sz, Platform.sz)).convert()
                    s.blit(screen, (-(self.x+(self.width//2)-Platform.sz//2), -(self.y-Platform.sz-10)))
                    s.blit(pygame.transform.scale(smth, (Platform.sz,Platform.sz)), (0, 0))
                    s.set_alpha(self.opacity)
                    screen.blit(s, (self.x+(self.width//2)-Platform.sz//2, self.y-Platform.sz-10))
                else:
                    s = pygame.Surface((smth.get_width(), smth.get_height())).convert()
                    s.blit(screen, (-(self.x+(self.width//2)-smth.get_width()//2), -(self.y-smth.get_height()-10)))
                    s.blit(smth, (0, 0))
                    s.set_alpha(self.opacity)
                    screen.blit(s, (self.x+(self.width//2)-smth.get_width()//2, self.y-smth.get_height()-10))
                    
            if Platform.cnt>15 and Platform.cnt<=30:
                Platform.sz-=2
            else:
                Platform.sz+=2
            Platform.cnt+=1
            

class Enemy(Platform):
    def __init__(self, x, y, image, picname, dx=3, special=False, opacity=0, alpha=2, move_sharply=False):
        super().__init__(x, y, image, picname, dx, special, opacity, alpha, None, None, move_sharply)

def background(user_stars):
    global cloud_x
    screen.blit(back_img, (0,0))
    if cloud_x + opp.get_width() + 400 < 0:
        cloud_x = 600
    cloud_x += -2
    screen.blit(opp, (cloud_x+200, 100))
    screen.blit(opp, (cloud_x+50, 50))
    screen.blit(opp, (cloud_x, 150))
    screen.blit(opp, (cloud_x-150, 300))
    screen.blit(pygame.transform.scale(star,(28,28)), (10,10))
    screen.blit(star_font.render(f"{user_stars}", False, (255,132,37)), (40, 8))

def menu(): 
    pix_Img = pygame.image.load(character_image)
    # pix_Img = pygame.transform.scale(pix_Img, (50,50))
    start_btn = pygame.image.load("play_btn.png")
    x = 0
    dx = 1
    running = True
    click = False 
    while running:
        background(user_stars)
        mx, my = pygame.mouse.get_pos()
        btn = pygame.Rect(size[0]//2-start_btn.get_width()//2 + x, 
                            size[1] //3 + pix_Img.get_height(), 
                            start_btn.get_width(), 
                            start_btn.get_height()
                            )
        click = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                cur.close()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
        
        if btn.collidepoint((mx, my)):
            if click:
                platforms = [Platform(data[i][0], data[i][1], data[i][2][0], data[i][2][1]) for i in range(2)]
                enemys = [Enemy(data[i][0], data[i][1], data[i][2][0], data[i][2][1]) for i in range(2,5)]
                game(pix_Img, 0, platforms, enemys)
                running = False
        x += dx
        if x <= -25 or x >= 25:
            dx *= -1
            
        screen.blit(best_score_img, (size[0]//2-best_score_img.get_width()//2 + x , size[1]//3 - best_score_img.get_height() - 5 ))
        best_score = best_score_font.render(f"{user_best_score}", False, (255,140,16))
        screen.blit(best_score, 
        (size[0]//2- best_score.get_width()//2 + x , size[1]//3 - best_score_img.get_height()))
        screen.blit(pix_Img, (size[0]//2-pix_Img.get_width()//2 + x , size[1]//3))
        screen.blit(start_btn, (size[0]//2-start_btn.get_width()//2 + x, size[1]//3 + pix_Img.get_height()))
        pygame.display.flip()
        clock.tick(fps)

def game(pix_Img, user_score, platforms, enemys):
    global user_best_score, user_stars
    pix_X = 100
    pix_Y = 0
    my_pix = Pix(pix_X, pix_Y, pix_Img)
    platforms[-1].trick = trick["star"]
    platforms[-1].trick_name = "star"
    running = True
    fall = False
    camera_fall = False
    bomb = False
    c = 0
    bar_size = (100, 8)
    bar_rect = pygame.Rect(size[0]//2-bar_size[0]//2, 110, bar_size[0], bar_size[1])
    max_width = bar_size[0]-2
    min_time = 0  
    time = 10
    trick_time = 10
    coefficient = max_width / time
    dt = 0
    start = False
    while running:
        background(user_stars)
        col = my_pix.collide(platforms[0])
        if col==False:
            my_pix.draw((my_pix.width, my_pix.height+20))
            my_pix.fall()
        elif col==True and fall==True:
            if platforms[0].trick_name == "star":
                user_stars += 1
            elif platforms[0].trick_name == "leaf":
                pass
            elif platforms[0].trick_name == "mashroom":
                pass
            elif platforms[0].trick_name == "carrot":
                pass
            user_score += 1
            Platform.cnt = 0
            Platform.sz = 0
            fall = False
            update_platform(platforms, enemys)
            my_pix.draw()
            time = 10
            start = True
        else:
            my_pix.draw()
            if start == True:
                if time > min_time:
                    time -= dt

        for i in range(len(platforms)):
            platforms[i].move()
            if platforms[i].opacity == 0:
                platforms[i].draw()
            else:
                platforms[i].draw_alpha()
        platforms[-1].draw_smth(platforms[-1].trick)
        for i in range(len(enemys)):
            enemys[i].move()
            if enemys[i].opacity == 0:
                enemys[i].draw()
            else:
                enemys[i].draw_alpha()

        if my_pix.y > platforms[0].y + platforms[0].height and col == False:
            # if my_pix.collide(enemys[0]) or my_pix.collide(enemys[1]) or my_pix.collide(enemys[2]):
            #     my_pix.image = dead_pix
            if user_score>user_best_score:
                user_best_score = user_score
                cur.execute('UPDATE User SET best_score = (?)', (user_best_score,))
            cur.execute('UPDATE User SET stars = (?)', (user_stars,))
            conn.commit()
            if user_stars>=100:
                continue_game(pix_Img, user_score, platforms, enemys)
            else:
                restart(pix_Img, user_score)
            running = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                cur.close()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu()
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    fall = True
                    del platforms[0]
                    my_pix.fall()
                    camera_fall = True
                    c = c - 40
                if event.button == 3 and user_stars>=10:
                    user_stars -= 10
                    del platforms[-1]
                    update_platform(platforms, enemys)
                    camera_fall = True
                    bomb = True
                    c = c - 40
                    time = 10

        if time<=0 and fall==False:
            fall = True
            del platforms[0]
            my_pix.fall()
            camera_fall = True
            c = c - 40

        if camera_fall:
            dy = 3
            my_pix.y-= dy
            if bomb:
                platforms[-1].y-=dy
            else:
                for i in range(len(platforms)):
                    platforms[i].y-=dy
            for i in range(len(enemys)):
                enemys[i].y-=dy
            c+=1
            if c==0:
                camera_fall=False
                bomb = False
        
        score_txt = font.render(f"{user_score}", False, (255,255,255))
        score_txt_b = bord.render(f"{user_score}", False, (47,109,246))
        screen.blit(score_txt, (size[0]//2-score_txt.get_width()//2, 30))
        screen.blit(score_txt_b, (size[0]//2-score_txt_b.get_width()//2, 30))
        width = time * coefficient
        pygame.draw.rect(screen, (118,200,250), (size[0]//2-bar_size[0]//2 - 3, 110 - 3, bar_size[0]+6, bar_size[1]+6))
        pygame.draw.rect(screen, (212,246,254), (size[0]//2-bar_size[0]//2 - 2, 110 - 2, bar_size[0]+4, bar_size[1]+4))
        pygame.draw.rect(screen, (47,109,246), bar_rect)
        pygame.draw.rect(screen, (249,229,106), (size[0]//2-bar_size[0]//2 + 1, 110 + 1, width, bar_size[1]-2))
    
        pygame.display.flip()
        dt = clock.tick(fps)/500

def update_platform(platforms, enemys):
    spec_case = rand(0,15)
    if 'long' in enemys[0].picname:
        image = py_platform[0]
    elif 'short' in enemys[0].picname:
        image = py_platform[1]
    if spec_case == 1:
        choose = "leaf"
    elif spec_case == 2:
        choose = "mushroom"
    elif spec_case == 3:
        choose = "carrot"
    else:
        choose = "star"
    platforms.append(Platform(enemys[0].x, enemys[0].y, image[0], image[1], enemys[0].dx, enemys[0].special, enemys[0].opacity, 2, trick[choose], choose))
    platforms[-1].dx = enemys[0].dx
    del enemys[0]
    new = data[rand(2,4)]
    if spec_case == 10:
        enemys.append(Enemy(new[0], enemys[-1].y+120, new[2][0], new[2][1], 10))
    elif spec_case == 5:
        enemys.append(Enemy(new[0], enemys[-1].y+120, new[2][0], new[2][1], 3, True))
    elif spec_case == 4:
        enemys.append(Enemy(new[0], enemys[-1].y+120, new[2][0], new[2][1], 3, False, 20))
    elif spec_case == 6:
        enemys.append(Enemy(new[0], enemys[-1].y+120, new[2][0], new[2][1], 3, False, 0, 2, True))
    else:
        enemys.append(Enemy(new[0], enemys[-1].y+120, new[2][0], new[2][1]))

def restart(pix, score):
    global user_best_score, user_stars
    running = True
    while running:
        background(user_stars)
        mx, my = pygame.mouse.get_pos()
        restart_btn = pygame.Rect(size[0]//2-restart_btn_img.get_width()//2, size[1]//2-restart_btn_img.get_height()//2, 
                            restart_btn_img.get_width(), 
                            restart_btn_img.get_height())
        home_btn = pygame.Rect(size[0]-home.get_width()-10, 10, home.get_width(), home.get_height())
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                cur.close()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
        if restart_btn.collidepoint((mx, my)):
            if click:
                platforms = [Platform(data[i][0], data[i][1], data[i][2][0], data[i][2][1]) for i in range(2)]
                enemys = [Enemy(data[i][0], data[i][1], data[i][2][0], data[i][2][1]) for i in range(2,5)]
                game(pix, 0, platforms, enemys)
                running = False
        if home_btn.collidepoint((mx, my)):
            if click:
                menu()
                running = False
        score_f = star_font.render(f"score", False, (47,109,246))
        user_score = font.render(f"{score}", False, (47,109,246))
        best_score = star_font.render(f"best: {user_best_score}", False, (255,140,16))
        screen.blit(score_f, (size[0]//2 - score_f.get_width()//2, size[1]//2 - 225))
        screen.blit(user_score, (size[0]//2 - user_score.get_width()//2, size[1]//2 - 200))
        screen.blit(best_score, (size[0]//2 - best_score.get_width()//2, size[1]//2 - 125))
        screen.blit(restart_btn_img,  (size[0]//2-restart_btn_img.get_width()//2, size[1]//2-restart_btn_img.get_height()//2))
        screen.blit(home, (size[0]-home.get_width()-10, 10))
        pygame.display.flip()
        clock.tick(fps)

def continue_game(pix, score, platforms, enemys):
    global user_best_score, user_stars
    running = True
    while running:
        background(user_stars)
        mx, my = pygame.mouse.get_pos()
        cont_btn = pygame.Rect(size[0]//2-cont_btn_img.get_width()//2, size[1]//2-cont.get_height()//2 + 150, 
                            cont_btn_img.get_width(), 
                            cont_btn_img.get_height())
        not_cont_btn = pygame.Rect(size[0]//2-not_cont_img.get_width()//2, size[1]//2+cont.get_height()//2 - 40, 
                            not_cont_img.get_width(), 
                            not_cont_img.get_height())
        click = False
        
        for i in range(len(platforms)):
            platforms[i].move()
            platforms[i].draw()
        for i in range(len(enemys)):
            enemys[i].move()
            enemys[i].draw()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                cur.close()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
        if cont_btn.collidepoint((mx, my)):
            if click:
                platforms = [Platform(data[i][0], data[i][1], data[i][2][0], data[i][2][1]) for i in range(2)]
                enemys = [Enemy(data[i][0], data[i][1], data[i][2][0], data[i][2][1]) for i in range(2,5)]
                game(pix, score, platforms, enemys)
                running = False
        elif not_cont_btn.collidepoint((mx, my)):
            if click:
                restart(pix, score)
                running = False

        s = pygame.Surface((size[0],size[1]), pygame.SRCALPHA)   
        s.fill((0,0,0,32)) 
        screen.blit(s, (0,0))
        screen.blit(cont, (size[0]//2-cont.get_width()//2, size[1]//2-cont.get_height()//2 - 50 ))
        best_score = star_font.render(f"best score {user_best_score}", False, (255,140,16))
        screen.blit(best_score, 
        (size[0]//2- best_score.get_width()//2, size[1]//2-cont.get_height()//2 + 100))
        screen.blit(cont_btn_img,  (size[0]//2-cont_btn_img.get_width()//2, size[1]//2-cont.get_height()//2 + 150))
        screen.blit(not_cont_img, (size[0]//2-not_cont_img.get_width()//2, size[1]//2+cont.get_height()//2 - 40))
       
        pygame.display.flip()
        clock.tick(fps)

menu()
pygame.quit()
cur.close()