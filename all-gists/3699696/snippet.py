# -*- coding: utf-8 -*-
# java.py - sublimelint package for checking java files

import sublime
import subprocess
import os
import os.path
import re

from base_linter import BaseLinter, INPUT_METHOD_FILE

CONFIG = {
    'language': 'UnityC#'
}

#書いてる途中のファイルを書き出すtempフォルダ
TMPPATH_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '.dtmpfiles'))
if not os.path.exists(TMPPATH_DIR):
    os.mkdir(TMPPATH_DIR)

class Linter(BaseLinter):
    def built_in_check(self, view, code, filename):
        #パス取得
        work_path = os.path.dirname(filename)
        file_name = os.path.basename(filename)

         #コンパイル場所の設定取得
        settings = view.settings().get('SublimeLinter', {}).get(self.language, {})
        if(settings):
            dwd = settings.get('working_directory', [])
            if(dwd):
                #プロジェクトに設定あったらそれを取得
                work_path = dwd

        #書いてる途中のファイルをtempファイルとしてcsharp.py直下に書き出し
        tempfilePath = os.path.join(TMPPATH_DIR, file_name)

        with open(tempfilePath, 'w') as f:
            f.write(code)

        args = ["mcs", tempfilePath, "-target:library", "-r:/Applications/Unity/Unity.app/Contents/Frameworks/Managed/UnityEngine.dll,/Applications/Unity/Unity.app/Contents/Frameworks/Managed/UnityEditor.dll,/Users/username/project/Unity/project/simpledata/Library/ScriptAssemblies/Assembly-CSharp.dll"]

        try:
            #コンパイル
            process = subprocess.Popen(args,
                                        cwd=work_path,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT,
                                        startupinfo=self.get_startupinfo())
            result = process.communicate(None)[0]
        finally:
            if tempfilePath:
                #保存したファイルの削除
                os.remove(tempfilePath)

        return result.strip()

    def parse_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):
        for line in errors.splitlines():
            print line
            # Template.cs(24,16): error CS0246: The type or namespace name `TemplateFrame' could not be found. Are you missing a using directive or an assembly reference?
            match = re.match(r'^(?P<filename>.+\.cs)\((?P<line>\d+),(?P<col>\d+)\): (?P<level>\w+) (?P<error>.+)', line)

            if match:
                tab_filename = os.path.basename(view.file_name())
                error_filename = os.path.basename(match.group('filename'))
                level = match.group('level')
                error, line = level + ' ' + match.group('error'), match.group('line')
                col = match.group('col')

                messages = None
                underlines = None
                if level == 'warning':
                    messages = warningMessages
                    underlines = warningUnderlines
                else:
                    messages = errorMessages
                    underlines = errorUnderlines

                if(tab_filename == error_filename):
                    self.add_message(int(line), lines, error, messages)
                    self.underline_word(view, int(line), int(col), underlines)
