import cv2
import os

#call visualize(QTable)  tod display the qtable
#Press space to proceed, and q to exit (Frame render pauses execution)

def write(image, output_dir="visualize", name=None, is_test_image=False):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if name is None:
        name = str(int(time.time() * 1000000)) + ".jpg"
    cv2.imwrite(os.path.join(output_dir, name), normalize(image.copy()))

def discretize(pos):
    return pos[0]*10 + pos[1]

def un_discretize(pos):
    return int(round(pos/10)), pos%10

def normalize(image,min=0,max=255):
    dst=None
    image = cv2.normalize(image.copy(),dst,min,max,cv2.NORM_MINMAX)
    return image.astype(np.uint8)

def colorize(img,scheme=cv2.COLORMAP_JET):
    img = cv2.cvtColor(normalize(img), cv2.COLOR_GRAY2BGR)
    img = cv2.applyColorMap(img,scheme)
    return img

def show(src, name="C2",pause=None,color=False):
    img = src.copy()

    if color:
        img=colorize(img)

    if pause == None:
        try:
            if eval("__IPYTHON__"): #don't pause in interactive shell
                pause=False
        except:
            pause=True #pause by default in interactive shell

    cv2.imshow(name, normalize(img))
    if pause:
        key = cv2.waitKey(0)
        if key == 113:
            exit()
            quit()

def visualize(Q):
    rows=10
    cols=10

    cell_w=30
    cell_h=30

    width=rows*cell_w
    height=rows*cell_h

    img = np.zeros((width,height))

    for i in range(Q.shape[0]):
        row, col = un_discretize(i)

        top   = row * cell_w
        bot   = top+cell_w
        left  = col * cell_h
        right = left + cell_h

        color = Q[i].max()
        direction = np.argmax(Q[i])

        img[top:bot,left:right] = color

        #draw arrow
        font = cv2.FONT_HERSHEY_SIMPLEX
        sym = {0: '^', 1: '>', 2: 'v', 3: '<', '*': '*'}
        cv2.putText(img,sym[direction],(right-cell_h+5,bot-8), font, 0.5, (1),2,cv2.CV_AA)

    show(img,color=True) #show the image 
    #write(colorize(img))  #write the image