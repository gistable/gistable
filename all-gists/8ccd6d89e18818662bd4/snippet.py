#!/usr/bin/env python3
import sys
import struct

if len(sys.argv) < 2:
  print("Usage: aac_parer.py <target.aac>")
  exit()

aacfile = open(sys.argv[1], 'rb')
frame_no = 1

while True:
  data = aacfile.read(7)
  if not data:
    exit()
  hdr = struct.unpack(">7B", data)

  # parse adts_fixed_header()
  syncword = (hdr[0] << 4) | (hdr[1] >> 4)  # bslbf(12)
  if syncword != 0b111111111111:
    print("Invalid `syncword` for {} frame".format(frame_no))
    exit()
  ID                 = (hdr[1] >> 3) & 0b1    # bslbf(1)
  layer              = (hdr[1] >> 1) & 0b11   # uimsbf(2)
  protection_absent  = (hdr[1]     ) & 0b1    # bslbf(1)
  profile            = (hdr[2] >> 6) & 0b11   # uimsbf(2)
  sampling_freq_idx  = (hdr[2] >> 2) & 0b1111 # uimsbf(4)
  private_bit        = (hdr[2] >> 1) & 0b1    # bslbf(1)
  channel_cfg        = ((hdr[2] & 0b1) << 2) | (hdr[3] >> 6)  # uimsbf(3)
  original_copy      = (hdr[3] >> 5) & 0b1    # bslbf(1)
  home               = (hdr[3] >> 4) & 0b1    # bslbf(1)
  # parse adts_variable_header()
  copyright_id_bit   = (hdr[3] >> 3) & 0b1    # bslbf(1)
  copyright_id_start = (hdr[3] >> 2) & 0b1    # bslbf(1)
  frame_length       = ((hdr[3] & 0b11) << 11) | (hdr[4] << 3) | (hdr[5] >> 5)  # bslbf(13)
  adts_buf_fullness  = ((hdr[5] & 0b11111) << 6) | (hdr[6] >> 2)  # bslbf(11)
  num_rawdata_blocks = (hdr[6]     ) & 0b11   # uimsbf(2)

  crc_check = 0
  size = frame_length - 7
  if num_rawdata_blocks == 0:
    # adts_error_check()
    if protection_absent == 0:
      crc_check = struct.unpack(">H", aacfile.read(2))[0]  # rpchof(16)
      size -= 2
    # raw_data_block()
    aacfile.read(size)
  else:
    # adts_header_error_check()
    if protection_absent == 0:
      crc_check = struct.unpack(">H", aacfile.read(2))[0]  # rpchof(16)
      size -= (2 * num_rawdata_blocks) + 2
    # {raw_data_block() + adts_raw_data_block_error_check()} x N
    aacfile.read(size)

  if frame_no == 1:
    # dump adts_fixed_header()
    print("adts_fixed_header():")
    print("ID={}".format(ID))
    print("layer={:02b}".format(layer))
    print("protection_absent={}".format(protection_absent))
    print("profile={}".format(profile))
    print("sampling_frequency_index=0x{:x}".format(sampling_freq_idx))
    print("private_bit={}".format(private_bit))
    print("channel_configuration={}".format(channel_cfg))
    print("original/copy={}".format(original_copy))
    print("home={}".format(home))
    print("adts_variable_header():")
  # dump adts_variable_header()
  print("#{},{},{},{},{},{},0x{:04x}".format(
    frame_no, copyright_id_bit, copyright_id_start, frame_length, adts_buf_fullness, num_rawdata_blocks, crc_check))
  frame_no += 1
