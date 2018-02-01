class MaxSearch:
    def __init__(self, max_value=2**16):
        self.max_value = max_value

    # Override this method with your validity check
    def check_result(self, number):
        pass

    def scan(self, min_=0):
        max_ = self.max_value
        while True:
            pivot = min_ + (max_ - min_) / 2
            if self.check_result(pivot):
                min_ = pivot
                # We got to the end
                if max_ - min_ == 1:
                    break
            else:
                max_ = pivot
        return pivot
