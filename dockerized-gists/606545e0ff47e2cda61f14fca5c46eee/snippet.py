import os

GPIO_PATH = "/sys/class/gpio"  # The root of the GPIO directories
EXPANDER = "pcf8574a"  # This is the expander that is used on CHIP for the XIOs

def get_xio_base():
    '''
    Determines the base of the XIOs on the system by iterating through the /sys/class/gpio
    directory and looking for the expander that is used. It then looks for the 
    "base" file and returns its contents as an integer
    '''
    names = os.listdir(GPIO_PATH)
    for name in names:  # loop through child directories
        prefix = GPIO_PATH + "/" + name + "/"
        file_name = prefix + "label"
        if os.path.isfile(file_name):  # is there a label file in the directory?
            with open(file_name) as label:
                contents = label.read()
            if contents.startswith(EXPANDER):  # does label contain our expander?
                file_name = prefix + "base"
                with open(file_name) as base:  # read the sibling file named base
                    contents = base.read()
                return int(contents)  # convert result to an int

if __name__ == '__main__':
    print get_xio_base()
