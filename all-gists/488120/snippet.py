""" 
Script to convert a Xcode3 Color theme into a Xcode4 one.
Example:
bash# python xcode3_theme_to_xcode4.py Twilight.xcolortheme
It will write a new file: Twilight.dvtcolortheme into the same folder as the script is residing in.
"""

import plistlib,sys
""" Define boilerplate of the color theme """
defaultConfig = {	
		'DVTConsoleDebuggerInputTextColor': '0 0 0 1',
		'DVTConsoleDebuggerInputTextFont': 'Menlo-Bold - 11.0',
		'DVTConsoleDebuggerOutputTextColor': '0 0 0 1',
		'DVTConsoleDebuggerOutputTextFont': 'Menlo-Regular - 11.0',
		'DVTConsoleDebuggerPromptTextColor': '0.317071 0.437736 1 1',
		'DVTConsoleDebuggerPromptTextFont': 'Menlo-Bold - 11.0',
		'DVTConsoleExectuableInputTextColor': '0 0 0 1',
		'DVTConsoleExectuableInputTextFont': 'Menlo-Regular - 11.0',
		'DVTConsoleExectuableOutputTextColor': '0 0 0 1',
		'DVTConsoleExectuableOutputTextFont': 'Menlo-Bold - 11.0',
		'DVTConsoleTextBackgroundColor': '0.999899 1 0.999842 1',
		'DVTConsoleTextInsertionPointColor': '0 0 0 1',
		'DVTConsoleTextSelectionColor': '0.576266 0.81005 1 1',
		'DVTDebuggerInstructionPointerColor': '0.705792 0.8 0.544 1',
		'DVTSourceTextBackground': '1 0.995635 0.982541 1',
		'DVTSourceTextBlockDimBackgroundColor': '0.5 0.5 0.5 1',
		'DVTSourceTextInsertionPointColor': '0 0 0 1',
		'DVTSourceTextInvisiblesColor': '0.5 0.5 0.5 1',
		'DVTSourceTextSelectionColor': '0.576266 0.81005 1 1',
		'DVTSourceTextSyntaxColors': {   
			'xcode.syntax.attribute': '0.512 0.423 0.157 1',
			'xcode.syntax.character': '0.11 0 0.81 1',
			'xcode.syntax.comment': '0 0.456 0 1',
			'xcode.syntax.comment.doc': '0 0.456 0 1',
			'xcode.syntax.comment.doc.keyword': '0.008 0.239 0.063 1',
			'xcode.syntax.identifier.class': '0.247 0.431 0.456 1',
			'xcode.syntax.identifier.class.system': '0.359 0.149 0.601 1',
			'xcode.syntax.identifier.constant': '0.149 0.278 0.294 1',
			'xcode.syntax.identifier.constant.system': '0.181 0.052 0.431 1',
			'xcode.syntax.identifier.function': '0.149 0.278 0.294 1',
			'xcode.syntax.identifier.function.system': '0.181 0.052 0.431 1',
			'xcode.syntax.identifier.macro': '0.391 0.22 0.125 1',
			'xcode.syntax.identifier.macro.system': '0.391 0.22 0.125 1',
			'xcode.syntax.identifier.type': '0.247 0.431 0.456 1',
			'xcode.syntax.identifier.type.system': '0.359 0.149 0.601 1',
			'xcode.syntax.identifier.variable': '0.247 0.431 0.456 1',
			'xcode.syntax.identifier.variable.system': '0.359 0.149 0.601 1',
			'xcode.syntax.keyword': '0.665 0.052 0.569 1',
			'xcode.syntax.number': '0.11 0 0.81 1',
			'xcode.syntax.plain': '0 0 0 1',
			'xcode.syntax.preprocessor': '0.391 0.22 0.125 1',
			'xcode.syntax.string': '0.77 0.102 0.086 1',
			'xcode.syntax.url': '0.055 0.055 1 1'
		},
		'DVTSourceTextSyntaxFonts': {  
			'xcode.syntax.plain': 'Menlo-Regular - 11.0'
		}
	}

replacementPoints = [ 
			{"DVTSourceTextBackground": ["Colors","Background" ]},
			{"DVTSourceTextInsertionPointColor": ["Colors","InsertionPoint"]},
			{"DVTSourceTextSelectionColor": ["Colors","Selection"]},
			{"DVTSourceTextSyntaxColors":"Colors"},
			{"DVTSourceTextSyntaxFonts": "Fonts" }
]

xcolortheme = plistlib.readPlist(sys.argv[1])

for x in replacementPoints:
	key = x.keys()[0]
	value = x.values()[0]
	if isinstance(value,list):
		data = xcolortheme
		for y in value:
			data = data[y]

		defaultConfig[key] = data[:]

		del data

		arrayList = ""
		data = xcolortheme
		for y in value:
			arrayList = "%s[\'%s\']" % (arrayList,y)

		exec("del xcolortheme%s" % arrayList)
	else:	
		defaultConfig[key] = xcolortheme[x[key]]

file = "%sdvtcolortheme" % (sys.argv[1][:-12])
plistlib.writePlist(defaultConfig,file)
