#!/usr/bin/python
import pygame
import re 
from numpy import int32
import ctypes
import time
w=1280
h=1024
#this is the debugfs entry for the trackpad, you can figure
#this out by watching the system log when you connect the trackpad
fd = open('/sys/kernel/debug/hid/0005:05AC:030E.0008/events','r')
screen = pygame.display.set_mode((w,h))
pygame.font.init()
font1 = pygame.font.match_font('mikachan')
mikaFont = pygame.font.Font(font1,28) 

for index in range(20000): 
    oline=fd.readline();
    line=oline.split();
    #repaint black background
    #if you move this outside the loop, you get 
    #fingerpainting-like behaviour, i.e. fingers leave tracks
    screen.fill((0,0,0))

    packets=[]
    if((len(line)<4) or (line[0]!= "report")):
        continue
    #strip out everything but digits
    reportsize=re.sub(r'\D',"",line[2])
    header=line[5:9]
    #handle the double packet message ID
    if(int(header[0],16)==0xf7):
        firstpktlength=int(header[1],16) 
        numpackets=2
        packets.append(line[7:7+firstpktlength])
        packets.append(line[firstpktlength+7:(len(line))])
    elif(int(header[0],16)==0x28):
        packets.append(line[5:(len(line))])
        numpackets=1

    if(len(packets)<=0):
        continue

    for ipkt in range(0,numpackets):
        pkt=packets[ipkt]
        data=pkt[4:len(pkt)]
        numtouches=len(data)/9;

        text1 = mikaFont.render(str(numtouches),1,(255,0,0),(0,0,0))
        screen.blit(text1,(200,200)) 
        for itouch in range(0,(numtouches)):
            color=(0,0,100)
            if(itouch%5==0):
                color=(0,0,255)
            if(itouch%5==1):
                color=(0,255,0)
            if(itouch%5==2):
                color=(255,0,0)
 tdata=data[itouch*9:(itouch+1)*9+1]
            if(len(tdata)<9):
                continue
            X=(((int(tdata[1],16)&0x1F)<<27) | (int(int(tdata[0],16)<<19)))
            Y=((((int(tdata[3],16)&0x3)<<30) | (int(tdata[2],16)<<22)|(int(tdata[1],16)<<14))>>19)
            X=(((X>>19)))
            X=ctypes.c_int32(X).value
            X=X&0x1FFF
            Y=Y&0x1FFF
            #handle 2's complement
            if(X&0x1000):
                X=X-8192
            if(Y&0x1000):
                Y=Y-8192
            #invert Y
            Y=-Y
            #push coordinates up into positive range
            #then rescale to fit inside our pygame window
            X=(X+3499)/6
            Y=(Y+2856)/6
            radius=int(tdata[6],16)&0x3f
            orientation=(int(tdata[7],16)>>2)-32
            touch_major=int(tdata[4],16)
            touch_minor=int(tdata[5],16)

            if((radius==0) or (touch_minor==0) or (touch_major==0)):
                continue
            if (radius>60):
                radius=60

            #if((int(tdata[8],16)&0xf0)==0x40): #only display fingers in drag state
            if(1):
                surface=pygame.Surface((touch_minor*2,touch_major*2))
                surface.set_colorkey((0,0,0))
                pygame.draw.ellipse(surface, color, (0,0,2*touch_minor,2*touch_major))
                surface=pygame.transform.rotate(surface,orientation)
                screen.blit(surface,(X,Y)) 
    pygame.display.flip()
fd.close
