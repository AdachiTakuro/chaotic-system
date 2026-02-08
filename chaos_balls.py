from pygame.gfxdraw import circle
# from reflection import arrow, yellow
from drawing import aacirlce
import drawing
import pygame
import os
import time as t
from math import acos, atan2, sin, cos, sqrt, pi
# import math
from test import dot, simul
import cv2
import numpy as np

# Game presets
start_time = t.time()
fps = 60
width, height = 1080, 1920

# Centers window
x, y = 1360 - width, 40
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x, y)


pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Bouncing balls")
clock = pygame.time.Clock()
drawing.screen = screen  # drawing.pyのscreen参照を更新

background = pygame.image.load("img/start_img.png")
background = pygame.transform.scale(background, (width, height))

# initialize pygame mixer and load audio file
audio_enabled = False
try:
    pygame.mixer.init()
    audio_enabled = True
except Exception:
    print("[警告] オーディオデバイスが見つかりません。音声なしで続行します。")
# pygame.mixer.music.load('audio/golf_ball.wav')  # audio options [golfball, ground_impact, metalmicrowave, golf_ball]

font = pygame.font.Font('freesansbold.ttf', 15)

white        = (255, 255, 255)
whitest      = (204, 234, 234)
# grey       = (45 ,  45,  45)
grey         = ( 27,  27,  27)
black        = (  0,   0,   0)
blackcoral   = ( 39,  22,  16)
deepblue     = (  0,   4,  30)
red          = (225,  40,  40)
green        = ( 10, 200,  27)
yellowish    = (191, 202,  37)
orange       = (255,  72,   0)
velvet       = (232,  20,  20)
bluish_white = (179, 255, 251)
blue         = (17 , 200, 251)
tastyellow   = (255, 230,   0)
arrow_color  = (255, 255, 255)
golden       = (255, 166,  32)
golden       = (245, 170,  10)
algeablue    = (7  , 197,  70)
magenta      = (255,  13, 130)
magenta2     = (214,   0, 100)
bg = deepblue


# g = -0.1
g = -9.81
bigr = width//2 - 40 # rad of big circle (縦長画面の幅に収まるように)
centx, centy = width//2, height//2 # center of circle
frames = 0
class Balls():
    trail = True
    balls = list()
    def __init__(self, name, color, radius, thicc, posx, posy, sound="metalmicrowave.wav", growth_rate=1.7, speed_boost=1.0005):
        Balls.balls.append(self)
        
        self.name   = name
        self.color  = color
        self.radius = radius
        self.thicc  = thicc
        self.posx   = posx
        self.posy   = posy
        self.sound  = f"audio/{sound}"
        self.velx   = 0
        self.vely   = 0
        self.acc    = g/fps
        self.track  = list()
        self.growth_rate = growth_rate  # 衝突ごとに増加するサイズ
        self.speed_boost = speed_boost  # 衝突ごとに速度を増加させる係数
        self.sides  = 3  # 三角形からスタート


    def drawball(self):
        # 多角形の頂点を計算
        points = []
        for i in range(self.sides):
            angle = 2 * pi * i / self.sides - pi / 2  # -pi/2で上向きからスタート
            x = self.posx + self.radius * cos(angle)
            y = self.posy + self.radius * sin(angle)
            points.append((x, y))
        
        if self.thicc == 0:
            pygame.draw.polygon(screen, self.color, points, 0)
        else:
            pygame.draw.polygon(screen, self.color, points, self.thicc)
        
        # 角の数を表示（ボールサイズに比例）
        font_size = max(10, int(self.radius * 0.8))
        dynamic_font = pygame.font.Font('freesansbold.ttf', font_size)
        text = dynamic_font.render(str(self.sides), True, white)
        text_rect = text.get_rect(center=(self.posx, self.posy))
        screen.blit(text, text_rect)
    
    def collision_handling(self):
        vel = sqrt(self.velx**2 + self.vely**2)
        # vel = 2 if vel >= 2 else vel

        x,y = centx, centy # center of cirlce
        ballx, bally = self.posx, self.posy
        velx, vely = self.velx, self.vely
        # center to ball is the distance between ball's center and the ring's center
        center_to_ball = sqrt((x-ballx)**2 + (y-bally)**2)
        


        if center_to_ball >= (bigr - self.radius):
            # play bounce sound effect
            if audio_enabled:
                try:
                    pygame.mixer.Sound.play(pygame.mixer.Sound(self.sound))
                except Exception:
                    pass

            # ボールのサイズを増加
            self.radius += self.growth_rate
            
            # 角の数を1つ増やす
            self.sides += 1

            while sqrt((x-self.posx)**2 + (y-self.posy)**2) > (bigr - self.radius):
                step = 0.2
                # moving the ball backwawrds in dir of velocity by small steps
                self.posx += -self.velx*step/vel
                self.posy -= -self.vely*step/vel

                
            normal = ballx - x, bally - y
            normal_mag = center_to_ball #sqrt(normal[0]**2 + normal[1]**2)
            n = normal[0]/normal_mag, normal[1]/normal_mag
            nx, ny = n[0], n[1]

            d = velx, -vely # incident
            dx, dy = d[0], d[1]

            reflected = dx-2*dot(n,d)*nx, dy-2*dot(n,d)*ny

            # 反射後の速度を設定し、speed_boostで速度を増加
            self.velx = reflected[0] * self.speed_boost
            self.vely = -reflected[1] * self.speed_boost

            # a shitty fix to speed's gradual loss

            # r_size = sqrt(self.velx**2 + self.vely**2)
            # self.velx = reflected[0]*vel/r_size
            # self.vely = -reflected[1]*vel/r_size


    def motion(self):

        self.velx += 0
        self.vely += self.acc

        self.posx += self.velx
        self.posy -= self.vely

        every   = 2
        period  = 5
        if frames % every == 0 and Balls.trail:
            self.track.append((self.posx, self.posy))
        if Balls.trail is False:
            self.track.clear()
        elif len(self.track) > fps*period/every : #240:
            self.track.pop(0)
        


def draw_cricle(color, radius, thicc, posx, posy):
    pygame.draw.circle(screen, color, (posx, posy), radius, thicc)



# redball   = Balls("red ball", red, 8, 0, width//2-bigr+20, height//2-59, "bm.wav")
redball   = Balls("red ball", golden, 15, 0, width//2-bigr+80, height//2, "bm.wav", growth_rate=3.0)
redball.vely = -5
# greenball = Balls("green ball", algeablue, 8, 0, width//2+bigr-20, height//2-50, "golf_ball.wav")
# yellowball = Balls("green ball", magenta2, 8, 0, width//3, height//2,"trm.wav")
# blueball = Balls("green ball", blue, 8, 0, width*2//3+5, height//2, "trm.wav")
# greenball = Balls("green ball", green, 12, 0, width//2+70, height//2-60)

# === 動画保存設定 ===
os.makedirs('outputs/videos', exist_ok=True)
video_filename = f'outputs/videos/tiktok_chaos_{int(t.time())}.mp4'
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_writer = cv2.VideoWriter(video_filename, fourcc, fps, (width, height))
print(f"[録画開始] 保存先: {video_filename}")

pause = False
start_sim = False 


while start_sim is False:
    
    screen.fill(bg)
    screen.blit(background, [0,0])
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            video_writer.release()
            print(f"[録画終了] 保存先: {video_filename}")
            pygame.quit()
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                start_sim = True
    


    pygame.display.update()
    clock.tick(fps)


while True:

    # draw_cricle(yellow, 2, 0, width//2, height//2)
    # draw(red, height//3, 3, width//2, height//2)
    

    screen.fill(bg)
    aacirlce(bigr, width//2, height//2, whitest, 1)

    for ball in Balls.balls:
        if len(ball.track)> 2 and Balls.trail:
            pygame.draw.aalines(screen, ball.color, False, ball.track, 2)
    for ball in Balls.balls:
        ball.drawball()
        if not pause:
            ball.collision_handling()
            ball.motion()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            video_writer.release()
            print(f"[録画終了] 保存先: {video_filename}")
            pygame.quit()
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                pause = not pause
            if event.key == pygame.K_t:
                Balls.trail = not Balls.trail
                # if trail is False:
                #     for ball in Balls.balls:
                #         ball.track.clear()
    

    # フレームをキャプチャして動画に書き込む
    frame = pygame.surfarray.array3d(screen)
    frame = np.transpose(frame, (1, 0, 2))  # (W,H,3) -> (H,W,3)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    video_writer.write(frame)

    pygame.display.update()
    clock.tick(fps)
    frames += 1


























# vel = redball.vel
# arrow(arrow_color, arrow_color, (redball.posx, redball.posy), (redball.posx+vel*10*cos(redball.theta), redball.posy-vel*10*sin(redball.theta)), 1)
# rect = [redball.posx - 15 ,redball.posy-15, 30,30]
# pygame.draw.line(screen, orange, (redball.posx, redball.posy), (redball.posx +25, redball.posy), 2 )
# pygame.draw.rect(screen, yellow, rect, 4)
# draw_cricle(red, 2, 0, redball.posx-15, redball.posy-15)
# pygame.draw.arc(screen, white, rect, 0, redball.theta, 2)
# arrow(arrow_color, arrow_color, (greenball.posx, greenball.posy), (greenball.posx+vel*10*cos(greenball.theta), greenball.posy-vel*10*sin(greenball.theta)), 1)
    
    