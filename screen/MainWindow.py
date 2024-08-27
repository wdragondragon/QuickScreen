import os
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QAction, QApplication, QSystemTrayIcon, QMenu

from screen.ScreenCaptureTool import ScreenCaptureTool


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.icon = None
        self.tray_icon = None
        self.screen_capture_tool = None
        self.exit_action = None
        self.initUI()
        self.create_menus()
        self.create_tray_icon()

    def initUI(self):
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Main Window')
        self.hide()  # 启动时隐藏主窗口

    def create_menus(self):
        config_action = QAction("截图", self)
        config_action.triggered.connect(self.open_screen)
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("功能")
        file_menu.addAction(config_action)

    def open_screen(self):
        print("正在截图...")
        self.screen_capture_tool = ScreenCaptureTool()

    def create_tray_icon(self):
        # 创建系统托盘图标
        super().__init__()
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self.logger.print_log("系统托盘不可用")
            return
        path = "images/icon.png"

        if not os.path.exists(path):
            bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
            path = os.path.join(bundle_dir, path)
            if not os.path.exists(path):
                self.logger.print_log("无法找到图标")
        self.icon = QIcon(path)
        if self.icon.isNull():
            self.logger.print_log("无效的图标")
            return

        self.exit_action = QAction("退出", self)
        self.tray_icon = QSystemTrayIcon(self.icon)
        self.tray_icon.setIcon(QIcon("images/icon.png"))  # 设置托盘图标

        # 创建托盘菜单
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.exit_app)

        tray_menu = QMenu()
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def exit_app(self):
        # 退出应用程序
        QApplication.instance().quit()

    def closeEvent(self, event):
        # 重写关闭事件，防止窗口被关闭，而是隐藏窗口
        event.ignore()
        self.hide()
