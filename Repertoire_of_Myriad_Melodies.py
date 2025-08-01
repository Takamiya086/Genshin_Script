import pyautogui
import time

# 注意必须管理员身份运行
# 使用的是单线程的循环监控，优化的话就是开6线程，单线程循环会导致有些延迟，不能连续点

README = """
简介：
不喜欢玩原神里面的音游小游戏，但是想拿奖励怎么办，使用这个脚本就对了，非常简单

使用方法：
脚本运行后，将鼠标依次移动到6个判定点处，记录间隔为2秒，然后点击回到游戏内即可

输入y/n，决定是/否开始
"""
print(README)
while True:
    user_input = input().strip().lower()
    if user_input in ("y", "yes"):
        print("执行脚本逻辑...")
        break
    elif user_input in ("n", "no"):
        print("取消执行。")
        break
    else:
        print("输入无效，请重新输入！")

# 选择检测的六个点
POINTS = []
# 常态
NORMAL = (228, 231, 230)
# 需要点击
CLICK = (249, 207, 118)
# 需要按住
HOVER = (184, 165, 250)
# 按键映射
KEYS = ["A", "S", "D", "J", "K", "F"]

print("开始记录")
for i in range(6):
    time.sleep(2)
    pos = pyautogui.position()
    print(f"第{i+1}个点：{pos}")
    POINTS.append(pos)


# 获取单像素点的颜色
def get_color(pos: tuple[int, int, int]) -> tuple:
    x, y = pos
    return pyautogui.pixel(x, y)


# 区分颜色 判断需要做的事情
# NORMAL：不需要
# CLICK：需要点击
# HOVER：需要按住
def classify_color(input_rgb: tuple[int, int, int]) -> str:
    # 用字典映射基准，方便返回状态名
    benchmarks = {"NORMAL": NORMAL, "CLICK": CLICK, "HOVER": HOVER}

    min_dist_sq = float("inf")
    closest_state = None

    for state, (r_b, g_b, b_b) in benchmarks.items():
        # 计算距离平方
        delta_r = input_rgb[0] - r_b
        delta_g = input_rgb[1] - g_b
        delta_b = input_rgb[2] - b_b
        dist_sq = delta_r**2 + delta_g**2 + delta_b**2

        if dist_sq < min_dist_sq:
            min_dist_sq = dist_sq
            closest_state = state
    return closest_state


# 配置键盘的按键（A-S-D-J-K-L）
while True:
    x, y = pyautogui.position()
    # 安全保护 鼠标放到左上角退出 不过pyautogui有自保 也不用太在意
    if x < 100 and y < 100:
        break
    for idx, i in enumerate(POINTS):
        state = classify_color(get_color(i))
        if state == "CLICK":
            pyautogui.press(KEYS[idx])
        elif state == "HOVER":
            pyautogui.keyDown(KEYS[idx])
            time.sleep(1)
            pyautogui.keyUp(KEYS[idx])
        else:
            pass
