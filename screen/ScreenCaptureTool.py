from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton
import sys
import uuid
import mss
import mss.tools
from PIL import Image
import io
import win32clipboard


class ScreenCaptureTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.is_selecting = False
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.setWindowTitle("Screen Capture Tool")
        self.setWindowOpacity(0.3)  # 设置窗口半透明
        self.setCursor(Qt.CrossCursor)
        self.sct = mss.mss()
        self.rect = QLabel(self)
        self.rect.setGeometry(QRect())
        self.showFullScreen()

        # 创建确认和取消按钮
        self.confirm_button = QPushButton('确认截图', self)
        self.confirm_button.hide()
        self.confirm_button.clicked.connect(self.confirm_capture)

        self.cancel_button = QPushButton('取消', self)
        self.cancel_button.hide()
        self.cancel_button.clicked.connect(self.cancel_capture)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.is_selecting and not self.is_dragging:
                # 开始选择区域
                self.start_x = event.x()
                self.start_y = event.y()
                self.end_x = self.start_x
                self.end_y = self.start_y
                self.is_selecting = True
            elif self.is_dragging:
                # 记录开始拖动的位置
                self.drag_start_x = event.x()
                self.drag_start_y = event.y()

        elif event.button() == Qt.RightButton:
            # 右键取消截图
            self.cancel_capture()

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            # 更新结束坐标
            self.end_x = event.x()
            self.end_y = event.y()
            self.update()  # 触发重绘事件
        elif self.is_dragging:
            # 计算新的矩形位置
            dx = event.x() - self.drag_start_x
            dy = event.y() - self.drag_start_y
            self.start_x += dx
            self.start_y += dy
            self.end_x += dx
            self.end_y += dy
            self.drag_start_x = event.x()
            self.drag_start_y = event.y()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.is_selecting:
                # 完成选择，显示确认和取消按钮
                self.is_selecting = False
                self.is_dragging = True
                self.update_buttons()
                self.confirm_button.show()
                self.cancel_button.show()
            elif self.is_dragging:
                # 停止拖动
                self.update_buttons()

    def paintEvent(self, event):
        if self.start_x is not None and self.start_y is not None:
            painter = QPainter(self)
            painter.setPen(QPen(QColor(255, 0, 0), 2, Qt.SolidLine))
            rect = QRect(self.start_x, self.start_y, self.end_x - self.start_x, self.end_y - self.start_y)
            painter.drawRect(rect)  # 绘制矩形

    def update_buttons(self):
        # 更新按钮位置，使其跟随矩形右下方
        x2 = max(self.start_x, self.end_x)
        y2 = max(self.start_y, self.end_y)
        self.confirm_button.move(x2 - self.confirm_button.width(), y2 + 10)
        self.cancel_button.move(x2 - self.cancel_button.width() - self.confirm_button.width() - 10, y2 + 10)

    def confirm_capture(self):
        # 确认截图
        x1 = min(self.start_x, self.end_x)
        y1 = min(self.start_y, self.end_y)
        x2 = max(self.start_x, self.end_x)
        y2 = max(self.start_y, self.end_y)
        self.hide()
        self.capture_screen(x1, y1, x2, y2)
        self.destroy()

    def cancel_capture(self):
        # 取消截图，关闭窗口
        self.destroy()

    def capture_screen(self, x1, y1, x2, y2):
        # 使用mss库截图，不包含蒙版窗口
        monitor = {"top": y1, "left": x1, "width": x2 - x1, "height": y2 - y1}
        sct_img = self.sct.grab(monitor)
        # 保存图像到文件（可选）
        output = f"screenshot_{uuid.uuid4()}.png"
        print(f"({x1},{y1},{x2},{y2})-{output}")
        mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
        # 将截图转换为 PIL 图像
        img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)

        # 将图像保存到内存中的字节流
        output = io.BytesIO()
        img.save(output, format='BMP')
        data = output.getvalue()[14:]  # BMP 文件需要去除文件头部的 14 字节

        # 打开剪贴板
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()


def main():
    app = QApplication(sys.argv)
    screen_capture_tool = ScreenCaptureTool()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
