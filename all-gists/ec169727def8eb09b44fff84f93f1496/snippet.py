import gremlin
import logging

left_t16000m = gremlin.input_devices.JoystickDecorator(
    name="T.16000M",
    device_id=1325664945,
    mode="Default"
)


@left_t16000m.hat(1)
def hat_management(event, vjoy):
    if event.value == (0, 1):
        vjoy[1].button[1].is_pressed = True
        vjoy[1].button[2].is_pressed = False
        vjoy[1].button[3].is_pressed = False
        vjoy[1].button[4].is_pressed = False
        gremlin.util.display_error("Error popup")
    elif event.value == (1, 0):
        vjoy[1].button[1].is_pressed = False
        vjoy[1].button[2].is_pressed = True
        vjoy[1].button[3].is_pressed = False
        vjoy[1].button[4].is_pressed = False
        logging.debug("Log message")
    elif event.value == (0, -1):
        vjoy[1].button[1].is_pressed = False
        vjoy[1].button[2].is_pressed = False
        vjoy[1].button[3].is_pressed = True
        vjoy[1].button[4].is_pressed = False
    elif event.value == (-1, 0):
        vjoy[1].button[1].is_pressed = False
        vjoy[1].button[2].is_pressed = False
        vjoy[1].button[3].is_pressed = False
        vjoy[1].button[4].is_pressed = True
    elif event.value == (0, 0):
        vjoy[1].button[1].is_pressed = False
        vjoy[1].button[2].is_pressed = False
        vjoy[1].button[3].is_pressed = False
        vjoy[1].button[4].is_pressed = False