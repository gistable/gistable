from microbit import *

def clear_line(line):

    display.set_pixel(0, line, 0)
    display.set_pixel(1, line, 0)
    display.set_pixel(2, line, 0)
    display.set_pixel(3, line, 0)
    display.set_pixel(4, line, 0)

    return

def clear_row(row):

    display.set_pixel(row, 0, 0)
    display.set_pixel(row, 1, 0)
    display.set_pixel(row, 2, 0)
    display.set_pixel(row, 3, 0)
    display.set_pixel(row, 4, 0)

    return

time = 0
target = 1000
display_time = 0

x_sec = -1
y_sec = 0
val_sec = 4

x_sec_ten = -1
y_sec_ten = 1
val_sec_ten = 9

x_min = -1
y_min = 2
val_min = 4

x_min_ten = -1

y_min_ten = 3

val_min_ten = 9


x_hour = -1
y_hour = 4
val_hour = 4
debounce = 0

start_stop = 0


while True:


    if debounce == 0:

        if button_a.is_pressed() == True:

            debounce = 1

            sleep(100)

            start_stop = start_stop + 1
        

            if start_stop >= 2:

                start_stop = 0
        

    if debounce == 0:

        if start_stop == 0:

            if button_b.is_pressed() == True:

                debounce = 1
                sleep(100)
                start_stop = 0

                x_sec = -1
                y_sec = 0
                val_sec = 4

                x_sec_ten = -1
                y_sec_ten = 1
                val_sec_ten = 9

                x_min = -1
                y_min = 2
                val_min = 4

                x_min_ten = -1
                y_min_ten = 3
                val_min_ten = 9

                x_hour = -1
                y_hour = 4
                val_hour = 4

                display.clear()
                display.scroll("Stopwatch reset !!!", delay=100)


    if debounce == 1:

        if button_a.is_pressed() == False:

            debounce = 0
            sleep(100)        
        

    if start_stop == 1:

        
        if (running_time() - time) >= target:

            time = running_time()
            display_time = display_time + 1

            if val_sec == 4:

                x_sec = x_sec + 1

                if x_sec >= 0:

                    display.set_pixel(x_sec, y_sec, val_sec)


                if x_sec == 4:

                    x_sec = -2

                    val_sec = 9


            if val_sec == 9:
                x_sec = x_sec + 1


                if x_sec >= 0:
                    display.set_pixel(x_sec, y_sec, val_sec)

                if x_sec == 4:
                    x_sec = -1
                    val_sec = 4
                    x_sec_ten = x_sec_ten + 1 
                    clear_line(0)
                 
                    if x_sec_ten < 5:

                        display.set_pixel(x_sec_ten, y_sec_ten, val_sec_ten)

            if x_sec_ten == 5:

                x_sec_ten = -1
                clear_line(1)

                if val_min == 4:

                    x_min = x_min +1

                    if x_min >= 0:

                        display.set_pixel(x_min, y_min, val_min)
                

                    if x_min == 4:

                        x_min = -2
                        val_min = 9
            

                if val_min == 9:

                    x_min = x_min +1

                    if x_min >= 0:

                        display.set_pixel(x_min, y_min, val_min)

                    if x_min == 4:

                        x_min = -1
                        val_min = 4
                        x_min_ten = x_min_ten + 1 
                        clear_line(2)
                    

                        if x_min_ten < 5:

                            display.set_pixel(x_min_ten, y_min_ten, val_min_ten)
                              

            if x_min_ten == 5:

                x_min_ten = -1
                clear_line(3)

                if val_hour == 4:

                    x_hour = x_hour +1

                    if x_hour >= 0:

                        display.set_pixel(x_hour, y_hour, val_hour)
               

                    if x_hour == 4:

                        x_hour = -2
                        val_hour = 9
                      

                if val_hour == 9:

                    x_hour = x_hour +1

                    if x_hour >= 0:

                        display.set_pixel(x_hour, y_hour, val_hour)
              

                    if x_hour == 4:

                        x_sec = -1
                        y_sec = 0
                        val_sec = 4

                        x_sec_ten = -1
                        y_sec_ten = 1
                        val_sec_ten = 9

                        x_min = -1
                        y_min = 2
                        val_min = 4

                        x_min_ten = -1
                        y_min_ten = 3
                        val_min_ten = 9

                        x_hour = -1
                        y_hour = 4
                        val_hour = 4

                        display.clear()
                        display.scroll("Stopwatch reset !!!", delay=100)