import keyboard
import ctypes
from time import sleep
from ctypes import wintypes
from threading import Lock


# python 3.13.2

# 定义Windows API结构体
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ('dx', wintypes.LONG),
        ('dy', wintypes.LONG),
        ('mouseData', wintypes.DWORD),
        ('dwFlags', wintypes.DWORD),
        ('time', wintypes.DWORD),
        ('dwExtraInfo', ctypes.POINTER(wintypes.ULONG)),
    ]


class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = [('mi', MOUSEINPUT)]

    _anonymous_ = ('_input',)
    _fields_ = [
        ('type', wintypes.DWORD),
        ('_input', _INPUT),
    ]


'''
相当于C语言的：
typedef struct tagMOUSEINPUT()
{
    long dx;
    long dy;
    DWORD mouseData;
    DWORD dwFlags;
    DWORD time;
    ULONG_PTR dwExtraInfo;
}MOUSEINPUT;

// Windows官方定义文档：https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-mouseinput

typedef struct tarINPUT
{
    DWORD type;
    Union
    {
        struct MOUSEINPUT mi;
    };
}INPUT

// 仅仅只是按照意思转换，不能直接跑的
'''

# 配置参数
rotation_speed = 300
loop_interval = 0.01
toggle_hotkey = "f10"
exit_hotkey = "f11"

INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000


def send_mouse_input(dx, dy):
    # 构造MOUSEINPUT结构体：
    # 使用dx和dy设置相对移动量。
    # mouseData设为0（未使用滚轮或额外按键）。
    # dwFlags设为MOUSEEVENTF_MOVE（表示相对移动）。
    # time和dwExtraInfo设为默认值（系统自动处理时间戳和额外信息）。
    mouse_input = MOUSEINPUT(dx, dy, 0, MOUSEEVENTF_MOVE, 0, None)

    # 封装为INPUT结构体：
    # type设为INPUT_MOUSE，表示输入类型为鼠标事件。
    # 通过联合体_INPUT将MOUSEINPUT实例嵌入到INPUT结构体中，确保数据布局符合API要求。
    input_struct = INPUT(INPUT_MOUSE, _input=INPUT._INPUT(mi=mouse_input))

    # 调用SendInput函数：
    # 参数1表示发送一个输入事件。
    # ctypes.byref(input_struct)
    # 传递INPUT结构体的指针。
    # ctypes.sizeof(INPUT)
    # 确保正确传递结构体大小。
    ctypes.windll.user32.SendInput(1, ctypes.byref(input_struct), ctypes.sizeof(INPUT))


class RotationController:
    def __init__(self):
        self.is_rotating = False
        self.lock = Lock()
        self.running = True
        keyboard.add_hotkey(toggle_hotkey, self.toggle_rotation)
        keyboard.add_hotkey(exit_hotkey, self.safe_exit)

    def toggle_rotation(self):
        with self.lock:
            self.is_rotating = not self.is_rotating
            print(f"旋转状态: {'开启' if self.is_rotating else '关闭'}")

    def safe_exit(self):
        with self.lock:
            self.running = False
            print("正在退出...")

    def run(self):
        try:
            while self.running:
                if self.is_rotating:
                    send_mouse_input(rotation_speed, 0)
                sleep(loop_interval)
        finally:
            keyboard.unhook_all()


if __name__ == "__main__":
    print("那维莱特旋转控制脚本")
    print(f"热键配置：[{toggle_hotkey.upper()}]启用/禁用  [{exit_hotkey.upper()}]退出")

    # 请求管理员权限
    if ctypes.windll.shell32.IsUserAnAdmin() == 0:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", 'python', __file__, None, 1)
        exit()

    controller = RotationController()
    try:
        controller.run()
    except KeyboardInterrupt:
        pass
    finally:
        print("脚本已退出")
