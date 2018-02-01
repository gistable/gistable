# [h] interpolated nudge dialog

'''a simple RoboFont dialog for the famous "interpolated nudge" script'''

# Interpolated Nudge for RoboFont -- Travis Kochel
# http://tktype.tumblr.com/post/15254264845/interpolated-nudge-for-robofont

# Interpolated Nudge -- Christian Robertson
# http://betatype.com/node/18

from vanilla import *

from NudgeCore import *

class interpolatedNudgeDialog(object):

    _title = "Nudge"
    _button_1 = 30
    _button_2 = 20
    _padding = 10
    _width = (_button_1 * 3) + (_padding * 2) - 2
    _height = (_button_1 * 4) + (_padding * 3) - 2

    _nudge = 10

    def __init__(self):
        self.w = FloatingWindow(
                (self._width,
                self._height),
                self._title)
        self.w._up = SquareButton(
                (self._button_1 + self._padding - 1,
                self._padding,
                self._button_1,
                self._button_1),
                "+",
                callback=self._up_callback)
        self.w._left = SquareButton(
                (self._padding,
                self._button_1 + self._padding - 1,
                self._button_1,
                self._button_1),
                "-",
                callback=self._left_callback)
        self.w._right = SquareButton(
                ((self._button_1 * 2) + self._padding - 2,
                self._button_1 + (self._padding - 1),
                self._button_1,
                self._button_1),
                "+",
                callback=self._right_callback)
        self.w._down = SquareButton(
                (self._button_1 + self._padding - 1,
                (self._button_1 * 2) + (self._padding - 2),
                self._button_1,
                self._button_1),
                "-",
                callback=self._down_callback)
        # nudge size
        self.w._nudge_value = EditText(
                (self._padding,
                (self._button_1 * 3) + (self._padding * 2) + 5,
                (self._width / 2) - (self._padding * 1.5),
                20),
                self._nudge,
                sizeStyle='small',
                readOnly=True)
        self.w._nudge_plus = SquareButton(
                (-self._padding - 20,
                (self._button_1 * 3) + (self._padding * 2) + 5,
                self._button_2,
                self._button_2),
                '+',
                sizeStyle='small',
                callback=self.nudge_plus_callback)
        self.w._nudge_minus = SquareButton(
                (-self._padding - 39,
                (self._button_1 * 3) + (self._padding * 2) + 5,
                self._button_2,
                self._button_2),
                '-',
                sizeStyle='small',
                callback=self.nudge_minus_callback)
        # open dialog
        self.w.open()

    def nudge_minus_callback(self, sender):
        _nudge = int(self.w._nudge_value.get()) - 10
        if _nudge >= 0:
            self._nudge = _nudge
            self.w._nudge_value.set(self._nudge)

    def nudge_plus_callback(self, sender):
        self._nudge = int(self.w._nudge_value.get()) + 10
        self.w._nudge_value.set(self._nudge)

    def _left_callback(self, sender):
        nudgeSelected((-self._nudge, 0))

    def _right_callback(self, sender):
        nudgeSelected((self._nudge, 0))

    def _up_callback(self, sender):
        nudgeSelected((0, self._nudge))

    def _down_callback(self, sender):
        nudgeSelected((0, -self._nudge))

# run

interpolatedNudgeDialog()
