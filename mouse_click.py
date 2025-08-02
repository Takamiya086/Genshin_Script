import pyautogui
import keyboard
import time

# 初始化设置
pyautogui.PAUSE = 0.3  # 每次点击后的间隔（秒）
is_running = False  # 连点器开关状态（默认关闭）


def toggle_running():
    """切换连点器状态（F8触发）"""
    global is_running
    is_running = not is_running
    status = "开启" if is_running else "关闭"
    print(f"连点器已{status}（F8键切换）")


# 绑定F8热键到切换函数
keyboard.add_hotkey("f8", toggle_running)

print("=== 连点器已启动 ===")
print("1. 按F8键切换连点开关")
print("2. 按Ctrl+C退出程序")

try:
    while True:
        if is_running:  # 仅当开关开启时执行点击
            pyautogui.click()
        time.sleep(0.01)  # 减少CPU占用（关键，否则会吃满CPU）
except KeyboardInterrupt:
    print("\n程序已退出")
    keyboard.unhook_all()  # 清理热键监听
