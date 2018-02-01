# coding: utf8
'''
对于图片相似度比较有很多方法，我们这以RGB直方图为例。
我们以一种规则，使得每个图片生成一组描述的特征向量。
opencv的直方图比较函数我们可以巧妙的利用，其有若干比较规则，但只支持直方图的数据结构，我们可以将特征向量拟合成直方图的数据结构，然后使用其的相似度比较函数。
具体的数学计算方法有兴趣的可以看opencv的官方教程，这里我们期望生成百分比形式的相似度参数，所以使用CV_COMP_CORREL
 
以下是代码，以python编写
'''
import cv2.cv as cv
 
def createHist(img):
    #cv.CvtColor(img,img,cv.CV_BGR2HSV)
    b_plane = cv.CreateImage((img.width,img.height), 8, 1)
    g_plane = cv.CreateImage((img.width,img.height), 8, 1)
    r_plane = cv.CreateImage((img.width,img.height), 8, 1)
 
 
    cv.Split(img,b_plane,g_plane,r_plane,None)
    planes = [b_plane, g_plane, r_plane]
    
    bins = 4
    b_bins = bins
    g_bins = bins
    r_bins = bins
 
    hist_size = [b_bins,g_bins,r_bins]
    b_range = [0,255]
    g_range = [0,255]
    r_range = [0,255]
 
    ranges = [b_range,g_range,r_range]
    hist = cv.CreateHist(hist_size, cv.CV_HIST_ARRAY, ranges, 1)
    cv.CalcHist([cv.GetImage(i) for i in planes], hist)
    cv.NormalizeHist(hist,1)
    return hist
 
def imgcompare(image1,image2):
    img1 = cv.LoadImage(image1)
    hist1 = createHist(img1)
    img2 = cv.LoadImage(image2)
    hist2 = createHist(img2)
    return cv.CompareHist(hist1,hist2,cv.CV_COMP_CORREL)
    
print imgcompare("/Users/michael/Pictures/355.jpg","/Users/michael/Pictures/356.jpg")
print imgcompare("/Users/michael/Pictures/img_0379.jpg","/Users/michael/Pictures/img_0377.jpg")
# print imgcompare("test_19037_19037_source.jpg","19014.jpg")