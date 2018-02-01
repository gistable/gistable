import traceback

def fn():
    if "psst" not in "".join(traceback.format_stack()[:-1]):
        raise ValueError("hey go away")

def call_with_comment():
    fn()  # psst let me in

def call_without_comment():
    fn()

def does_raise(target):
    try:
        target()
        return False
    except Exception:
        return True

if __name__ == '__main__':
    print does_raise(call_with_comment)     # False
    print does_raise(call_without_comment)  # True
