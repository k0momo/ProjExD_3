import os
import random
import sys
import time
import pygame as pg

WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 5  # 爆弾の数

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate

class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {
        pg.K_UP:    (0, -5),
        pg.K_DOWN:  (0, +5),
        pg.K_LEFT:  (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    img = pg.transform.flip(img0, True, False)
    imgs = {
        (+5, 0):  img,
        (+5, -5): pg.transform.rotozoom(img,  45, 0.9),
        (0, -5):  pg.transform.rotozoom(img,  90, 0.9),
        (-5, -5): pg.transform.rotozoom(img0, -45, 0.9),
        (-5, 0):  img0,
        (-5, +5): pg.transform.rotozoom(img0,  45, 0.9),
        (0, +5):  pg.transform.rotozoom(img, -90, 0.9),
        (+5, +5): pg.transform.rotozoom(img, -45, 0.9),
    }

    def __init__(self, xy: tuple[int, int]):
        self.img = __class__.imgs[(+5, 0)]
        self.rct: pg.Rect = self.img.get_rect()
        self.rct.center = xy

    def change_img(self, num: int, screen: pg.Surface):
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        if sum_mv != [0, 0]:
            self.img = __class__.imgs[tuple(sum_mv)]
        screen.blit(self.img, self.rct)

class Beam:
    """
    こうかとんが放つビームに関するクラス
    """
    def __init__(self, bird: Bird):
        self.img = pg.image.load("fig/beam.png")
        self.rct = self.img.get_rect()
        self.rct.centery = bird.rct.centery
        self.rct.left = bird.rct.right
        self.vx, self.vy = +5, 0

    def update(self, screen: pg.Surface):
        if check_bound(self.rct) == (True, True):
            self.rct.move_ip(self.vx, self.vy)
            screen.blit(self.img, self.rct)

class Bomb:
    """
    爆弾に関するクラス
    """
    def __init__(self, color: tuple[int, int, int], rad: int):
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5

    def update(self, screen: pg.Surface):
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)

def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bird = Bird((300, 200))

    # 練習5：複数爆弾の初期化
    bombs = [Bomb((255, 0, 0), 10) for _ in range(NUM_OF_BOMBS)]
    beam = None
    clock = pg.time.Clock()
    tmr = 0

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                beam = Beam(bird)

        screen.blit(bg_img, [0, 0])

        # 練習5-1：ビーム⇔爆弾の衝突判定
        for i, b in enumerate(bombs):
            if beam is not None and b is not None and beam.rct.colliderect(b.rct):
                # 喜ぶエフェクト（練習3）
                bird.change_img(6, screen)
                pg.display.update()
                time.sleep(1)
                beam = None 
                bomb = None
                
        
        if bomb is not None and bird.rct.colliderect(bomb.rct):
            # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
            bird.change_img(8, screen)
            pg.display.update()
            time.sleep(1)
            return

        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)

        if beam is not None:
            beam.update(screen)
        for b in bombs:
            b.update(screen)

        pg.display.update()
        tmr += 1
        clock.tick(50)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
