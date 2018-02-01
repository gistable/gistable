#! /usr/bin/python
# -*- coding: utf-8 -*-

###############################################################################
# LIBSVM(LIBLINEAR)の学習データをコサイン正規化する．
#
# 次のコマンドで実行できる．
# 	$ python libsvm_cos-normalize.py [options]
# 		[options]
# 		-i file: 入力ファイル．省略すると35行目付近のINPUT_PATHで指定した値となる．
# 		-o file: 出力ファイル．基本は省略して構わないが，名前を指定したい時に．
#
# 入力ファイルのフォーマットはLIBSVMの学習データのフォーマットと同様．
#
# 出力ファイルはスケーリングを行った学習データのファイル．フォーマットは入力と同じ．
# デフォルトでは入力ファイルと同一ディレクトリに出力される．
#
# LIBSVM
# http://www.csie.ntu.edu.tw/~cjlin/libsvm/
##############################################################################

import argparse
import os
import sys
import numpy as np

# デフォルトの入力ファイル
INPUT_PATH = ''


def exec_argparse():
    '''
    引数をパースした結果を連想配列で返す．
    input_file: 入力ファイルパス
    output_file: 出力ファイルパス
    '''
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
        '-i', '--input_file', help='入力するファイル', default=INPUT_PATH)
    parser.add_argument('-o', '--output_file', help='出力するファイル')
    return parser.parse_args()


def cos_normalize(input_file, output_file):
    '''
    liblinear形式のファイルを読み込みコサイン正規化して出力
    '''

    # 出力ファイルが指定されていなければinput_file.outに出力
    if output_file == None:
        output_file = input_file + '.cos-normalize.scale'

    # 出力ファイルの初期化（削除）
    if os.path.exists(output_file):
        os.remove(output_file)

    # 入出力ファイルを開く
    f_input_file = open(input_file, 'r')
    f_output_file = open(output_file, "a")

    # 1行ずつ処理．
    for line in f_input_file:
        line = line.rstrip()  # 末尾の改行を削除
        field = line.split(' ')  # 半角スペースでフィールド分割
        label = field[0]  # ラベルを格納
        del field[0]  # ラベルフィールドは素性値配列に不要なので削除

        # 配列の初期化
        id_array = []  # 素性id配列
        value_array = []  # 素性値配列

        # 素性idと値を配列に格納
        for feature in field:
            field2 = feature.split(':')
            if float(field2[1]) != 0:  # 素性値0のものは省略
                id_array.append(field2[0])
                value_array.append(field2[1])

        # 素性値配列をnumpy配列に
        value_array = np.array(value_array, dtype=float)

        # コサイン正規化
        value_array = value_array / np.linalg.norm(value_array)

        # 出力
        line = []
        line.append(label)
        line.append(' ')
        for i in range(0, len(id_array)):
            line.append(id_array[i])
            line.append(':')
            line.append(str(value_array[i]))
            line.append(' ')
        line.append('\n')
        f_output_file.write(''.join(line))

        sys.stdout.write('.')

    f_output_file.close()
    f_input_file.close()


def main():
    # 引数をパースしてargsに格納
    args = exec_argparse()

    # ファイルを読み込みコサイン正規化して出力
    sys.stdout.write('normalizing ...')
    cos_normalize(args.input_file, args.output_file)
    print ' done'

    print 'Finish.'


if __name__ == "__main__":
    main()