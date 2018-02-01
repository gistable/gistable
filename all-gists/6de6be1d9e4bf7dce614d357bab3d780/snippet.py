'''
#  ショートカットキーを押した時、押している間、離した時に何かをするスクリプト
#  このスクリプト起動時のキー押下状態保存してそのキーの持続状態を判定している
#
# 　持続時間中に何かをするのでないのであれば、このようなスクリプトを使用するの
#　　でなく素直に2つコマンド用意し同じキーに on press / on release としてそれぞれ
#　　のコマンドを割り当てるほうが良い
#
#　　winapi 使用するので win 専用
#
#
#           maya が大変不安定になるので覚悟キめること
#
#
#  以下の実装例では
#　例えばスペースキーにこのスクリプトを割り振ったとしてスペース押している間のみ
#　『移動モード中の選択ロックを解除』し、キーを離せば 『選択ロックを施錠』する
'''

import ctypes
import time
import threading

import maya.mel as mel
import maya.cmds as cmds
##############################################################################

POLLING = 0.1  # in seconds


##############################################################################
def on_key_pressed_begin():
    # mel.eval("selectPref -xformNoSelect false;")
    cmds.selectPref(xformNoSelect=False)


def while_key_pressed():
    ''' おしてる間中一定間隔で実行される 未実装'''
    pass


def on_key_released():
    # mel.eval("selectPref -xformNoSelect true;")
    cmds.selectPref(xformNoSelect=True)


##############################################################################
def get_key_pressed(key):
    ''' https://msdn.microsoft.com/ja-jp/library/cc364583.aspx '''
    now_pressed = 0b1000000000000000
    # was_pressed = 0b0000000000000001

    return bool((ctypes.windll.user32.GetAsyncKeyState(key) & now_pressed) >> 15)


def get_key_released(key):
    return not get_key_pressed(key)


def get_keystates():
    ''' https://msdn.microsoft.com/ja-jp/library/cc364674.aspx '''

    key_states = (ctypes.c_ubyte * 256)()
    ctypes.windll.user32.GetKeyboardState(key_states)

    ks = [0 for x in range(256)]
    for i in range(len(key_states)):
        ks[i] = bool((key_states[i] & 128) >> 7)
    return ks


def get_keys_pressed():
    ks = get_keystates()
    res = []
    for i, x in enumerate(ks):
        if bool(x):
            res.append(i)

    return filter_ignore_keys(res)


def filter_ignore_keys(keycodes):
    ''' https://msdn.microsoft.com/ja-jp/library/windows/desktop/dd375731(v=vs.85).aspx

        使わないけど何故かフラグ立ってるようなキーコード除外する '''

    filtered_codes = filter(lambda n: not ( n < 8 ), keycodes)
    filtered_codes = filter(lambda n: not ( 0x0E <= n and n <= 0x0F ), keycodes)
    filtered_codes = filter(lambda n: not ( 0x13 <= n and n <= 0x1A ), keycodes)
    filtered_codes = filter(lambda n: not ( 0x3A <= n and n <= 0x40 ), keycodes)
    filtered_codes = filter(lambda n: not ( 0x88 <= n and n <= 0x8F ), keycodes)
    filtered_codes = filter(lambda n: not ( 0x90 == n ), keycodes)
    filtered_codes = filter(lambda n: not ( 0x91 == n ), keycodes)
    filtered_codes = filter(lambda n: not ( 0x92 <= n and n <= 0x9F ), keycodes)
    filtered_codes = filter(lambda n: not ( 0xA6 <= n ), keycodes)

    return filtered_codes


##############################################################################
def main_loop(*pressed_keys):
    # begin_time = 0  # 何らかの原因でリリースされない場合の保護用

    def check_press_continued(pressed_keys):

        for k in pressed_keys:
            if get_key_released(k):
                return False
        else:
            return True

    try:
        while check_press_continued(pressed_keys):
            time.sleep(POLLING)
            while_key_pressed()

    except Exception as e:
        print e

    finally:
        on_key_released()
        # pymel.mayautils.executeDeferred(on_key_released)


k = get_keys_pressed()
# pymel.mayautils.executeDeferred(on_key_pressed_begin)
on_key_pressed_begin()
t = threading.Thread(target=main_loop, args=(k))
t.start()
