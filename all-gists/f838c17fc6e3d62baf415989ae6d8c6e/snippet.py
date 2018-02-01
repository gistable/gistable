#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import os
import subprocess
import time
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import skimage
from PIL import Image
ADB_PATH = r'C:\adb\adb.exe'
PWD = os.path.dirname(__file__)
si = subprocess.STARTUPINFO()
si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
#si.wShowWindow = subprocess.SW_HIDE # default
class JUMP():
    def __init__(self):
        self.img = None
        self.update_data()
        self.update = True
        self.index = 0
        self.cor = [0, 0]
        self.update = True
        self.click_count = 0
        self.jump_speed = 1.393
        self.cor = []
    def start(self):
        self.fig = plt.figure()
        self.im = plt.imshow(self.img, animated=True)
        self.fig.canvas.mpl_connect('button_press_event', self.onClick)
        self.ani = animation.FuncAnimation(
            self.fig, self.updatefig, interval=50, blit=True)
        plt.show()
    def start_auto(self):
        self.fig = plt.figure()
        self.ax_im = plt.imshow(self.img)
        self.ax_line = plt.plot([0,0],[0,0]) 
        plt.show(block=False)
        while True:
            # 获取棋子和 board 的位置
            piece_x, piece_y, board_x, board_y = self.find_piece_and_board(
                self.img)
            ts = int(time.time())
            print(ts, piece_x, piece_y, board_x, board_y)
            self.ax_im.set_array(self.update_data())
            plt.plot([piece_x, piece_y], [board_x, board_y])
            plt.draw()
            plt.pause(0.001)
            self.jump(math.sqrt(abs(board_x - piece_x) **
                                2 + abs(board_y - piece_y) ** 2))
            time.sleep(1.5)   # 为了保证截图的时候应落稳了，多延迟一会儿
    def pull_image(self):
        subprocess.call(
            f'{ADB_PATH} shell screencap -p /sdcard/screen.png', startupinfo=si)
        subprocess.call(f'{ADB_PATH} pull /sdcard/screen.png', startupinfo=si)
        subprocess.call(
            f'{ADB_PATH} shell rm /sdcard/screen.png', startupinfo=si)
    def read_image(self, delete=True):
        self.pull_image()
        img_path = os.path.join(PWD, 'screen.png')
        with Image.open(img_path, mode='r') as img_file:
            img = np.array(img_file)
        if delete == True:
            subprocess.call(f'rm -f {img_path}', startupinfo=si)
        return img
    def jump(self, distance):
        press_time = distance * self.jump_speed
        press_time = max(press_time, 200)
        press_time = int(press_time)
        cmd = f'{ADB_PATH} shell input swipe 500 1600 500 1601 ' + \
            str(press_time)
        print(cmd)
        subprocess.call(cmd, startupinfo=si)
    def update_data(self):
        self.img = self.read_image()
        return self.img
    def updatefig(self, *args):
        if self.update:
            time.sleep(1)
            self.im.set_array(self.update_data())
            self.update = False
        return self.im,
    def find_piece_and_board(self, img):
        im = Image.fromarray(img)
        w, h = im.size
        piece_x_sum = 0
        piece_x_c = 0
        piece_y_max = 0
        board_x = 0
        board_y = 0
        for i in range(h):
            for j in range(w):
                pixel = im.getpixel((j, i))
                # 根据棋子的最低行的颜色判断，找最后一行那些点的平均值
                if (50 < pixel[0] < 60) and (53 < pixel[1] < 63) and (95 < pixel[2] < 110):
                    piece_x_sum += j
                    piece_x_c += 1
                    piece_y_max = max(i, piece_y_max)
        if not all((piece_x_sum, piece_x_c)):
            return 0, 0, 0, 0
        piece_x = piece_x_sum / piece_x_c
        # TODO: 大小根据截图的 size 来计算
        piece_y = piece_y_max - 20  # 上移棋子底盘高度的一半
        for i in range(h):
            if i < 300:
                continue
            last_pixel = im.getpixel((0, i))
            if board_x or board_y:
                break
            board_x_sum = 0
            board_x_c = 0
            for j in range(w):
                pixel = im.getpixel((j, i))
                # 修掉脑袋比下一个小格子还高的情况的 bug
                if abs(j - piece_x) < 70:
                    continue
                # 修掉圆顶的时候一条线导致的小 bug
                if abs(pixel[0] - last_pixel[0]) + abs(pixel[1] - last_pixel[1]) + abs(pixel[2] - last_pixel[2]) > 10:
                    board_x_sum += j
                    board_x_c += 1
            if board_x_sum:
                board_x = board_x_sum / board_x_c
        # 按实际的角度来算，找到接近下一个 board 中心的坐标
        board_y = piece_y + abs(board_x - piece_x) * \
            abs(1122 - 831) / abs(813 - 310)
        if not all((board_x, board_y)):
            return 0, 0, 0, 0
        return piece_x, piece_y, board_x, board_y
    def onClick(self, event):
        # next screenshot
        self.ix, self.iy = event.xdata, event.ydata
        self.coords = []
        self.coords.append((self.ix, self.iy))
        piece_x, piece_y, board_x, board_y = self.find_piece_and_board(
                self.img)
        print('now = ', self.coords)
        self.cor.append(self.coords)
        cor1 = self.cor.pop()
        cor2 = [(piece_x, piece_y)]
        distance = (cor1[0][0] - cor2[0][0])**2 + \
            (cor1[0][1] - cor2[0][1])**2
        distance = distance ** 0.5
        print('distance = ', distance)
        self.jump(distance)
        self.update = True
def main(auto=False):
    jump = JUMP()
    if auto:
        jump.start_auto()
    else:
        jump.start()
if __name__ == "__main__":
    import sys
    auto = False
    if len(sys.argv) != 1:
        auto = True
    main(auto)