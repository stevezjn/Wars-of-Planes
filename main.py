import pygame
import sys
import traceback
from pygame.locals import *
import myplane
import enemy
import bullet
import supply
from random import *

pygame.init()
pygame.mixer.init()

bg_size = width, height = 480, 700
screen = pygame.display.set_mode(bg_size)
pygame.display.set_caption('War Of Planes...')

# 初始飞机数量,可直接修改
enemy3_num = 12
enemy2_num = 8
enemy1_num = 2

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

background = pygame.image.load('images/background.png').convert_alpha()

# 载入游戏音乐
pygame.mixer.music.load('sound/game_music.ogg')
pygame.mixer.music.set_volume(0.2)
bullet_sound = pygame.mixer.Sound('sound/bullet.wav')
bullet_sound.set_volume(0.2)
bomb_sound = pygame.mixer.Sound('sound/use_bomb.wav')
bomb_sound.set_volume(0.2)
supply_sound = pygame.mixer.Sound('sound/supply.wav')
supply_sound.set_volume(0.2)
get_bomb_sound = pygame.mixer.Sound('sound/get_bomb.wav')
get_bomb_sound.set_volume(0.2)
get_bullet_sound = pygame.mixer.Sound('sound/get_bullet.wav')
get_bullet_sound.set_volume(0.2)
upgrade_sound = pygame.mixer.Sound('sound/upgrade.wav')
upgrade_sound.set_volume(0.2)
enemy3_fly_sound = pygame.mixer.Sound('sound/enemy3_flying.wav')
enemy3_fly_sound.set_volume(0.2)
enemy1_down_sound = pygame.mixer.Sound('sound/enemy1_down.wav')
enemy1_down_sound.set_volume(0.1)
enemy2_down_sound = pygame.mixer.Sound('sound/enemy2_down.wav')
enemy2_down_sound.set_volume(0.2)
enemy3_down_sound = pygame.mixer.Sound('sound/enemy3_down.wav')
enemy3_down_sound.set_volume(0.5)
me_down_sound = pygame.mixer.Sound('sound/me_down.wav')
me_down_sound.set_volume(0.2)
update_sound = pygame.mixer.Sound('sound/upgrade.wav')
supply_sound = pygame.mixer.Sound('sound/supply.wav')
get_bomb_sound = pygame.mixer.Sound('sound/get_bomb.wav')
get_bullet_sound = pygame.mixer.Sound('sound/get_bullet.wav')


def add_small_enemies(group1, group2, number):
    for i in range(number):
        e1 = enemy.SmallEnemy(bg_size)
        group1.add(e1)
        group2.add(e1)


def add_mid_enemies(group1, group2, number):
    for i in range(number):
        e2 = enemy.MidEnemy(bg_size)
        group1.add(e2)
        group2.add(e2)


def add_big_enemies(group1, group2, number):
    for i in range(number):
        e3 = enemy.BigEnemy(bg_size)
        group1.add(e3)
        group2.add(e3)


def increase_speed(target, inc):
    for each in target:
        each.speed += inc


def main():
    pygame.mixer.music.play(-1)

    # 生成我方飞机
    me = myplane.MyPlane(bg_size)

    # 生成敌方飞机
    enemies = pygame.sprite.Group()

    # 生成大飞机
    big_enemies = pygame.sprite.Group()
    add_big_enemies(big_enemies, enemies, enemy3_num)

    # 生成中飞机
    mid_enemies = pygame.sprite.Group()
    add_mid_enemies(mid_enemies, enemies, enemy2_num)

    # 生成小飞机
    small_enemies = pygame.sprite.Group()
    add_small_enemies(small_enemies, enemies, enemy1_num)

    # 生成普通子弹
    bullet1 = []
    bullet1_index = 0
    BULLET1_NUM = 4
    for i in range(BULLET1_NUM):
        bullet1.append(bullet.Bullet1(me.rect.midtop))

    # 生成超级子弹
    bullet2 = []
    bullet2_index = 0
    BULLET2_NUM = 8
    for i in range(BULLET2_NUM//2):
        bullet2.append(bullet.Bullet2((me.rect.centerx - 33, me.rect.centery)))
        bullet2.append(bullet.Bullet2((me.rect.centerx + 30, me.rect.centery)))

    # 用户切换图片
    switch = True

    # 用于延迟
    delay = 100

    clock = pygame.time.Clock()

    e1_destroy_index = 0
    e2_destroy_index = 0
    e3_destroy_index = 0
    me_destroy_index = 0

    # 统计得分
    score = 0
    score_font = pygame.font.Font('font/font.ttf', 36)

    # 是否暂停游戏
    paused = False
    pause_nor_image = pygame.image.load('images/pause_nor.png').convert_alpha()
    pause_pressed_image = pygame.image.load('images/pause_pressed.png').convert_alpha()
    resume_nor_image = pygame.image.load('images/resume_nor.png').convert_alpha()
    resume_pressed_image = pygame.image.load('images/resume_pressed.png').convert_alpha()
    pause_rect = pause_nor_image.get_rect()
    pause_rect.left, pause_rect.top = width - pause_rect.width - 10, 10
    pause_image = pause_nor_image

    # 难度级别
    level = 1

    # 炸弹
    bomb_image = pygame.image.load('images/bomb.png').convert_alpha()
    bomb_rect = bomb_image.get_rect()
    bomb_font = pygame.font.Font('font/font.ttf', 40)
    bomb_num = 3

    # 每30秒发放一个补给包
    bullet_supply = supply.Bullet_Supply(bg_size)
    bomb_supply = supply.Bomb_Supply(bg_size)
    SUPPLY_TIME = USEREVENT
    pygame.time.set_timer(SUPPLY_TIME, 30*1000)

    # 超级子弹定时器
    DOUBLE_BULLET_TIME = USEREVENT + 1

    # 是否使用超级子弹
    is_double_bullet = False

    # 生命数量
    life_image = pygame.image.load('images/life.png').convert_alpha()
    life_rect = life_image.get_rect()
    life_num = 3

    #  无敌时间计时器
    INVINCIBLE_TIME = USEREVENT + 2

    # 防止重复打开记录文件
    recorded = False

    running = True

    # 是否播放大飞机fly的音效
    play_fly_sound = False

    while running:
        for event in pygame.event.get():
            if event.type==QUIT:
                pygame.quit()
                sys.exit()

            # 暂停
            elif event.type==MOUSEBUTTONDOWN:
                if event.button==1 and pause_rect.collidepoint(event.pos):
                    paused = not paused
                    if paused:
                        pygame.time.set_timer(SUPPLY_TIME, 0)
                        pygame.mixer.music.pause()
                        pygame.mixer.pause()
                    else:
                        pygame.time.set_timer(SUPPLY_TIME, 30*1000)
                        pygame.mixer.music.unpause()
                        pygame.mixer.unpause()

            elif event.type == MOUSEMOTION:
                if pause_rect.collidepoint(event.pos):
                    if paused:
                        pause_image = resume_pressed_image
                    else:
                        pause_image = pause_pressed_image
                else:
                    if paused:
                        pause_image = resume_nor_image
                    else:
                        pause_image = pause_nor_image

            elif event.type == KEYDOWN:
                # 非停止状态下按下空格才释放炸弹
                if not paused and event.key == K_SPACE:
                    if bomb_num > 0:
                        bomb_num -= 1
                        bomb_sound.play()
                        for each in enemies:
                            if each.rect.bottom > 0:
                                each.active = False

            elif event.type==SUPPLY_TIME:
                supply_sound.play()
                if choice([True, False]):
                    bomb_supply.reset()
                else:
                    bullet_supply.reset()

            elif event.type == DOUBLE_BULLET_TIME:
                is_double_bullet = False
                pygame.time.set_timer(DOUBLE_BULLET_TIME, 0)

            elif event.type==INVINCIBLE_TIME:
                me.invincible = False
                pygame.time.set_timer(INVINCIBLE_TIME, 0)

        # 根据得分增加难度
        # 可根据自己喜好修改
        if level == 1 and score > 50:
            level = 2
            update_sound.play()
            # 增加
            add_small_enemies(small_enemies, enemies, 2)
            add_mid_enemies(mid_enemies, enemies, 1)
            add_big_enemies(big_enemies, enemies, 1)
        elif level == 2 and score > 200:
            level = 3
            update_sound.play()
            # 增加
            add_small_enemies(small_enemies, enemies, 2)
            add_mid_enemies(mid_enemies, enemies, 2)
            add_big_enemies(big_enemies, enemies, 0)
            # 提升速度
            increase_speed(small_enemies, 1)
        elif level == 3 and score > 500:
            level = 4
            update_sound.play()
            # 增加
            add_small_enemies(small_enemies, enemies, 3)
            add_mid_enemies(mid_enemies, enemies, 2)
            add_big_enemies(big_enemies, enemies, 1)
            # 提升速度
            increase_speed(mid_enemies, 1)
        elif level == 4 and score > 1200:
            level = 5
            update_sound.play()
            # 增加
            add_small_enemies(small_enemies, enemies, 3)
            add_mid_enemies(mid_enemies, enemies, 1)
            add_big_enemies(big_enemies, enemies, 1)
            # 提升速度
            increase_speed(small_enemies, 1)
            increase_speed(mid_enemies, 1)

        screen.blit(background, (0, 0))

        if life_num and not paused:
            # 检测用户的键盘操作
            key_pressed = pygame.key.get_pressed()

            if key_pressed[K_w] or key_pressed[K_UP]:
                me.moveUp()
            if key_pressed[K_s] or key_pressed[K_DOWN]:
                me.moveDown()
            if key_pressed[K_a] or key_pressed[K_LEFT]:
                me.moveLeft()
            if key_pressed[K_d] or key_pressed[K_RIGHT]:
                me.moveRight()

            # 绘制全屏炸弹补给并检测是否获得
            if bomb_supply.active:
                bomb_supply.move()
                screen.blit(bomb_supply.image, bomb_supply.rect)
                if pygame.sprite.collide_mask(bomb_supply, me):
                    get_bomb_sound.play()
                    if bomb_num < 3:
                        bomb_num += 1
                    bomb_supply.active = False

            # 绘制超级子弹补给并检测是否获得
            if bullet_supply.active:
                bullet_supply.move()
                screen.blit(bullet_supply.image, bullet_supply.rect)
                if pygame.sprite.collide_mask(bullet_supply, me):
                    get_bullet_sound.play()
                    # 发射超级子弹
                    is_double_bullet = True
                    pygame.time.set_timer(DOUBLE_BULLET_TIME, 18*1000)
                    bullet_supply.active = False

            # 发射子弹
            if not (delay % 10):
                bullet_sound.play()
                if is_double_bullet:
                    bullets = bullet2
                    bullets[bullet2_index].reset((me.rect.centerx - 33, me.rect.centery))
                    bullets[bullet2_index + 1].reset((me.rect.centerx + 30, me.rect.centery))
                    bullet2_index = (bullet2_index + 2) % BULLET2_NUM
                else:
                    bullets = bullet1
                    bullets[bullet1_index].reset(me.rect.midtop)
                    bullet1_index = (bullet1_index + 1) % BULLET1_NUM

            # 检测子弹是否击中敌机
            for b in bullets:
                enemies_hit = []
                if b.active:
                    b.move()
                    screen.blit(b.image, b.rect)
                    enemies_hit = pygame.sprite.spritecollide(b, enemies, False, pygame.sprite.collide_mask)
                if enemies_hit:
                    b.active = False
                    for e in enemies_hit:
                        e.hit = True
                        if e in mid_enemies or e in big_enemies:
                            e.energy -= 1
                            if e.energy == 0:
                                e.active = False
                        else:
                            e.active = False

            # 绘制大飞机
            # 一开始先认为不需要播放大飞机飞行的音效
            play_fly_sound = False
            for each in big_enemies:
                if each.active:
                    each.move()
                    if each.hit:
                        screen.blit(each.image_hit, each.rect)
                        each.hit = False
                    else:
                        if switch:
                            screen.blit(each.image1, each.rect)
                        else:
                            screen.blit(each.image2, each.rect)

                    # 绘制血槽
                    pygame.draw.line(screen, BLACK,
                                     (each.rect.left, each.rect.top - 5),
                                     (each.rect.right, each.rect.top - 5),
                                     2)
                    # 当生命大于20%显示绿色，否则显示红色
                    energy_remain = each.energy/enemy.BigEnemy.energy
                    if energy_remain > 0.2:
                        energy_color = GREEN
                    else:
                        energy_color = RED
                    pygame.draw.line(screen, energy_color,
                                     (each.rect.left, each.rect.top - 5),
                                     (each.rect.left + each.rect.width*energy_remain,
                                      each.rect.top - 5), 2)

                    # 即将出现在画面中播放音效
                    # 只要有一个大飞机处于这个范围内，就播放大飞机飞行音效
                    if each.rect.bottom > -50 and each.rect.top < bg_size[1]:
                        play_fly_sound = True

                else:
                    # 毁灭
                    if not (delay % 3):
                        if e3_destroy_index == 0:
                            enemy3_down_sound.play()
                        screen.blit(each.destroy_images[e3_destroy_index], each.rect)
                        e3_destroy_index = (e3_destroy_index + 1) % 6
                        if e3_destroy_index == 0:
                            score += 10
                            each.reset()

            # 决定是否播放大飞机飞行音效
            if play_fly_sound:
                enemy3_fly_sound.play(-1)
                play_fly_sound = False
            else:
                enemy3_fly_sound.stop()

            # 绘制中飞机
            for each in mid_enemies:
                if each.active:
                    each.move()

                    if each.hit:
                        screen.blit(each.image_hit, each.rect)
                        each.hit = False
                    else:
                        screen.blit(each.image, each.rect)

                    # 绘制血槽
                    pygame.draw.line(screen, BLACK,
                                     (each.rect.left, each.rect.top - 5),
                                     (each.rect.right, each.rect.top - 5),
                                     2)
                    # 当生命大于20%显示绿色，否则显示红色
                    energy_remain = each.energy/enemy.MidEnemy.energy
                    if energy_remain > 0.2:
                        energy_color = GREEN
                    else:
                        energy_color = RED
                    pygame.draw.line(screen, energy_color,
                                     (each.rect.left, each.rect.top - 5),
                                     (each.rect.left + each.rect.width*energy_remain,
                                      each.rect.top - 5), 2)
                else:
                    # 毁灭
                    if not (delay % 3):
                        if e2_destroy_index == 0:
                            enemy2_down_sound.play()
                        screen.blit(each.destroy_images[e2_destroy_index], each.rect)
                        e2_destroy_index = (e2_destroy_index + 1) % 4
                        if e2_destroy_index == 0:
                            score += 6
                            each.reset()

            # 绘制小飞机
            for each in small_enemies:
                if each.active:
                    each.move()
                    screen.blit(each.image, each.rect)
                else:
                    # 毁灭
                    if not (delay % 3):
                        if e1_destroy_index == 0:
                            enemy1_down_sound.play()
                        screen.blit(each.destroy_images[e1_destroy_index], each.rect)
                        e1_destroy_index = (e1_destroy_index + 1) % 4
                        if e1_destroy_index == 0:
                            score += 1
                            each.reset()

            # 检测我方飞机是否被撞
            enemies_down = pygame.sprite.spritecollide(me, enemies, False, pygame.sprite.collide_mask)
            if enemies_down and not me.invincible:

                me.active = False
                for e in enemies_down:
                    e.active = False

            # 绘制我方飞机
            if me.active:
                if switch:
                    screen.blit(me.image1, me.rect)
                else:
                    screen.blit(me.image2, me.rect)
            else:
                # 毁灭
                if not (delay % 3):
                    if me_destroy_index == 0:
                        me_down_sound.play()
                    screen.blit(me.destroy_images[me_destroy_index], me.rect)
                    me_destroy_index = (me_destroy_index + 1) % 4
                    if me_destroy_index == 0:
                        life_num -= 1
                        me.reset()
                        pygame.time.set_timer(INVINCIBLE_TIME, 3*1000)

            # 绘制炸弹
            bomb_text = bomb_font.render('x %d' % bomb_num, True, WHITE)
            text_rect = bomb_text.get_rect()
            screen.blit(bomb_image, (10, height - 10 - bomb_rect.height))
            screen.blit(bomb_text, (20 + bomb_rect.width, height - 5 - text_rect.height))

            # 绘制生命数量
            if life_num:
                for i in range(life_num):
                    screen.blit(life_image,
                                (width - (i + 1)*life_rect.width - 10,
                                 height - life_rect.height - 10))

            # 绘制得分
            score_text = score_font.render('Score : %s' % str(score), True, WHITE)
            screen.blit(score_text, (10, 5))

        # 绘制游戏结束画面
        elif life_num == 0:
            # 停止背景音乐
            pygame.mixer.music.stop()

            # 停止音效
            pygame.mixer.stop()

            # 停止补给
            pygame.time.set_timer(SUPPLY_TIME, 0)

            # 读取历史最高分
            if not recorded:
                recorded = True
                with open('record.txt', 'r') as f:
                    record_score = int(f.read())
                if score > record_score:
                    with open('record.txt', 'w') as f:
                        f.write(str(score))

            # 绘制结束界面
            score_font = pygame.font.Font('font/font.ttf', 40)
            gameover_font = pygame.font.Font('font/font.ttf', 40)
            again_image = pygame.image.load('images/again.png').convert_alpha()
            gameover_image = pygame.image.load('images/gameover.png').convert_alpha()

            record_score_text = score_font.render('Best : %d' % record_score, True, WHITE)
            screen.blit(record_score_text, (10, 10))

            gameover_text1 = gameover_font.render('Your Score', True, WHITE)
            gameover_text1_rect = gameover_text1.get_rect()
            gameover_text1_rect.left, gameover_text1_rect.top = \
                (width - gameover_text1_rect.width)//2, height//2
            screen.blit(gameover_text1, gameover_text1_rect)

            gameover_text2 = gameover_font.render(str(score), True, WHITE)
            gameover_text2_rect = gameover_text2.get_rect()
            gameover_text2_rect.left, gameover_text2_rect.top = \
                (width - gameover_text2_rect.width)//2, \
                gameover_text1_rect.bottom + 10
            screen.blit(gameover_text2, gameover_text2_rect)

            again_rect = again_image.get_rect()
            again_rect.left, again_rect.top = \
                (width - again_rect.width)//2, \
                gameover_text2_rect.bottom + 50
            screen.blit(again_image, again_rect)

            gameover_rect = gameover_image.get_rect()
            gameover_rect.left, gameover_rect.top = \
                (width - gameover_rect.width)//2, \
                again_rect.bottom + 50
            screen.blit(gameover_image, gameover_rect)

            # 检测用户操作，重新开始或者结束游戏
            # 检测是否按下左键
            if pygame.mouse.get_pressed()[0]:  # 表示按下左键
                # 获取鼠标坐标
                pos = pygame.mouse.get_pos()
                if again_rect.left < pos[0] < again_rect.right and \
                        again_rect.top < pos[1] < again_rect.bottom:
                    main()
                elif gameover_rect.left < pos[0] < gameover_rect.right and \
                        gameover_rect.top < pos[1] < gameover_rect.bottom:
                    pygame.quit()
                    sys.exit()

        screen.blit(pause_image, pause_rect)

        if not delay % 5:
            switch = not switch

        delay -= 1
        if not delay:
            delay = 100

        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        pass
    except:
        traceback.print_exc()
        pygame.quit()
        input()
