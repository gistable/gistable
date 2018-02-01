import subprocess
import time


def wait(seconds):
    time.sleep(seconds)


def play_note(note='C', duration=4, delay=0):
    # requires sox to be installed
    command = (
        "play -qn synth {duration} pluck {note}"
        " fade l 0 {duration} 2 reverb"
    ).format(note=note, duration=duration)

    subprocess.Popen(command.split())

    if delay:
        wait(delay)


play_note('C', delay=0.1)
play_note('E', delay=0.1)
play_note('G')

wait(0.5)

play_note('C', delay=0.1)
play_note('F', delay=0.1)
play_note('A')
