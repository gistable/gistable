#!/usr/bin/python
#-*-coding:utf-8 -*-
# E-HentaiのページURLをもとにギャラリー画像を取得するスクリプト


# パッケージのインポート
import os
import sys
import re
import urllib2
import codecs
import StringIO
import gzip
import time
from datetime import datetime
import os.path
from os.path import join, getsize


# 関数定義
# 指定したURLのHTMLページの内容をダウンロードする関数
def html_download(html_url):

	# ダウンロード間隔を開けるため一時停止
	time.sleep(2)		# 2秒間一時停止する

	# 例外処理
	# HTMLページを取得しリストに格納
	# 失敗時にはエラーメッセージのみ返す
	try:
		# HTTPリクエスト
		req = urllib2.Request(html_url, headers={'User-Agent' : 'Magic Browser', 'Accept-encoding' : 'gzip'})
		con = urllib2.urlopen(req)
		html = con.read()
		
		# body部分がgzip化されている場合の処理
		if con.info().get('Content-Encoding') == 'gzip':
			data = StringIO.StringIO(html)
			gzipper = gzip.GzipFile(fileobj=data)
			html = gzipper.read()

	except urllib2.URLError, e:
		sys.exit("Error! : URLエラーにより画像を取得できません")
	except urllib2.HTTPError, e:
		sys.exit("Error! : HTTPエラーにより画像を取得できません")

	# 戻り値
	return html

	

# URLを元に画像をダウンロードする関数
def image_download(img_url, output):

	# ダウンロード間隔を開けるため一時停止
	time.sleep(4)		# 4秒間一時停止する

	# HTTPリクエスト
	opener = urllib2.build_opener()
	req = urllib2.Request(img_url, headers={'User-Agent' : 'Magic Browser', 'Accept-encoding' : 'gzip'})

	# もし同名の画像ファイルが存在するならば、上書きは行わない
	if not os.path.exists(output):
		img_file = open(output, 'wb')
		img_file.write(opener.open(req).read())
		img_file.close()

	# 戻り値
	return True



# HTMLタイトルを取得する関数
def get_page_title(html):

	# 変数
	title = ""							# Webページのタイトル

	# 正規表現
	pat_title = re.compile('<title>(.*?)</title>')		# ページタイトルを抜き出す

	# ページタイトルを取得
	m = pat_title.search(html)
	
	# タイトルが取得できなかった場合は日時をタイトルとする
	if not m is None:
		title = m.group(1)
	else:
		d = datetime.now()
		title = d.strftime('%Y%m%d%H%M%S')

	# ページタイトル内のスラッシュを変換する
	title = title.replace("/", "_")

	# 戻り値
	return title



# E-Hentaiギャラリーの最初の画像ページURLを取得する関数
def get_first_img_page_url(html_url):

	# 変数
	gallary_top_url    = ""		# ギャラリートップのURL
	first_img_page_url = ""		# 最初の画像ページURL

	# 正規表現
	pat_gallery         = re.compile('^(http://g.e-hentai.org/g/.*/).*$')								# ギャラリーのURLであるか / URLからギャラリーを抜き出す
	pat_img_page        = re.compile('^http://g.e-hentai.org/s/.+/.*$')								# 画像ページのURLであるか
	pat_gallary_top     = re.compile('<a href="(http[s]*?://g.e-hentai.org/g/.*)".*?>')						# HTMLからギャラリートップのURLを抜き出す	
	pat_first_img_page1 = re.compile('<div id="gdt"><div class="gdtm".*?>(?=<div.*?>)*<a href="(.*?)"><img.*alt="[0]*1"')	# ギャラリーのトップページのHTMLから最初の画像ページURLを抜き出す
	pat_first_img_page2 = re.compile('<div class="sn"><a onclick=".*?" href="(.*?)".*?>')					# 画像ページのHTMLから最初の画像ページURLを抜き出す

	# 入力したE-Hentaiのページの判定
	m1 = pat_gallery.search(html_url)
	m2 = pat_img_page.search(html_url)

	# 途中からのダウンロード再開の場合
	if os.path.exists("htmlurl.dat"):
		for i in open("htmlurl.dat"):
			return i

	# 入力URLがギャラリーページの場合
	if not m1 is None:
		# ギャラリーのトップページURLを取得
		gallery_top_url = m1.group(1)

		# 最初の画像ページURLを取得
		m3 = pat_first_img_page1.search(html_download(gallery_top_url))
		first_img_page_url = m3.group(1)

	# 入力URLが画像ページの場合
	elif not m2 is None:
		# 最初の画像のURLを取得
		m4 = pat_first_img_page2.search(html_download(html_url))
		first_img_page_url = m4.group(1)

	# どれにもあてはまらない場合
	else:
		sys.exit("Error! : 入力URLはE-Hentaiのギャラリーページあるいは画像ページではありません。")

	# 戻り値
	return first_img_page_url



# E-Hentaiギャラリーの最初の画像ページURLから全画像のURLのリストを取得する関数
def get_img_url_list(first_img_page_url, count_limit):
	
	# 変数
	count = 0						# リスト要素の番号
	current_page_url = first_img_page_url		# 現在のg.e-hentai.orgページのURL
	lofi_page_url    = ""				# lofi.e-hentai.orgページのURL
	img_url = []						# 画像ファイルのURLを格納するリスト

	# 正規表現
	pat_img  = re.compile('<img id="img" src="(.*?)".*?>')				# g.e-hentai.orgの画像URLを抜き出す
	pat_next = re.compile('<a id="next" onclick=".*?" href="(.*?)".*?>')		# 次ページURLを抜き出す


	# g.e-hentai.orgの画像URL一覧を一時ファイルから読み込み
	line = ""
	prev = ""
	if os.path.exists("imgurl.dat"):
		for line in open("imgurl.dat"):
			line = line.rstrip()
			if line == "Getting URLs list Done":
				# URLが取得済みなら終了
				return img_url
			else:
				# 文字列が空文字列や改行文字でなく、前と重複していなければリストに追加
				if line != "" and line != "\n" and line != prev:
					img_url.append(line)
			# 前ページのURL
			prev = line


	# 現在ページのURLを一時ファイルから読み込み
	line = ""
	prev = ""
	if os.path.exists("htmlurl.dat"):
		for line in open("htmlurl.dat"):
			# ファイルの文字列をURLとして読み込む
			if line != "" and line != "\n":
				current_page_url = line
				# 文字列が前と重複していなければカウント
				if line != prev:
					count += 1
			# 前ページのURL
			prev = line


	# 変数countが0ならば値を1にする
	if count == 0:
		count = 1

	# ループで繰り返しURLを取得
	while True:

		# 現在のg.e-hentai.orgページのHTMLの内容
		html = html_download(current_page_url)

		# マッチング
		# 現在のHTMLページ内から画像のURLを抜き出す
		m1 = pat_img.search(html)
		if not m1 is None:
			# 一時変数にURLを格納する
			tmp = m1.group(1)

			# URL文字列中の"&amp;"を変換する
			tmp = tmp.replace("&amp;", "&")

			# リストに要素を追加
			img_url.append(tmp)

			# URLの出力
			print "%d : %s"%(count, tmp)

			# カウントの増加
			count += 1

			# ダウンロード途中の状況を一時ファイルに書き出す
			f = open("imgurl.dat", "a")
			f.write(m1.group(1) + "\n")
			f.close()


		# HTMLページを取得したURLの一覧をファイルに書き込む
		f = open("htmlurl.dat", "a")
		f.write(current_page_url + "\n")
		f.close()


		# 現在のHTMLページ内から次ページへのリンクを抜き出す
		m2 = pat_next.search(html)
		if not m2 is None:
			# URLを取得
			# 同じURLが現れた場合には終了
			if not current_page_url == m2.group(1):
				current_page_url = m2.group(1)
			else:
				break
		else:
			# リンクが無い場合は終了
			break


		# countの値が制限を越えた場合は終了
		if count > count_limit:
			break


	# 一時ファイルにURL取得終了の文字列を追加する
	f = open("imgurl.dat", "a")
	f.write("Getting URLs list Done")
	f.close()

	# リストの重複をなくす
	#img_url = list(set(img_url))

	# 戻り値
	return img_url



# 画像ファイル名の命名
def get_img_file_name(dl_path, name, ext, count, name_mode):

	# 変数
	output = ""

	# ファイルの命名モードによってファイル名を決定
	if name_mode == "number":
		output = "%s/%03d.%s"%(dl_path, count, ext)
	elif name_mode == "filename":
		output = "%s/%s.%s"%(dl_path, name, ext)
	elif name_mode == "date":
		d = datetime.now()
		output = d.strftime('%Y%m%d%H%M%S')

	# 戻り値
	return output



# 画像ファイルがダウンロードを許可された画像フォーマットかどうか判定する関数
def validate_img_format(file_ext, img_format):

	# 変数
	result = False		# 許可されているかどうかのフラグ

	# 画像フォーマットの判定
	for i in img_format:
		# 比較
		if i == file_ext:
			result = True
			break

	# 戻り値
	return result



# 画像サイズが0kbのものを削除する
def remove_zero_file(file):

	# 文字コードの変換
	file = file.decode('utf-8')

	# 変数
	filesize = os.path.getsize(file)	# 画像のサイズ

	# 画像を削除する
	if filesize < 10:
		os.remove(file)



# HTMLページの取得・タグの抜き出しの処理後、画像収集を行う
def start_collect_image(html_url, img_path, start_pos, finish_pos, count_limit, name_mode, img_format):
	
	# 変数
	count              = 0						# ファイル番号
	title              = ""						# Webページのタイトル
	first_img_page_url = ""						# 最初の画像ページのURL
	tmp_buffer         = ""						# ダウンロード情報を格納するバッファ
	img_url            = []						# 画像URLのリスト(初期値は空リスト)

	# 正規表現
	pat_img_name = re.compile('.+/(.+)\.(.*)')			# 画像ファイル名と拡張子を取得する


	# 画像ダウンロードの開始地点の値が1よりも小さければ1にする
	if start_pos < 1:
		start_pos = 1

	# URLが空かどうかの確認
	if html_url == "":
		# エラーメッセージ
		sys.exit("Error! : URLが入力されていません")
	elif html_url == "resume":
		# ダウンロード処理再開のメッセージ
		print "画像ダウンロードを再開します..."
	else:
		# URLが有効であるかどうかの確認
		if re.match('^http[s]*://', html_url) is None:
			sys.exit("Error! : 有効なURLではありません")
		# e-hentaiのURLであるかどうかの確認
		elif re.match('^http[s]*://g.e-hentai.org/', html_url) is None:
			sys.exit("Error! : E-hentai GallaryのURLではありません")
		# ダウンロード処理開始のメッセージ
		print "画像ダウンロードを開始します..."

	# E-hentaiギャラリーの最初の画像ページURLを取得する
	first_img_page_url = get_first_img_page_url(html_url)

	# ページタイトルを取得
	title = get_page_title(html_download(first_img_page_url))

	# ページタイトルと同名のディレクトリを作成する
	dl_path = "%s/%s"%(img_path, title)	# 画像をダウンロードするディレクトリ名
	if not os.path.exists(dl_path):
		os.makedirs(dl_path)
	os.chmod(dl_path, 0777)			# ディレクトリ権限の変更

	#  画像URLのリストを取得する
	img_url = get_img_url_list(first_img_page_url, count_limit)

	# 画像URLのリストから実際の画像をダウンロードする
	for i in img_url:
		# 変数countの値のインクリメント
		count += 1

		# 画像がダウンロード範囲内かどうか判定
		if count < start_pos:
			continue
		elif count > finish_pos:
			break

		# 画像ファイル名を決定
		m = pat_img_name.search(i)
		if not m is None:
			# 画像ファイル名と拡張子を取得する
			name = m.group(1)
			ext  = m.group(2)

			# ファイルの命名モードによってファイル名を決定
			output = get_img_file_name(dl_path, name, ext, count, name_mode)

			# すでに画像ファイルが存在する場合は次へ
			if os.path.exists(output):
				continue

			# 許可されていないファイル形式ならば次へ
			if not validate_img_format(ext, img_format):
				continue

			# 画像のダウンロード
			image_download(i, output)	# ダウンロードした画像ファイルを指定パスにダウンロード
			
		else:
			# ファイル名が見つからない場合は次へ
			continue

	
	# ファイルサイズが0のものを消去する
	# 指定したパス内の全てのファイルとディレクトリを要素とするリストを返す
	files = os.listdir(img_path)
	for file in files:
		file_path = "%s/%s"%(img_path, file)
		remove_zero_file(file_path)
	
	# 戻り値
	return




# main関数
if __name__ == '__main__':

	# 変数
	html_url      = ""					# E-Hentai GalleryのURL
	img_path      = "./downloads"				# 画像のダウンロード先ディレクトリ
	count_limit   = 1000					# ダウンロードする画像の数の上限
	start_pos     = 1					# 画像ダウンロードの開始点
	finish_pos    = 1000					# 画像ダウンロードの終了点
	img_format    = ["jpg", "png", "gif", "bmp"]		# ダウンロードを許可する画像ファイル形式(拡張子)

	# 画像ファイルの命名モード
	# "number"   => ダウンロード番号を画像ファイル名とする
	# "filename" => ダウンロード時URLの画像ファイル名をそのまま流用して画像ファイル名とする
	# "date"     => ダウンロード時の時刻を画像ファイル名とする
	name_mode     = "number"			


	# 新規ダウンロードの場合
	if not os.path.exists("htmlurl.dat") and not os.path.exists("imgurl.dat"):
		# URLの入力を受け付ける
		print "E-Hentaiのギャラリー、または画像のあるURLを入力してください。"		# メッセージの出力
		html_url = raw_input("URL : ")						# ユーザの入力を受け付ける

	# 前回、ダウンロードが途中で終了している場合
	else:
		print "前回、ダウンロードが途中で終了しました。"			# メッセージの出力
		print "途中からダウンロードを再開しますか？(y/N)",
		choice_flag = False						# ユーザ入力が有効かどうかのフラグ

		# 正しい入力が得られる間でループする
		while choice_flag == False:
			# ユーザの入力を受け付ける
			choice = raw_input()										

			# ユーザの入力に応じた分岐
			# 再開する場合
			if choice == 'y' or choice == 'Y' or choice == 'yes' or choice == 'YES':
				# ファイルからダウンロードが途中で終了したURLの読み込み
				for line in open("htmlurl.dat"):
					if line != "" and line != "\n":
						html_url = line
						break

				# フラグの切り替え
				choice_flag = True

				# URLの代わりにダウンロード再開であることを通知
				html_url = "resume"

			# 再開しない場合
			elif choice == 'n' or choice == 'N' or choice == 'no' or choice == 'NO':
				# 一時ファイルを削除する
				if os.path.exists("htmlurl.dat"):
					os.remove('htmlurl.dat')
				if os.path.exists("imgurl.dat"):
					os.remove('imgurl.dat')

				# URLの入力を受け付ける
				print "E-Hentaiのギャラリー、または画像のあるURLを入力してください。"		# メッセージの出力
				html_url = raw_input("URL : ")						# ユーザの入力を受け付ける

				# フラグの切り替え
				choice_flag = True
			else:
				print "入力が正しくありません。"	


	# ダウンロード処理
	start_collect_image(html_url, img_path, start_pos, finish_pos, count_limit, name_mode, img_format)

	# 成功のメッセージを出力
	print "Success! : 画像の取得が完了しました"

	# 処理が終了したら一時ファイルを削除する
	os.remove('htmlurl.dat')
	os.remove('imgurl.dat')



