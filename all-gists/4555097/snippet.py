#!/usr/bin/env python                                                                                                                                           
#-*- coding:utf-8 -*-                                                                                                                                           
import MeCab

m = MeCab.Tagger("-Ochasen")
string = u"それサバンナでも同じ事言えんの？"

# MeCabでUnicode文字列を扱う場合は、一度エンコードする必要がある。                                                                                              
# この際、                                                                                                                                                      
# node = tagger.parseToNode(string.encode("utf-8"))                                                                                                             
# とすると、stringがパース中にガベコレされてしまって、                                                                                                          
# 変な挙動になる場合があるので注意。このように一度変数に代入すれば問題ない。                                                                                    
string = string.encode("utf-8")
node = m.parseToNode(string)

# ノードを順番にたどる。                                                                                                                                        
# node.surface, node.feature はstr型なので、                                                                                                                    
# この時点でunicode型に変換する方がトラブル防止のためにはいいかも。                                                                                             
while node:
    print node.surface, node.feature
    node = node.next

