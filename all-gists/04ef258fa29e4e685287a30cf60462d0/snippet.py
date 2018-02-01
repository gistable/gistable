#!/usr/bin/env python3

import flotilla
import time

client = flotilla.Client(
    requires={
        'one':flotilla.Matrix,
        'eight':flotilla.Number,
	'two':flotilla.Weather,
        'three':flotilla.Touch,
        'seven':flotilla.Light
        })

matrix = client.first(flotilla.Matrix)
number = client.first(flotilla.Number)
light = client.first(flotilla.Light)
weather = client.first(flotilla.Weather)
touch = client.first(flotilla.Touch)

matrix.clear()
number.clear()

def logo(name):
    if name == "temp":
        print ("temp")
        matrix.clear()
        mylistx=[0,7,1,2,3,4,5,6,1,2,5,6,1,3,4,6,1,3,4,6,1,2,5,6,1,2,3,4,5,6,0,7]
        mylisty=[0,0,1,1,1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,6,6,6,6,6,6,7,7]
        for i in range(len(mylistx)):
            x = mylistx[i]
            y = mylisty[i]
            matrix.set_pixel(x,y, True)
        matrix.update()
        time.sleep(2)
        matrix.clear()
        matrix.update()

    if name == "light":
        print ("light")
        matrix.clear()
        mylistx=[2,0,3,1,4,2,5,3,6,7,1,4,5,6,7,2,4,5,6,7,3,4,5,6,7]
        mylisty=[0,1,1,2,2,3,3,4,4,4,5,5,5,5,5,6,6,6,6,6,7,7,7,7,7]
        for i in range(len(mylistx)):
            x = mylistx[i]
            y = mylisty[i]
            matrix.set_pixel(x,y, True)
        matrix.update()
        time.sleep(2)
        matrix.clear()

    if name == "pressure":
        print ("pressure")
        matrix.clear()
        mylistx=[3,4,5,2,6,1,3,4,7,0,2,5,7,0,3,5,7,1,3,4,7,2,6,3,4,5]
        mylisty=[0,0,0,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,6,6,7,7,7]
        for i in range(len(mylistx)):
            x = mylistx[i]
            y = mylisty[i]
            matrix.set_pixel(x,y, True)
        matrix.update()
        time.sleep(2)
        matrix.clear()

    if name == "button":
        print ("button")
        matrix.clear()
        mylistx=[0,1,2,3,4,5,6,7,0,3,4,7,0,3,4,7,0,3,4,7,0,3,4,7,0,3,4,7,0,3,4,7,0,1,2,3,4,5,6,7]
        mylisty=[0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,6,6,6,6,7,7,7,7,7,7,7,7]
        for i in range(len(mylistx)):
            x = mylistx[i]
            y = mylisty[i]
            matrix.set_pixel(x,y, True)
        matrix.update()
        
def get_temp():
    for wait in range (20):
        matrix.clear()
        for y in range(8):
            matrix.set_pixel(7, y, True)
        for x in range(8):
            matrix.set_pixel(x,0, True)
        try:
            t_value = int(weather.temperature)
            print(t_value)
            number.clear()
            number.set_number(t_value)
            number.update()
            if t_value in range (0,9):
                m_l_value = 0
            if t_value in range (10,19):
                m_l_value = 1
            if t_value in range (20,28):
                m_l_value = 2
            if t_value in range (30,39):
                m_l_value = 3
            if t_value in range (40,49):
                m_l_value = 4
            if t_value in range (50,59):
                m_l_value = 5
            if t_value in range (60,69):
                m_l_value = 6
            if t_value in range (70,79):
                m_l_value = 7
            if t_value in range (80,90):
                m_l_value = 8
            print (m_l_value)
            for count in range(m_l_value):
                matrix.set_pixel(3,count+1,True)
                matrix.set_pixel(4,count+1,True)
            matrix.update()
            time.sleep(1)
        except Exception:
            pass

def get_pressure():
    for wait in range (20):
        matrix.clear()
        for y in range(8):
            matrix.set_pixel(7, y, True)
        for x in range(8):
            matrix.set_pixel(x,0, True)
       
        try:
            p_value = int(weather.pressure)
            print(p_value)
            number.clear()
            p_display=int((p_value/1000))
            print (p_display)
            number.set_number(p_display)
            number.update()
            if p_value in range (0,10000):
                m_l_value = 0
            if p_value in range (10000,19999):
                m_l_value = 1
            if p_value in range (20000,29999):
                m_l_value = 2
            if p_value in range (30000,39999):
                m_l_value = 3
            if p_value in range (40000,49999):
                m_l_value = 4
            if p_value in range (50000,59999):
                m_l_value = 5
            if p_value in range (60000,69999):
                m_l_value = 6
            if p_value in range (70000,79999):
                m_l_value = 7
            if p_value in range (80000,99999):
                m_l_value = 8
            print (m_l_value)
            for count in range(m_l_value):
                matrix.set_pixel(3,count+1,True)
                matrix.set_pixel(4,count+1,True)
            matrix.update()
        except Exception:
            pass
        time.sleep(1)

def get_light():
    for wait in range (20):
        matrix.clear()
        for y in range(8):
            matrix.set_pixel(7, y, True)
        for x in range(8):
            matrix.set_pixel(x,0, True)
        print (light.data)
        
        try:
            l_value = int(light.data[0])
            print(l_value)
            number.clear()
            number.set_number(l_value)
            number.update()
            if l_value in range (0,99):
                m_l_value = 0
            if l_value in range (100,199):
                m_l_value = 1
            if l_value in range (200,299):
                m_l_value = 2
            if l_value in range (300,399):
                m_l_value = 3
            if l_value in range (400,499):
                m_l_value = 4
            if l_value in range (500,599):
                m_l_value = 5
            if l_value in range (600,699):
                m_l_value = 6
            if l_value in range (700,799):
                m_l_value = 7
            if l_value in range (800,5000):
                m_l_value = 8
            print (m_l_value)
            for count in range(m_l_value):
                matrix.set_pixel(3,count+1,True)
                matrix.set_pixel(4,count+1,True)
            matrix.update()
            time.sleep(1)
        except Exception:
            pass




try:
    while True:
        logo("button")
        light_v = (touch.one)
        temp_v = (touch.two)
        pressure_v = (touch.three)
            
        if light_v == True:
            print ("Light Meter")
            logo("light")
            get_light()
            logo("button")

        if temp_v == True:
            print ("Temperature")
            logo("temp")
            get_temp()
            logo("button")

        if pressure_v == True:
            print ("Pressure")
            logo("pressure")
            get_pressure()
            logo("button")

    time.sleep(0.5)

except KeyboardInterrupt:
    client.stop()
    
