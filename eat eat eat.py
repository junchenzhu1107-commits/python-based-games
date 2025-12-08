import pygame
import sys
import random

pygame.init()

# 画面大小
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
UI_HEIGHT = 80
BORDER_WIDTH = 5

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("EAT EAT EAT")
clock = pygame.time.Clock()

font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)
large_font = pygame.font.Font(None, 48)


# 主菜单：选择游戏时间 或 退出

def select_game_mode():
    while True:
        screen.fill((30, 30, 30))

        title = large_font.render("Select Game Time", True, (255, 255, 255))
        opt1 = font.render("Press 1: 60 seconds (Easy)", True, (200, 200, 200))
        opt2 = font.render("Press 2: 120 seconds (Medium)", True, (200, 200, 200))
        opt3 = font.render("Press 3: 180 seconds (Hard)", True, (200, 200, 200))
        hint = small_font.render("Press ESC to exit", True, (150, 150, 150))

        screen.blit(title, (450 - title.get_width()//2, 150))
        screen.blit(opt1, (450 - opt1.get_width()//2, 250))
        screen.blit(opt2, (450 - opt2.get_width()//2, 300))
        screen.blit(opt3, (450 - opt3.get_width()//2, 350))
        screen.blit(hint, (450 - hint.get_width()//2, 450))

        pygame.display.flip()

        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "exit"
                if event.key == pygame.K_1:
                    return 60
                if event.key == pygame.K_2:
                    return 120
                if event.key == pygame.K_3:
                    return 180


# 游戏结束画面

def show_game_over(score):
    while True:
        screen.fill((30, 30, 30))

        title = large_font.render("GAME OVER!", True, (255, 0, 0))
        score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
        hint = small_font.render("Press ESC to return to menu", True, (200, 200, 200))

        screen.blit(title, (450 - title.get_width()//2, 200))
        screen.blit(score_text, (450 - score_text.get_width()//2, 300))
        screen.blit(hint, (450 - hint.get_width()//2, 400))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"



# 游戏主逻辑

def game_loop(total_time):

    # 游戏区域
    GAME_AREA = pygame.Rect(BORDER_WIDTH, UI_HEIGHT + BORDER_WIDTH,
                            SCREEN_WIDTH - 2*BORDER_WIDTH,
                            SCREEN_HEIGHT - UI_HEIGHT - 2*BORDER_WIDTH)

    # 玩家
    player_pos = [400, 300]
    player_size = [30, 30]
    player_speed = 5

    # 小食物
    food_size = [15, 15]
    food_active = False
    food_lifetime = 180
    food_timer = 0
    food_color = (0, 255, 0)

    # 大食物
    big_food_size = [25, 25]
    big_food_active = False
    big_food_lifetime = 300
    big_food_timer = 0
    big_food_color = (255, 165, 0)

    # 陷阱
    trap_list = []
    trap_size = [35, 35]
    trap_color = (50, 50, 255)
    trap_lifetime = 600
    trap_blink_duration = 180
    trap_spawn_timer = 0
    trap_spawn_interval = 90
    MAX_TRAPS = 3

    # 游戏状态
    score = 0
    health = 3
    time_remaining = total_time * 60
    game_over = False

    def create_food():
        return [
            random.randint(GAME_AREA.left, GAME_AREA.right - food_size[0]),
            random.randint(GAME_AREA.top, GAME_AREA.bottom - food_size[1])
        ]

    def create_big_food():
        return [
            random.randint(GAME_AREA.left, GAME_AREA.right - big_food_size[0]),
            random.randint(GAME_AREA.top, GAME_AREA.bottom - big_food_size[1])
        ]

    def create_trap():
        for _ in range(20):
            x = random.randint(GAME_AREA.left, GAME_AREA.right - trap_size[0])
            y = random.randint(GAME_AREA.top, GAME_AREA.bottom - trap_size[1])
            return [x, y]
        return [200, 200]

    running = True

    while running:

        # ESC逻辑
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"

        # 游戏倒计时
        if not game_over:
            time_remaining -= 1
        if time_remaining <= 0:
            result = show_game_over(score)
            return result

        # 生成食物
        if not food_active:
            food_pos = create_food()
            food_active = True
            food_timer = 0

        if food_active:
            food_timer += 1
            if food_timer >= food_lifetime:
                food_active = False

        # 大食物
        if not big_food_active:
            big_food_pos = create_big_food()
            big_food_active = True
            big_food_timer = 0

        if big_food_active:
            big_food_timer += 1
            if big_food_timer >= big_food_lifetime:
                big_food_active = False

        # 陷阱生成
        trap_spawn_timer += 1
        if len(trap_list) < MAX_TRAPS and trap_spawn_timer >= trap_spawn_interval:
            if random.random() < 0.6:
                trap_list.append({"pos": create_trap(), "timer": 0, "blink_phase": True})
            trap_spawn_timer = 0

        # 陷阱更新
        for trap in trap_list[:]:
            trap["timer"] += 1
            if trap["timer"] < trap_blink_duration:
                if trap["timer"] % 10 == 0:
                    trap["blink_phase"] = not trap["blink_phase"]
            else:
                trap["blink_phase"] = True

            if trap["timer"] >= trap_lifetime:
                trap_list.remove(trap)

        # 玩家移动
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: player_pos[0] -= player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: player_pos[0] += player_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: player_pos[1] -= player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: player_pos[1] += player_speed

        # 边界约束
        if player_pos[0] < GAME_AREA.left: player_pos[0] = GAME_AREA.left
        if player_pos[0] > GAME_AREA.right - player_size[0]: player_pos[0] = GAME_AREA.right - player_size[0]
        if player_pos[1] < GAME_AREA.top: player_pos[1] = GAME_AREA.top
        if player_pos[1] > GAME_AREA.bottom - player_size[1]: player_pos[1] = GAME_AREA.bottom - player_size[1]

        # 碰撞检测
        player_rect = pygame.Rect(player_pos[0], player_pos[1], player_size[0], player_size[1])

        # 小食物
        if food_active:
            food_rect = pygame.Rect(food_pos[0], food_pos[1], food_size[0], food_size[1])
            if player_rect.colliderect(food_rect):
                food_active = False
                score += 1
                player_size[0] += 3
                player_size[1] += 3

        # 大食物
        if big_food_active:
            big_rect = pygame.Rect(big_food_pos[0], big_food_pos[1], big_food_size[0], big_food_size[1])
            if player_rect.colliderect(big_rect):
                big_food_active = False
                score += 2
                player_size[0] += 5
                player_size[1] += 5

        # 陷阱伤害（闪烁完毕才有伤害）
        for trap in trap_list[:]:
            trap_rect = pygame.Rect(trap["pos"][0], trap["pos"][1], trap_size[0], trap_size[1])
            if trap["timer"] >= trap_blink_duration and player_rect.colliderect(trap_rect):
                trap_list.remove(trap)
                health -= 1
                score = score // 2
                if health <= 0:
                    return show_game_over(score)

        # 图像部分
        screen.fill((50, 50, 50))

        pygame.draw.rect(screen, (200,200,200), [0,UI_HEIGHT,900,700-UI_HEIGHT], BORDER_WIDTH)
        pygame.draw.rect(screen, (135,206,235), GAME_AREA)

        pygame.draw.rect(screen, (255,0,0), [player_pos[0],player_pos[1],player_size[0],player_size[1]])

        if food_active:
            pygame.draw.rect(screen, food_color, [food_pos[0],food_pos[1],food_size[0],food_size[1]])
        if big_food_active:
            pygame.draw.rect(screen, big_food_color, [big_food_pos[0],big_food_pos[1],big_food_size[0],big_food_size[1]])

        for trap in trap_list:
            if trap["blink_phase"]:
                pygame.draw.rect(screen, trap_color, [trap["pos"][0],trap["pos"][1],trap_size[0],trap_size[1]])
                pygame.draw.rect(screen, (255,255,255), [trap["pos"][0],trap["pos"][1],trap_size[0],trap_size[1]], 2)

        pygame.draw.rect(screen, (40,40,40), [0,0,900,UI_HEIGHT])
        screen.blit(font.render(f"Score: {score}", True, (255,255,255)), (20, 20))
        screen.blit(font.render(f"Health: {health}/3", True, (255,0,0)), (400, 20))

        seconds = max(0, time_remaining // 60)
        screen.blit(font.render(f"Time: {seconds:02d}", True, (255,255,255)), (750, 20))

        pygame.display.flip()
        clock.tick(70)


# 主程序循环

while True:
    mode = select_game_mode()
    if mode == "exit":
        break

    result = game_loop(mode)
    if result == "exit":
        break

pygame.quit()
sys.exit()
