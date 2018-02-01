#!/usr/bin/python

import os
import AppKit
import Foundation

theDictionary = {
	'DVTConsoleDebuggerInputTextColor': '0 0 0 1',
	'DVTConsoleDebuggerInputTextFont': 'Menlo-Bold - 11.0',
	'DVTConsoleDebuggerOutputTextColor': '0 0 0 1',
	'DVTConsoleDebuggerOutputTextFont': 'Menlo-Regular - 11.0',
	'DVTConsoleDebuggerPromptTextColor': '0 0 0 1',
	'DVTConsoleDebuggerPromptTextFont': 'Menlo-Bold - 11.0',
	'DVTConsoleExectuableInputTextColor': '0 0 0 1',
	'DVTConsoleExectuableInputTextFont': 'Menlo-Regular - 11.0',
	'DVTConsoleExectuableOutputTextColor': '0 0 0 1',
	'DVTConsoleExectuableOutputTextFont': 'Menlo-Bold - 11.0',
	'DVTConsoleTextBackgroundColor': '1 1 1 1',
	'DVTConsoleTextInsertionPointColor': '0 0 0 1',
	'DVTConsoleTextSelectionColor': '0.737119 0.982014 0.469429 1',
	'DVTDebuggerInstructionPointerColor': '0.705792 0.8 0.544 1',
	'DVTSourceTextBackground': '1 1 1 1',
	'DVTSourceTextBlockDimBackgroundColor': '0.5 0.5 0.5 1',
	'DVTSourceTextInsertionPointColor': '0 0 0 1',
	'DVTSourceTextInvisiblesColor': '0.5 0.5 0.5 1',
	'DVTSourceTextSelectionColor': '0.737119 0.982014 0.469429 1',
	'DVTSourceTextSyntaxFonts': {'xcode.syntax.plain': 'Menlo-Regular - 11.0'},
	'DVTSourceTextSyntaxColors': {},
	}

theNames = ['attribute','character','comment','comment.doc','comment.doc.keyword','identifier.class','identifier.class.system','identifier.constant','identifier.constant.system','identifier.function','identifier.function.system','identifier.macro','identifier.macro.system','identifier.type','identifier.type.system','identifier.variable','identifier.variable.system','keyword','number','plain','preprocessor','string','url']


for N, theName in enumerate(theNames):
	theName = 'xcode.syntax.' + theName
	theHue = float(N) / len(theNames)
	theColor = AppKit.NSColor.colorWithDeviceHue_saturation_brightness_alpha_(theHue, 1, 1, 1)

	theColor = theColor.colorUsingColorSpace_(AppKit.NSColorSpace.deviceRGBColorSpace())

	theDictionary['DVTSourceTextSyntaxColors'][theName] = '%f %f %f %f' % (theColor.redComponent(), theColor.greenComponent(), theColor.blueComponent(), theColor.alphaComponent())

print theDictionary

theDictionary = Foundation.NSDictionary.dictionaryWithDictionary_(theDictionary)

theDictionary.writeToFile_atomically_(os.path.expanduser('~/Desktop/Rainbow.dvtcolortheme'), True)
