import datetime

class EventTimer:

    def __init__(self, name):
        self.events = []
        self.timer = None
        self.name = name

    def reset(self):
        self.timer = datetime.datetime.utcnow()
        self.events = []

    def event(self, label):
        self.events.append((label, datetime.datetime.utcnow()))

    def to_string(self):
        out = self.name + ' '
        prev_stamp_ms = 0
        for event in self.events:
            stamp = event[1] - self.timer
            stamp_ms = stamp.seconds * 1000 + stamp.microseconds / 1000
            delta_ms = stamp_ms - prev_stamp_ms
            prev_stamp_ms = stamp_ms
            out += (event[0] + ': ' + str(stamp_ms) + 'ms(' + str(delta_ms) + 'ms) ')
        return out
        
        
timer = EventTimer('Data processing')
timer.reset()
timer.event('Start')
items = load_items()
timer.event('Loaded')
preprocess_items(items)
timer.event('Preprocessed')
process_items(items)
timer.event('Processed')
save_items(items)
timer.event('Saved')
print timer.to_string()
