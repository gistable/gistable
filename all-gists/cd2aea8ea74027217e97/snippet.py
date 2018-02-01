#!/usr/bin/env python2
#
# Copyright 2013 Google, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Google Author(s): Behdad Esfahbod, Stuart Gill
#
# Adapted to convert an AppleColorEmoji.ttf by angelsl

import sys
import io
import struct
import StringIO

ligature_xml = """<?xml version="1.0" encoding="UTF-8"?>
<ttFont sfntVersion="\\x00\\x01\\x00\\x00" ttLibVersion="3.0">
  <GDEF>
    <Version value="1.0"/>
    <GlyphClassDef>
      <ClassDef glyph=".controlCR" class="1"/>
      <ClassDef glyph="NULL" class="1"/>
      <ClassDef glyph="ZWJ" class="1"/>
      <ClassDef glyph="asterisk" class="1"/>
      <ClassDef glyph="eight" class="1"/>
      <ClassDef glyph="five" class="1"/>
      <ClassDef glyph="four" class="1"/>
      <ClassDef glyph="hiddenglyph" class="1"/>
      <ClassDef glyph="nine" class="1"/>
      <ClassDef glyph="numbersign" class="1"/>
      <ClassDef glyph="one" class="1"/>
      <ClassDef glyph="seven" class="1"/>
      <ClassDef glyph="six" class="1"/>
      <ClassDef glyph="space" class="1"/>
      <ClassDef glyph="three" class="1"/>
      <ClassDef glyph="two" class="1"/>
      <ClassDef glyph="u0023_u20E3" class="2"/>
      <ClassDef glyph="u002A_u20E3" class="2"/>
      <ClassDef glyph="u0030_u20E3" class="2"/>
      <ClassDef glyph="u0031_u20E3" class="2"/>
      <ClassDef glyph="u0032_u20E3" class="2"/>
      <ClassDef glyph="u0033_u20E3" class="2"/>
      <ClassDef glyph="u0034_u20E3" class="2"/>
      <ClassDef glyph="u0035_u20E3" class="2"/>
      <ClassDef glyph="u0036_u20E3" class="2"/>
      <ClassDef glyph="u0037_u20E3" class="2"/>
      <ClassDef glyph="u0038_u20E3" class="2"/>
      <ClassDef glyph="u0039_u20E3" class="2"/>
      <ClassDef glyph="u00A9" class="1"/>
      <ClassDef glyph="u00AE" class="1"/>
      <ClassDef glyph="u1F004" class="1"/>
      <ClassDef glyph="u1F0CF" class="1"/>
      <ClassDef glyph="u1F170" class="1"/>
      <ClassDef glyph="u1F171" class="1"/>
      <ClassDef glyph="u1F17E" class="1"/>
      <ClassDef glyph="u1F17F" class="1"/>
      <ClassDef glyph="u1F18E" class="1"/>
      <ClassDef glyph="u1F191" class="1"/>
      <ClassDef glyph="u1F192" class="1"/>
      <ClassDef glyph="u1F193" class="1"/>
      <ClassDef glyph="u1F194" class="1"/>
      <ClassDef glyph="u1F195" class="1"/>
      <ClassDef glyph="u1F196" class="1"/>
      <ClassDef glyph="u1F197" class="1"/>
      <ClassDef glyph="u1F198" class="1"/>
      <ClassDef glyph="u1F199" class="1"/>
      <ClassDef glyph="u1F19A" class="1"/>
      <ClassDef glyph="u1F1E6" class="1"/>
      <ClassDef glyph="u1F1E6_u1F1E9" class="2"/>
      <ClassDef glyph="u1F1E6_u1F1EA" class="2"/>
      <ClassDef glyph="u1F1E6_u1F1EB" class="2"/>
      <ClassDef glyph="u1F1E6_u1F1EC" class="2"/>
      <ClassDef glyph="u1F1E6_u1F1EE" class="2"/>
      <ClassDef glyph="u1F1E6_u1F1F1" class="2"/>
      <ClassDef glyph="u1F1E6_u1F1F2" class="2"/>
      <ClassDef glyph="u1F1E6_u1F1F4" class="2"/>
      <ClassDef glyph="u1F1E6_u1F1F6" class="2"/>
      <ClassDef glyph="u1F1E6_u1F1F7" class="2"/>
      <ClassDef glyph="u1F1E6_u1F1F8" class="2"/>
      <ClassDef glyph="u1F1E6_u1F1F9" class="2"/>
      <ClassDef glyph="u1F1E6_u1F1FA" class="2"/>
      <ClassDef glyph="u1F1E6_u1F1FC" class="2"/>
      <ClassDef glyph="u1F1E6_u1F1FD" class="2"/>
      <ClassDef glyph="u1F1E6_u1F1FF" class="2"/>
      <ClassDef glyph="u1F1E7" class="1"/>
      <ClassDef glyph="u1F1E7_u1F1E6" class="2"/>
      <ClassDef glyph="u1F1E7_u1F1E7" class="2"/>
      <ClassDef glyph="u1F1E7_u1F1E9" class="2"/>
      <ClassDef glyph="u1F1E7_u1F1EA" class="2"/>
      <ClassDef glyph="u1F1E7_u1F1EB" class="2"/>
      <ClassDef glyph="u1F1E7_u1F1EC" class="2"/>
      <ClassDef glyph="u1F1E7_u1F1ED" class="2"/>
      <ClassDef glyph="u1F1E7_u1F1EE" class="2"/>
      <ClassDef glyph="u1F1E7_u1F1EF" class="2"/>
      <ClassDef glyph="u1F1E7_u1F1F1" class="2"/>
      <ClassDef glyph="u1F1E7_u1F1F2" class="2"/>
      <ClassDef glyph="u1F1E7_u1F1F3" class="2"/>
      <ClassDef glyph="u1F1E7_u1F1F4" class="2"/>
      <ClassDef glyph="u1F1E7_u1F1F6" class="2"/>
      <ClassDef glyph="u1F1E7_u1F1F7" class="2"/>
      <ClassDef glyph="u1F1E7_u1F1F8" class="2"/>
      <ClassDef glyph="u1F1E7_u1F1F9" class="2"/>
      <ClassDef glyph="u1F1E7_u1F1FC" class="2"/>
      <ClassDef glyph="u1F1E7_u1F1FE" class="2"/>
      <ClassDef glyph="u1F1E7_u1F1FF" class="2"/>
      <ClassDef glyph="u1F1E8" class="1"/>
      <ClassDef glyph="u1F1E8_u1F1E6" class="2"/>
      <ClassDef glyph="u1F1E8_u1F1E8" class="2"/>
      <ClassDef glyph="u1F1E8_u1F1E9" class="2"/>
      <ClassDef glyph="u1F1E8_u1F1EB" class="2"/>
      <ClassDef glyph="u1F1E8_u1F1EC" class="2"/>
      <ClassDef glyph="u1F1E8_u1F1ED" class="2"/>
      <ClassDef glyph="u1F1E8_u1F1EE" class="2"/>
      <ClassDef glyph="u1F1E8_u1F1F0" class="2"/>
      <ClassDef glyph="u1F1E8_u1F1F1" class="2"/>
      <ClassDef glyph="u1F1E8_u1F1F2" class="2"/>
      <ClassDef glyph="u1F1E8_u1F1F3" class="2"/>
      <ClassDef glyph="u1F1E8_u1F1F4" class="2"/>
      <ClassDef glyph="u1F1E8_u1F1F7" class="2"/>
      <ClassDef glyph="u1F1E8_u1F1FA" class="2"/>
      <ClassDef glyph="u1F1E8_u1F1FB" class="2"/>
      <ClassDef glyph="u1F1E8_u1F1FC" class="2"/>
      <ClassDef glyph="u1F1E8_u1F1FD" class="2"/>
      <ClassDef glyph="u1F1E8_u1F1FE" class="2"/>
      <ClassDef glyph="u1F1E8_u1F1FF" class="2"/>
      <ClassDef glyph="u1F1E9" class="1"/>
      <ClassDef glyph="u1F1E9_u1F1EA" class="2"/>
      <ClassDef glyph="u1F1E9_u1F1EF" class="2"/>
      <ClassDef glyph="u1F1E9_u1F1F0" class="2"/>
      <ClassDef glyph="u1F1E9_u1F1F2" class="2"/>
      <ClassDef glyph="u1F1E9_u1F1F4" class="2"/>
      <ClassDef glyph="u1F1E9_u1F1FF" class="2"/>
      <ClassDef glyph="u1F1EA" class="1"/>
      <ClassDef glyph="u1F1EA_u1F1E8" class="2"/>
      <ClassDef glyph="u1F1EA_u1F1EA" class="2"/>
      <ClassDef glyph="u1F1EA_u1F1EC" class="2"/>
      <ClassDef glyph="u1F1EA_u1F1ED" class="2"/>
      <ClassDef glyph="u1F1EA_u1F1F7" class="2"/>
      <ClassDef glyph="u1F1EA_u1F1F8" class="2"/>
      <ClassDef glyph="u1F1EA_u1F1F9" class="2"/>
      <ClassDef glyph="u1F1EA_u1F1FA" class="2"/>
      <ClassDef glyph="u1F1EB" class="1"/>
      <ClassDef glyph="u1F1EB_u1F1EE" class="2"/>
      <ClassDef glyph="u1F1EB_u1F1EF" class="2"/>
      <ClassDef glyph="u1F1EB_u1F1F0" class="2"/>
      <ClassDef glyph="u1F1EB_u1F1F2" class="2"/>
      <ClassDef glyph="u1F1EB_u1F1F4" class="2"/>
      <ClassDef glyph="u1F1EB_u1F1F7" class="2"/>
      <ClassDef glyph="u1F1EC" class="1"/>
      <ClassDef glyph="u1F1EC_u1F1E6" class="2"/>
      <ClassDef glyph="u1F1EC_u1F1E7" class="2"/>
      <ClassDef glyph="u1F1EC_u1F1E9" class="2"/>
      <ClassDef glyph="u1F1EC_u1F1EA" class="2"/>
      <ClassDef glyph="u1F1EC_u1F1EB" class="2"/>
      <ClassDef glyph="u1F1EC_u1F1EC" class="2"/>
      <ClassDef glyph="u1F1EC_u1F1ED" class="2"/>
      <ClassDef glyph="u1F1EC_u1F1EE" class="2"/>
      <ClassDef glyph="u1F1EC_u1F1F1" class="2"/>
      <ClassDef glyph="u1F1EC_u1F1F2" class="2"/>
      <ClassDef glyph="u1F1EC_u1F1F3" class="2"/>
      <ClassDef glyph="u1F1EC_u1F1F5" class="2"/>
      <ClassDef glyph="u1F1EC_u1F1F6" class="2"/>
      <ClassDef glyph="u1F1EC_u1F1F7" class="2"/>
      <ClassDef glyph="u1F1EC_u1F1F8" class="2"/>
      <ClassDef glyph="u1F1EC_u1F1F9" class="2"/>
      <ClassDef glyph="u1F1EC_u1F1FA" class="2"/>
      <ClassDef glyph="u1F1EC_u1F1FC" class="2"/>
      <ClassDef glyph="u1F1EC_u1F1FE" class="2"/>
      <ClassDef glyph="u1F1ED" class="1"/>
      <ClassDef glyph="u1F1ED_u1F1F0" class="2"/>
      <ClassDef glyph="u1F1ED_u1F1F3" class="2"/>
      <ClassDef glyph="u1F1ED_u1F1F7" class="2"/>
      <ClassDef glyph="u1F1ED_u1F1F9" class="2"/>
      <ClassDef glyph="u1F1ED_u1F1FA" class="2"/>
      <ClassDef glyph="u1F1EE" class="1"/>
      <ClassDef glyph="u1F1EE_u1F1E8" class="2"/>
      <ClassDef glyph="u1F1EE_u1F1E9" class="2"/>
      <ClassDef glyph="u1F1EE_u1F1EA" class="2"/>
      <ClassDef glyph="u1F1EE_u1F1F1" class="2"/>
      <ClassDef glyph="u1F1EE_u1F1F2" class="2"/>
      <ClassDef glyph="u1F1EE_u1F1F3" class="2"/>
      <ClassDef glyph="u1F1EE_u1F1F4" class="2"/>
      <ClassDef glyph="u1F1EE_u1F1F6" class="2"/>
      <ClassDef glyph="u1F1EE_u1F1F7" class="2"/>
      <ClassDef glyph="u1F1EE_u1F1F8" class="2"/>
      <ClassDef glyph="u1F1EE_u1F1F9" class="2"/>
      <ClassDef glyph="u1F1EF" class="1"/>
      <ClassDef glyph="u1F1EF_u1F1EA" class="2"/>
      <ClassDef glyph="u1F1EF_u1F1F2" class="2"/>
      <ClassDef glyph="u1F1EF_u1F1F4" class="2"/>
      <ClassDef glyph="u1F1EF_u1F1F5" class="2"/>
      <ClassDef glyph="u1F1F0" class="1"/>
      <ClassDef glyph="u1F1F0_u1F1EA" class="2"/>
      <ClassDef glyph="u1F1F0_u1F1EC" class="2"/>
      <ClassDef glyph="u1F1F0_u1F1ED" class="2"/>
      <ClassDef glyph="u1F1F0_u1F1EE" class="2"/>
      <ClassDef glyph="u1F1F0_u1F1F2" class="2"/>
      <ClassDef glyph="u1F1F0_u1F1F3" class="2"/>
      <ClassDef glyph="u1F1F0_u1F1F5" class="2"/>
      <ClassDef glyph="u1F1F0_u1F1F7" class="2"/>
      <ClassDef glyph="u1F1F0_u1F1FC" class="2"/>
      <ClassDef glyph="u1F1F0_u1F1FE" class="2"/>
      <ClassDef glyph="u1F1F0_u1F1FF" class="2"/>
      <ClassDef glyph="u1F1F1" class="1"/>
      <ClassDef glyph="u1F1F1_u1F1E6" class="2"/>
      <ClassDef glyph="u1F1F1_u1F1E7" class="2"/>
      <ClassDef glyph="u1F1F1_u1F1E8" class="2"/>
      <ClassDef glyph="u1F1F1_u1F1EE" class="2"/>
      <ClassDef glyph="u1F1F1_u1F1F0" class="2"/>
      <ClassDef glyph="u1F1F1_u1F1F7" class="2"/>
      <ClassDef glyph="u1F1F1_u1F1F8" class="2"/>
      <ClassDef glyph="u1F1F1_u1F1F9" class="2"/>
      <ClassDef glyph="u1F1F1_u1F1FA" class="2"/>
      <ClassDef glyph="u1F1F1_u1F1FB" class="2"/>
      <ClassDef glyph="u1F1F1_u1F1FE" class="2"/>
      <ClassDef glyph="u1F1F2" class="1"/>
      <ClassDef glyph="u1F1F2_u1F1E6" class="2"/>
      <ClassDef glyph="u1F1F2_u1F1E8" class="2"/>
      <ClassDef glyph="u1F1F2_u1F1E9" class="2"/>
      <ClassDef glyph="u1F1F2_u1F1EA" class="2"/>
      <ClassDef glyph="u1F1F2_u1F1EC" class="2"/>
      <ClassDef glyph="u1F1F2_u1F1ED" class="2"/>
      <ClassDef glyph="u1F1F2_u1F1F0" class="2"/>
      <ClassDef glyph="u1F1F2_u1F1F1" class="2"/>
      <ClassDef glyph="u1F1F2_u1F1F2" class="2"/>
      <ClassDef glyph="u1F1F2_u1F1F3" class="2"/>
      <ClassDef glyph="u1F1F2_u1F1F4" class="2"/>
      <ClassDef glyph="u1F1F2_u1F1F5" class="2"/>
      <ClassDef glyph="u1F1F2_u1F1F6" class="2"/>
      <ClassDef glyph="u1F1F2_u1F1F7" class="2"/>
      <ClassDef glyph="u1F1F2_u1F1F8" class="2"/>
      <ClassDef glyph="u1F1F2_u1F1F9" class="2"/>
      <ClassDef glyph="u1F1F2_u1F1FA" class="2"/>
      <ClassDef glyph="u1F1F2_u1F1FB" class="2"/>
      <ClassDef glyph="u1F1F2_u1F1FC" class="2"/>
      <ClassDef glyph="u1F1F2_u1F1FD" class="2"/>
      <ClassDef glyph="u1F1F2_u1F1FE" class="2"/>
      <ClassDef glyph="u1F1F2_u1F1FF" class="2"/>
      <ClassDef glyph="u1F1F3" class="1"/>
      <ClassDef glyph="u1F1F3_u1F1E6" class="2"/>
      <ClassDef glyph="u1F1F3_u1F1E8" class="2"/>
      <ClassDef glyph="u1F1F3_u1F1EA" class="2"/>
      <ClassDef glyph="u1F1F3_u1F1EB" class="2"/>
      <ClassDef glyph="u1F1F3_u1F1EC" class="2"/>
      <ClassDef glyph="u1F1F3_u1F1EE" class="2"/>
      <ClassDef glyph="u1F1F3_u1F1F1" class="2"/>
      <ClassDef glyph="u1F1F3_u1F1F4" class="2"/>
      <ClassDef glyph="u1F1F3_u1F1F5" class="2"/>
      <ClassDef glyph="u1F1F3_u1F1F7" class="2"/>
      <ClassDef glyph="u1F1F3_u1F1FA" class="2"/>
      <ClassDef glyph="u1F1F3_u1F1FF" class="2"/>
      <ClassDef glyph="u1F1F4" class="1"/>
      <ClassDef glyph="u1F1F4_u1F1F2" class="2"/>
      <ClassDef glyph="u1F1F5" class="1"/>
      <ClassDef glyph="u1F1F5_u1F1E6" class="2"/>
      <ClassDef glyph="u1F1F5_u1F1EA" class="2"/>
      <ClassDef glyph="u1F1F5_u1F1EB" class="2"/>
      <ClassDef glyph="u1F1F5_u1F1EC" class="2"/>
      <ClassDef glyph="u1F1F5_u1F1ED" class="2"/>
      <ClassDef glyph="u1F1F5_u1F1F0" class="2"/>
      <ClassDef glyph="u1F1F5_u1F1F1" class="2"/>
      <ClassDef glyph="u1F1F5_u1F1F2" class="2"/>
      <ClassDef glyph="u1F1F5_u1F1F3" class="2"/>
      <ClassDef glyph="u1F1F5_u1F1F7" class="2"/>
      <ClassDef glyph="u1F1F5_u1F1F8" class="2"/>
      <ClassDef glyph="u1F1F5_u1F1F9" class="2"/>
      <ClassDef glyph="u1F1F5_u1F1FC" class="2"/>
      <ClassDef glyph="u1F1F5_u1F1FE" class="2"/>
      <ClassDef glyph="u1F1F6" class="1"/>
      <ClassDef glyph="u1F1F6_u1F1E6" class="2"/>
      <ClassDef glyph="u1F1F7" class="1"/>
      <ClassDef glyph="u1F1F7_u1F1EA" class="2"/>
      <ClassDef glyph="u1F1F7_u1F1F4" class="2"/>
      <ClassDef glyph="u1F1F7_u1F1F8" class="2"/>
      <ClassDef glyph="u1F1F7_u1F1FA" class="2"/>
      <ClassDef glyph="u1F1F7_u1F1FC" class="2"/>
      <ClassDef glyph="u1F1F8" class="1"/>
      <ClassDef glyph="u1F1F8_u1F1E6" class="2"/>
      <ClassDef glyph="u1F1F8_u1F1E7" class="2"/>
      <ClassDef glyph="u1F1F8_u1F1E8" class="2"/>
      <ClassDef glyph="u1F1F8_u1F1E9" class="2"/>
      <ClassDef glyph="u1F1F8_u1F1EA" class="2"/>
      <ClassDef glyph="u1F1F8_u1F1EC" class="2"/>
      <ClassDef glyph="u1F1F8_u1F1ED" class="2"/>
      <ClassDef glyph="u1F1F8_u1F1EE" class="2"/>
      <ClassDef glyph="u1F1F8_u1F1F0" class="2"/>
      <ClassDef glyph="u1F1F8_u1F1F1" class="2"/>
      <ClassDef glyph="u1F1F8_u1F1F2" class="2"/>
      <ClassDef glyph="u1F1F8_u1F1F3" class="2"/>
      <ClassDef glyph="u1F1F8_u1F1F4" class="2"/>
      <ClassDef glyph="u1F1F8_u1F1F7" class="2"/>
      <ClassDef glyph="u1F1F8_u1F1F8" class="2"/>
      <ClassDef glyph="u1F1F8_u1F1F9" class="2"/>
      <ClassDef glyph="u1F1F8_u1F1FB" class="2"/>
      <ClassDef glyph="u1F1F8_u1F1FD" class="2"/>
      <ClassDef glyph="u1F1F8_u1F1FE" class="2"/>
      <ClassDef glyph="u1F1F8_u1F1FF" class="2"/>
      <ClassDef glyph="u1F1F9" class="1"/>
      <ClassDef glyph="u1F1F9_u1F1E8" class="2"/>
      <ClassDef glyph="u1F1F9_u1F1E9" class="2"/>
      <ClassDef glyph="u1F1F9_u1F1EB" class="2"/>
      <ClassDef glyph="u1F1F9_u1F1EC" class="2"/>
      <ClassDef glyph="u1F1F9_u1F1ED" class="2"/>
      <ClassDef glyph="u1F1F9_u1F1EF" class="2"/>
      <ClassDef glyph="u1F1F9_u1F1F0" class="2"/>
      <ClassDef glyph="u1F1F9_u1F1F1" class="2"/>
      <ClassDef glyph="u1F1F9_u1F1F2" class="2"/>
      <ClassDef glyph="u1F1F9_u1F1F3" class="2"/>
      <ClassDef glyph="u1F1F9_u1F1F4" class="2"/>
      <ClassDef glyph="u1F1F9_u1F1F7" class="2"/>
      <ClassDef glyph="u1F1F9_u1F1F9" class="2"/>
      <ClassDef glyph="u1F1F9_u1F1FB" class="2"/>
      <ClassDef glyph="u1F1F9_u1F1FC" class="2"/>
      <ClassDef glyph="u1F1F9_u1F1FF" class="2"/>
      <ClassDef glyph="u1F1FA" class="1"/>
      <ClassDef glyph="u1F1FA_u1F1E6" class="2"/>
      <ClassDef glyph="u1F1FA_u1F1EC" class="2"/>
      <ClassDef glyph="u1F1FA_u1F1F8" class="2"/>
      <ClassDef glyph="u1F1FA_u1F1FE" class="2"/>
      <ClassDef glyph="u1F1FA_u1F1FF" class="2"/>
      <ClassDef glyph="u1F1FB" class="1"/>
      <ClassDef glyph="u1F1FB_u1F1E6" class="2"/>
      <ClassDef glyph="u1F1FB_u1F1E8" class="2"/>
      <ClassDef glyph="u1F1FB_u1F1EA" class="2"/>
      <ClassDef glyph="u1F1FB_u1F1EC" class="2"/>
      <ClassDef glyph="u1F1FB_u1F1EE" class="2"/>
      <ClassDef glyph="u1F1FB_u1F1F3" class="2"/>
      <ClassDef glyph="u1F1FB_u1F1FA" class="2"/>
      <ClassDef glyph="u1F1FC" class="1"/>
      <ClassDef glyph="u1F1FC_u1F1EB" class="2"/>
      <ClassDef glyph="u1F1FC_u1F1F8" class="2"/>
      <ClassDef glyph="u1F1FD" class="1"/>
      <ClassDef glyph="u1F1FD_u1F1F0" class="2"/>
      <ClassDef glyph="u1F1FE" class="1"/>
      <ClassDef glyph="u1F1FE_u1F1EA" class="2"/>
      <ClassDef glyph="u1F1FE_u1F1F9" class="2"/>
      <ClassDef glyph="u1F1FF" class="1"/>
      <ClassDef glyph="u1F1FF_u1F1E6" class="2"/>
      <ClassDef glyph="u1F1FF_u1F1F2" class="2"/>
      <ClassDef glyph="u1F1FF_u1F1FC" class="2"/>
      <ClassDef glyph="u1F201" class="1"/>
      <ClassDef glyph="u1F202" class="1"/>
      <ClassDef glyph="u1F21A" class="1"/>
      <ClassDef glyph="u1F22F" class="1"/>
      <ClassDef glyph="u1F232" class="1"/>
      <ClassDef glyph="u1F233" class="1"/>
      <ClassDef glyph="u1F234" class="1"/>
      <ClassDef glyph="u1F235" class="1"/>
      <ClassDef glyph="u1F236" class="1"/>
      <ClassDef glyph="u1F237" class="1"/>
      <ClassDef glyph="u1F238" class="1"/>
      <ClassDef glyph="u1F239" class="1"/>
      <ClassDef glyph="u1F23A" class="1"/>
      <ClassDef glyph="u1F250" class="1"/>
      <ClassDef glyph="u1F251" class="1"/>
      <ClassDef glyph="u1F300" class="1"/>
      <ClassDef glyph="u1F301" class="1"/>
      <ClassDef glyph="u1F302" class="1"/>
      <ClassDef glyph="u1F303" class="1"/>
      <ClassDef glyph="u1F304" class="1"/>
      <ClassDef glyph="u1F305" class="1"/>
      <ClassDef glyph="u1F306" class="1"/>
      <ClassDef glyph="u1F307" class="1"/>
      <ClassDef glyph="u1F308" class="1"/>
      <ClassDef glyph="u1F309" class="1"/>
      <ClassDef glyph="u1F30A" class="1"/>
      <ClassDef glyph="u1F30B" class="1"/>
      <ClassDef glyph="u1F30C" class="1"/>
      <ClassDef glyph="u1F30D" class="1"/>
      <ClassDef glyph="u1F30E" class="1"/>
      <ClassDef glyph="u1F30F" class="1"/>
      <ClassDef glyph="u1F310" class="1"/>
      <ClassDef glyph="u1F311" class="1"/>
      <ClassDef glyph="u1F312" class="1"/>
      <ClassDef glyph="u1F313" class="1"/>
      <ClassDef glyph="u1F314" class="1"/>
      <ClassDef glyph="u1F315" class="1"/>
      <ClassDef glyph="u1F316" class="1"/>
      <ClassDef glyph="u1F317" class="1"/>
      <ClassDef glyph="u1F318" class="1"/>
      <ClassDef glyph="u1F319" class="1"/>
      <ClassDef glyph="u1F31A" class="1"/>
      <ClassDef glyph="u1F31B" class="1"/>
      <ClassDef glyph="u1F31C" class="1"/>
      <ClassDef glyph="u1F31D" class="1"/>
      <ClassDef glyph="u1F31E" class="1"/>
      <ClassDef glyph="u1F31F" class="1"/>
      <ClassDef glyph="u1F320" class="1"/>
      <ClassDef glyph="u1F321" class="1"/>
      <ClassDef glyph="u1F324" class="1"/>
      <ClassDef glyph="u1F325" class="1"/>
      <ClassDef glyph="u1F326" class="1"/>
      <ClassDef glyph="u1F327" class="1"/>
      <ClassDef glyph="u1F328" class="1"/>
      <ClassDef glyph="u1F329" class="1"/>
      <ClassDef glyph="u1F32A" class="1"/>
      <ClassDef glyph="u1F32B" class="1"/>
      <ClassDef glyph="u1F32C" class="1"/>
      <ClassDef glyph="u1F32D" class="1"/>
      <ClassDef glyph="u1F32E" class="1"/>
      <ClassDef glyph="u1F32F" class="1"/>
      <ClassDef glyph="u1F330" class="1"/>
      <ClassDef glyph="u1F331" class="1"/>
      <ClassDef glyph="u1F332" class="1"/>
      <ClassDef glyph="u1F333" class="1"/>
      <ClassDef glyph="u1F334" class="1"/>
      <ClassDef glyph="u1F335" class="1"/>
      <ClassDef glyph="u1F336" class="1"/>
      <ClassDef glyph="u1F337" class="1"/>
      <ClassDef glyph="u1F338" class="1"/>
      <ClassDef glyph="u1F339" class="1"/>
      <ClassDef glyph="u1F33A" class="1"/>
      <ClassDef glyph="u1F33B" class="1"/>
      <ClassDef glyph="u1F33C" class="1"/>
      <ClassDef glyph="u1F33D" class="1"/>
      <ClassDef glyph="u1F33E" class="1"/>
      <ClassDef glyph="u1F33F" class="1"/>
      <ClassDef glyph="u1F340" class="1"/>
      <ClassDef glyph="u1F341" class="1"/>
      <ClassDef glyph="u1F342" class="1"/>
      <ClassDef glyph="u1F343" class="1"/>
      <ClassDef glyph="u1F344" class="1"/>
      <ClassDef glyph="u1F345" class="1"/>
      <ClassDef glyph="u1F346" class="1"/>
      <ClassDef glyph="u1F347" class="1"/>
      <ClassDef glyph="u1F348" class="1"/>
      <ClassDef glyph="u1F349" class="1"/>
      <ClassDef glyph="u1F34A" class="1"/>
      <ClassDef glyph="u1F34B" class="1"/>
      <ClassDef glyph="u1F34C" class="1"/>
      <ClassDef glyph="u1F34D" class="1"/>
      <ClassDef glyph="u1F34E" class="1"/>
      <ClassDef glyph="u1F34F" class="1"/>
      <ClassDef glyph="u1F350" class="1"/>
      <ClassDef glyph="u1F351" class="1"/>
      <ClassDef glyph="u1F352" class="1"/>
      <ClassDef glyph="u1F353" class="1"/>
      <ClassDef glyph="u1F354" class="1"/>
      <ClassDef glyph="u1F355" class="1"/>
      <ClassDef glyph="u1F356" class="1"/>
      <ClassDef glyph="u1F357" class="1"/>
      <ClassDef glyph="u1F358" class="1"/>
      <ClassDef glyph="u1F359" class="1"/>
      <ClassDef glyph="u1F35A" class="1"/>
      <ClassDef glyph="u1F35B" class="1"/>
      <ClassDef glyph="u1F35C" class="1"/>
      <ClassDef glyph="u1F35D" class="1"/>
      <ClassDef glyph="u1F35E" class="1"/>
      <ClassDef glyph="u1F35F" class="1"/>
      <ClassDef glyph="u1F360" class="1"/>
      <ClassDef glyph="u1F361" class="1"/>
      <ClassDef glyph="u1F362" class="1"/>
      <ClassDef glyph="u1F363" class="1"/>
      <ClassDef glyph="u1F364" class="1"/>
      <ClassDef glyph="u1F365" class="1"/>
      <ClassDef glyph="u1F366" class="1"/>
      <ClassDef glyph="u1F367" class="1"/>
      <ClassDef glyph="u1F368" class="1"/>
      <ClassDef glyph="u1F369" class="1"/>
      <ClassDef glyph="u1F36A" class="1"/>
      <ClassDef glyph="u1F36B" class="1"/>
      <ClassDef glyph="u1F36C" class="1"/>
      <ClassDef glyph="u1F36D" class="1"/>
      <ClassDef glyph="u1F36E" class="1"/>
      <ClassDef glyph="u1F36F" class="1"/>
      <ClassDef glyph="u1F370" class="1"/>
      <ClassDef glyph="u1F371" class="1"/>
      <ClassDef glyph="u1F372" class="1"/>
      <ClassDef glyph="u1F373" class="1"/>
      <ClassDef glyph="u1F374" class="1"/>
      <ClassDef glyph="u1F375" class="1"/>
      <ClassDef glyph="u1F376" class="1"/>
      <ClassDef glyph="u1F377" class="1"/>
      <ClassDef glyph="u1F378" class="1"/>
      <ClassDef glyph="u1F379" class="1"/>
      <ClassDef glyph="u1F37A" class="1"/>
      <ClassDef glyph="u1F37B" class="1"/>
      <ClassDef glyph="u1F37C" class="1"/>
      <ClassDef glyph="u1F37D" class="1"/>
      <ClassDef glyph="u1F37E" class="1"/>
      <ClassDef glyph="u1F37F" class="1"/>
      <ClassDef glyph="u1F380" class="1"/>
      <ClassDef glyph="u1F381" class="1"/>
      <ClassDef glyph="u1F382" class="1"/>
      <ClassDef glyph="u1F383" class="1"/>
      <ClassDef glyph="u1F384" class="1"/>
      <ClassDef glyph="u1F385.0" class="1"/>
      <ClassDef glyph="u1F385.1" class="2"/>
      <ClassDef glyph="u1F385.2" class="2"/>
      <ClassDef glyph="u1F385.3" class="2"/>
      <ClassDef glyph="u1F385.4" class="2"/>
      <ClassDef glyph="u1F385.5" class="2"/>
      <ClassDef glyph="u1F386" class="1"/>
      <ClassDef glyph="u1F387" class="1"/>
      <ClassDef glyph="u1F388" class="1"/>
      <ClassDef glyph="u1F389" class="1"/>
      <ClassDef glyph="u1F38A" class="1"/>
      <ClassDef glyph="u1F38B" class="1"/>
      <ClassDef glyph="u1F38C" class="1"/>
      <ClassDef glyph="u1F38D" class="1"/>
      <ClassDef glyph="u1F38E" class="1"/>
      <ClassDef glyph="u1F38F" class="1"/>
      <ClassDef glyph="u1F390" class="1"/>
      <ClassDef glyph="u1F391" class="1"/>
      <ClassDef glyph="u1F392" class="1"/>
      <ClassDef glyph="u1F393" class="1"/>
      <ClassDef glyph="u1F396" class="1"/>
      <ClassDef glyph="u1F397" class="1"/>
      <ClassDef glyph="u1F399" class="1"/>
      <ClassDef glyph="u1F39A" class="1"/>
      <ClassDef glyph="u1F39B" class="1"/>
      <ClassDef glyph="u1F39E" class="1"/>
      <ClassDef glyph="u1F39F" class="1"/>
      <ClassDef glyph="u1F3A0" class="1"/>
      <ClassDef glyph="u1F3A1" class="1"/>
      <ClassDef glyph="u1F3A2" class="1"/>
      <ClassDef glyph="u1F3A3" class="1"/>
      <ClassDef glyph="u1F3A4" class="1"/>
      <ClassDef glyph="u1F3A5" class="1"/>
      <ClassDef glyph="u1F3A6" class="1"/>
      <ClassDef glyph="u1F3A7" class="1"/>
      <ClassDef glyph="u1F3A8" class="1"/>
      <ClassDef glyph="u1F3A9" class="1"/>
      <ClassDef glyph="u1F3AA" class="1"/>
      <ClassDef glyph="u1F3AB" class="1"/>
      <ClassDef glyph="u1F3AC" class="1"/>
      <ClassDef glyph="u1F3AD" class="1"/>
      <ClassDef glyph="u1F3AE" class="1"/>
      <ClassDef glyph="u1F3AF" class="1"/>
      <ClassDef glyph="u1F3B0" class="1"/>
      <ClassDef glyph="u1F3B1" class="1"/>
      <ClassDef glyph="u1F3B2" class="1"/>
      <ClassDef glyph="u1F3B3" class="1"/>
      <ClassDef glyph="u1F3B4" class="1"/>
      <ClassDef glyph="u1F3B5" class="1"/>
      <ClassDef glyph="u1F3B6" class="1"/>
      <ClassDef glyph="u1F3B7" class="1"/>
      <ClassDef glyph="u1F3B8" class="1"/>
      <ClassDef glyph="u1F3B9" class="1"/>
      <ClassDef glyph="u1F3BA" class="1"/>
      <ClassDef glyph="u1F3BB" class="1"/>
      <ClassDef glyph="u1F3BC" class="1"/>
      <ClassDef glyph="u1F3BD" class="1"/>
      <ClassDef glyph="u1F3BE" class="1"/>
      <ClassDef glyph="u1F3BF" class="1"/>
      <ClassDef glyph="u1F3C0" class="1"/>
      <ClassDef glyph="u1F3C1" class="1"/>
      <ClassDef glyph="u1F3C2" class="1"/>
      <ClassDef glyph="u1F3C3.0" class="1"/>
      <ClassDef glyph="u1F3C3.1" class="2"/>
      <ClassDef glyph="u1F3C3.2" class="2"/>
      <ClassDef glyph="u1F3C3.3" class="2"/>
      <ClassDef glyph="u1F3C3.4" class="2"/>
      <ClassDef glyph="u1F3C3.5" class="2"/>
      <ClassDef glyph="u1F3C4.0" class="1"/>
      <ClassDef glyph="u1F3C4.1" class="2"/>
      <ClassDef glyph="u1F3C4.2" class="2"/>
      <ClassDef glyph="u1F3C4.3" class="2"/>
      <ClassDef glyph="u1F3C4.4" class="2"/>
      <ClassDef glyph="u1F3C4.5" class="2"/>
      <ClassDef glyph="u1F3C5" class="1"/>
      <ClassDef glyph="u1F3C6" class="1"/>
      <ClassDef glyph="u1F3C7.0" class="1"/>
      <ClassDef glyph="u1F3C7.1" class="2"/>
      <ClassDef glyph="u1F3C7.2" class="2"/>
      <ClassDef glyph="u1F3C7.3" class="2"/>
      <ClassDef glyph="u1F3C7.4" class="2"/>
      <ClassDef glyph="u1F3C7.5" class="2"/>
      <ClassDef glyph="u1F3C8" class="1"/>
      <ClassDef glyph="u1F3C9" class="1"/>
      <ClassDef glyph="u1F3CA.0" class="1"/>
      <ClassDef glyph="u1F3CA.1" class="2"/>
      <ClassDef glyph="u1F3CA.2" class="2"/>
      <ClassDef glyph="u1F3CA.3" class="2"/>
      <ClassDef glyph="u1F3CA.4" class="2"/>
      <ClassDef glyph="u1F3CA.5" class="2"/>
      <ClassDef glyph="u1F3CB.0" class="1"/>
      <ClassDef glyph="u1F3CB.1" class="2"/>
      <ClassDef glyph="u1F3CB.2" class="2"/>
      <ClassDef glyph="u1F3CB.3" class="2"/>
      <ClassDef glyph="u1F3CB.4" class="2"/>
      <ClassDef glyph="u1F3CB.5" class="2"/>
      <ClassDef glyph="u1F3CC" class="1"/>
      <ClassDef glyph="u1F3CD" class="1"/>
      <ClassDef glyph="u1F3CE" class="1"/>
      <ClassDef glyph="u1F3CF" class="1"/>
      <ClassDef glyph="u1F3D0" class="1"/>
      <ClassDef glyph="u1F3D1" class="1"/>
      <ClassDef glyph="u1F3D2" class="1"/>
      <ClassDef glyph="u1F3D3" class="1"/>
      <ClassDef glyph="u1F3D4" class="1"/>
      <ClassDef glyph="u1F3D5" class="1"/>
      <ClassDef glyph="u1F3D6" class="1"/>
      <ClassDef glyph="u1F3D7" class="1"/>
      <ClassDef glyph="u1F3D8" class="1"/>
      <ClassDef glyph="u1F3D9" class="1"/>
      <ClassDef glyph="u1F3DA" class="1"/>
      <ClassDef glyph="u1F3DB" class="1"/>
      <ClassDef glyph="u1F3DC" class="1"/>
      <ClassDef glyph="u1F3DD" class="1"/>
      <ClassDef glyph="u1F3DE" class="1"/>
      <ClassDef glyph="u1F3DF" class="1"/>
      <ClassDef glyph="u1F3E0" class="1"/>
      <ClassDef glyph="u1F3E1" class="1"/>
      <ClassDef glyph="u1F3E2" class="1"/>
      <ClassDef glyph="u1F3E3" class="1"/>
      <ClassDef glyph="u1F3E4" class="1"/>
      <ClassDef glyph="u1F3E5" class="1"/>
      <ClassDef glyph="u1F3E6" class="1"/>
      <ClassDef glyph="u1F3E7" class="1"/>
      <ClassDef glyph="u1F3E8" class="1"/>
      <ClassDef glyph="u1F3E9" class="1"/>
      <ClassDef glyph="u1F3EA" class="1"/>
      <ClassDef glyph="u1F3EB" class="1"/>
      <ClassDef glyph="u1F3EC" class="1"/>
      <ClassDef glyph="u1F3ED" class="1"/>
      <ClassDef glyph="u1F3EE" class="1"/>
      <ClassDef glyph="u1F3EF" class="1"/>
      <ClassDef glyph="u1F3F0" class="1"/>
      <ClassDef glyph="u1F3F3" class="1"/>
      <ClassDef glyph="u1F3F4" class="1"/>
      <ClassDef glyph="u1F3F5" class="1"/>
      <ClassDef glyph="u1F3F7" class="1"/>
      <ClassDef glyph="u1F3F8" class="1"/>
      <ClassDef glyph="u1F3F9" class="1"/>
      <ClassDef glyph="u1F3FA" class="1"/>
      <ClassDef glyph="u1F3FB" class="1"/>
      <ClassDef glyph="u1F3FC" class="1"/>
      <ClassDef glyph="u1F3FD" class="1"/>
      <ClassDef glyph="u1F3FE" class="1"/>
      <ClassDef glyph="u1F3FF" class="1"/>
      <ClassDef glyph="u1F400" class="1"/>
      <ClassDef glyph="u1F401" class="1"/>
      <ClassDef glyph="u1F402" class="1"/>
      <ClassDef glyph="u1F403" class="1"/>
      <ClassDef glyph="u1F404" class="1"/>
      <ClassDef glyph="u1F405" class="1"/>
      <ClassDef glyph="u1F406" class="1"/>
      <ClassDef glyph="u1F407" class="1"/>
      <ClassDef glyph="u1F408" class="1"/>
      <ClassDef glyph="u1F409" class="1"/>
      <ClassDef glyph="u1F40A" class="1"/>
      <ClassDef glyph="u1F40B" class="1"/>
      <ClassDef glyph="u1F40C" class="1"/>
      <ClassDef glyph="u1F40D" class="1"/>
      <ClassDef glyph="u1F40E" class="1"/>
      <ClassDef glyph="u1F40F" class="1"/>
      <ClassDef glyph="u1F410" class="1"/>
      <ClassDef glyph="u1F411" class="1"/>
      <ClassDef glyph="u1F412" class="1"/>
      <ClassDef glyph="u1F413" class="1"/>
      <ClassDef glyph="u1F414" class="1"/>
      <ClassDef glyph="u1F415" class="1"/>
      <ClassDef glyph="u1F416" class="1"/>
      <ClassDef glyph="u1F417" class="1"/>
      <ClassDef glyph="u1F418" class="1"/>
      <ClassDef glyph="u1F419" class="1"/>
      <ClassDef glyph="u1F41A" class="1"/>
      <ClassDef glyph="u1F41B" class="1"/>
      <ClassDef glyph="u1F41C" class="1"/>
      <ClassDef glyph="u1F41D" class="1"/>
      <ClassDef glyph="u1F41E" class="1"/>
      <ClassDef glyph="u1F41F" class="1"/>
      <ClassDef glyph="u1F420" class="1"/>
      <ClassDef glyph="u1F421" class="1"/>
      <ClassDef glyph="u1F422" class="1"/>
      <ClassDef glyph="u1F423" class="1"/>
      <ClassDef glyph="u1F424" class="1"/>
      <ClassDef glyph="u1F425" class="1"/>
      <ClassDef glyph="u1F426" class="1"/>
      <ClassDef glyph="u1F427" class="1"/>
      <ClassDef glyph="u1F428" class="1"/>
      <ClassDef glyph="u1F429" class="1"/>
      <ClassDef glyph="u1F42A" class="1"/>
      <ClassDef glyph="u1F42B" class="1"/>
      <ClassDef glyph="u1F42C" class="1"/>
      <ClassDef glyph="u1F42D" class="1"/>
      <ClassDef glyph="u1F42E" class="1"/>
      <ClassDef glyph="u1F42F" class="1"/>
      <ClassDef glyph="u1F430" class="1"/>
      <ClassDef glyph="u1F431" class="1"/>
      <ClassDef glyph="u1F432" class="1"/>
      <ClassDef glyph="u1F433" class="1"/>
      <ClassDef glyph="u1F434" class="1"/>
      <ClassDef glyph="u1F435" class="1"/>
      <ClassDef glyph="u1F436" class="1"/>
      <ClassDef glyph="u1F437" class="1"/>
      <ClassDef glyph="u1F438" class="1"/>
      <ClassDef glyph="u1F439" class="1"/>
      <ClassDef glyph="u1F43A" class="1"/>
      <ClassDef glyph="u1F43B" class="1"/>
      <ClassDef glyph="u1F43C" class="1"/>
      <ClassDef glyph="u1F43D" class="1"/>
      <ClassDef glyph="u1F43E" class="1"/>
      <ClassDef glyph="u1F43F" class="1"/>
      <ClassDef glyph="u1F440" class="1"/>
      <ClassDef glyph="u1F441" class="1"/>
      <ClassDef glyph="u1F441_u1F5E8" class="2"/>
      <ClassDef glyph="u1F442.0" class="1"/>
      <ClassDef glyph="u1F442.1" class="2"/>
      <ClassDef glyph="u1F442.2" class="2"/>
      <ClassDef glyph="u1F442.3" class="2"/>
      <ClassDef glyph="u1F442.4" class="2"/>
      <ClassDef glyph="u1F442.5" class="2"/>
      <ClassDef glyph="u1F443.0" class="1"/>
      <ClassDef glyph="u1F443.1" class="2"/>
      <ClassDef glyph="u1F443.2" class="2"/>
      <ClassDef glyph="u1F443.3" class="2"/>
      <ClassDef glyph="u1F443.4" class="2"/>
      <ClassDef glyph="u1F443.5" class="2"/>
      <ClassDef glyph="u1F444" class="1"/>
      <ClassDef glyph="u1F445" class="1"/>
      <ClassDef glyph="u1F446.0" class="1"/>
      <ClassDef glyph="u1F446.1" class="2"/>
      <ClassDef glyph="u1F446.2" class="2"/>
      <ClassDef glyph="u1F446.3" class="2"/>
      <ClassDef glyph="u1F446.4" class="2"/>
      <ClassDef glyph="u1F446.5" class="2"/>
      <ClassDef glyph="u1F447.0" class="1"/>
      <ClassDef glyph="u1F447.1" class="2"/>
      <ClassDef glyph="u1F447.2" class="2"/>
      <ClassDef glyph="u1F447.3" class="2"/>
      <ClassDef glyph="u1F447.4" class="2"/>
      <ClassDef glyph="u1F447.5" class="2"/>
      <ClassDef glyph="u1F448.0" class="1"/>
      <ClassDef glyph="u1F448.1" class="2"/>
      <ClassDef glyph="u1F448.2" class="2"/>
      <ClassDef glyph="u1F448.3" class="2"/>
      <ClassDef glyph="u1F448.4" class="2"/>
      <ClassDef glyph="u1F448.5" class="2"/>
      <ClassDef glyph="u1F449.0" class="1"/>
      <ClassDef glyph="u1F449.1" class="2"/>
      <ClassDef glyph="u1F449.2" class="2"/>
      <ClassDef glyph="u1F449.3" class="2"/>
      <ClassDef glyph="u1F449.4" class="2"/>
      <ClassDef glyph="u1F449.5" class="2"/>
      <ClassDef glyph="u1F44A.0" class="1"/>
      <ClassDef glyph="u1F44A.1" class="2"/>
      <ClassDef glyph="u1F44A.2" class="2"/>
      <ClassDef glyph="u1F44A.3" class="2"/>
      <ClassDef glyph="u1F44A.4" class="2"/>
      <ClassDef glyph="u1F44A.5" class="2"/>
      <ClassDef glyph="u1F44B.0" class="1"/>
      <ClassDef glyph="u1F44B.1" class="2"/>
      <ClassDef glyph="u1F44B.2" class="2"/>
      <ClassDef glyph="u1F44B.3" class="2"/>
      <ClassDef glyph="u1F44B.4" class="2"/>
      <ClassDef glyph="u1F44B.5" class="2"/>
      <ClassDef glyph="u1F44C.0" class="1"/>
      <ClassDef glyph="u1F44C.1" class="2"/>
      <ClassDef glyph="u1F44C.2" class="2"/>
      <ClassDef glyph="u1F44C.3" class="2"/>
      <ClassDef glyph="u1F44C.4" class="2"/>
      <ClassDef glyph="u1F44C.5" class="2"/>
      <ClassDef glyph="u1F44D.0" class="1"/>
      <ClassDef glyph="u1F44D.1" class="2"/>
      <ClassDef glyph="u1F44D.2" class="2"/>
      <ClassDef glyph="u1F44D.3" class="2"/>
      <ClassDef glyph="u1F44D.4" class="2"/>
      <ClassDef glyph="u1F44D.5" class="2"/>
      <ClassDef glyph="u1F44E.0" class="1"/>
      <ClassDef glyph="u1F44E.1" class="2"/>
      <ClassDef glyph="u1F44E.2" class="2"/>
      <ClassDef glyph="u1F44E.3" class="2"/>
      <ClassDef glyph="u1F44E.4" class="2"/>
      <ClassDef glyph="u1F44E.5" class="2"/>
      <ClassDef glyph="u1F44F.0" class="1"/>
      <ClassDef glyph="u1F44F.1" class="2"/>
      <ClassDef glyph="u1F44F.2" class="2"/>
      <ClassDef glyph="u1F44F.3" class="2"/>
      <ClassDef glyph="u1F44F.4" class="2"/>
      <ClassDef glyph="u1F44F.5" class="2"/>
      <ClassDef glyph="u1F450.0" class="1"/>
      <ClassDef glyph="u1F450.1" class="2"/>
      <ClassDef glyph="u1F450.2" class="2"/>
      <ClassDef glyph="u1F450.3" class="2"/>
      <ClassDef glyph="u1F450.4" class="2"/>
      <ClassDef glyph="u1F450.5" class="2"/>
      <ClassDef glyph="u1F451" class="1"/>
      <ClassDef glyph="u1F452" class="1"/>
      <ClassDef glyph="u1F453" class="1"/>
      <ClassDef glyph="u1F454" class="1"/>
      <ClassDef glyph="u1F455" class="1"/>
      <ClassDef glyph="u1F456" class="1"/>
      <ClassDef glyph="u1F457" class="1"/>
      <ClassDef glyph="u1F458" class="1"/>
      <ClassDef glyph="u1F459" class="1"/>
      <ClassDef glyph="u1F45A" class="1"/>
      <ClassDef glyph="u1F45B" class="1"/>
      <ClassDef glyph="u1F45C" class="1"/>
      <ClassDef glyph="u1F45D" class="1"/>
      <ClassDef glyph="u1F45E" class="1"/>
      <ClassDef glyph="u1F45F" class="1"/>
      <ClassDef glyph="u1F460" class="1"/>
      <ClassDef glyph="u1F461" class="1"/>
      <ClassDef glyph="u1F462" class="1"/>
      <ClassDef glyph="u1F463" class="1"/>
      <ClassDef glyph="u1F464" class="1"/>
      <ClassDef glyph="u1F465" class="1"/>
      <ClassDef glyph="u1F466.0" class="1"/>
      <ClassDef glyph="u1F466.1" class="2"/>
      <ClassDef glyph="u1F466.2" class="2"/>
      <ClassDef glyph="u1F466.3" class="2"/>
      <ClassDef glyph="u1F466.4" class="2"/>
      <ClassDef glyph="u1F466.5" class="2"/>
      <ClassDef glyph="u1F467.0" class="1"/>
      <ClassDef glyph="u1F467.1" class="2"/>
      <ClassDef glyph="u1F467.2" class="2"/>
      <ClassDef glyph="u1F467.3" class="2"/>
      <ClassDef glyph="u1F467.4" class="2"/>
      <ClassDef glyph="u1F467.5" class="2"/>
      <ClassDef glyph="u1F468.0" class="1"/>
      <ClassDef glyph="u1F468.1" class="2"/>
      <ClassDef glyph="u1F468.2" class="2"/>
      <ClassDef glyph="u1F468.3" class="2"/>
      <ClassDef glyph="u1F468.4" class="2"/>
      <ClassDef glyph="u1F468.5" class="2"/>
      <ClassDef glyph="u1F469.0" class="1"/>
      <ClassDef glyph="u1F469.1" class="2"/>
      <ClassDef glyph="u1F469.2" class="2"/>
      <ClassDef glyph="u1F469.3" class="2"/>
      <ClassDef glyph="u1F469.4" class="2"/>
      <ClassDef glyph="u1F469.5" class="2"/>
      <ClassDef glyph="u1F46A.0.FAMDEF" class="2"/>
      <ClassDef glyph="u1F46A.0.MMB" class="2"/>
      <ClassDef glyph="u1F46A.0.MMBB" class="1"/>
      <ClassDef glyph="u1F46A.0.MMG" class="2"/>
      <ClassDef glyph="u1F46A.0.MMGB" class="1"/>
      <ClassDef glyph="u1F46A.0.MMGG" class="1"/>
      <ClassDef glyph="u1F46A.0.MWBB" class="1"/>
      <ClassDef glyph="u1F46A.0.MWG" class="2"/>
      <ClassDef glyph="u1F46A.0.MWGB" class="1"/>
      <ClassDef glyph="u1F46A.0.MWGG" class="1"/>
      <ClassDef glyph="u1F46A.0.WWB" class="2"/>
      <ClassDef glyph="u1F46A.0.WWBB" class="1"/>
      <ClassDef glyph="u1F46A.0.WWG" class="2"/>
      <ClassDef glyph="u1F46A.0.WWGB" class="1"/>
      <ClassDef glyph="u1F46A.0.WWGG" class="1"/>
      <ClassDef glyph="u1F46B" class="1"/>
      <ClassDef glyph="u1F46C" class="1"/>
      <ClassDef glyph="u1F46D" class="1"/>
      <ClassDef glyph="u1F46E.0" class="1"/>
      <ClassDef glyph="u1F46E.1" class="2"/>
      <ClassDef glyph="u1F46E.2" class="2"/>
      <ClassDef glyph="u1F46E.3" class="2"/>
      <ClassDef glyph="u1F46E.4" class="2"/>
      <ClassDef glyph="u1F46E.5" class="2"/>
      <ClassDef glyph="u1F46F" class="1"/>
      <ClassDef glyph="u1F470.0" class="1"/>
      <ClassDef glyph="u1F470.1" class="2"/>
      <ClassDef glyph="u1F470.2" class="2"/>
      <ClassDef glyph="u1F470.3" class="2"/>
      <ClassDef glyph="u1F470.4" class="2"/>
      <ClassDef glyph="u1F470.5" class="2"/>
      <ClassDef glyph="u1F471.0" class="1"/>
      <ClassDef glyph="u1F471.1" class="2"/>
      <ClassDef glyph="u1F471.2" class="2"/>
      <ClassDef glyph="u1F471.3" class="2"/>
      <ClassDef glyph="u1F471.4" class="2"/>
      <ClassDef glyph="u1F471.5" class="2"/>
      <ClassDef glyph="u1F472.0" class="1"/>
      <ClassDef glyph="u1F472.1" class="2"/>
      <ClassDef glyph="u1F472.2" class="2"/>
      <ClassDef glyph="u1F472.3" class="2"/>
      <ClassDef glyph="u1F472.4" class="2"/>
      <ClassDef glyph="u1F472.5" class="2"/>
      <ClassDef glyph="u1F473.0" class="1"/>
      <ClassDef glyph="u1F473.1" class="2"/>
      <ClassDef glyph="u1F473.2" class="2"/>
      <ClassDef glyph="u1F473.3" class="2"/>
      <ClassDef glyph="u1F473.4" class="2"/>
      <ClassDef glyph="u1F473.5" class="2"/>
      <ClassDef glyph="u1F474.0" class="1"/>
      <ClassDef glyph="u1F474.1" class="2"/>
      <ClassDef glyph="u1F474.2" class="2"/>
      <ClassDef glyph="u1F474.3" class="2"/>
      <ClassDef glyph="u1F474.4" class="2"/>
      <ClassDef glyph="u1F474.5" class="2"/>
      <ClassDef glyph="u1F475.0" class="1"/>
      <ClassDef glyph="u1F475.1" class="2"/>
      <ClassDef glyph="u1F475.2" class="2"/>
      <ClassDef glyph="u1F475.3" class="2"/>
      <ClassDef glyph="u1F475.4" class="2"/>
      <ClassDef glyph="u1F475.5" class="2"/>
      <ClassDef glyph="u1F476.0" class="1"/>
      <ClassDef glyph="u1F476.1" class="2"/>
      <ClassDef glyph="u1F476.2" class="2"/>
      <ClassDef glyph="u1F476.3" class="2"/>
      <ClassDef glyph="u1F476.4" class="2"/>
      <ClassDef glyph="u1F476.5" class="2"/>
      <ClassDef glyph="u1F477.0" class="1"/>
      <ClassDef glyph="u1F477.1" class="2"/>
      <ClassDef glyph="u1F477.2" class="2"/>
      <ClassDef glyph="u1F477.3" class="2"/>
      <ClassDef glyph="u1F477.4" class="2"/>
      <ClassDef glyph="u1F477.5" class="2"/>
      <ClassDef glyph="u1F478.0" class="1"/>
      <ClassDef glyph="u1F478.1" class="2"/>
      <ClassDef glyph="u1F478.2" class="2"/>
      <ClassDef glyph="u1F478.3" class="2"/>
      <ClassDef glyph="u1F478.4" class="2"/>
      <ClassDef glyph="u1F478.5" class="2"/>
      <ClassDef glyph="u1F479" class="1"/>
      <ClassDef glyph="u1F47A" class="1"/>
      <ClassDef glyph="u1F47B" class="1"/>
      <ClassDef glyph="u1F47C.0" class="1"/>
      <ClassDef glyph="u1F47C.1" class="2"/>
      <ClassDef glyph="u1F47C.2" class="2"/>
      <ClassDef glyph="u1F47C.3" class="2"/>
      <ClassDef glyph="u1F47C.4" class="2"/>
      <ClassDef glyph="u1F47C.5" class="2"/>
      <ClassDef glyph="u1F47D" class="1"/>
      <ClassDef glyph="u1F47E" class="1"/>
      <ClassDef glyph="u1F47F" class="1"/>
      <ClassDef glyph="u1F480" class="1"/>
      <ClassDef glyph="u1F481.0" class="1"/>
      <ClassDef glyph="u1F481.1" class="2"/>
      <ClassDef glyph="u1F481.2" class="2"/>
      <ClassDef glyph="u1F481.3" class="2"/>
      <ClassDef glyph="u1F481.4" class="2"/>
      <ClassDef glyph="u1F481.5" class="2"/>
      <ClassDef glyph="u1F482.0" class="1"/>
      <ClassDef glyph="u1F482.1" class="2"/>
      <ClassDef glyph="u1F482.2" class="2"/>
      <ClassDef glyph="u1F482.3" class="2"/>
      <ClassDef glyph="u1F482.4" class="2"/>
      <ClassDef glyph="u1F482.5" class="2"/>
      <ClassDef glyph="u1F483.0" class="1"/>
      <ClassDef glyph="u1F483.1" class="2"/>
      <ClassDef glyph="u1F483.2" class="2"/>
      <ClassDef glyph="u1F483.3" class="2"/>
      <ClassDef glyph="u1F483.4" class="2"/>
      <ClassDef glyph="u1F483.5" class="2"/>
      <ClassDef glyph="u1F484" class="1"/>
      <ClassDef glyph="u1F485.0" class="1"/>
      <ClassDef glyph="u1F485.1" class="2"/>
      <ClassDef glyph="u1F485.2" class="2"/>
      <ClassDef glyph="u1F485.3" class="2"/>
      <ClassDef glyph="u1F485.4" class="2"/>
      <ClassDef glyph="u1F485.5" class="2"/>
      <ClassDef glyph="u1F486.0" class="1"/>
      <ClassDef glyph="u1F486.1" class="2"/>
      <ClassDef glyph="u1F486.2" class="2"/>
      <ClassDef glyph="u1F486.3" class="2"/>
      <ClassDef glyph="u1F486.4" class="2"/>
      <ClassDef glyph="u1F486.5" class="2"/>
      <ClassDef glyph="u1F487.0" class="1"/>
      <ClassDef glyph="u1F487.1" class="2"/>
      <ClassDef glyph="u1F487.2" class="2"/>
      <ClassDef glyph="u1F487.3" class="2"/>
      <ClassDef glyph="u1F487.4" class="2"/>
      <ClassDef glyph="u1F487.5" class="2"/>
      <ClassDef glyph="u1F488" class="1"/>
      <ClassDef glyph="u1F489" class="1"/>
      <ClassDef glyph="u1F48A" class="1"/>
      <ClassDef glyph="u1F48B" class="1"/>
      <ClassDef glyph="u1F48C" class="1"/>
      <ClassDef glyph="u1F48D" class="1"/>
      <ClassDef glyph="u1F48E" class="1"/>
      <ClassDef glyph="u1F48F.0.DEFWM" class="2"/>
      <ClassDef glyph="u1F48F.0.MM" class="2"/>
      <ClassDef glyph="u1F48F.0.WW" class="2"/>
      <ClassDef glyph="u1F490" class="1"/>
      <ClassDef glyph="u1F491.0.DEFWM" class="2"/>
      <ClassDef glyph="u1F491.0.MM" class="2"/>
      <ClassDef glyph="u1F491.0.WW" class="2"/>
      <ClassDef glyph="u1F492" class="1"/>
      <ClassDef glyph="u1F493" class="1"/>
      <ClassDef glyph="u1F494" class="1"/>
      <ClassDef glyph="u1F495" class="1"/>
      <ClassDef glyph="u1F496" class="1"/>
      <ClassDef glyph="u1F497" class="1"/>
      <ClassDef glyph="u1F498" class="1"/>
      <ClassDef glyph="u1F499" class="1"/>
      <ClassDef glyph="u1F49A" class="1"/>
      <ClassDef glyph="u1F49B" class="1"/>
      <ClassDef glyph="u1F49C" class="1"/>
      <ClassDef glyph="u1F49D" class="1"/>
      <ClassDef glyph="u1F49E" class="1"/>
      <ClassDef glyph="u1F49F" class="1"/>
      <ClassDef glyph="u1F4A0" class="1"/>
      <ClassDef glyph="u1F4A1" class="1"/>
      <ClassDef glyph="u1F4A2" class="1"/>
      <ClassDef glyph="u1F4A3" class="1"/>
      <ClassDef glyph="u1F4A4" class="1"/>
      <ClassDef glyph="u1F4A5" class="1"/>
      <ClassDef glyph="u1F4A6" class="1"/>
      <ClassDef glyph="u1F4A7" class="1"/>
      <ClassDef glyph="u1F4A8" class="1"/>
      <ClassDef glyph="u1F4A9" class="1"/>
      <ClassDef glyph="u1F4AA.0" class="1"/>
      <ClassDef glyph="u1F4AA.1" class="2"/>
      <ClassDef glyph="u1F4AA.2" class="2"/>
      <ClassDef glyph="u1F4AA.3" class="2"/>
      <ClassDef glyph="u1F4AA.4" class="2"/>
      <ClassDef glyph="u1F4AA.5" class="2"/>
      <ClassDef glyph="u1F4AB" class="1"/>
      <ClassDef glyph="u1F4AC" class="1"/>
      <ClassDef glyph="u1F4AD" class="1"/>
      <ClassDef glyph="u1F4AE" class="1"/>
      <ClassDef glyph="u1F4AF" class="1"/>
      <ClassDef glyph="u1F4B0" class="1"/>
      <ClassDef glyph="u1F4B1" class="1"/>
      <ClassDef glyph="u1F4B2" class="1"/>
      <ClassDef glyph="u1F4B3" class="1"/>
      <ClassDef glyph="u1F4B4" class="1"/>
      <ClassDef glyph="u1F4B5" class="1"/>
      <ClassDef glyph="u1F4B6" class="1"/>
      <ClassDef glyph="u1F4B7" class="1"/>
      <ClassDef glyph="u1F4B8" class="1"/>
      <ClassDef glyph="u1F4B9" class="1"/>
      <ClassDef glyph="u1F4BA" class="1"/>
      <ClassDef glyph="u1F4BB" class="1"/>
      <ClassDef glyph="u1F4BC" class="1"/>
      <ClassDef glyph="u1F4BD" class="1"/>
      <ClassDef glyph="u1F4BE" class="1"/>
      <ClassDef glyph="u1F4BF" class="1"/>
      <ClassDef glyph="u1F4C0" class="1"/>
      <ClassDef glyph="u1F4C1" class="1"/>
      <ClassDef glyph="u1F4C2" class="1"/>
      <ClassDef glyph="u1F4C3" class="1"/>
      <ClassDef glyph="u1F4C4" class="1"/>
      <ClassDef glyph="u1F4C5" class="1"/>
      <ClassDef glyph="u1F4C6" class="1"/>
      <ClassDef glyph="u1F4C7" class="1"/>
      <ClassDef glyph="u1F4C8" class="1"/>
      <ClassDef glyph="u1F4C9" class="1"/>
      <ClassDef glyph="u1F4CA" class="1"/>
      <ClassDef glyph="u1F4CB" class="1"/>
      <ClassDef glyph="u1F4CC" class="1"/>
      <ClassDef glyph="u1F4CD" class="1"/>
      <ClassDef glyph="u1F4CE" class="1"/>
      <ClassDef glyph="u1F4CF" class="1"/>
      <ClassDef glyph="u1F4D0" class="1"/>
      <ClassDef glyph="u1F4D1" class="1"/>
      <ClassDef glyph="u1F4D2" class="1"/>
      <ClassDef glyph="u1F4D3" class="1"/>
      <ClassDef glyph="u1F4D4" class="1"/>
      <ClassDef glyph="u1F4D5" class="1"/>
      <ClassDef glyph="u1F4D6" class="1"/>
      <ClassDef glyph="u1F4D7" class="1"/>
      <ClassDef glyph="u1F4D8" class="1"/>
      <ClassDef glyph="u1F4D9" class="1"/>
      <ClassDef glyph="u1F4DA" class="1"/>
      <ClassDef glyph="u1F4DB" class="1"/>
      <ClassDef glyph="u1F4DC" class="1"/>
      <ClassDef glyph="u1F4DD" class="1"/>
      <ClassDef glyph="u1F4DE" class="1"/>
      <ClassDef glyph="u1F4DF" class="1"/>
      <ClassDef glyph="u1F4E0" class="1"/>
      <ClassDef glyph="u1F4E1" class="1"/>
      <ClassDef glyph="u1F4E2" class="1"/>
      <ClassDef glyph="u1F4E3" class="1"/>
      <ClassDef glyph="u1F4E4" class="1"/>
      <ClassDef glyph="u1F4E5" class="1"/>
      <ClassDef glyph="u1F4E6" class="1"/>
      <ClassDef glyph="u1F4E7" class="1"/>
      <ClassDef glyph="u1F4E8" class="1"/>
      <ClassDef glyph="u1F4E9" class="1"/>
      <ClassDef glyph="u1F4EA" class="1"/>
      <ClassDef glyph="u1F4EB" class="1"/>
      <ClassDef glyph="u1F4EC" class="1"/>
      <ClassDef glyph="u1F4ED" class="1"/>
      <ClassDef glyph="u1F4EE" class="1"/>
      <ClassDef glyph="u1F4EF" class="1"/>
      <ClassDef glyph="u1F4F0" class="1"/>
      <ClassDef glyph="u1F4F1" class="1"/>
      <ClassDef glyph="u1F4F2" class="1"/>
      <ClassDef glyph="u1F4F3" class="1"/>
      <ClassDef glyph="u1F4F4" class="1"/>
      <ClassDef glyph="u1F4F5" class="1"/>
      <ClassDef glyph="u1F4F6" class="1"/>
      <ClassDef glyph="u1F4F7" class="1"/>
      <ClassDef glyph="u1F4F8" class="1"/>
      <ClassDef glyph="u1F4F9" class="1"/>
      <ClassDef glyph="u1F4FA" class="1"/>
      <ClassDef glyph="u1F4FB" class="1"/>
      <ClassDef glyph="u1F4FC" class="1"/>
      <ClassDef glyph="u1F4FD" class="1"/>
      <ClassDef glyph="u1F4FF" class="1"/>
      <ClassDef glyph="u1F500" class="1"/>
      <ClassDef glyph="u1F501" class="1"/>
      <ClassDef glyph="u1F502" class="1"/>
      <ClassDef glyph="u1F503" class="1"/>
      <ClassDef glyph="u1F504" class="1"/>
      <ClassDef glyph="u1F505" class="1"/>
      <ClassDef glyph="u1F506" class="1"/>
      <ClassDef glyph="u1F507" class="1"/>
      <ClassDef glyph="u1F508" class="1"/>
      <ClassDef glyph="u1F509" class="1"/>
      <ClassDef glyph="u1F50A" class="1"/>
      <ClassDef glyph="u1F50B" class="1"/>
      <ClassDef glyph="u1F50C" class="1"/>
      <ClassDef glyph="u1F50D" class="1"/>
      <ClassDef glyph="u1F50E" class="1"/>
      <ClassDef glyph="u1F50F" class="1"/>
      <ClassDef glyph="u1F510" class="1"/>
      <ClassDef glyph="u1F511" class="1"/>
      <ClassDef glyph="u1F512" class="1"/>
      <ClassDef glyph="u1F513" class="1"/>
      <ClassDef glyph="u1F514" class="1"/>
      <ClassDef glyph="u1F515" class="1"/>
      <ClassDef glyph="u1F516" class="1"/>
      <ClassDef glyph="u1F517" class="1"/>
      <ClassDef glyph="u1F518" class="1"/>
      <ClassDef glyph="u1F519" class="1"/>
      <ClassDef glyph="u1F51A" class="1"/>
      <ClassDef glyph="u1F51B" class="1"/>
      <ClassDef glyph="u1F51C" class="1"/>
      <ClassDef glyph="u1F51D" class="1"/>
      <ClassDef glyph="u1F51E" class="1"/>
      <ClassDef glyph="u1F51F" class="1"/>
      <ClassDef glyph="u1F520" class="1"/>
      <ClassDef glyph="u1F521" class="1"/>
      <ClassDef glyph="u1F522" class="1"/>
      <ClassDef glyph="u1F523" class="1"/>
      <ClassDef glyph="u1F524" class="1"/>
      <ClassDef glyph="u1F525" class="1"/>
      <ClassDef glyph="u1F526" class="1"/>
      <ClassDef glyph="u1F527" class="1"/>
      <ClassDef glyph="u1F528" class="1"/>
      <ClassDef glyph="u1F529" class="1"/>
      <ClassDef glyph="u1F52A" class="1"/>
      <ClassDef glyph="u1F52B" class="1"/>
      <ClassDef glyph="u1F52C" class="1"/>
      <ClassDef glyph="u1F52D" class="1"/>
      <ClassDef glyph="u1F52E" class="1"/>
      <ClassDef glyph="u1F52F" class="1"/>
      <ClassDef glyph="u1F530" class="1"/>
      <ClassDef glyph="u1F531" class="1"/>
      <ClassDef glyph="u1F532" class="1"/>
      <ClassDef glyph="u1F533" class="1"/>
      <ClassDef glyph="u1F534" class="1"/>
      <ClassDef glyph="u1F535" class="1"/>
      <ClassDef glyph="u1F536" class="1"/>
      <ClassDef glyph="u1F537" class="1"/>
      <ClassDef glyph="u1F538" class="1"/>
      <ClassDef glyph="u1F539" class="1"/>
      <ClassDef glyph="u1F53A" class="1"/>
      <ClassDef glyph="u1F53B" class="1"/>
      <ClassDef glyph="u1F53C" class="1"/>
      <ClassDef glyph="u1F53D" class="1"/>
      <ClassDef glyph="u1F549" class="1"/>
      <ClassDef glyph="u1F54A" class="1"/>
      <ClassDef glyph="u1F54B" class="1"/>
      <ClassDef glyph="u1F54C" class="1"/>
      <ClassDef glyph="u1F54D" class="1"/>
      <ClassDef glyph="u1F54E" class="1"/>
      <ClassDef glyph="u1F550" class="1"/>
      <ClassDef glyph="u1F551" class="1"/>
      <ClassDef glyph="u1F552" class="1"/>
      <ClassDef glyph="u1F553" class="1"/>
      <ClassDef glyph="u1F554" class="1"/>
      <ClassDef glyph="u1F555" class="1"/>
      <ClassDef glyph="u1F556" class="1"/>
      <ClassDef glyph="u1F557" class="1"/>
      <ClassDef glyph="u1F558" class="1"/>
      <ClassDef glyph="u1F559" class="1"/>
      <ClassDef glyph="u1F55A" class="1"/>
      <ClassDef glyph="u1F55B" class="1"/>
      <ClassDef glyph="u1F55C" class="1"/>
      <ClassDef glyph="u1F55D" class="1"/>
      <ClassDef glyph="u1F55E" class="1"/>
      <ClassDef glyph="u1F55F" class="1"/>
      <ClassDef glyph="u1F560" class="1"/>
      <ClassDef glyph="u1F561" class="1"/>
      <ClassDef glyph="u1F562" class="1"/>
      <ClassDef glyph="u1F563" class="1"/>
      <ClassDef glyph="u1F564" class="1"/>
      <ClassDef glyph="u1F565" class="1"/>
      <ClassDef glyph="u1F566" class="1"/>
      <ClassDef glyph="u1F567" class="1"/>
      <ClassDef glyph="u1F56F" class="1"/>
      <ClassDef glyph="u1F570" class="1"/>
      <ClassDef glyph="u1F573" class="1"/>
      <ClassDef glyph="u1F574" class="1"/>
      <ClassDef glyph="u1F575" class="1"/>
      <ClassDef glyph="u1F576" class="1"/>
      <ClassDef glyph="u1F577" class="1"/>
      <ClassDef glyph="u1F578" class="1"/>
      <ClassDef glyph="u1F579" class="1"/>
      <ClassDef glyph="u1F587" class="1"/>
      <ClassDef glyph="u1F58A" class="1"/>
      <ClassDef glyph="u1F58B" class="1"/>
      <ClassDef glyph="u1F58C" class="1"/>
      <ClassDef glyph="u1F58D" class="1"/>
      <ClassDef glyph="u1F590.0" class="1"/>
      <ClassDef glyph="u1F590.1" class="2"/>
      <ClassDef glyph="u1F590.2" class="2"/>
      <ClassDef glyph="u1F590.3" class="2"/>
      <ClassDef glyph="u1F590.4" class="2"/>
      <ClassDef glyph="u1F590.5" class="2"/>
      <ClassDef glyph="u1F595.0" class="1"/>
      <ClassDef glyph="u1F595.1" class="2"/>
      <ClassDef glyph="u1F595.2" class="2"/>
      <ClassDef glyph="u1F595.3" class="2"/>
      <ClassDef glyph="u1F595.4" class="2"/>
      <ClassDef glyph="u1F595.5" class="2"/>
      <ClassDef glyph="u1F596.0" class="1"/>
      <ClassDef glyph="u1F596.1" class="2"/>
      <ClassDef glyph="u1F596.2" class="2"/>
      <ClassDef glyph="u1F596.3" class="2"/>
      <ClassDef glyph="u1F596.4" class="2"/>
      <ClassDef glyph="u1F596.5" class="2"/>
      <ClassDef glyph="u1F5A5" class="1"/>
      <ClassDef glyph="u1F5A8" class="1"/>
      <ClassDef glyph="u1F5B1" class="1"/>
      <ClassDef glyph="u1F5B2" class="1"/>
      <ClassDef glyph="u1F5BC" class="1"/>
      <ClassDef glyph="u1F5C2" class="1"/>
      <ClassDef glyph="u1F5C3" class="1"/>
      <ClassDef glyph="u1F5C4" class="1"/>
      <ClassDef glyph="u1F5D1" class="1"/>
      <ClassDef glyph="u1F5D2" class="1"/>
      <ClassDef glyph="u1F5D3" class="1"/>
      <ClassDef glyph="u1F5DC" class="1"/>
      <ClassDef glyph="u1F5DD" class="1"/>
      <ClassDef glyph="u1F5DE" class="1"/>
      <ClassDef glyph="u1F5E1" class="1"/>
      <ClassDef glyph="u1F5E3" class="1"/>
      <ClassDef glyph="u1F5E8" class="1"/>
      <ClassDef glyph="u1F5EF" class="1"/>
      <ClassDef glyph="u1F5F3" class="1"/>
      <ClassDef glyph="u1F5FA" class="1"/>
      <ClassDef glyph="u1F5FB" class="1"/>
      <ClassDef glyph="u1F5FC" class="1"/>
      <ClassDef glyph="u1F5FD" class="1"/>
      <ClassDef glyph="u1F5FE" class="1"/>
      <ClassDef glyph="u1F5FF" class="1"/>
      <ClassDef glyph="u1F600" class="1"/>
      <ClassDef glyph="u1F601" class="1"/>
      <ClassDef glyph="u1F602" class="1"/>
      <ClassDef glyph="u1F603" class="1"/>
      <ClassDef glyph="u1F604" class="1"/>
      <ClassDef glyph="u1F605" class="1"/>
      <ClassDef glyph="u1F606" class="1"/>
      <ClassDef glyph="u1F607" class="1"/>
      <ClassDef glyph="u1F608" class="1"/>
      <ClassDef glyph="u1F609" class="1"/>
      <ClassDef glyph="u1F60A" class="1"/>
      <ClassDef glyph="u1F60B" class="1"/>
      <ClassDef glyph="u1F60C" class="1"/>
      <ClassDef glyph="u1F60D" class="1"/>
      <ClassDef glyph="u1F60E" class="1"/>
      <ClassDef glyph="u1F60F" class="1"/>
      <ClassDef glyph="u1F610" class="1"/>
      <ClassDef glyph="u1F611" class="1"/>
      <ClassDef glyph="u1F612" class="1"/>
      <ClassDef glyph="u1F613" class="1"/>
      <ClassDef glyph="u1F614" class="1"/>
      <ClassDef glyph="u1F615" class="1"/>
      <ClassDef glyph="u1F616" class="1"/>
      <ClassDef glyph="u1F617" class="1"/>
      <ClassDef glyph="u1F618" class="1"/>
      <ClassDef glyph="u1F619" class="1"/>
      <ClassDef glyph="u1F61A" class="1"/>
      <ClassDef glyph="u1F61B" class="1"/>
      <ClassDef glyph="u1F61C" class="1"/>
      <ClassDef glyph="u1F61D" class="1"/>
      <ClassDef glyph="u1F61E" class="1"/>
      <ClassDef glyph="u1F61F" class="1"/>
      <ClassDef glyph="u1F620" class="1"/>
      <ClassDef glyph="u1F621" class="1"/>
      <ClassDef glyph="u1F622" class="1"/>
      <ClassDef glyph="u1F623" class="1"/>
      <ClassDef glyph="u1F624" class="1"/>
      <ClassDef glyph="u1F625" class="1"/>
      <ClassDef glyph="u1F626" class="1"/>
      <ClassDef glyph="u1F627" class="1"/>
      <ClassDef glyph="u1F628" class="1"/>
      <ClassDef glyph="u1F629" class="1"/>
      <ClassDef glyph="u1F62A" class="1"/>
      <ClassDef glyph="u1F62B" class="1"/>
      <ClassDef glyph="u1F62C" class="1"/>
      <ClassDef glyph="u1F62D" class="1"/>
      <ClassDef glyph="u1F62E" class="1"/>
      <ClassDef glyph="u1F62F" class="1"/>
      <ClassDef glyph="u1F630" class="1"/>
      <ClassDef glyph="u1F631" class="1"/>
      <ClassDef glyph="u1F632" class="1"/>
      <ClassDef glyph="u1F633" class="1"/>
      <ClassDef glyph="u1F634" class="1"/>
      <ClassDef glyph="u1F635" class="1"/>
      <ClassDef glyph="u1F636" class="1"/>
      <ClassDef glyph="u1F637" class="1"/>
      <ClassDef glyph="u1F638" class="1"/>
      <ClassDef glyph="u1F639" class="1"/>
      <ClassDef glyph="u1F63A" class="1"/>
      <ClassDef glyph="u1F63B" class="1"/>
      <ClassDef glyph="u1F63C" class="1"/>
      <ClassDef glyph="u1F63D" class="1"/>
      <ClassDef glyph="u1F63E" class="1"/>
      <ClassDef glyph="u1F63F" class="1"/>
      <ClassDef glyph="u1F640" class="1"/>
      <ClassDef glyph="u1F641" class="1"/>
      <ClassDef glyph="u1F642" class="1"/>
      <ClassDef glyph="u1F643" class="1"/>
      <ClassDef glyph="u1F644" class="1"/>
      <ClassDef glyph="u1F645.0" class="1"/>
      <ClassDef glyph="u1F645.1" class="2"/>
      <ClassDef glyph="u1F645.2" class="2"/>
      <ClassDef glyph="u1F645.3" class="2"/>
      <ClassDef glyph="u1F645.4" class="2"/>
      <ClassDef glyph="u1F645.5" class="2"/>
      <ClassDef glyph="u1F646.0" class="1"/>
      <ClassDef glyph="u1F646.1" class="2"/>
      <ClassDef glyph="u1F646.2" class="2"/>
      <ClassDef glyph="u1F646.3" class="2"/>
      <ClassDef glyph="u1F646.4" class="2"/>
      <ClassDef glyph="u1F646.5" class="2"/>
      <ClassDef glyph="u1F647.0" class="1"/>
      <ClassDef glyph="u1F647.1" class="2"/>
      <ClassDef glyph="u1F647.2" class="2"/>
      <ClassDef glyph="u1F647.3" class="2"/>
      <ClassDef glyph="u1F647.4" class="2"/>
      <ClassDef glyph="u1F647.5" class="2"/>
      <ClassDef glyph="u1F648" class="1"/>
      <ClassDef glyph="u1F649" class="1"/>
      <ClassDef glyph="u1F64A" class="1"/>
      <ClassDef glyph="u1F64B.0" class="1"/>
      <ClassDef glyph="u1F64B.1" class="2"/>
      <ClassDef glyph="u1F64B.2" class="2"/>
      <ClassDef glyph="u1F64B.3" class="2"/>
      <ClassDef glyph="u1F64B.4" class="2"/>
      <ClassDef glyph="u1F64B.5" class="2"/>
      <ClassDef glyph="u1F64C.0" class="1"/>
      <ClassDef glyph="u1F64C.1" class="2"/>
      <ClassDef glyph="u1F64C.2" class="2"/>
      <ClassDef glyph="u1F64C.3" class="2"/>
      <ClassDef glyph="u1F64C.4" class="2"/>
      <ClassDef glyph="u1F64C.5" class="2"/>
      <ClassDef glyph="u1F64D.0" class="1"/>
      <ClassDef glyph="u1F64D.1" class="2"/>
      <ClassDef glyph="u1F64D.2" class="2"/>
      <ClassDef glyph="u1F64D.3" class="2"/>
      <ClassDef glyph="u1F64D.4" class="2"/>
      <ClassDef glyph="u1F64D.5" class="2"/>
      <ClassDef glyph="u1F64E.0" class="1"/>
      <ClassDef glyph="u1F64E.1" class="2"/>
      <ClassDef glyph="u1F64E.2" class="2"/>
      <ClassDef glyph="u1F64E.3" class="2"/>
      <ClassDef glyph="u1F64E.4" class="2"/>
      <ClassDef glyph="u1F64E.5" class="2"/>
      <ClassDef glyph="u1F64F.0" class="1"/>
      <ClassDef glyph="u1F64F.1" class="2"/>
      <ClassDef glyph="u1F64F.2" class="2"/>
      <ClassDef glyph="u1F64F.3" class="2"/>
      <ClassDef glyph="u1F64F.4" class="2"/>
      <ClassDef glyph="u1F64F.5" class="2"/>
      <ClassDef glyph="u1F680" class="1"/>
      <ClassDef glyph="u1F681" class="1"/>
      <ClassDef glyph="u1F682" class="1"/>
      <ClassDef glyph="u1F683" class="1"/>
      <ClassDef glyph="u1F684" class="1"/>
      <ClassDef glyph="u1F685" class="1"/>
      <ClassDef glyph="u1F686" class="1"/>
      <ClassDef glyph="u1F687" class="1"/>
      <ClassDef glyph="u1F688" class="1"/>
      <ClassDef glyph="u1F689" class="1"/>
      <ClassDef glyph="u1F68A" class="1"/>
      <ClassDef glyph="u1F68B" class="1"/>
      <ClassDef glyph="u1F68C" class="1"/>
      <ClassDef glyph="u1F68D" class="1"/>
      <ClassDef glyph="u1F68E" class="1"/>
      <ClassDef glyph="u1F68F" class="1"/>
      <ClassDef glyph="u1F690" class="1"/>
      <ClassDef glyph="u1F691" class="1"/>
      <ClassDef glyph="u1F692" class="1"/>
      <ClassDef glyph="u1F693" class="1"/>
      <ClassDef glyph="u1F694" class="1"/>
      <ClassDef glyph="u1F695" class="1"/>
      <ClassDef glyph="u1F696" class="1"/>
      <ClassDef glyph="u1F697" class="1"/>
      <ClassDef glyph="u1F698" class="1"/>
      <ClassDef glyph="u1F699" class="1"/>
      <ClassDef glyph="u1F69A" class="1"/>
      <ClassDef glyph="u1F69B" class="1"/>
      <ClassDef glyph="u1F69C" class="1"/>
      <ClassDef glyph="u1F69D" class="1"/>
      <ClassDef glyph="u1F69E" class="1"/>
      <ClassDef glyph="u1F69F" class="1"/>
      <ClassDef glyph="u1F6A0" class="1"/>
      <ClassDef glyph="u1F6A1" class="1"/>
      <ClassDef glyph="u1F6A2" class="1"/>
      <ClassDef glyph="u1F6A3.0" class="1"/>
      <ClassDef glyph="u1F6A3.1" class="2"/>
      <ClassDef glyph="u1F6A3.2" class="2"/>
      <ClassDef glyph="u1F6A3.3" class="2"/>
      <ClassDef glyph="u1F6A3.4" class="2"/>
      <ClassDef glyph="u1F6A3.5" class="2"/>
      <ClassDef glyph="u1F6A4" class="1"/>
      <ClassDef glyph="u1F6A5" class="1"/>
      <ClassDef glyph="u1F6A6" class="1"/>
      <ClassDef glyph="u1F6A7" class="1"/>
      <ClassDef glyph="u1F6A8" class="1"/>
      <ClassDef glyph="u1F6A9" class="1"/>
      <ClassDef glyph="u1F6AA" class="1"/>
      <ClassDef glyph="u1F6AB" class="1"/>
      <ClassDef glyph="u1F6AC" class="1"/>
      <ClassDef glyph="u1F6AD" class="1"/>
      <ClassDef glyph="u1F6AE" class="1"/>
      <ClassDef glyph="u1F6AF" class="1"/>
      <ClassDef glyph="u1F6B0" class="1"/>
      <ClassDef glyph="u1F6B1" class="1"/>
      <ClassDef glyph="u1F6B2" class="1"/>
      <ClassDef glyph="u1F6B3" class="1"/>
      <ClassDef glyph="u1F6B4.0" class="1"/>
      <ClassDef glyph="u1F6B4.1" class="2"/>
      <ClassDef glyph="u1F6B4.2" class="2"/>
      <ClassDef glyph="u1F6B4.3" class="2"/>
      <ClassDef glyph="u1F6B4.4" class="2"/>
      <ClassDef glyph="u1F6B4.5" class="2"/>
      <ClassDef glyph="u1F6B5.0" class="1"/>
      <ClassDef glyph="u1F6B5.1" class="2"/>
      <ClassDef glyph="u1F6B5.2" class="2"/>
      <ClassDef glyph="u1F6B5.3" class="2"/>
      <ClassDef glyph="u1F6B5.4" class="2"/>
      <ClassDef glyph="u1F6B5.5" class="2"/>
      <ClassDef glyph="u1F6B6.0" class="1"/>
      <ClassDef glyph="u1F6B6.1" class="2"/>
      <ClassDef glyph="u1F6B6.2" class="2"/>
      <ClassDef glyph="u1F6B6.3" class="2"/>
      <ClassDef glyph="u1F6B6.4" class="2"/>
      <ClassDef glyph="u1F6B6.5" class="2"/>
      <ClassDef glyph="u1F6B7" class="1"/>
      <ClassDef glyph="u1F6B8" class="1"/>
      <ClassDef glyph="u1F6B9" class="1"/>
      <ClassDef glyph="u1F6BA" class="1"/>
      <ClassDef glyph="u1F6BB" class="1"/>
      <ClassDef glyph="u1F6BC" class="1"/>
      <ClassDef glyph="u1F6BD" class="1"/>
      <ClassDef glyph="u1F6BE" class="1"/>
      <ClassDef glyph="u1F6BF" class="1"/>
      <ClassDef glyph="u1F6C0.0" class="1"/>
      <ClassDef glyph="u1F6C0.1" class="2"/>
      <ClassDef glyph="u1F6C0.2" class="2"/>
      <ClassDef glyph="u1F6C0.3" class="2"/>
      <ClassDef glyph="u1F6C0.4" class="2"/>
      <ClassDef glyph="u1F6C0.5" class="2"/>
      <ClassDef glyph="u1F6C1" class="1"/>
      <ClassDef glyph="u1F6C2" class="1"/>
      <ClassDef glyph="u1F6C3" class="1"/>
      <ClassDef glyph="u1F6C4" class="1"/>
      <ClassDef glyph="u1F6C5" class="1"/>
      <ClassDef glyph="u1F6CB" class="1"/>
      <ClassDef glyph="u1F6CC" class="1"/>
      <ClassDef glyph="u1F6CD" class="1"/>
      <ClassDef glyph="u1F6CE" class="1"/>
      <ClassDef glyph="u1F6CF" class="1"/>
      <ClassDef glyph="u1F6D0" class="1"/>
      <ClassDef glyph="u1F6E0" class="1"/>
      <ClassDef glyph="u1F6E1" class="1"/>
      <ClassDef glyph="u1F6E2" class="1"/>
      <ClassDef glyph="u1F6E3" class="1"/>
      <ClassDef glyph="u1F6E4" class="1"/>
      <ClassDef glyph="u1F6E5" class="1"/>
      <ClassDef glyph="u1F6E9" class="1"/>
      <ClassDef glyph="u1F6EB" class="1"/>
      <ClassDef glyph="u1F6EC" class="1"/>
      <ClassDef glyph="u1F6F0" class="1"/>
      <ClassDef glyph="u1F6F3" class="1"/>
      <ClassDef glyph="u1F910" class="1"/>
      <ClassDef glyph="u1F911" class="1"/>
      <ClassDef glyph="u1F912" class="1"/>
      <ClassDef glyph="u1F913" class="1"/>
      <ClassDef glyph="u1F914" class="1"/>
      <ClassDef glyph="u1F915" class="1"/>
      <ClassDef glyph="u1F916" class="1"/>
      <ClassDef glyph="u1F917" class="1"/>
      <ClassDef glyph="u1F918.0" class="1"/>
      <ClassDef glyph="u1F918.1" class="2"/>
      <ClassDef glyph="u1F918.2" class="2"/>
      <ClassDef glyph="u1F918.3" class="2"/>
      <ClassDef glyph="u1F918.4" class="2"/>
      <ClassDef glyph="u1F918.5" class="2"/>
      <ClassDef glyph="u1F980" class="1"/>
      <ClassDef glyph="u1F981" class="1"/>
      <ClassDef glyph="u1F982" class="1"/>
      <ClassDef glyph="u1F983" class="1"/>
      <ClassDef glyph="u1F984" class="1"/>
      <ClassDef glyph="u1F9C0" class="1"/>
      <ClassDef glyph="u203C" class="1"/>
      <ClassDef glyph="u2049" class="1"/>
      <ClassDef glyph="u20E3" class="1"/>
      <ClassDef glyph="u2122" class="1"/>
      <ClassDef glyph="u2139" class="1"/>
      <ClassDef glyph="u2194" class="1"/>
      <ClassDef glyph="u2195" class="1"/>
      <ClassDef glyph="u2196" class="1"/>
      <ClassDef glyph="u2197" class="1"/>
      <ClassDef glyph="u2198" class="1"/>
      <ClassDef glyph="u2199" class="1"/>
      <ClassDef glyph="u21A9" class="1"/>
      <ClassDef glyph="u21AA" class="1"/>
      <ClassDef glyph="u231A" class="1"/>
      <ClassDef glyph="u231B" class="1"/>
      <ClassDef glyph="u2328" class="1"/>
      <ClassDef glyph="u23E9" class="1"/>
      <ClassDef glyph="u23EA" class="1"/>
      <ClassDef glyph="u23EB" class="1"/>
      <ClassDef glyph="u23EC" class="1"/>
      <ClassDef glyph="u23ED" class="1"/>
      <ClassDef glyph="u23EE" class="1"/>
      <ClassDef glyph="u23EF" class="1"/>
      <ClassDef glyph="u23F0" class="1"/>
      <ClassDef glyph="u23F1" class="1"/>
      <ClassDef glyph="u23F2" class="1"/>
      <ClassDef glyph="u23F3" class="1"/>
      <ClassDef glyph="u23F8" class="1"/>
      <ClassDef glyph="u23F9" class="1"/>
      <ClassDef glyph="u23FA" class="1"/>
      <ClassDef glyph="u24C2" class="1"/>
      <ClassDef glyph="u25AA" class="1"/>
      <ClassDef glyph="u25AB" class="1"/>
      <ClassDef glyph="u25B6" class="1"/>
      <ClassDef glyph="u25C0" class="1"/>
      <ClassDef glyph="u25FB" class="1"/>
      <ClassDef glyph="u25FC" class="1"/>
      <ClassDef glyph="u25FD" class="1"/>
      <ClassDef glyph="u25FE" class="1"/>
      <ClassDef glyph="u2600" class="1"/>
      <ClassDef glyph="u2601" class="1"/>
      <ClassDef glyph="u2602" class="1"/>
      <ClassDef glyph="u2603" class="1"/>
      <ClassDef glyph="u2604" class="1"/>
      <ClassDef glyph="u260E" class="1"/>
      <ClassDef glyph="u2611" class="1"/>
      <ClassDef glyph="u2614" class="1"/>
      <ClassDef glyph="u2615" class="1"/>
      <ClassDef glyph="u2618" class="1"/>
      <ClassDef glyph="u261D.0" class="1"/>
      <ClassDef glyph="u261D.1" class="2"/>
      <ClassDef glyph="u261D.2" class="2"/>
      <ClassDef glyph="u261D.3" class="2"/>
      <ClassDef glyph="u261D.4" class="2"/>
      <ClassDef glyph="u261D.5" class="2"/>
      <ClassDef glyph="u2620" class="1"/>
      <ClassDef glyph="u2622" class="1"/>
      <ClassDef glyph="u2623" class="1"/>
      <ClassDef glyph="u2626" class="1"/>
      <ClassDef glyph="u262A" class="1"/>
      <ClassDef glyph="u262E" class="1"/>
      <ClassDef glyph="u262F" class="1"/>
      <ClassDef glyph="u2638" class="1"/>
      <ClassDef glyph="u2639" class="1"/>
      <ClassDef glyph="u263A" class="1"/>
      <ClassDef glyph="u2648" class="1"/>
      <ClassDef glyph="u2649" class="1"/>
      <ClassDef glyph="u264A" class="1"/>
      <ClassDef glyph="u264B" class="1"/>
      <ClassDef glyph="u264C" class="1"/>
      <ClassDef glyph="u264D" class="1"/>
      <ClassDef glyph="u264E" class="1"/>
      <ClassDef glyph="u264F" class="1"/>
      <ClassDef glyph="u2650" class="1"/>
      <ClassDef glyph="u2651" class="1"/>
      <ClassDef glyph="u2652" class="1"/>
      <ClassDef glyph="u2653" class="1"/>
      <ClassDef glyph="u2660" class="1"/>
      <ClassDef glyph="u2663" class="1"/>
      <ClassDef glyph="u2665" class="1"/>
      <ClassDef glyph="u2666" class="1"/>
      <ClassDef glyph="u2668" class="1"/>
      <ClassDef glyph="u267B" class="1"/>
      <ClassDef glyph="u267F" class="1"/>
      <ClassDef glyph="u2692" class="1"/>
      <ClassDef glyph="u2693" class="1"/>
      <ClassDef glyph="u2694" class="1"/>
      <ClassDef glyph="u2696" class="1"/>
      <ClassDef glyph="u2697" class="1"/>
      <ClassDef glyph="u2699" class="1"/>
      <ClassDef glyph="u269B" class="1"/>
      <ClassDef glyph="u269C" class="1"/>
      <ClassDef glyph="u26A0" class="1"/>
      <ClassDef glyph="u26A1" class="1"/>
      <ClassDef glyph="u26AA" class="1"/>
      <ClassDef glyph="u26AB" class="1"/>
      <ClassDef glyph="u26B0" class="1"/>
      <ClassDef glyph="u26B1" class="1"/>
      <ClassDef glyph="u26BD" class="1"/>
      <ClassDef glyph="u26BE" class="1"/>
      <ClassDef glyph="u26C4" class="1"/>
      <ClassDef glyph="u26C5" class="1"/>
      <ClassDef glyph="u26C8" class="1"/>
      <ClassDef glyph="u26CE" class="1"/>
      <ClassDef glyph="u26CF" class="1"/>
      <ClassDef glyph="u26D1" class="1"/>
      <ClassDef glyph="u26D3" class="1"/>
      <ClassDef glyph="u26D4" class="1"/>
      <ClassDef glyph="u26E9" class="1"/>
      <ClassDef glyph="u26EA" class="1"/>
      <ClassDef glyph="u26F0" class="1"/>
      <ClassDef glyph="u26F1" class="1"/>
      <ClassDef glyph="u26F2" class="1"/>
      <ClassDef glyph="u26F3" class="1"/>
      <ClassDef glyph="u26F4" class="1"/>
      <ClassDef glyph="u26F5" class="1"/>
      <ClassDef glyph="u26F7" class="1"/>
      <ClassDef glyph="u26F8" class="1"/>
      <ClassDef glyph="u26F9.0" class="1"/>
      <ClassDef glyph="u26F9.1" class="2"/>
      <ClassDef glyph="u26F9.2" class="2"/>
      <ClassDef glyph="u26F9.3" class="2"/>
      <ClassDef glyph="u26F9.4" class="2"/>
      <ClassDef glyph="u26F9.5" class="2"/>
      <ClassDef glyph="u26FA" class="1"/>
      <ClassDef glyph="u26FD" class="1"/>
      <ClassDef glyph="u2702" class="1"/>
      <ClassDef glyph="u2705" class="1"/>
      <ClassDef glyph="u2708" class="1"/>
      <ClassDef glyph="u2709" class="1"/>
      <ClassDef glyph="u270A.0" class="1"/>
      <ClassDef glyph="u270A.1" class="2"/>
      <ClassDef glyph="u270A.2" class="2"/>
      <ClassDef glyph="u270A.3" class="2"/>
      <ClassDef glyph="u270A.4" class="2"/>
      <ClassDef glyph="u270A.5" class="2"/>
      <ClassDef glyph="u270B.0" class="1"/>
      <ClassDef glyph="u270B.1" class="2"/>
      <ClassDef glyph="u270B.2" class="2"/>
      <ClassDef glyph="u270B.3" class="2"/>
      <ClassDef glyph="u270B.4" class="2"/>
      <ClassDef glyph="u270B.5" class="2"/>
      <ClassDef glyph="u270C.0" class="1"/>
      <ClassDef glyph="u270C.1" class="2"/>
      <ClassDef glyph="u270C.2" class="2"/>
      <ClassDef glyph="u270C.3" class="2"/>
      <ClassDef glyph="u270C.4" class="2"/>
      <ClassDef glyph="u270C.5" class="2"/>
      <ClassDef glyph="u270D.0" class="1"/>
      <ClassDef glyph="u270D.1" class="2"/>
      <ClassDef glyph="u270D.2" class="2"/>
      <ClassDef glyph="u270D.3" class="2"/>
      <ClassDef glyph="u270D.4" class="2"/>
      <ClassDef glyph="u270D.5" class="2"/>
      <ClassDef glyph="u270F" class="1"/>
      <ClassDef glyph="u2712" class="1"/>
      <ClassDef glyph="u2714" class="1"/>
      <ClassDef glyph="u2716" class="1"/>
      <ClassDef glyph="u271D" class="1"/>
      <ClassDef glyph="u2721" class="1"/>
      <ClassDef glyph="u2728" class="1"/>
      <ClassDef glyph="u2733" class="1"/>
      <ClassDef glyph="u2734" class="1"/>
      <ClassDef glyph="u2744" class="1"/>
      <ClassDef glyph="u2747" class="1"/>
      <ClassDef glyph="u274C" class="1"/>
      <ClassDef glyph="u274E" class="1"/>
      <ClassDef glyph="u2753" class="1"/>
      <ClassDef glyph="u2754" class="1"/>
      <ClassDef glyph="u2755" class="1"/>
      <ClassDef glyph="u2757" class="1"/>
      <ClassDef glyph="u2763" class="1"/>
      <ClassDef glyph="u2764" class="1"/>
      <ClassDef glyph="u2795" class="1"/>
      <ClassDef glyph="u2796" class="1"/>
      <ClassDef glyph="u2797" class="1"/>
      <ClassDef glyph="u27A1" class="1"/>
      <ClassDef glyph="u27B0" class="1"/>
      <ClassDef glyph="u27BF" class="1"/>
      <ClassDef glyph="u2934" class="1"/>
      <ClassDef glyph="u2935" class="1"/>
      <ClassDef glyph="u2B05" class="1"/>
      <ClassDef glyph="u2B06" class="1"/>
      <ClassDef glyph="u2B07" class="1"/>
      <ClassDef glyph="u2B1B" class="1"/>
      <ClassDef glyph="u2B1C" class="1"/>
      <ClassDef glyph="u2B50" class="1"/>
      <ClassDef glyph="u2B55" class="1"/>
      <ClassDef glyph="u3030" class="1"/>
      <ClassDef glyph="u303D" class="1"/>
      <ClassDef glyph="u3297" class="1"/>
      <ClassDef glyph="u3299" class="1"/>
      <ClassDef glyph="uniFE0F" class="1"/>
      <ClassDef glyph="zero" class="1"/>
    </GlyphClassDef>
    <LigCaretList>
      <Coverage>
      </Coverage>
      <!-- LigGlyphCount=0 -->
    </LigCaretList>
  </GDEF>

  <GSUB>
    <Version value="1.0"/>
    <ScriptList>
      <!-- ScriptCount=1 -->
      <ScriptRecord index="0">
        <ScriptTag value="DFLT"/>
        <Script>
          <DefaultLangSys>
            <ReqFeatureIndex value="65535"/>
            <!-- FeatureCount=1 -->
            <FeatureIndex index="0" value="0"/>
          </DefaultLangSys>
          <!-- LangSysCount=0 -->
        </Script>
      </ScriptRecord>
    </ScriptList>
    <FeatureList>
      <!-- FeatureCount=1 -->
      <FeatureRecord index="0">
        <FeatureTag value="rlig"/>
        <Feature>
          <!-- LookupCount=4 -->
          <LookupListIndex index="0" value="0"/>
          <LookupListIndex index="1" value="1"/>
          <LookupListIndex index="2" value="2"/>
          <LookupListIndex index="3" value="3"/>
        </Feature>
      </FeatureRecord>
    </FeatureList>
    <LookupList>
      <!-- LookupCount=4 -->
      <Lookup index="0">
        <!-- LookupType=4 -->
        <LookupFlag value="0"/>
        <!-- SubTableCount=1 -->
        <LigatureSubst index="0">
          <LigatureSet glyph="asterisk">
            <Ligature components="uniFE0F,u20E3" glyph="u002A_u20E3"/>
          </LigatureSet>
          <LigatureSet glyph="eight">
            <Ligature components="uniFE0F,u20E3" glyph="u0038_u20E3"/>
          </LigatureSet>
          <LigatureSet glyph="five">
            <Ligature components="uniFE0F,u20E3" glyph="u0035_u20E3"/>
          </LigatureSet>
          <LigatureSet glyph="four">
            <Ligature components="uniFE0F,u20E3" glyph="u0034_u20E3"/>
          </LigatureSet>
          <LigatureSet glyph="nine">
            <Ligature components="uniFE0F,u20E3" glyph="u0039_u20E3"/>
          </LigatureSet>
          <LigatureSet glyph="numbersign">
            <Ligature components="uniFE0F,u20E3" glyph="u0023_u20E3"/>
          </LigatureSet>
          <LigatureSet glyph="one">
            <Ligature components="uniFE0F,u20E3" glyph="u0031_u20E3"/>
          </LigatureSet>
          <LigatureSet glyph="seven">
            <Ligature components="uniFE0F,u20E3" glyph="u0037_u20E3"/>
          </LigatureSet>
          <LigatureSet glyph="six">
            <Ligature components="uniFE0F,u20E3" glyph="u0036_u20E3"/>
          </LigatureSet>
          <LigatureSet glyph="three">
            <Ligature components="uniFE0F,u20E3" glyph="u0033_u20E3"/>
          </LigatureSet>
          <LigatureSet glyph="two">
            <Ligature components="uniFE0F,u20E3" glyph="u0032_u20E3"/>
          </LigatureSet>
          <LigatureSet glyph="zero">
            <Ligature components="uniFE0F,u20E3" glyph="u0030_u20E3"/>
          </LigatureSet>
        </LigatureSubst>
      </Lookup>
      <Lookup index="1">
        <!-- LookupType=4 -->
        <LookupFlag value="0"/>
        <!-- SubTableCount=1 -->
        <LigatureSubst index="0">
          <LigatureSet glyph="asterisk">
            <Ligature components="u20E3" glyph="u002A_u20E3"/>
          </LigatureSet>
          <LigatureSet glyph="eight">
            <Ligature components="u20E3" glyph="u0038_u20E3"/>
          </LigatureSet>
          <LigatureSet glyph="five">
            <Ligature components="u20E3" glyph="u0035_u20E3"/>
          </LigatureSet>
          <LigatureSet glyph="four">
            <Ligature components="u20E3" glyph="u0034_u20E3"/>
          </LigatureSet>
          <LigatureSet glyph="nine">
            <Ligature components="u20E3" glyph="u0039_u20E3"/>
          </LigatureSet>
          <LigatureSet glyph="numbersign">
            <Ligature components="u20E3" glyph="u0023_u20E3"/>
          </LigatureSet>
          <LigatureSet glyph="one">
            <Ligature components="u20E3" glyph="u0031_u20E3"/>
          </LigatureSet>
          <LigatureSet glyph="seven">
            <Ligature components="u20E3" glyph="u0037_u20E3"/>
          </LigatureSet>
          <LigatureSet glyph="six">
            <Ligature components="u20E3" glyph="u0036_u20E3"/>
          </LigatureSet>
          <LigatureSet glyph="three">
            <Ligature components="u20E3" glyph="u0033_u20E3"/>
          </LigatureSet>
          <LigatureSet glyph="two">
            <Ligature components="u20E3" glyph="u0032_u20E3"/>
          </LigatureSet>
          <LigatureSet glyph="zero">
            <Ligature components="u20E3" glyph="u0030_u20E3"/>
          </LigatureSet>
        </LigatureSubst>
      </Lookup>
      <Lookup index="2">
        <!-- LookupType=4 -->
        <LookupFlag value="0"/>
        <!-- SubTableCount=1 -->
        <LigatureSubst index="0">
          <LigatureSet glyph="u1F1E6">
            <Ligature components="u1F1E8" glyph="u1F1F8_u1F1ED"/>
            <Ligature components="u1F1FF" glyph="u1F1E6_u1F1FF"/>
            <Ligature components="u1F1FD" glyph="u1F1E6_u1F1FD"/>
            <Ligature components="u1F1FC" glyph="u1F1E6_u1F1FC"/>
            <Ligature components="u1F1FA" glyph="u1F1E6_u1F1FA"/>
            <Ligature components="u1F1F9" glyph="u1F1E6_u1F1F9"/>
            <Ligature components="u1F1F8" glyph="u1F1E6_u1F1F8"/>
            <Ligature components="u1F1F7" glyph="u1F1E6_u1F1F7"/>
            <Ligature components="u1F1F6" glyph="u1F1E6_u1F1F6"/>
            <Ligature components="u1F1F4" glyph="u1F1E6_u1F1F4"/>
            <Ligature components="u1F1F2" glyph="u1F1E6_u1F1F2"/>
            <Ligature components="u1F1F1" glyph="u1F1E6_u1F1F1"/>
            <Ligature components="u1F1EE" glyph="u1F1E6_u1F1EE"/>
            <Ligature components="u1F1EC" glyph="u1F1E6_u1F1EC"/>
            <Ligature components="u1F1EB" glyph="u1F1E6_u1F1EB"/>
            <Ligature components="u1F1EA" glyph="u1F1E6_u1F1EA"/>
            <Ligature components="u1F1E9" glyph="u1F1E6_u1F1E9"/>
          </LigatureSet>
          <LigatureSet glyph="u1F1E7">
            <Ligature components="u1F1FB" glyph="u1F1F3_u1F1F4"/>
            <Ligature components="u1F1FF" glyph="u1F1E7_u1F1FF"/>
            <Ligature components="u1F1FE" glyph="u1F1E7_u1F1FE"/>
            <Ligature components="u1F1FC" glyph="u1F1E7_u1F1FC"/>
            <Ligature components="u1F1F9" glyph="u1F1E7_u1F1F9"/>
            <Ligature components="u1F1F8" glyph="u1F1E7_u1F1F8"/>
            <Ligature components="u1F1F7" glyph="u1F1E7_u1F1F7"/>
            <Ligature components="u1F1F6" glyph="u1F1E7_u1F1F6"/>
            <Ligature components="u1F1F4" glyph="u1F1E7_u1F1F4"/>
            <Ligature components="u1F1F3" glyph="u1F1E7_u1F1F3"/>
            <Ligature components="u1F1F2" glyph="u1F1E7_u1F1F2"/>
            <Ligature components="u1F1F1" glyph="u1F1E7_u1F1F1"/>
            <Ligature components="u1F1EF" glyph="u1F1E7_u1F1EF"/>
            <Ligature components="u1F1EE" glyph="u1F1E7_u1F1EE"/>
            <Ligature components="u1F1ED" glyph="u1F1E7_u1F1ED"/>
            <Ligature components="u1F1EC" glyph="u1F1E7_u1F1EC"/>
            <Ligature components="u1F1EB" glyph="u1F1E7_u1F1EB"/>
            <Ligature components="u1F1EA" glyph="u1F1E7_u1F1EA"/>
            <Ligature components="u1F1E9" glyph="u1F1E7_u1F1E9"/>
            <Ligature components="u1F1E7" glyph="u1F1E7_u1F1E7"/>
            <Ligature components="u1F1E6" glyph="u1F1E7_u1F1E6"/>
          </LigatureSet>
          <LigatureSet glyph="u1F1E8">
            <Ligature components="u1F1F5" glyph="u1F1EB_u1F1F7"/>
            <Ligature components="u1F1FF" glyph="u1F1E8_u1F1FF"/>
            <Ligature components="u1F1FE" glyph="u1F1E8_u1F1FE"/>
            <Ligature components="u1F1FD" glyph="u1F1E8_u1F1FD"/>
            <Ligature components="u1F1FC" glyph="u1F1E8_u1F1FC"/>
            <Ligature components="u1F1FB" glyph="u1F1E8_u1F1FB"/>
            <Ligature components="u1F1FA" glyph="u1F1E8_u1F1FA"/>
            <Ligature components="u1F1F7" glyph="u1F1E8_u1F1F7"/>
            <Ligature components="u1F1F4" glyph="u1F1E8_u1F1F4"/>
            <Ligature components="u1F1F3" glyph="u1F1E8_u1F1F3"/>
            <Ligature components="u1F1F2" glyph="u1F1E8_u1F1F2"/>
            <Ligature components="u1F1F1" glyph="u1F1E8_u1F1F1"/>
            <Ligature components="u1F1F0" glyph="u1F1E8_u1F1F0"/>
            <Ligature components="u1F1EE" glyph="u1F1E8_u1F1EE"/>
            <Ligature components="u1F1ED" glyph="u1F1E8_u1F1ED"/>
            <Ligature components="u1F1EC" glyph="u1F1E8_u1F1EC"/>
            <Ligature components="u1F1EB" glyph="u1F1E8_u1F1EB"/>
            <Ligature components="u1F1E9" glyph="u1F1E8_u1F1E9"/>
            <Ligature components="u1F1E8" glyph="u1F1E8_u1F1E8"/>
            <Ligature components="u1F1E6" glyph="u1F1E8_u1F1E6"/>
          </LigatureSet>
          <LigatureSet glyph="u1F1E9">
            <Ligature components="u1F1EC" glyph="u1F1EE_u1F1F4"/>
            <Ligature components="u1F1FF" glyph="u1F1E9_u1F1FF"/>
            <Ligature components="u1F1F4" glyph="u1F1E9_u1F1F4"/>
            <Ligature components="u1F1F2" glyph="u1F1E9_u1F1F2"/>
            <Ligature components="u1F1F0" glyph="u1F1E9_u1F1F0"/>
            <Ligature components="u1F1EF" glyph="u1F1E9_u1F1EF"/>
            <Ligature components="u1F1EA" glyph="u1F1E9_u1F1EA"/>
          </LigatureSet>
          <LigatureSet glyph="u1F1EA">
            <Ligature components="u1F1FA" glyph="u1F1EA_u1F1FA"/>
            <Ligature components="u1F1F9" glyph="u1F1EA_u1F1F9"/>
            <Ligature components="u1F1E6" glyph="u1F1EA_u1F1F8"/>
            <Ligature components="u1F1F8" glyph="u1F1EA_u1F1F8"/>
            <Ligature components="u1F1F7" glyph="u1F1EA_u1F1F7"/>
            <Ligature components="u1F1ED" glyph="u1F1EA_u1F1ED"/>
            <Ligature components="u1F1EC" glyph="u1F1EA_u1F1EC"/>
            <Ligature components="u1F1EA" glyph="u1F1EA_u1F1EA"/>
            <Ligature components="u1F1E8" glyph="u1F1EA_u1F1E8"/>
          </LigatureSet>
          <LigatureSet glyph="u1F1EB">
            <Ligature components="u1F1F7" glyph="u1F1EB_u1F1F7"/>
            <Ligature components="u1F1F4" glyph="u1F1EB_u1F1F4"/>
            <Ligature components="u1F1F2" glyph="u1F1EB_u1F1F2"/>
            <Ligature components="u1F1F0" glyph="u1F1EB_u1F1F0"/>
            <Ligature components="u1F1EF" glyph="u1F1EB_u1F1EF"/>
            <Ligature components="u1F1EE" glyph="u1F1EB_u1F1EE"/>
          </LigatureSet>
          <LigatureSet glyph="u1F1EC">
            <Ligature components="u1F1FE" glyph="u1F1EC_u1F1FE"/>
            <Ligature components="u1F1FC" glyph="u1F1EC_u1F1FC"/>
            <Ligature components="u1F1FA" glyph="u1F1EC_u1F1FA"/>
            <Ligature components="u1F1F9" glyph="u1F1EC_u1F1F9"/>
            <Ligature components="u1F1F8" glyph="u1F1EC_u1F1F8"/>
            <Ligature components="u1F1F7" glyph="u1F1EC_u1F1F7"/>
            <Ligature components="u1F1F6" glyph="u1F1EC_u1F1F6"/>
            <Ligature components="u1F1F5" glyph="u1F1EC_u1F1F5"/>
            <Ligature components="u1F1F3" glyph="u1F1EC_u1F1F3"/>
            <Ligature components="u1F1F2" glyph="u1F1EC_u1F1F2"/>
            <Ligature components="u1F1F1" glyph="u1F1EC_u1F1F1"/>
            <Ligature components="u1F1EE" glyph="u1F1EC_u1F1EE"/>
            <Ligature components="u1F1ED" glyph="u1F1EC_u1F1ED"/>
            <Ligature components="u1F1EC" glyph="u1F1EC_u1F1EC"/>
            <Ligature components="u1F1EB" glyph="u1F1EC_u1F1EB"/>
            <Ligature components="u1F1EA" glyph="u1F1EC_u1F1EA"/>
            <Ligature components="u1F1E9" glyph="u1F1EC_u1F1E9"/>
            <Ligature components="u1F1E7" glyph="u1F1EC_u1F1E7"/>
            <Ligature components="u1F1E6" glyph="u1F1EC_u1F1E6"/>
          </LigatureSet>
          <LigatureSet glyph="u1F1ED">
            <Ligature components="u1F1FA" glyph="u1F1ED_u1F1FA"/>
            <Ligature components="u1F1F9" glyph="u1F1ED_u1F1F9"/>
            <Ligature components="u1F1F7" glyph="u1F1ED_u1F1F7"/>
            <Ligature components="u1F1F3" glyph="u1F1ED_u1F1F3"/>
            <Ligature components="u1F1F0" glyph="u1F1ED_u1F1F0"/>
            <Ligature components="u1F1F2" glyph="u1F1E6_u1F1FA"/>
          </LigatureSet>
          <LigatureSet glyph="u1F1EE">
            <Ligature components="u1F1F9" glyph="u1F1EE_u1F1F9"/>
            <Ligature components="u1F1F8" glyph="u1F1EE_u1F1F8"/>
            <Ligature components="u1F1F7" glyph="u1F1EE_u1F1F7"/>
            <Ligature components="u1F1F6" glyph="u1F1EE_u1F1F6"/>
            <Ligature components="u1F1F4" glyph="u1F1EE_u1F1F4"/>
            <Ligature components="u1F1F3" glyph="u1F1EE_u1F1F3"/>
            <Ligature components="u1F1F2" glyph="u1F1EE_u1F1F2"/>
            <Ligature components="u1F1F1" glyph="u1F1EE_u1F1F1"/>
            <Ligature components="u1F1EA" glyph="u1F1EE_u1F1EA"/>
            <Ligature components="u1F1E9" glyph="u1F1EE_u1F1E9"/>
            <Ligature components="u1F1E8" glyph="u1F1EE_u1F1E8"/>
          </LigatureSet>
          <LigatureSet glyph="u1F1EF">
            <Ligature components="u1F1F5" glyph="u1F1EF_u1F1F5"/>
            <Ligature components="u1F1F4" glyph="u1F1EF_u1F1F4"/>
            <Ligature components="u1F1F2" glyph="u1F1EF_u1F1F2"/>
            <Ligature components="u1F1EA" glyph="u1F1EF_u1F1EA"/>
          </LigatureSet>
          <LigatureSet glyph="u1F1F0">
            <Ligature components="u1F1FF" glyph="u1F1F0_u1F1FF"/>
            <Ligature components="u1F1FE" glyph="u1F1F0_u1F1FE"/>
            <Ligature components="u1F1FC" glyph="u1F1F0_u1F1FC"/>
            <Ligature components="u1F1F7" glyph="u1F1F0_u1F1F7"/>
            <Ligature components="u1F1F5" glyph="u1F1F0_u1F1F5"/>
            <Ligature components="u1F1F3" glyph="u1F1F0_u1F1F3"/>
            <Ligature components="u1F1F2" glyph="u1F1F0_u1F1F2"/>
            <Ligature components="u1F1EE" glyph="u1F1F0_u1F1EE"/>
            <Ligature components="u1F1ED" glyph="u1F1F0_u1F1ED"/>
            <Ligature components="u1F1EC" glyph="u1F1F0_u1F1EC"/>
            <Ligature components="u1F1EA" glyph="u1F1F0_u1F1EA"/>
          </LigatureSet>
          <LigatureSet glyph="u1F1F1">
            <Ligature components="u1F1FE" glyph="u1F1F1_u1F1FE"/>
            <Ligature components="u1F1FB" glyph="u1F1F1_u1F1FB"/>
            <Ligature components="u1F1FA" glyph="u1F1F1_u1F1FA"/>
            <Ligature components="u1F1F9" glyph="u1F1F1_u1F1F9"/>
            <Ligature components="u1F1F8" glyph="u1F1F1_u1F1F8"/>
            <Ligature components="u1F1F7" glyph="u1F1F1_u1F1F7"/>
            <Ligature components="u1F1F0" glyph="u1F1F1_u1F1F0"/>
            <Ligature components="u1F1EE" glyph="u1F1F1_u1F1EE"/>
            <Ligature components="u1F1E8" glyph="u1F1F1_u1F1E8"/>
            <Ligature components="u1F1E7" glyph="u1F1F1_u1F1E7"/>
            <Ligature components="u1F1E6" glyph="u1F1F1_u1F1E6"/>
          </LigatureSet>
          <LigatureSet glyph="u1F1F2">
            <Ligature components="u1F1FF" glyph="u1F1F2_u1F1FF"/>
            <Ligature components="u1F1FE" glyph="u1F1F2_u1F1FE"/>
            <Ligature components="u1F1FD" glyph="u1F1F2_u1F1FD"/>
            <Ligature components="u1F1FC" glyph="u1F1F2_u1F1FC"/>
            <Ligature components="u1F1FB" glyph="u1F1F2_u1F1FB"/>
            <Ligature components="u1F1FA" glyph="u1F1F2_u1F1FA"/>
            <Ligature components="u1F1F9" glyph="u1F1F2_u1F1F9"/>
            <Ligature components="u1F1F8" glyph="u1F1F2_u1F1F8"/>
            <Ligature components="u1F1F7" glyph="u1F1F2_u1F1F7"/>
            <Ligature components="u1F1F6" glyph="u1F1F2_u1F1F6"/>
            <Ligature components="u1F1F5" glyph="u1F1F2_u1F1F5"/>
            <Ligature components="u1F1F4" glyph="u1F1F2_u1F1F4"/>
            <Ligature components="u1F1F3" glyph="u1F1F2_u1F1F3"/>
            <Ligature components="u1F1F2" glyph="u1F1F2_u1F1F2"/>
            <Ligature components="u1F1F1" glyph="u1F1F2_u1F1F1"/>
            <Ligature components="u1F1F0" glyph="u1F1F2_u1F1F0"/>
            <Ligature components="u1F1ED" glyph="u1F1F2_u1F1ED"/>
            <Ligature components="u1F1EC" glyph="u1F1F2_u1F1EC"/>
            <Ligature components="u1F1EA" glyph="u1F1F2_u1F1EA"/>
            <Ligature components="u1F1E9" glyph="u1F1F2_u1F1E9"/>
            <Ligature components="u1F1E8" glyph="u1F1F2_u1F1E8"/>
            <Ligature components="u1F1E6" glyph="u1F1F2_u1F1E6"/>
            <Ligature components="u1F1EB" glyph="u1F1EB_u1F1F7"/>
          </LigatureSet>
          <LigatureSet glyph="u1F1F3">
            <Ligature components="u1F1FF" glyph="u1F1F3_u1F1FF"/>
            <Ligature components="u1F1FA" glyph="u1F1F3_u1F1FA"/>
            <Ligature components="u1F1F7" glyph="u1F1F3_u1F1F7"/>
            <Ligature components="u1F1F5" glyph="u1F1F3_u1F1F5"/>
            <Ligature components="u1F1F4" glyph="u1F1F3_u1F1F4"/>
            <Ligature components="u1F1F1" glyph="u1F1F3_u1F1F1"/>
            <Ligature components="u1F1EE" glyph="u1F1F3_u1F1EE"/>
            <Ligature components="u1F1EC" glyph="u1F1F3_u1F1EC"/>
            <Ligature components="u1F1EB" glyph="u1F1F3_u1F1EB"/>
            <Ligature components="u1F1EA" glyph="u1F1F3_u1F1EA"/>
            <Ligature components="u1F1E8" glyph="u1F1F3_u1F1E8"/>
            <Ligature components="u1F1E6" glyph="u1F1F3_u1F1E6"/>
          </LigatureSet>
          <LigatureSet glyph="u1F1F4">
            <Ligature components="u1F1F2" glyph="u1F1F4_u1F1F2"/>
          </LigatureSet>
          <LigatureSet glyph="u1F1F5">
            <Ligature components="u1F1FE" glyph="u1F1F5_u1F1FE"/>
            <Ligature components="u1F1FC" glyph="u1F1F5_u1F1FC"/>
            <Ligature components="u1F1F9" glyph="u1F1F5_u1F1F9"/>
            <Ligature components="u1F1F8" glyph="u1F1F5_u1F1F8"/>
            <Ligature components="u1F1F7" glyph="u1F1F5_u1F1F7"/>
            <Ligature components="u1F1F3" glyph="u1F1F5_u1F1F3"/>
            <Ligature components="u1F1F2" glyph="u1F1F5_u1F1F2"/>
            <Ligature components="u1F1F1" glyph="u1F1F5_u1F1F1"/>
            <Ligature components="u1F1F0" glyph="u1F1F5_u1F1F0"/>
            <Ligature components="u1F1ED" glyph="u1F1F5_u1F1ED"/>
            <Ligature components="u1F1EC" glyph="u1F1F5_u1F1EC"/>
            <Ligature components="u1F1EB" glyph="u1F1F5_u1F1EB"/>
            <Ligature components="u1F1EA" glyph="u1F1F5_u1F1EA"/>
            <Ligature components="u1F1E6" glyph="u1F1F5_u1F1E6"/>
          </LigatureSet>
          <LigatureSet glyph="u1F1F6">
            <Ligature components="u1F1E6" glyph="u1F1F6_u1F1E6"/>
          </LigatureSet>
          <LigatureSet glyph="u1F1F7">
            <Ligature components="u1F1FC" glyph="u1F1F7_u1F1FC"/>
            <Ligature components="u1F1FA" glyph="u1F1F7_u1F1FA"/>
            <Ligature components="u1F1F8" glyph="u1F1F7_u1F1F8"/>
            <Ligature components="u1F1F4" glyph="u1F1F7_u1F1F4"/>
            <Ligature components="u1F1EA" glyph="u1F1F7_u1F1EA"/>
          </LigatureSet>
          <LigatureSet glyph="u1F1F8">
            <Ligature components="u1F1FF" glyph="u1F1F8_u1F1FF"/>
            <Ligature components="u1F1FE" glyph="u1F1F8_u1F1FE"/>
            <Ligature components="u1F1FD" glyph="u1F1F8_u1F1FD"/>
            <Ligature components="u1F1FB" glyph="u1F1F8_u1F1FB"/>
            <Ligature components="u1F1F9" glyph="u1F1F8_u1F1F9"/>
            <Ligature components="u1F1F8" glyph="u1F1F8_u1F1F8"/>
            <Ligature components="u1F1F7" glyph="u1F1F8_u1F1F7"/>
            <Ligature components="u1F1F4" glyph="u1F1F8_u1F1F4"/>
            <Ligature components="u1F1F3" glyph="u1F1F8_u1F1F3"/>
            <Ligature components="u1F1F2" glyph="u1F1F8_u1F1F2"/>
            <Ligature components="u1F1F1" glyph="u1F1F8_u1F1F1"/>
            <Ligature components="u1F1F0" glyph="u1F1F8_u1F1F0"/>
            <Ligature components="u1F1EE" glyph="u1F1F8_u1F1EE"/>
            <Ligature components="u1F1ED" glyph="u1F1F8_u1F1ED"/>
            <Ligature components="u1F1EC" glyph="u1F1F8_u1F1EC"/>
            <Ligature components="u1F1EA" glyph="u1F1F8_u1F1EA"/>
            <Ligature components="u1F1E9" glyph="u1F1F8_u1F1E9"/>
            <Ligature components="u1F1E8" glyph="u1F1F8_u1F1E8"/>
            <Ligature components="u1F1E7" glyph="u1F1F8_u1F1E7"/>
            <Ligature components="u1F1E6" glyph="u1F1F8_u1F1E6"/>
            <Ligature components="u1F1EF" glyph="u1F1F3_u1F1F4"/>
          </LigatureSet>
          <LigatureSet glyph="u1F1F9">
            <Ligature components="u1F1FF" glyph="u1F1F9_u1F1FF"/>
            <Ligature components="u1F1FC" glyph="u1F1F9_u1F1FC"/>
            <Ligature components="u1F1FB" glyph="u1F1F9_u1F1FB"/>
            <Ligature components="u1F1F9" glyph="u1F1F9_u1F1F9"/>
            <Ligature components="u1F1F7" glyph="u1F1F9_u1F1F7"/>
            <Ligature components="u1F1F4" glyph="u1F1F9_u1F1F4"/>
            <Ligature components="u1F1F3" glyph="u1F1F9_u1F1F3"/>
            <Ligature components="u1F1F2" glyph="u1F1F9_u1F1F2"/>
            <Ligature components="u1F1F1" glyph="u1F1F9_u1F1F1"/>
            <Ligature components="u1F1F0" glyph="u1F1F9_u1F1F0"/>
            <Ligature components="u1F1EF" glyph="u1F1F9_u1F1EF"/>
            <Ligature components="u1F1ED" glyph="u1F1F9_u1F1ED"/>
            <Ligature components="u1F1EC" glyph="u1F1F9_u1F1EC"/>
            <Ligature components="u1F1EB" glyph="u1F1F9_u1F1EB"/>
            <Ligature components="u1F1E9" glyph="u1F1F9_u1F1E9"/>
            <Ligature components="u1F1E8" glyph="u1F1F9_u1F1E8"/>
            <Ligature components="u1F1E6" glyph="u1F1F8_u1F1ED"/>
          </LigatureSet>
          <LigatureSet glyph="u1F1FA">
            <Ligature components="u1F1FF" glyph="u1F1FA_u1F1FF"/>
            <Ligature components="u1F1FE" glyph="u1F1FA_u1F1FE"/>
            <Ligature components="u1F1F2" glyph="u1F1FA_u1F1F8"/>
            <Ligature components="u1F1F8" glyph="u1F1FA_u1F1F8"/>
            <Ligature components="u1F1EC" glyph="u1F1FA_u1F1EC"/>
            <Ligature components="u1F1E6" glyph="u1F1FA_u1F1E6"/>
          </LigatureSet>
          <LigatureSet glyph="u1F1FB">
            <Ligature components="u1F1FA" glyph="u1F1FB_u1F1FA"/>
            <Ligature components="u1F1F3" glyph="u1F1FB_u1F1F3"/>
            <Ligature components="u1F1EE" glyph="u1F1FB_u1F1EE"/>
            <Ligature components="u1F1EC" glyph="u1F1FB_u1F1EC"/>
            <Ligature components="u1F1EA" glyph="u1F1FB_u1F1EA"/>
            <Ligature components="u1F1E8" glyph="u1F1FB_u1F1E8"/>
            <Ligature components="u1F1E6" glyph="u1F1FB_u1F1E6"/>
          </LigatureSet>
          <LigatureSet glyph="u1F1FC">
            <Ligature components="u1F1F8" glyph="u1F1FC_u1F1F8"/>
            <Ligature components="u1F1EB" glyph="u1F1FC_u1F1EB"/>
          </LigatureSet>
          <LigatureSet glyph="u1F1FD">
            <Ligature components="u1F1F0" glyph="u1F1FD_u1F1F0"/>
          </LigatureSet>
          <LigatureSet glyph="u1F1FE">
            <Ligature components="u1F1F9" glyph="u1F1FE_u1F1F9"/>
            <Ligature components="u1F1EA" glyph="u1F1FE_u1F1EA"/>
          </LigatureSet>
          <LigatureSet glyph="u1F1FF">
            <Ligature components="u1F1FC" glyph="u1F1FF_u1F1FC"/>
            <Ligature components="u1F1F2" glyph="u1F1FF_u1F1F2"/>
            <Ligature components="u1F1E6" glyph="u1F1FF_u1F1E6"/>
          </LigatureSet>
        </LigatureSubst>
      </Lookup>
      <Lookup index="3">
        <!-- LookupType=4 -->
        <LookupFlag value="0"/>
        <!-- SubTableCount=1 -->
        <LigatureSubst index="0">
          <LigatureSet glyph="u1F385.0">
            <Ligature components="u1F3FF" glyph="u1F385.5"/>
            <Ligature components="u1F3FE" glyph="u1F385.4"/>
            <Ligature components="u1F3FD" glyph="u1F385.3"/>
            <Ligature components="u1F3FC" glyph="u1F385.2"/>
            <Ligature components="u1F3FB" glyph="u1F385.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F3C3.0">
            <Ligature components="u1F3FF" glyph="u1F3C3.5"/>
            <Ligature components="u1F3FE" glyph="u1F3C3.4"/>
            <Ligature components="u1F3FD" glyph="u1F3C3.3"/>
            <Ligature components="u1F3FC" glyph="u1F3C3.2"/>
            <Ligature components="u1F3FB" glyph="u1F3C3.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F3C4.0">
            <Ligature components="u1F3FF" glyph="u1F3C4.5"/>
            <Ligature components="u1F3FE" glyph="u1F3C4.4"/>
            <Ligature components="u1F3FD" glyph="u1F3C4.3"/>
            <Ligature components="u1F3FC" glyph="u1F3C4.2"/>
            <Ligature components="u1F3FB" glyph="u1F3C4.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F3C7.0">
            <Ligature components="u1F3FF" glyph="u1F3C7.5"/>
            <Ligature components="u1F3FE" glyph="u1F3C7.4"/>
            <Ligature components="u1F3FD" glyph="u1F3C7.3"/>
            <Ligature components="u1F3FC" glyph="u1F3C7.2"/>
            <Ligature components="u1F3FB" glyph="u1F3C7.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F3CA.0">
            <Ligature components="u1F3FF" glyph="u1F3CA.5"/>
            <Ligature components="u1F3FE" glyph="u1F3CA.4"/>
            <Ligature components="u1F3FD" glyph="u1F3CA.3"/>
            <Ligature components="u1F3FC" glyph="u1F3CA.2"/>
            <Ligature components="u1F3FB" glyph="u1F3CA.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F3CB.0">
            <Ligature components="u1F3FF" glyph="u1F3CB.5"/>
            <Ligature components="u1F3FE" glyph="u1F3CB.4"/>
            <Ligature components="u1F3FD" glyph="u1F3CB.3"/>
            <Ligature components="u1F3FC" glyph="u1F3CB.2"/>
            <Ligature components="u1F3FB" glyph="u1F3CB.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F441">
            <Ligature components="ZWJ,u1F5E8" glyph="u1F441_u1F5E8"/>
          </LigatureSet>
          <LigatureSet glyph="u1F442.0">
            <Ligature components="u1F3FF" glyph="u1F442.5"/>
            <Ligature components="u1F3FE" glyph="u1F442.4"/>
            <Ligature components="u1F3FD" glyph="u1F442.3"/>
            <Ligature components="u1F3FC" glyph="u1F442.2"/>
            <Ligature components="u1F3FB" glyph="u1F442.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F443.0">
            <Ligature components="u1F3FF" glyph="u1F443.5"/>
            <Ligature components="u1F3FE" glyph="u1F443.4"/>
            <Ligature components="u1F3FD" glyph="u1F443.3"/>
            <Ligature components="u1F3FC" glyph="u1F443.2"/>
            <Ligature components="u1F3FB" glyph="u1F443.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F446.0">
            <Ligature components="u1F3FF" glyph="u1F446.5"/>
            <Ligature components="u1F3FE" glyph="u1F446.4"/>
            <Ligature components="u1F3FD" glyph="u1F446.3"/>
            <Ligature components="u1F3FC" glyph="u1F446.2"/>
            <Ligature components="u1F3FB" glyph="u1F446.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F447.0">
            <Ligature components="u1F3FF" glyph="u1F447.5"/>
            <Ligature components="u1F3FE" glyph="u1F447.4"/>
            <Ligature components="u1F3FD" glyph="u1F447.3"/>
            <Ligature components="u1F3FC" glyph="u1F447.2"/>
            <Ligature components="u1F3FB" glyph="u1F447.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F448.0">
            <Ligature components="u1F3FF" glyph="u1F448.5"/>
            <Ligature components="u1F3FE" glyph="u1F448.4"/>
            <Ligature components="u1F3FD" glyph="u1F448.3"/>
            <Ligature components="u1F3FC" glyph="u1F448.2"/>
            <Ligature components="u1F3FB" glyph="u1F448.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F449.0">
            <Ligature components="u1F3FF" glyph="u1F449.5"/>
            <Ligature components="u1F3FE" glyph="u1F449.4"/>
            <Ligature components="u1F3FD" glyph="u1F449.3"/>
            <Ligature components="u1F3FC" glyph="u1F449.2"/>
            <Ligature components="u1F3FB" glyph="u1F449.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F44A.0">
            <Ligature components="u1F3FF" glyph="u1F44A.5"/>
            <Ligature components="u1F3FE" glyph="u1F44A.4"/>
            <Ligature components="u1F3FD" glyph="u1F44A.3"/>
            <Ligature components="u1F3FC" glyph="u1F44A.2"/>
            <Ligature components="u1F3FB" glyph="u1F44A.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F44B.0">
            <Ligature components="u1F3FF" glyph="u1F44B.5"/>
            <Ligature components="u1F3FE" glyph="u1F44B.4"/>
            <Ligature components="u1F3FD" glyph="u1F44B.3"/>
            <Ligature components="u1F3FC" glyph="u1F44B.2"/>
            <Ligature components="u1F3FB" glyph="u1F44B.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F44C.0">
            <Ligature components="u1F3FF" glyph="u1F44C.5"/>
            <Ligature components="u1F3FE" glyph="u1F44C.4"/>
            <Ligature components="u1F3FD" glyph="u1F44C.3"/>
            <Ligature components="u1F3FC" glyph="u1F44C.2"/>
            <Ligature components="u1F3FB" glyph="u1F44C.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F44D.0">
            <Ligature components="u1F3FF" glyph="u1F44D.5"/>
            <Ligature components="u1F3FE" glyph="u1F44D.4"/>
            <Ligature components="u1F3FD" glyph="u1F44D.3"/>
            <Ligature components="u1F3FC" glyph="u1F44D.2"/>
            <Ligature components="u1F3FB" glyph="u1F44D.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F44E.0">
            <Ligature components="u1F3FF" glyph="u1F44E.5"/>
            <Ligature components="u1F3FE" glyph="u1F44E.4"/>
            <Ligature components="u1F3FD" glyph="u1F44E.3"/>
            <Ligature components="u1F3FC" glyph="u1F44E.2"/>
            <Ligature components="u1F3FB" glyph="u1F44E.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F44F.0">
            <Ligature components="u1F3FF" glyph="u1F44F.5"/>
            <Ligature components="u1F3FE" glyph="u1F44F.4"/>
            <Ligature components="u1F3FD" glyph="u1F44F.3"/>
            <Ligature components="u1F3FC" glyph="u1F44F.2"/>
            <Ligature components="u1F3FB" glyph="u1F44F.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F450.0">
            <Ligature components="u1F3FF" glyph="u1F450.5"/>
            <Ligature components="u1F3FE" glyph="u1F450.4"/>
            <Ligature components="u1F3FD" glyph="u1F450.3"/>
            <Ligature components="u1F3FC" glyph="u1F450.2"/>
            <Ligature components="u1F3FB" glyph="u1F450.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F466.0">
            <Ligature components="u1F3FF" glyph="u1F466.5"/>
            <Ligature components="u1F3FE" glyph="u1F466.4"/>
            <Ligature components="u1F3FD" glyph="u1F466.3"/>
            <Ligature components="u1F3FC" glyph="u1F466.2"/>
            <Ligature components="u1F3FB" glyph="u1F466.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F467.0">
            <Ligature components="u1F3FF" glyph="u1F467.5"/>
            <Ligature components="u1F3FE" glyph="u1F467.4"/>
            <Ligature components="u1F3FD" glyph="u1F467.3"/>
            <Ligature components="u1F3FC" glyph="u1F467.2"/>
            <Ligature components="u1F3FB" glyph="u1F467.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F468.0">
            <Ligature components="ZWJ,u2764,uniFE0F,ZWJ,u1F48B,ZWJ,u1F468.0" glyph="u1F48F.0.MM"/>
            <Ligature components="ZWJ,u2764,uniFE0F,ZWJ,u1F468.0" glyph="u1F491.0.MM"/>
            <Ligature components="ZWJ,u1F469.0,ZWJ,u1F467.0,ZWJ,u1F466.0" glyph="u1F46A.0.MWGB"/>
            <Ligature components="ZWJ,u1F469.0,ZWJ,u1F467.0,ZWJ,u1F467.0" glyph="u1F46A.0.MWGG"/>
            <Ligature components="ZWJ,u1F469.0,ZWJ,u1F466.0,ZWJ,u1F466.0" glyph="u1F46A.0.MWBB"/>
            <Ligature components="ZWJ,u1F468.0,ZWJ,u1F467.0,ZWJ,u1F466.0" glyph="u1F46A.0.MMGB"/>
            <Ligature components="ZWJ,u1F468.0,ZWJ,u1F467.0,ZWJ,u1F467.0" glyph="u1F46A.0.MMGG"/>
            <Ligature components="ZWJ,u1F468.0,ZWJ,u1F466.0,ZWJ,u1F466.0" glyph="u1F46A.0.MMBB"/>
            <Ligature components="ZWJ,u1F469.0,ZWJ,u1F467.0" glyph="u1F46A.0.MWG"/>
            <Ligature components="ZWJ,u1F468.0,ZWJ,u1F467.0" glyph="u1F46A.0.MMG"/>
            <Ligature components="ZWJ,u1F468.0,ZWJ,u1F466.0" glyph="u1F46A.0.MMB"/>
            <Ligature components="ZWJ,u1F469.0,ZWJ,u1F466.0" glyph="u1F46A.0.FAMDEF"/>
            <Ligature components="u1F3FF" glyph="u1F468.5"/>
            <Ligature components="u1F3FE" glyph="u1F468.4"/>
            <Ligature components="u1F3FD" glyph="u1F468.3"/>
            <Ligature components="u1F3FC" glyph="u1F468.2"/>
            <Ligature components="u1F3FB" glyph="u1F468.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F469.0">
            <Ligature components="ZWJ,u2764,uniFE0F,ZWJ,u1F48B,ZWJ,u1F469.0" glyph="u1F48F.0.WW"/>
            <Ligature components="ZWJ,u2764,uniFE0F,ZWJ,u1F48B,ZWJ,u1F468.0" glyph="u1F48F.0.DEFWM"/>
            <Ligature components="ZWJ,u1F469.0,ZWJ,u1F467.0,ZWJ,u1F467.0" glyph="u1F46A.0.WWGG"/>
            <Ligature components="ZWJ,u1F469.0,ZWJ,u1F467.0,ZWJ,u1F466.0" glyph="u1F46A.0.WWGB"/>
            <Ligature components="ZWJ,u1F469.0,ZWJ,u1F466.0,ZWJ,u1F466.0" glyph="u1F46A.0.WWBB"/>
            <Ligature components="ZWJ,u2764,uniFE0F,ZWJ,u1F469.0" glyph="u1F491.0.WW"/>
            <Ligature components="ZWJ,u2764,uniFE0F,ZWJ,u1F468.0" glyph="u1F491.0.DEFWM"/>
            <Ligature components="ZWJ,u1F469.0,ZWJ,u1F467.0" glyph="u1F46A.0.WWG"/>
            <Ligature components="ZWJ,u1F469.0,ZWJ,u1F466.0" glyph="u1F46A.0.WWB"/>
            <Ligature components="u1F3FF" glyph="u1F469.5"/>
            <Ligature components="u1F3FE" glyph="u1F469.4"/>
            <Ligature components="u1F3FD" glyph="u1F469.3"/>
            <Ligature components="u1F3FC" glyph="u1F469.2"/>
            <Ligature components="u1F3FB" glyph="u1F469.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F46E.0">
            <Ligature components="u1F3FF" glyph="u1F46E.5"/>
            <Ligature components="u1F3FE" glyph="u1F46E.4"/>
            <Ligature components="u1F3FD" glyph="u1F46E.3"/>
            <Ligature components="u1F3FC" glyph="u1F46E.2"/>
            <Ligature components="u1F3FB" glyph="u1F46E.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F470.0">
            <Ligature components="u1F3FF" glyph="u1F470.5"/>
            <Ligature components="u1F3FE" glyph="u1F470.4"/>
            <Ligature components="u1F3FD" glyph="u1F470.3"/>
            <Ligature components="u1F3FC" glyph="u1F470.2"/>
            <Ligature components="u1F3FB" glyph="u1F470.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F471.0">
            <Ligature components="u1F3FF" glyph="u1F471.5"/>
            <Ligature components="u1F3FE" glyph="u1F471.4"/>
            <Ligature components="u1F3FD" glyph="u1F471.3"/>
            <Ligature components="u1F3FC" glyph="u1F471.2"/>
            <Ligature components="u1F3FB" glyph="u1F471.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F472.0">
            <Ligature components="u1F3FF" glyph="u1F472.5"/>
            <Ligature components="u1F3FE" glyph="u1F472.4"/>
            <Ligature components="u1F3FD" glyph="u1F472.3"/>
            <Ligature components="u1F3FC" glyph="u1F472.2"/>
            <Ligature components="u1F3FB" glyph="u1F472.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F473.0">
            <Ligature components="u1F3FF" glyph="u1F473.5"/>
            <Ligature components="u1F3FE" glyph="u1F473.4"/>
            <Ligature components="u1F3FD" glyph="u1F473.3"/>
            <Ligature components="u1F3FC" glyph="u1F473.2"/>
            <Ligature components="u1F3FB" glyph="u1F473.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F474.0">
            <Ligature components="u1F3FF" glyph="u1F474.5"/>
            <Ligature components="u1F3FE" glyph="u1F474.4"/>
            <Ligature components="u1F3FD" glyph="u1F474.3"/>
            <Ligature components="u1F3FC" glyph="u1F474.2"/>
            <Ligature components="u1F3FB" glyph="u1F474.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F475.0">
            <Ligature components="u1F3FF" glyph="u1F475.5"/>
            <Ligature components="u1F3FE" glyph="u1F475.4"/>
            <Ligature components="u1F3FD" glyph="u1F475.3"/>
            <Ligature components="u1F3FC" glyph="u1F475.2"/>
            <Ligature components="u1F3FB" glyph="u1F475.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F476.0">
            <Ligature components="u1F3FF" glyph="u1F476.5"/>
            <Ligature components="u1F3FE" glyph="u1F476.4"/>
            <Ligature components="u1F3FD" glyph="u1F476.3"/>
            <Ligature components="u1F3FC" glyph="u1F476.2"/>
            <Ligature components="u1F3FB" glyph="u1F476.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F477.0">
            <Ligature components="u1F3FF" glyph="u1F477.5"/>
            <Ligature components="u1F3FE" glyph="u1F477.4"/>
            <Ligature components="u1F3FD" glyph="u1F477.3"/>
            <Ligature components="u1F3FC" glyph="u1F477.2"/>
            <Ligature components="u1F3FB" glyph="u1F477.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F478.0">
            <Ligature components="u1F3FF" glyph="u1F478.5"/>
            <Ligature components="u1F3FE" glyph="u1F478.4"/>
            <Ligature components="u1F3FD" glyph="u1F478.3"/>
            <Ligature components="u1F3FC" glyph="u1F478.2"/>
            <Ligature components="u1F3FB" glyph="u1F478.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F47C.0">
            <Ligature components="u1F3FF" glyph="u1F47C.5"/>
            <Ligature components="u1F3FE" glyph="u1F47C.4"/>
            <Ligature components="u1F3FD" glyph="u1F47C.3"/>
            <Ligature components="u1F3FC" glyph="u1F47C.2"/>
            <Ligature components="u1F3FB" glyph="u1F47C.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F481.0">
            <Ligature components="u1F3FF" glyph="u1F481.5"/>
            <Ligature components="u1F3FE" glyph="u1F481.4"/>
            <Ligature components="u1F3FD" glyph="u1F481.3"/>
            <Ligature components="u1F3FC" glyph="u1F481.2"/>
            <Ligature components="u1F3FB" glyph="u1F481.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F482.0">
            <Ligature components="u1F3FF" glyph="u1F482.5"/>
            <Ligature components="u1F3FE" glyph="u1F482.4"/>
            <Ligature components="u1F3FD" glyph="u1F482.3"/>
            <Ligature components="u1F3FC" glyph="u1F482.2"/>
            <Ligature components="u1F3FB" glyph="u1F482.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F483.0">
            <Ligature components="u1F3FF" glyph="u1F483.5"/>
            <Ligature components="u1F3FE" glyph="u1F483.4"/>
            <Ligature components="u1F3FD" glyph="u1F483.3"/>
            <Ligature components="u1F3FC" glyph="u1F483.2"/>
            <Ligature components="u1F3FB" glyph="u1F483.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F485.0">
            <Ligature components="u1F3FF" glyph="u1F485.5"/>
            <Ligature components="u1F3FE" glyph="u1F485.4"/>
            <Ligature components="u1F3FD" glyph="u1F485.3"/>
            <Ligature components="u1F3FC" glyph="u1F485.2"/>
            <Ligature components="u1F3FB" glyph="u1F485.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F486.0">
            <Ligature components="u1F3FF" glyph="u1F486.5"/>
            <Ligature components="u1F3FE" glyph="u1F486.4"/>
            <Ligature components="u1F3FD" glyph="u1F486.3"/>
            <Ligature components="u1F3FC" glyph="u1F486.2"/>
            <Ligature components="u1F3FB" glyph="u1F486.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F487.0">
            <Ligature components="u1F3FF" glyph="u1F487.5"/>
            <Ligature components="u1F3FE" glyph="u1F487.4"/>
            <Ligature components="u1F3FD" glyph="u1F487.3"/>
            <Ligature components="u1F3FC" glyph="u1F487.2"/>
            <Ligature components="u1F3FB" glyph="u1F487.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F4AA.0">
            <Ligature components="u1F3FF" glyph="u1F4AA.5"/>
            <Ligature components="u1F3FE" glyph="u1F4AA.4"/>
            <Ligature components="u1F3FD" glyph="u1F4AA.3"/>
            <Ligature components="u1F3FC" glyph="u1F4AA.2"/>
            <Ligature components="u1F3FB" glyph="u1F4AA.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F590.0">
            <Ligature components="u1F3FF" glyph="u1F590.5"/>
            <Ligature components="u1F3FE" glyph="u1F590.4"/>
            <Ligature components="u1F3FD" glyph="u1F590.3"/>
            <Ligature components="u1F3FC" glyph="u1F590.2"/>
            <Ligature components="u1F3FB" glyph="u1F590.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F595.0">
            <Ligature components="u1F3FF" glyph="u1F595.5"/>
            <Ligature components="u1F3FE" glyph="u1F595.4"/>
            <Ligature components="u1F3FD" glyph="u1F595.3"/>
            <Ligature components="u1F3FC" glyph="u1F595.2"/>
            <Ligature components="u1F3FB" glyph="u1F595.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F596.0">
            <Ligature components="u1F3FF" glyph="u1F596.5"/>
            <Ligature components="u1F3FE" glyph="u1F596.4"/>
            <Ligature components="u1F3FD" glyph="u1F596.3"/>
            <Ligature components="u1F3FC" glyph="u1F596.2"/>
            <Ligature components="u1F3FB" glyph="u1F596.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F645.0">
            <Ligature components="u1F3FF" glyph="u1F645.5"/>
            <Ligature components="u1F3FE" glyph="u1F645.4"/>
            <Ligature components="u1F3FD" glyph="u1F645.3"/>
            <Ligature components="u1F3FC" glyph="u1F645.2"/>
            <Ligature components="u1F3FB" glyph="u1F645.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F646.0">
            <Ligature components="u1F3FF" glyph="u1F646.5"/>
            <Ligature components="u1F3FE" glyph="u1F646.4"/>
            <Ligature components="u1F3FD" glyph="u1F646.3"/>
            <Ligature components="u1F3FC" glyph="u1F646.2"/>
            <Ligature components="u1F3FB" glyph="u1F646.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F647.0">
            <Ligature components="u1F3FF" glyph="u1F647.5"/>
            <Ligature components="u1F3FE" glyph="u1F647.4"/>
            <Ligature components="u1F3FD" glyph="u1F647.3"/>
            <Ligature components="u1F3FC" glyph="u1F647.2"/>
            <Ligature components="u1F3FB" glyph="u1F647.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F64B.0">
            <Ligature components="u1F3FF" glyph="u1F64B.5"/>
            <Ligature components="u1F3FE" glyph="u1F64B.4"/>
            <Ligature components="u1F3FD" glyph="u1F64B.3"/>
            <Ligature components="u1F3FC" glyph="u1F64B.2"/>
            <Ligature components="u1F3FB" glyph="u1F64B.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F64C.0">
            <Ligature components="u1F3FF" glyph="u1F64C.5"/>
            <Ligature components="u1F3FE" glyph="u1F64C.4"/>
            <Ligature components="u1F3FD" glyph="u1F64C.3"/>
            <Ligature components="u1F3FC" glyph="u1F64C.2"/>
            <Ligature components="u1F3FB" glyph="u1F64C.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F64D.0">
            <Ligature components="u1F3FF" glyph="u1F64D.5"/>
            <Ligature components="u1F3FE" glyph="u1F64D.4"/>
            <Ligature components="u1F3FD" glyph="u1F64D.3"/>
            <Ligature components="u1F3FC" glyph="u1F64D.2"/>
            <Ligature components="u1F3FB" glyph="u1F64D.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F64E.0">
            <Ligature components="u1F3FF" glyph="u1F64E.5"/>
            <Ligature components="u1F3FE" glyph="u1F64E.4"/>
            <Ligature components="u1F3FD" glyph="u1F64E.3"/>
            <Ligature components="u1F3FC" glyph="u1F64E.2"/>
            <Ligature components="u1F3FB" glyph="u1F64E.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F64F.0">
            <Ligature components="u1F3FF" glyph="u1F64F.5"/>
            <Ligature components="u1F3FE" glyph="u1F64F.4"/>
            <Ligature components="u1F3FD" glyph="u1F64F.3"/>
            <Ligature components="u1F3FC" glyph="u1F64F.2"/>
            <Ligature components="u1F3FB" glyph="u1F64F.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F6A3.0">
            <Ligature components="u1F3FF" glyph="u1F6A3.5"/>
            <Ligature components="u1F3FE" glyph="u1F6A3.4"/>
            <Ligature components="u1F3FD" glyph="u1F6A3.3"/>
            <Ligature components="u1F3FC" glyph="u1F6A3.2"/>
            <Ligature components="u1F3FB" glyph="u1F6A3.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F6B4.0">
            <Ligature components="u1F3FF" glyph="u1F6B4.5"/>
            <Ligature components="u1F3FE" glyph="u1F6B4.4"/>
            <Ligature components="u1F3FD" glyph="u1F6B4.3"/>
            <Ligature components="u1F3FC" glyph="u1F6B4.2"/>
            <Ligature components="u1F3FB" glyph="u1F6B4.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F6B5.0">
            <Ligature components="u1F3FF" glyph="u1F6B5.5"/>
            <Ligature components="u1F3FE" glyph="u1F6B5.4"/>
            <Ligature components="u1F3FD" glyph="u1F6B5.3"/>
            <Ligature components="u1F3FC" glyph="u1F6B5.2"/>
            <Ligature components="u1F3FB" glyph="u1F6B5.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F6B6.0">
            <Ligature components="u1F3FF" glyph="u1F6B6.5"/>
            <Ligature components="u1F3FE" glyph="u1F6B6.4"/>
            <Ligature components="u1F3FD" glyph="u1F6B6.3"/>
            <Ligature components="u1F3FC" glyph="u1F6B6.2"/>
            <Ligature components="u1F3FB" glyph="u1F6B6.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F6C0.0">
            <Ligature components="u1F3FF" glyph="u1F6C0.5"/>
            <Ligature components="u1F3FE" glyph="u1F6C0.4"/>
            <Ligature components="u1F3FD" glyph="u1F6C0.3"/>
            <Ligature components="u1F3FC" glyph="u1F6C0.2"/>
            <Ligature components="u1F3FB" glyph="u1F6C0.1"/>
          </LigatureSet>
          <LigatureSet glyph="u1F918.0">
            <Ligature components="u1F3FF" glyph="u1F918.5"/>
            <Ligature components="u1F3FE" glyph="u1F918.4"/>
            <Ligature components="u1F3FD" glyph="u1F918.3"/>
            <Ligature components="u1F3FC" glyph="u1F918.2"/>
            <Ligature components="u1F3FB" glyph="u1F918.1"/>
          </LigatureSet>
          <LigatureSet glyph="u261D.0">
            <Ligature components="uniFE0F,u1F3FF" glyph="u261D.5"/>
            <Ligature components="uniFE0F,u1F3FE" glyph="u261D.4"/>
            <Ligature components="uniFE0F,u1F3FD" glyph="u261D.3"/>
            <Ligature components="uniFE0F,u1F3FC" glyph="u261D.2"/>
            <Ligature components="uniFE0F,u1F3FB" glyph="u261D.1"/>
            <Ligature components="u1F3FD" glyph="u261D.3"/>
            <Ligature components="u1F3FE" glyph="u261D.4"/>
            <Ligature components="u1F3FC" glyph="u261D.2"/>
            <Ligature components="u1F3FF" glyph="u261D.5"/>
            <Ligature components="u1F3FB" glyph="u261D.1"/>
          </LigatureSet>
          <LigatureSet glyph="u26F9.0">
            <Ligature components="uniFE0F,u1F3FF" glyph="u26F9.5"/>
            <Ligature components="uniFE0F,u1F3FE" glyph="u26F9.4"/>
            <Ligature components="uniFE0F,u1F3FD" glyph="u26F9.3"/>
            <Ligature components="uniFE0F,u1F3FC" glyph="u26F9.2"/>
            <Ligature components="uniFE0F,u1F3FB" glyph="u26F9.1"/>
            <Ligature components="u1F3FD" glyph="u26F9.3"/>
            <Ligature components="u1F3FE" glyph="u26F9.4"/>
            <Ligature components="u1F3FC" glyph="u26F9.2"/>
            <Ligature components="u1F3FF" glyph="u26F9.5"/>
            <Ligature components="u1F3FB" glyph="u26F9.1"/>
          </LigatureSet>
          <LigatureSet glyph="u270A.0">
            <Ligature components="uniFE0F,u1F3FF" glyph="u270A.5"/>
            <Ligature components="uniFE0F,u1F3FE" glyph="u270A.4"/>
            <Ligature components="uniFE0F,u1F3FD" glyph="u270A.3"/>
            <Ligature components="uniFE0F,u1F3FC" glyph="u270A.2"/>
            <Ligature components="uniFE0F,u1F3FB" glyph="u270A.1"/>
            <Ligature components="u1F3FD" glyph="u270A.3"/>
            <Ligature components="u1F3FE" glyph="u270A.4"/>
            <Ligature components="u1F3FC" glyph="u270A.2"/>
            <Ligature components="u1F3FF" glyph="u270A.5"/>
            <Ligature components="u1F3FB" glyph="u270A.1"/>
          </LigatureSet>
          <LigatureSet glyph="u270B.0">
            <Ligature components="uniFE0F,u1F3FF" glyph="u270B.5"/>
            <Ligature components="uniFE0F,u1F3FE" glyph="u270B.4"/>
            <Ligature components="uniFE0F,u1F3FD" glyph="u270B.3"/>
            <Ligature components="uniFE0F,u1F3FC" glyph="u270B.2"/>
            <Ligature components="uniFE0F,u1F3FB" glyph="u270B.1"/>
            <Ligature components="u1F3FD" glyph="u270B.3"/>
            <Ligature components="u1F3FE" glyph="u270B.4"/>
            <Ligature components="u1F3FC" glyph="u270B.2"/>
            <Ligature components="u1F3FF" glyph="u270B.5"/>
            <Ligature components="u1F3FB" glyph="u270B.1"/>
          </LigatureSet>
          <LigatureSet glyph="u270C.0">
            <Ligature components="uniFE0F,u1F3FF" glyph="u270C.5"/>
            <Ligature components="uniFE0F,u1F3FE" glyph="u270C.4"/>
            <Ligature components="uniFE0F,u1F3FD" glyph="u270C.3"/>
            <Ligature components="uniFE0F,u1F3FC" glyph="u270C.2"/>
            <Ligature components="uniFE0F,u1F3FB" glyph="u270C.1"/>
            <Ligature components="u1F3FD" glyph="u270C.3"/>
            <Ligature components="u1F3FE" glyph="u270C.4"/>
            <Ligature components="u1F3FC" glyph="u270C.2"/>
            <Ligature components="u1F3FF" glyph="u270C.5"/>
            <Ligature components="u1F3FB" glyph="u270C.1"/>
          </LigatureSet>
          <LigatureSet glyph="u270D.0">
            <Ligature components="uniFE0F,u1F3FF" glyph="u270D.5"/>
            <Ligature components="uniFE0F,u1F3FE" glyph="u270D.4"/>
            <Ligature components="uniFE0F,u1F3FD" glyph="u270D.3"/>
            <Ligature components="uniFE0F,u1F3FC" glyph="u270D.2"/>
            <Ligature components="uniFE0F,u1F3FB" glyph="u270D.1"/>
            <Ligature components="u1F3FD" glyph="u270D.3"/>
            <Ligature components="u1F3FE" glyph="u270D.4"/>
            <Ligature components="u1F3FC" glyph="u270D.2"/>
            <Ligature components="u1F3FF" glyph="u270D.5"/>
            <Ligature components="u1F3FB" glyph="u270D.1"/>
          </LigatureSet>
        </LigatureSubst>
      </Lookup>
    </LookupList>
  </GSUB>
</ttFont>
"""

def div(a, b):
    return int(round(a / float(b)))


class PNG:

    signature = bytearray((137, 80, 78, 71, 13, 10, 26, 10))

    def __init__(self, f):
        if isinstance(f, basestring):
            f = io.BytesIO(f)

        self.f = f
        self.IHDR = None

    def tell(self):
        return self.f.tell()

    def seek(self, pos):
        self.f.seek(pos)

    def stream(self):
        return self.f

    def data(self):
        self.seek(0)
        return bytearray(self.f.read())

    class BadSignature (Exception):
        pass

    class BadChunk (Exception):
        pass

    def read_signature(self):
        header = bytearray(self.f.read(8))
        if header != PNG.signature:
            raise PNG.BadSignature
        return PNG.signature

    def read_chunk(self):
        length = struct.unpack(">I", self.f.read(4))[0]
        chunk_type = self.f.read(4)
        chunk_data = self.f.read(length)
        if len(chunk_data) != length:
            raise PNG.BadChunk
        crc = self.f.read(4)
        if len(crc) != 4:
            raise PNG.BadChunk
        return (chunk_type, chunk_data, crc)

    def read_IHDR(self):
        (chunk_type, chunk_data, crc) = self.read_chunk()
        if chunk_type != "IHDR":
            raise PNG.BadChunk
        #  Width:              4 bytes
        #  Height:             4 bytes
        #  Bit depth:          1 byte
        #  Color type:         1 byte
        #  Compression method: 1 byte
        #  Filter method:      1 byte
        #  Interlace method:   1 byte
        return struct.unpack(">IIBBBBB", chunk_data)

    def read_header(self):
        self.read_signature()
        self.IHDR = self.read_IHDR()
        return self.IHDR

    def get_size(self):
        if not self.IHDR:
            pos = self.tell()
            self.seek(0)
            self.read_header()
            self.seek(pos)
        return self.IHDR[0:2]

    def filter_chunks(self, chunks):
        self.seek(0)
        out = StringIO.StringIO()
        out.write(self.read_signature())
        while True:
            chunk_type, chunk_data, crc = self.read_chunk()
            if chunk_type in chunks:
                out.write(struct.pack(">I", len(chunk_data)))
                out.write(chunk_type)
                out.write(chunk_data)
                out.write(crc)
            if chunk_type == "IEND":
                break
        return PNG(out)


class FontMetrics:

    def __init__(self, upem, ascent, descent):
        self.upem = upem
        self.ascent = ascent
        self.descent = descent


class StrikeMetrics:

    def __init__(self, bitmap_width, bitmap_height, ppem):
        self.width = bitmap_width  # in pixels
        self.height = bitmap_height  # in pixels
        self.x_ppem = self.y_ppem = ppem


class GlyphMap:

    def __init__(self, glyph, offset, image_format):
        self.glyph = glyph
        self.offset = offset
        self.image_format = image_format


# Based on http://www.microsoft.com/typography/otspec/ebdt.htm
class CBDT:

    def __init__(self, font_metrics, stream=None):
        self.stream = stream if stream != None else bytearray()
        self.font_metrics = font_metrics
        self.base_offset = 0
        self.base_offset = self.tell()

    def tell(self):
        return len(self.stream) - self.base_offset

    def write(self, data):
        self.stream.extend(data)

    def data(self):
        return self.stream

    def write_header(self):
        self.write(struct.pack(">L", 0x00020000))  # FIXED version

    def start_strike(self, strike_metrics):
        self.strike_metrics = strike_metrics
        self.glyph_maps = []

    def write_glyphs(self, glyphs, glyph_images, image_format):
        for glyph in glyphs:
            img_file = glyph_images[glyph]
            offset = self.tell()
            self.write_format17(PNG(img_file))
            self.glyph_maps.append(GlyphMap(glyph, offset, image_format))

    def end_strike(self):
        self.glyph_maps.append(GlyphMap(None, self.tell(), None))
        glyph_maps = self.glyph_maps
        del self.glyph_maps
        del self.strike_metrics
        return glyph_maps

    def write_smallGlyphMetrics(self, width, height):
        ascent = self.font_metrics.ascent
        descent = self.font_metrics.descent
        upem = self.font_metrics.upem
        y_ppem = self.strike_metrics.y_ppem

        x_bearing = 0
        # center vertically
        line_height = (ascent + descent) * y_ppem / float(upem)
        line_ascent = ascent * y_ppem / float(upem)
        y_bearing = int(round(line_ascent - .5 * (line_height - height)))
        y_bearing = min(y_bearing, 127)
        advance = width

        # smallGlyphMetrics
        # Type    Name
        # BYTE    height
        # BYTE    width
        # CHAR    BearingX
        # CHAR    BearingY
        # BYTE    Advance
        self.write(struct.pack("BBbbB",
                               height, width,
                               x_bearing, y_bearing,
                               advance))

    png_allowed_chunks = ["IHDR", "PLTE", "tRNS", "sRGB", "IDAT", "IEND"]

    def write_format17(self, png):
        width, height = png.get_size()

        png = png.filter_chunks(self.png_allowed_chunks)

        self.write_smallGlyphMetrics(width, height)

        png_data = png.data()
        # ULONG data length
        self.write(struct.pack(">L", len(png_data)))
        self.write(png_data)

# Based on http://www.microsoft.com/typography/otspec/eblc.htm


class CBLC:

    def __init__(self, font_metrics, stream=None):
        self.stream = stream if stream != None else bytearray()
        self.streams = []
        self.font_metrics = font_metrics
        self.base_offset = 0
        self.base_offset = self.tell()

    def tell(self):
        return len(self.stream) - self.base_offset

    def write(self, data):
        self.stream.extend(data)

    def data(self):
        return self.stream

    def push_stream(self, stream):
        self.streams.append(self.stream)
        self.stream = stream

    def pop_stream(self):
        stream = self.stream
        self.stream = self.streams.pop()
        return stream

    def write_header(self):
        self.write(struct.pack(">L", 0x00020000))  # FIXED version

    def start_strikes(self, num_strikes):
        self.num_strikes = num_strikes
        self.write(struct.pack(">L", self.num_strikes))  # ULONG numSizes
        self.bitmapSizeTables = bytearray()
        self.otherTables = bytearray()

    def write_strike(self, strike_metrics, glyph_maps):
        self.strike_metrics = strike_metrics
        self.write_bitmapSizeTable(glyph_maps)
        del self.strike_metrics

    def end_strikes(self):
        self.write(self.bitmapSizeTables)
        self.write(self.otherTables)
        del self.bitmapSizeTables
        del self.otherTables

    def write_sbitLineMetrics_hori(self):
        ascent = self.font_metrics.ascent
        descent = self.font_metrics.descent
        upem = self.font_metrics.upem
        y_ppem = self.strike_metrics.y_ppem

        # sbitLineMetrics
        # Type    Name
        # CHAR    ascender
        # CHAR    descender
        # BYTE    widthMax
        # CHAR    caretSlopeNumerator
        # CHAR    caretSlopeDenominator
        # CHAR    caretOffset
        # CHAR    minOriginSB
        # CHAR    minAdvanceSB
        # CHAR    maxBeforeBL
        # CHAR    minAfterBL
        # CHAR    pad1
        # CHAR    pad2
        line_height = div((ascent + descent) * y_ppem, upem)
        ascent = min(div(ascent * y_ppem, upem), 127)
        descent = - (line_height - ascent)
        self.write(struct.pack("bbBbbbbbbbbb",
                               ascent, descent,
                               self.strike_metrics.width,
                               0, 0, 0,
                               0, 0, 0, 0,  # TODO
                               0, 0))

    def write_sbitLineMetrics_vert(self):
        self.write_sbitLineMetrics_hori()  # XXX

    def write_indexSubTable1(self, glyph_maps):
        image_format = glyph_maps[0].image_format

        self.write(struct.pack(">H", 1))  # USHORT indexFormat
        self.write(struct.pack(">H", image_format))  # USHORT imageFormat
        imageDataOffset = glyph_maps[0].offset
        self.write(struct.pack(">L", imageDataOffset))  # ULONG imageDataOffset
        for gmap in glyph_maps[:-1]:
            # ULONG offsetArray
            self.write(struct.pack(">L", gmap.offset - imageDataOffset))
            assert gmap.image_format == image_format
        self.write(struct.pack(">L", glyph_maps[-1].offset - imageDataOffset))

    def write_bitmapSizeTable(self, glyph_maps):
        # count number of ranges
        count = 1
        start = glyph_maps[0].glyph
        last_glyph = start
        last_image_format = glyph_maps[0].image_format
        for gmap in glyph_maps[1:-1]:
            if last_glyph + 1 != gmap.glyph or last_image_format != gmap.image_format:
                count += 1
            last_glyph = gmap.glyph
            last_image_format = gmap.image_format
        headersLen = count * 8

        headers = bytearray()
        subtables = bytearray()
        start = glyph_maps[0].glyph
        start_id = 0
        last_glyph = start
        last_image_format = glyph_maps[0].image_format
        last_id = 0
        for gmap in glyph_maps[1:-1]:
            if last_glyph + 1 != gmap.glyph or last_image_format != gmap.image_format:
                headers.extend(struct.pack(
                    ">HHL", start, last_glyph, headersLen + len(subtables)))
                self.push_stream(subtables)
                self.write_indexSubTable1(glyph_maps[start_id:last_id + 2])
                self.pop_stream()

                start = gmap.glyph
                start_id = last_id + 1
            last_glyph = gmap.glyph
            last_image_format = gmap.image_format
            last_id += 1
        headers.extend(struct.pack(">HHL", start, last_glyph,
                                   headersLen + len(subtables)))
        self.push_stream(subtables)
        self.write_indexSubTable1(glyph_maps[start_id:last_id + 2])
        self.pop_stream()

        indexTablesSize = len(headers) + len(subtables)
        numberOfIndexSubTables = count
        bitmapSizeTableSize = 48 * self.num_strikes

        indexSubTableArrayOffset = 8 + \
            bitmapSizeTableSize + len(self.otherTables)

        self.push_stream(self.bitmapSizeTables)
        # bitmapSizeTable
        # Type    Name    Description
        # ULONG    indexSubTableArrayOffset    offset to index subtable from
        # beginning of CBLC.
        self.write(struct.pack(">L", indexSubTableArrayOffset))
        # ULONG    indexTablesSize    number of bytes in corresponding index
        # subtables and array
        self.write(struct.pack(">L", indexTablesSize))
        # ULONG    numberOfIndexSubTables    an index subtable for each range
        # or format change
        self.write(struct.pack(">L", numberOfIndexSubTables))
        # ULONG    colorRef    not used; set to 0.
        self.write(struct.pack(">L", 0))
        # sbitLineMetrics    hori    line metrics for text rendered
        # horizontally
        self.write_sbitLineMetrics_hori()
        self.write_sbitLineMetrics_vert()
        # sbitLineMetrics    vert    line metrics for text rendered vertically
        # USHORT    startGlyphIndex    lowest glyph index for this size
        self.write(struct.pack(">H", glyph_maps[0].glyph))
        # USHORT    endGlyphIndex    highest glyph index for this size
        self.write(struct.pack(">H", glyph_maps[-2].glyph))
        # BYTE    ppemX    horizontal pixels per Em
        self.write(struct.pack(">B", self.strike_metrics.x_ppem))
        # BYTE    ppemY    vertical pixels per Em
        self.write(struct.pack(">B", self.strike_metrics.y_ppem))
        # BYTE    bitDepth    the Microsoft rasterizer v.1.7 or greater supports the
        # following bitDepth values, as described below: 1, 2, 4, and 8.
        self.write(struct.pack(">B", 32))
        # CHAR    flags    vertical or horizontal (see bitmapFlags)
        self.write(struct.pack(">b", 0x01))
        self.pop_stream()

        self.push_stream(self.otherTables)
        self.write(headers)
        self.write(subtables)
        self.pop_stream()


def main(argv):
    import glob
    from fontTools import ttLib

    font_file = argv[1]
    out_file = argv[2]
    del argv

    def add_font_table(font, tag, data):
        tab = ttLib.tables.DefaultTable.DefaultTable(tag)
        tab.data = str(data)
        font[tag] = tab

    def drop_tables(font):
        for tag in ['cvt ', 'fpgm', 'glyf', 'loca', 'prep', 'CFF ', 'VORG', 'sbix', 'vmtx', 'vhea', 'morx']:
            try:
                del font[tag]
            except KeyError:
                pass

    print

    font = ttLib.TTFont(font_file, recalcBBoxes=False)
    print "Loaded font '%s'." % font_file

    font_metrics = FontMetrics(font['head'].unitsPerEm,
                               font['hhea'].ascent,
                               -font['hhea'].descent)
    print "Font metrics: upem=%d ascent=%d descent=%d." % \
          (font_metrics.upem, font_metrics.ascent, font_metrics.descent)

    glyph_metrics = font['hmtx'].metrics

    unicode_cmap = font['cmap'].tables[0]
    unicode_cmap.platformID = 3
    unicode_cmap.platEncID = 10

    sstr = font['sbix'].strikes[160]

    image_format = 17

    ebdt = CBDT(font_metrics)
    ebdt.write_header()
    eblc = CBLC(font_metrics)
    eblc.write_header()
    eblc.start_strikes(1)

    glyph_imgs = {}

    width = 0
    height = 0
    advance = 0
    count = 0

    for name, glyph in sstr.glyphs.iteritems():
        try:
            if glyph.imageData is None:
                print "%s has no image data, skipping" % name
                continue

            w, h = PNG(glyph.imageData).get_size()
            a = int(
                round(float(font['hhea'].ascent - font['hhea'].descent) * w / h))
            width = max(w, width)
            height = max(h, height)
            advance += a
            count += 1

            glyph_id = font.getGlyphID(name)
            glyph_imgs[glyph_id] = glyph.imageData
        except PNG.BadSignature:
            print "Bad PNG for %s, skipping" % name
            continue

    advance = div(advance, count)
    glyphs = sorted(glyph_imgs.keys())

    print "%d glyphs." % len(glyphs)

    strike_metrics = StrikeMetrics(
        width, height, div(width * font_metrics.upem, advance))
    print "PPEM: %d; Dim: %dx%d" % (strike_metrics.y_ppem, width, height)

    ebdt.start_strike(strike_metrics)
    ebdt.write_glyphs(glyphs, glyph_imgs, image_format)
    glyph_maps = ebdt.end_strike()

    eblc.write_strike(strike_metrics, glyph_maps)

    print

    ebdt = ebdt.data()
    add_font_table(font, 'CBDT', ebdt)
    print "CBDT table synthesized: %d bytes." % len(ebdt)
    eblc.end_strikes()
    eblc = eblc.data()
    add_font_table(font, 'CBLC', eblc)
    print "CBLC table synthesized: %d bytes." % len(eblc)

    print

    drop_tables(font)
    print "Dropped 'sbix', outline ('glyf', 'CFF ') and related tables."

    print "Inserting ligature tables"
    import os, tempfile
    thdl, tname = tempfile.mkstemp()
    print "temporary file at %s" % tname
    os.close(thdl)
    tfile = open(tname, 'wb')
    tfile.write(ligature_xml)
    tfile.flush()
    tfile.close()
    
    font.importXML(tname)
    
    font.save(out_file)
    
    os.unlink(tname)
    print "Output font '%s' generated." % out_file


if __name__ == '__main__':
    main(sys.argv)
