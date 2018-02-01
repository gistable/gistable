#!/usr/bin/env python3

import glob
import json
import sys
import shutil
import os

#this might change, not sure, but probably not since 16 is a great number
HEADER_LENGTH = 16

def decrypt_image(enc_png, key, path):
	print("Decrypting %s" % enc_png)
	dec_name = os.path.splitext(os.path.basename(enc_png))[0] + ".png"
	dec_data = decrypt_generic(enc_png, key)
	dec_file = open(os.path.join(path, "dump/img", dec_name), 'wb')
	dec_file.write(dec_data)
	dec_file.close()

def decrypt_audio(enc_ogg, key, path):
	print("Decrypting %s" % enc_ogg)
	dec_name = os.path.splitext(os.path.basename(enc_ogg))[0] + ".ogg"
	dec_data = decrypt_generic(enc_ogg, key)
	dec_file = open(os.path.join(path, "dump/audio", dec_name), 'wb')
	dec_file.write(dec_data)
	dec_file.close()

def decrypt_generic(file_name, key):
	enc_data = bytearray(open(file_name, 'rb').read())
	dec_data = enc_data[16:]
	for i in range(0, HEADER_LENGTH):
		dec_data[i] ^= key[i]
	return dec_data

if __name__ == "__main__":
	if len(sys.argv) == 1:
		print("Please supply path to Game.exe(s) to unpack")
		sys.exit(1)

	for i in range(1, len(sys.argv)):
		if os.path.basename(sys.argv[i]) != 'Game.exe':
			print("Please supply path to Game.exe(s) to unpack")
			sys.exit(1)

	for i in range(1, len(sys.argv)):
		game_path = os.path.dirname(sys.argv[i])
		sysjson_p = open(os.path.join(game_path, "www/data/System.json"), 'r')
		sysjson = json.loads(sysjson_p.read())
		enc_key = sysjson['encryptionKey']
		enc_key = bytearray.fromhex(enc_key)
		has_images = sysjson['hasEncryptedImages']
		has_audio = sysjson['hasEncryptedAudio']
		sysjson_p.close()

		if os.path.exists(os.path.join(game_path, "dump")):
			shutil.rmtree(os.path.join(game_path, "dump"))

		os.mkdir(os.path.join(game_path, "dump"))
		
		if has_images:
			os.mkdir(os.path.join(game_path, "dump/img"))
			for enc_png in glob.iglob(os.path.join(game_path, "www/img/**/*.rpgmvp")):
				decrypt_image(enc_png, enc_key, game_path)
		if has_audio:
			os.mkdir(os.path.join(game_path, "dump/audio"))
			for enc_ogg in glob.iglob(os.path.join(game_path, "www/audio/**/*.rpgmvo")):
				decrypt_audio(enc_ogg, enc_key, game_path)
