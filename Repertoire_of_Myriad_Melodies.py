import pyautogui
import time
import threading
from typing import Tuple
from pynput.keyboard import Listener

# 注意：必须以管理员身份运行！
# 优化亮点：
# 1. 解决HOVER长按导致的停止延迟（用循环检查替代固定sleep）
# 2. 增加ESC键+鼠标双停止方式（更便捷）
# 3. 完善状态提示
# 4. 降低CPU占用（合理控制循环频率）

# 问题
# 1. 开启多线程之后占用还是比较多，会造成卡顿
# 2. 没有做按住结束时间的检测，还是固定按住的时间为1.5秒，可自行修改，修改字段 GAP 即可

README = """
原神音游自动脚本 V2.0
---------------------
功能：自动识别音游判定点颜色，触发对应按键（点击/长按）
使用步骤：
1. 运行脚本，输入y开始（n取消）
2. 按提示依次移动鼠标到6个判定点（每2秒记录1个）
3. 脚本自动启动监测，游戏内开始音游即可
停止方式：
- 按ESC键（推荐）
- 将鼠标移至屏幕左上角（x<100且y<100）
"""

print(README)

# 用户确认
while True:
    user_input = input("请输入y/n开始：").strip().lower()
    if user_input in ("y", "yes"):
        break
    elif user_input in ("n", "no"):
        print("取消执行，脚本退出。")
        exit()
    else:
        print("输入无效，请重新输入！")

"""配置区"""
POINTS: list[Tuple[int, int]] = []  # 6个判定点坐标
NORMAL = (228, 231, 230)  # 常态（无需操作）
CLICK = (249, 207, 118)  # 点击（短按）
HOVER = (184, 165, 250)  # 长按
GAP = 1.5  # 长按的时间间隔
KEYS = ["A", "S", "D", "J", "K", "L"]  # 原神默认按键映射
stop_event = threading.Event()  # 全局停止信号
threads: list[threading.Thread] = []  # 线程池


def get_pixel_color(pos: Tuple[int, int]) -> Tuple[int, int, int]:
    # 获取指定坐标的RGB颜色
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


def monitor_point(index: int, pos: Tuple[int, int]):
    """单判定点的监测线程（核心优化：长按期间检查停止信号）"""
    print(f"线程[{index+1}]启动，监测点：{pos}")
    while not stop_event.is_set():
        try:
            color = get_pixel_color(pos)
            action = classify_color(color)

            if action == "CLICK":
                pyautogui.press(KEYS[index])
                # print(f"线程[{index+1}]：点击{KEYS[index]}")  # 调试用

            elif action == "HOVER":
                pyautogui.keyDown(KEYS[index])
                # print(f"线程[{index+1}]：长按{KEYS[index]}")  # 调试用
                start_time = time.time()
                # 长按期间每10ms检查一次停止信号（避免固定sleep阻塞）
                while time.time() - start_time < GAP and not stop_event.is_set():
                    time.sleep(0.01)
                pyautogui.keyUp(KEYS[index])  # 无论是否停止，都要抬键
                if stop_event.is_set():
                    break  # 收到停止信号，直接退出线程

        except Exception as e:
            print(f"线程[{index+1}]出错：{e}，即将停止所有线程")
            stop_event.set()
            break

        time.sleep(0.01)  # 控制监测频率（100次/秒）
    print(f"线程[{index+1}]已停止")


# 第一步：记录6个判定点
print("\n===== 开始记录判定点 =====")
print("提示：每2秒记录1个点，请依次移动鼠标到对应判定位置")
for i in range(6):
    print(f"\n准备记录第{i+1}个点...")
    time.sleep(2)
    pos = pyautogui.position()
    POINTS.append(pos)
    print(f"第{i+1}个点：{pos}")
print("===== 判定点记录完成 =====")


# 第二步：启动监测线程
print("\n===== 启动监测服务 =====")
for idx, pos in enumerate(POINTS):
    t = threading.Thread(target=monitor_point, args=(idx, pos), daemon=True)
    threads.append(t)
    t.start()


# 第三步：监听停止信号（ESC键+鼠标位置）
def handle_stop():
    """处理停止逻辑"""
    print("\n检测到停止信号，正在终止所有线程...")
    stop_event.set()
    for t in threads:
        t.join(timeout=1)  # 等待1秒，确保线程退出
    print("\n===== 脚本已完全停止 =====")
    exit()


# 1. 监听ESC键（推荐，更便捷）
def on_key_press(key):
    """pynput按键监听回调"""
    try:
        if key == key.esc:  # 按ESC键停止
            handle_stop()
    except AttributeError:
        pass


# 2. 监听鼠标位置（备用）
def check_mouse_position():
    """检查鼠标是否在左上角"""
    while not stop_event.is_set():
        x, y = pyautogui.position()
        if x < 100 and y < 100:
            handle_stop()
        time.sleep(0.05)  # 每50ms检查一次，降低CPU占用


# 启动停止监听
try:
    print("提示：按ESC键或移动鼠标到左上角即可停止脚本")
    # 启动ESC键监听线程
    listener = Listener(on_press=on_key_press)
    listener.start()
    # 启动鼠标位置监听线程
    mouse_thread = threading.Thread(target=check_mouse_position, daemon=True)
    mouse_thread.start()
    # 主程序挂起，等待停止信号
    listener.join()
except Exception as e:
    print(e)
    check_mouse_position()
