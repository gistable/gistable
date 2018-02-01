import sh
import re

evtest = sh.evtest("/dev/input/event9", _bg=True)

cur_slot = 0
slots = [0] * 10

tools = set()
slots.append(tools)

re_split = re.compile("[()]")

for line in evtest:
    if line.startswith("Event:"):
        line = line.strip()
        if "ABS_MT_SLOT" in line:
            value_part = line.split(",")[3].strip()
            value = int(value_part.split("value")[1])
            cur_slot = value
        if "BTN_" in line:
            split = line.split(",")
            value_part = split[3].strip()
            value = int(value_part.split("value")[1])
            tool = re.split(re_split, split[2])[1]
            if value == 1:
                tools.add(tool)
            else:
                tools.remove(tool)
            print(slots)

        if "ABS_MT_TRACKING_ID" in line:
            value_part = line.split(",")[3].strip()
            value = int(value_part.split("value")[1])
            if value == -1:
                if slots[cur_slot] == 1:
                    slots[cur_slot] = 0
                    print(slots)
            else:
                if slots[cur_slot] == 0:
                    slots[cur_slot] = 1
                    print(slots)
