RESET_COLOR = "\033[0m"

COLOR_CODES = {                                                                     
    "debug" : "\033[1;34m", # blue                                                  
    "info" : "\033[1;32m", # green                                                  
    "warning" : "\033[1;33m", # yellow                                              
    "error" : "\033[1;31m", # red                                                   
    "critical" : "\033[1;41m", # background red                                     
}                                                                                   

def color_msg(level, msg):                                                          
    return COLOR_CODES[level] + msg + RESET_COLOR