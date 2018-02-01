# Copy animation crudely to a file and back

import c4d
import c4d.gui as gui
import c4d.storage as storage
import json
import urllib
import os.path
import datetime
import platform
import functools
import traceback
import contextlib
import webbrowser

REPORT_SUBJ = "Error report for C4D Aimation Export Script"
REPORT_ADDR = "jason.dixon.email@gmail.com"

EXTENSION = ".anim"
DIVIDER = "|"

SELECT_CHILDREN = 16388
assert c4d.GetCommandName(SELECT_CHILDREN) == "Select Children"

INTERPOLATION = {
    "spline": c4d.CINTERPOLATION_SPLINE,
    "linear": c4d.CINTERPOLATION_LINEAR,
    "step": c4d.CINTERPOLATION_STEP
}
INTERPOLATION.update((b, a) for a, b in INTERPOLATION.items()) # Reverse lookup

@contextlib.contextmanager
def report():
    err = None
    try:
        yield
    except Exception:
        if gui.QuestionDialog("There was an error running the script. Would you like to send a brief report?"):
            # Generate Report
            webbrowser.open("mailto:{email}?subject={subject}&body={body}".format(
                email=REPORT_ADDR,
                subject=urllib.quote(REPORT_SUBJ),
                body=urllib.quote("\n".join((
                    str(datetime.datetime.now()),
                    platform.platform(),
                    "C4D version %s" % c4d.GetC4DVersion(),
                    __file__,
                    traceback.format_exc()
                )))
            ))
        raise

def strip_namespace(name):
    return name.split("::")[-1]

def get_selection(doc):
    c4d.CallCommand(SELECT_CHILDREN)
    return doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)

def get_tracks(obj):
    name = strip_namespace(obj.GetName())
    for track in obj.GetCTracks():
        yield name + DIVIDER + track.GetName(), track
    tags = obj.GetTags()
    for tag in tags:
        tag_name = strip_namespace(tag.GetName())
        for track in tag.GetCTracks():
            yield name + DIVIDER + tag_name + DIVIDER + track.GetName(), track

def get_keys(curve):
    """ Key: [0]Time, [1]Value, [2]left_time, [3]left_value, [4]right_time, [5]right_value, [6]interpolation """
    for i in range(curve.GetKeyCount()):
        key = curve.GetKey(i)
        interpolation = INTERPOLATION[key.GetInterpolation()]
        yield pull_key(key)

def set_key(curve, key_data):
    key = curve.FindKey(c4d.BaseTime(key_data[0])) # Check for an existing keyframe
    if key:
        key = push_key(curve, key["key"], key_data)
        new = False
    else:
        key = push_key(curve, c4d.CKey(), key_data)
        new = True
    if new:
        curve.InsertKey(key)
    c4d.EventAdd()

def pull_key(key):
    return [
        key.GetTime().Get(), key.GetValue(),
        key.GetTimeLeft().Get(), key.GetValueLeft(),
        key.GetTimeRight().Get(), key.GetValueRight(),
        interpolation
        ]

def push_key(curve, key, key_data):
    key.SetTime(curve, c4d.BaseTime(key_data[0]))
    key.SetValue(curve, key_data[1])
    key.SetInterpolation(curve, INTERPOLATION[key_data[6]])
    key.SetTimeLeft(curve, c4d.BaseTime(key_data[2]))
    key.SetTimeRight(curve, c4d.BaseTime(key_data[4]))
    key.SetValueLeft(curve, key_data[3])
    key.SetValueRight(curve, key_data[5])
    return key

def offset_key(key, time=0, value=0):
    if time:
        key[0] += time
        # key[2] += time
        # key[4] += time
    if value:
        key[1] += value
        # key[3] += value
        # key[5] += value
    return key

def zero_time(data):
    times = set(c[0] for a, b in data for c in b)
    offset = min(times) * -1 # Get inverse of min time
    for name, keys in data:
        keys = [offset_key(a, time=offset) for a in keys]
        yield name, keys

def choice(*choices):
    ids = dict((c4d.FIRST_POPUP_ID + a, b) for a, b in enumerate(choices))
    menu = c4d.BaseContainer()
    for a in ids.iteritems(): menu.SetString(*a)
    ids[0] = None # If nothing is chosen
    chosen = gui.ShowPopupDialog(cd=None, bc=menu, x=c4d.MOUSEPOS, y=c4d.MOUSEPOS)
    return ids[chosen]

def save_dialog(title="Save file"):
    win = storage.SaveDialog(title=title)
    return win.decode("utf-8") if win else ""

def load_dialog(title="Load file"):
    win = storage.LoadDialog(title=title)
    return win.decode("utf-8") if win else ""

def main(doc):
    options = ["Import Animation (absolute)", "Import Animation (relative)", "Export Animation"]
    picked = choice(*options)

    if picked == options[0] or picked == options[1]: # Import
        file_path = load_dialog(title="Load Animation")
        if file_path:
            with open(file_path, "r") as f:
                data = json.load(f)
            selection = get_selection(doc)
            if not selection: return gui.MessageDialog("Nothing Selected. :(")
            curves = dict(b for a in get_selection(doc) for b in get_tracks(a))
            exists = [(a, b) for a, b in data.iteritems() if a in curves]
            if not exists: return gui.MessageDialog("Nothing selected can have animation applied. :(")

            do_offset = gui.QuestionDialog("Would you like to import your Animation starting at the current time?")
            relative = picked == options[1]
            curr_time = doc.GetTime()
            fps = doc.GetFps()

            if do_offset:
                exists = zero_time(exists) # Zero out our time so we can offset successfully
                time_offset = curr_time.Get()
            else:
                time_offset = 0

            for name, keys in exists:
                curve = curves[name].GetCurve()

                if relative:
                    print name, curve.GetValue(c4d.BaseTime(keys[0][0]), fps), keys[0][1]
                    value_offset = curve.GetValue(c4d.BaseTime(keys[0][0]), fps) - keys[0][1]
                else:
                    value_offset = 0

                for key in keys:
                    offset_key(key, time=time_offset, value=value_offset)
                    set_key(curve, key)


                # Remove existing keyframes
                # times = set(a[0] for a in keys)
                # min_, max_ = min(times), max(times)
                # existing_keys = get_keys(curve)
                # for key in existing_keys: # Remove existing keys that eat into new animation space
                #     if min_ <= key[0] <= max_:
                #         key = curve.FindKey(c4d.BaseTime(key[0]))
                #         curve.DelKey(key["idx"])


    elif picked == options[2]: # Export
        data = dict((b, list(get_keys(c.GetCurve()))) for a in get_selection(doc) for b, c in get_tracks(a))
        if not data: return gui.MessageDialog("No Animation to Export. :(")
        # zero_time(data) # Zero time
        file_path = save_dialog("Save Animation")
        if file_path:
            _, ext = os.path.splitext(file_path)
            if ext != EXTENSION:
                file_path += EXTENSION
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)
            print "Animation Exported to ", file_path

if __name__ == '__main__':
    doc = c4d.documents.GetActiveDocument()
    with report():
        main(doc)
