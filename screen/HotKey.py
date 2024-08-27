import tkinter
from ctypes import windll
from ctypes.wintypes import MSG

import win32con
from PyQt5.QtCore import QThread, pyqtSignal
from _ctypes import byref


class HotKey(QThread):
    ShowWindow = pyqtSignal(int)

    def __init__(self):
        super(HotKey, self).__init__()
        self.main_key = 0x42

    def run(self):
        user32 = windll.user32
        while True:
            if not user32.RegisterHotKey(None, 1, win32con.MOD_SHIFT | win32con.MOD_CONTROL, self.main_key):  # alt+~
                tkinter.messagebox.showerror("错误", "全局热键注册失败。")
            try:
                msg = MSG()
                if user32.GetMessageA(byref(msg), None, 0, 0) != 0:
                    if msg.message == win32con.WM_HOTKEY:
                        if msg.wParam == win32con.MOD_ALT:
                            self.ShowWindow.emit(msg.lParam)
            finally:
                user32.UnregisterHotKey(None, 1)
