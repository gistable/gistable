# -*- coding: utf-8 -*-
#BoF(SIFT)により一般物体認識を行うサンプルコード
#今回はイルカと象を識別
#評価用のデータセットとしてCaltech 101を使用
#see also: http://www.vision.caltech.edu/Image_Datasets/Caltech101/

import cv2
import numpy as np
from sklearn import svm
from sklearn import cross_validation

from BagOfFeatures import *

#ディレクトリ内にある画像をすべて読み込む関数
def loadImages(path):
    import os
    imagePathes=map(lambda a:os.path.join(path,a),os.listdir(path))
    images=map(cv2.imread,imagePathes)
    return(images)

#画像群からそれぞれの記述子を計算する関数。一応特徴点を検出し、その周りから抽出
def extractDescriptors(images,method):
    detector = cv2.FeatureDetector_create(method)
    extractor = cv2.DescriptorExtractor_create(method)
    keypoints=map(detector.detect,images)
    descriptors=map(lambda a,b:extractor.compute(a,b)[1],images,keypoints)
    return(descriptors)

if __name__== "__main__":
    #イルカと象のディレクトリ内にある画像を読むこむ
    images={}
    images["dolphin"]=loadImages("./101_ObjectCategories/dolphin")
    images["elephant"]=loadImages("./101_ObjectCategories/elephant")

    #それぞれの画像からSIFT記述子を計算
    features={}
    features["dolphin"]=extractDescriptors(images["dolphin"],method="SIFT")
    features["elephant"]=extractDescriptors(images["elephant"],method="SIFT")
    features["all"]=np.vstack(np.append(features["dolphin"],features["elephant"]))
    
    #正解ラベル作成
    labels=np.append(["dolphin"]*len(images["dolphin"]),["elephant"]*len(images["elephant"]))
    
    #BoFの種類を変更しながら評価
    for oneOfBoF in [BagOfFeatures,BagOfFeaturesGMM]:
        #コードブック数を15として、BoFを計算できるように学習
        bof=oneOfBoF(codebookSize=15)
        bof.train(features["all"])
        
        #各画像に対応する記述子からヒストグラムを作成
        hist={}
        hist["dolphin"]=map(lambda a:bof.makeHistogram(np.matrix(a)),features["dolphin"])
        hist["elephant"]=map(lambda a:bof.makeHistogram(np.matrix(a)),features["elephant"])
        hist["all"]=np.vstack(np.vstack([hist["dolphin"],hist["elephant"]]))
            
        #非線形SVMを使い、5-fold cross validationで平均認識率を計算
        classifier=svm.SVC()
        scores=cross_validation.cross_val_score(classifier, hist["all"], labels, cv=5)
        score=np.mean(scores)*100
        
        #認識率を表示
        print("Ave. score(%s):%f[%%]"%(oneOfBoF.__name__, score))
