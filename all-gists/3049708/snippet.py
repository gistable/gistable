import time

class CodeTimer(object):
    def __init__(self):
        self.level = 0
        self.time = 0

    def __enter__(self):
        self.level += 1
        if self.level == 1:
            self.start_time = time.time()

    def __exit__(self, type, value, traceback):
        self.level -= 1
        if self.level == 0:
            self.time += time.time() - self.start_time

#sample code:
# timer_a = CodeTimer()
# timer_b = CodeTimer()
# def complicated_recursive_function():
#     if case_a:
#         with timer_a:
#             ...
#     else:
#         with timer_b:
#             ...
#
# complicated_recursive_function()
# print timer_a.time
# print timer_b.time

