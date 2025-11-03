import pygame
import sys
import random

# 1. 初始化Pygame的所有模块
pygame.init()

# 2. 设置游戏窗口的大小（宽度，高度）
screen = pygame.display.set_mode((900,700))

# 边框厚度
BORDER_WIDTH = 5
# UI区域高度
UI_HEIGHT = 80
# 游戏区域（边框内部）
GAME_AREA = pygame.Rect(BORDER_WIDTH, UI_HEIGHT + BORDER_WIDTH, 
                        900 - 2*BORDER_WIDTH, 700 - UI_HEIGHT - 2*BORDER_WIDTH)

# 3. 设置窗口的标题
pygame.display.set_caption("Time Survival Game")

# 4. 创建一个时钟对象，用来控制游戏循环的帧率
clock = pygame.time.Clock()

# 使用最简单的字体方案
font = pygame.font.Font(None, 36)  # 使用None，Pygame会使用默认字体
small_font = pygame.font.Font(None, 24)
large_font = pygame.font.Font(None, 48)

# 游戏模式选择
def select_game_mode():
    screen.fill((30, 30, 30))
    
    title_text = large_font.render("Select Game Time", True, (255, 255, 255))
    option1_text = font.render("Press 1: 60 seconds (Easy)", True, (200, 200, 200))
    option2_text = font.render("Press 2: 120 seconds (Medium)", True, (200, 200, 200))
    option3_text = font.render("Press 3: 180 seconds (Hard)", True, (200, 200, 200))
    hint_text = small_font.render("Use number keys 1,2,3 to select", True, (150, 150, 150))
    
    screen.blit(title_text, (450 - title_text.get_width()//2, 150))
    screen.blit(option1_text, (450 - option1_text.get_width()//2, 250))
    screen.blit(option2_text, (450 - option2_text.get_width()//2, 300))
    screen.blit(option3_text, (450 - option3_text.get_width()//2, 350))
    screen.blit(hint_text, (450 - hint_text.get_width()//2, 450))
    
    pygame.display.flip()
    
    waiting = True
    selected_time = 60  # 默认60秒
    
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected_time = 60
                    waiting = False
                elif event.key == pygame.K_2:
                    selected_time = 120
                    waiting = False
                elif event.key == pygame.K_3:
                    selected_time = 180
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
    
    return selected_time

# 显示游戏结束画面
def show_game_over(final_score):
    screen.fill((30, 30, 30))
    
    title_text = large_font.render("GAME OVER!", True, (255, 0, 0))
    score_text = font.render(f"Final Score: {final_score}", True, (255, 255, 255))
    info_text = small_font.render("Press ESC to exit", True, (200, 200, 200))
    
    screen.blit(title_text, (450 - title_text.get_width()//2, 200))
    screen.blit(score_text, (450 - score_text.get_width()//2, 300))
    screen.blit(info_text, (450 - info_text.get_width()//2, 400))
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False    
    return True

# 选择游戏时间
total_time = select_game_mode()

# 玩家的初始位置 [x, y]
player_pos = [400, 300]
# 玩家的移动速度
player_speed = 5
# 玩家的大小 [宽度, 高度]
player_size = [30, 30]
# 食物的位置和大小
food_pos = [100, 100]
food_size = [15,15]
food_color = (0, 255, 0)
food_timer = 0
food_lifetime = 180
food_active = False

big_food_pos = [200, 200]
big_food_size = [25, 25]
big_food_color = (255, 165, 0)
big_food_timer = 0
big_food_lifetime = 300
big_food_active = False

# 陷阱系统 - 支持多个陷阱
trap_list = []  # 陷阱列表
trap_size = [35, 35]
trap_color = (255, 50, 50)
trap_lifetime = 600  # 总存在时间10秒
trap_blink_duration = 180  # 闪烁3秒（180帧）
trap_spawn_timer = 0
trap_spawn_interval = 90
MAX_TRAPS = 3  # 最大陷阱数量

# 游戏状态变量
score = 0
game_time = 0
health = 3
MIN_PLAYER_SIZE = 20
time_remaining = total_time * 60  # 转换为帧数

def create_food():
    x = random.randint(GAME_AREA.left, GAME_AREA.right - food_size[0])
    y = random.randint(GAME_AREA.top, GAME_AREA.bottom - food_size[1])
    return [x, y]

def create_big_food():
    x = random.randint(GAME_AREA.left, GAME_AREA.right - big_food_size[0])
    y = random.randint(GAME_AREA.top, GAME_AREA.bottom - big_food_size[1])
    return [x, y]

def create_trap():
    """生成陷阱，确保不会生成在玩家位置"""
    max_attempts = 20  # 最大尝试次数，避免无限循环
    player_rect = pygame.Rect(player_pos[0], player_pos[1], player_size[0], player_size[1])
    
    for attempt in range(max_attempts):
        # 随机生成位置
        x = random.randint(GAME_AREA.left, GAME_AREA.right - trap_size[0])
        y = random.randint(GAME_AREA.top, GAME_AREA.bottom - trap_size[1])
        
        # 创建陷阱矩形
        trap_rect = pygame.Rect(x, y, trap_size[0], trap_size[1])
        
        # 检查是否与玩家重叠
        if not trap_rect.colliderect(player_rect):
            return [x, y]  # 找到不重叠的位置
    
    # 如果多次尝试都失败，返回一个默认位置（可能会重叠，但概率很低）
    x = random.randint(GAME_AREA.left, GAME_AREA.right - trap_size[0])
    y = random.randint(GAME_AREA.top, GAME_AREA.bottom - trap_size[1])
    return [x, y]

# 5. 游戏主循环
running = True
game_over = False

while running:
    # 更新游戏时间
    game_time += 1
    
    # 倒计时
    if not game_over:
        time_remaining -= 1
        seconds_remaining = max(0, time_remaining // 60)
    
    # 6. 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # 检查游戏是否结束（时间到或血量归零）
    if time_remaining <= 0 and not game_over:
        game_over = True
        if show_game_over(score):
            running = False
        else:
            running = False
        continue

    if game_over:
        continue

    # 食物更新逻辑
    if not food_active:
        food_pos = create_food()
        food_active = True
        food_timer = 0
    
    if food_active:
        food_timer += 1
        if food_timer >= food_lifetime:
            food_active = False

    if not big_food_active:
        big_food_pos = create_big_food()
        big_food_active = True
        big_food_timer = 0
    
    if big_food_active:
        big_food_timer += 1
        if big_food_timer >= big_food_lifetime:
            big_food_active = False

    # 陷阱生成逻辑（从游戏开始就生成，不依赖分数）
    trap_spawn_timer += 1
    if len(trap_list) < MAX_TRAPS and trap_spawn_timer >= trap_spawn_interval:
        if random.random() < 0.6:
            new_trap = {
                'pos': create_trap(),
                'timer': 0,
                'blink_phase': True
            }
            trap_list.append(new_trap)
        trap_spawn_timer = 0
    
    # 更新所有活跃的陷阱
    for trap in trap_list[:]:  # 使用切片复制避免修改时出错
        trap['timer'] += 1
        
        # 更新闪烁状态（前3秒闪烁）
        if trap['timer'] < trap_blink_duration:
            # 每0.2秒切换一次闪烁状态（10帧切换一次）
            if trap['timer'] % 10 == 0:
                trap['blink_phase'] = not trap['blink_phase']
        else:
            # 3秒后常亮
            trap['blink_phase'] = True
        
        # 移除超时的陷阱
        if trap['timer'] >= trap_lifetime:
            trap_list.remove(trap)

    # 获取按键状态
    keys = pygame.key.get_pressed()

    # 玩家移动
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_pos[0] -= player_speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_pos[0] += player_speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        player_pos[1] -= player_speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        player_pos[1] += player_speed

    # 边界限制
    if player_pos[0] < GAME_AREA.left:
        player_pos[0] = GAME_AREA.left
    if player_pos[0] > GAME_AREA.right - player_size[0]:
        player_pos[0] = GAME_AREA.right - player_size[0]
    if player_pos[1] < GAME_AREA.top:
        player_pos[1] = GAME_AREA.top
    if player_pos[1] > GAME_AREA.bottom - player_size[1]:
        player_pos[1] = GAME_AREA.bottom - player_size[1]

    # 碰撞检测
    player_rect = pygame.Rect(player_pos[0], player_pos[1], player_size[0], player_size[1])
    food_rect = pygame.Rect(food_pos[0], food_pos[1], food_size[0], food_size[1])
    
    # 小食物碰撞
    if food_active and player_rect.colliderect(food_rect):
        player_size[0] += 3
        player_size[1] += 3
        food_active = False
        score += 1

    # 大食物碰撞
    big_food_rect = pygame.Rect(big_food_pos[0], big_food_pos[1], big_food_size[0], big_food_size[1])
    if big_food_active and player_rect.colliderect(big_food_rect):
        player_size[0] += 5
        player_size[1] += 5
        big_food_active = False
        score += 2

    # 陷阱碰撞检测（遍历所有陷阱）
    for trap in trap_list[:]:
        trap_rect = pygame.Rect(trap['pos'][0], trap['pos'][1], trap_size[0], trap_size[1])
        # 只在常亮状态或闪烁的可见阶段检测碰撞
        if (trap['timer'] >= trap_blink_duration or trap['blink_phase']) and player_rect.colliderect(trap_rect):
            trap_list.remove(trap)  # 移除被触发的陷阱
            health -= 1
            
            # 新惩罚机制：分数减半，大小不变
            score = max(0, score // 2)
            
            if health <= 0:
                game_over = True
                if show_game_over(score):
                    running = False
                else:
                    running = False
                continue

            #受伤动画
            

    # 7. 绘制部分
    screen.fill((50, 50, 50)) #天蓝色
    
    # 绘制游戏区域边框
    pygame.draw.rect(screen, (200, 200, 200), 
                    [0, UI_HEIGHT, 900, 700 - UI_HEIGHT], 
                    BORDER_WIDTH)
    
    # 绘制游戏区域背景
    pygame.draw.rect(screen, (135, 206, 235), GAME_AREA)
    
    # 绘制玩家方块
    pygame.draw.rect(screen, (255, 0, 0), 
                    [player_pos[0], player_pos[1], player_size[0], player_size[1]])
    
    # 绘制食物
    if food_active:
        pygame.draw.rect(screen, food_color, 
                        [food_pos[0], food_pos[1], food_size[0], food_size[1]])
    
    if big_food_active:
        pygame.draw.rect(screen, big_food_color, 
                        [big_food_pos[0], big_food_pos[1], big_food_size[0], big_food_size[1]])
    
    # 绘制所有陷阱
    for trap in trap_list:
        # 只在闪烁阶段或常亮阶段绘制
        if trap['blink_phase']:
            pygame.draw.rect(screen, trap_color, 
                            [trap['pos'][0], trap['pos'][1], trap_size[0], trap_size[1]])
            # 添加白色边框让陷阱更明显
            pygame.draw.rect(screen, (255, 255, 255), 
                            [trap['pos'][0], trap['pos'][1], trap_size[0], trap_size[1]], 2)
    
    # 绘制UI背景
    pygame.draw.rect(screen, (40, 40, 40), [0, 0, 900, UI_HEIGHT])
    
    # 左边：显示分数
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (20, UI_HEIGHT // 2 - 18))
    
    # 中间：显示血量
    health_text = font.render(f"Health: {health}/3", True, (255, 0, 0))
    screen.blit(health_text, (450 - health_text.get_width() // 2, UI_HEIGHT // 2 - 18))
    
    # 右边：显示倒计时
    minutes = seconds_remaining // 60
    seconds = seconds_remaining % 60
    time_text = font.render(f"Time: {minutes:02d}:{seconds:02d}", True, (255, 255, 255))
    screen.blit(time_text, (750 - time_text.get_width(), UI_HEIGHT // 2 - 18))
    
    # 菜单图标（使用简单的白色方块）
    menu_color = (255, 255, 255)
    pygame.draw.rect(screen, menu_color, [850, 25, 30, 5])
    pygame.draw.rect(screen, menu_color, [850, 35, 30, 5])
    pygame.draw.rect(screen, menu_color, [850, 45, 30, 5])

    # 8. 更新屏幕显示
    pygame.display.flip()

    # 9. 控制帧率
    clock.tick(70)

# 10. 退出游戏
pygame.quit()
sys.exit()
