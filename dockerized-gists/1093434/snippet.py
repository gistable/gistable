# Generic build script that builds, tests, and creates nuget packages.
# 
# INSTRUCTIONS:
#	Update the following project paths:
#		proj		Path to the project file (.csproj)
#		test		Path to the test project (.csproj)
#		nuspec		Path to the package definition for NuGet.
#		
#		delete any of the lines if not applicable
#
#
#	Update the paths to the build tools:
#		msbuild		Path to msbuild
#		test		Path to mstest.exe (requires Visual Studio) (optional - delete line)
#		nuget		Path to nuget.exe (requires NuGet command line tool) (optional - delete line)
#		trx2html	Path to trx2html.exe (http://trx2html.codeplex.com/) (optional - delete line)
#
#
# USAGE:
#       
#     proj = r'path to project (.csproj)'
#     test = r'path to project containing test (.csproj)'
#     nuspec = r'path to nuspec definition (.nuspec)'
#
#
#     msbuild = r'C:\Windows\Microsoft.NET\Framework\v4.0.30319\MSBuild.exe'
#     mstest = r'C:\Program Files (x86)\Microsoft Visual Studio 10.0\Common7\IDE\MSTest.exe'
#     nuget = r'C:\BuildTools\nuget\2199eada12ce\nuget.exe'
#     trx2html = r'C:\BuildTools\trx2html\0.6\trx2html.exe'
#
#     bld = MsBuilder(msbuild=msbuild, mstest=mstest, nuget=nuget, trx2html=trx2html)
#     bld.run(proj, test, nuspec)
#

import os, shlex, subprocess, re, datetime	
		
class MsBuilder:
	def __init__(self, msbuild=None, mstest=None, nuget=None, trx2html=None):
		# The following dictionary holds the location of the various
		#	msbuild.exe paths for the .net framework versions
		if msbuild==None:
			self.msbuild = r'C:\Windows\Microsoft.NET\Framework\v4.0.30319\MSBuild.exe'
		else:
			self.msbuild = msbuild
			
		# Path to mstest (this requires vs2010 to be installed
		if mstest==None:
			self.mstest = r'C:\Program Files (x86)\Microsoft Visual Studio 10.0\Common7\IDE\MSTest.exe'
		else:
			self.mstest = mstest
		
		# Path to nuget packager
		if nuget==None:
			self.nuget = r'C:\BuildTools\nuget\2199eada12ce\nuget.exe'
		else:
			self.nuget = nuget
		
		# Path to trx2html transformation tool
		if trx2html==None:
			self.trx2html = r'C:\BuildTools\trx2html\0.6\trx2html.exe'
		else:
			self.trx2html = trx2html
		
	def build(self, projPath):
		# Ensure msbuild exists
		if not os.path.isfile(self.msbuild):
			raise Exception('MsBuild.exe not found. path=' + self.msbuild)
			
		arg1 = '/t:Rebuild'
		arg2 = '/p:Configuration=Release'
		p = subprocess.call([self.msbuild, projPath, arg1, arg2])
		if p==1: return False	# exit early
		
		return True
		
	def test(self, testProject):
		if not os.path.isfile(self.msbuild):
			raise Exception('MsBuild.exe not found. path=' + self.msbuild)
		if not os.path.isfile(self.mstest):
			raise Exception('MsTest.exe not found. path=' + self.mstest)
			
		# build the test project
		arg1 = '/t:Rebuild'
		arg2 = '/p:Configuration=Release'
		p = subprocess.call([self.msbuild, testProject, arg1, arg2])
		
		# find the test dll
		f = open(testProject)
		xml = f.read()
		f.close()
		match = re.search(r'<AssemblyName>(.*)</AssemblyName>', xml)
		if not match:
			print 'Could not find "AssemblyName" in test project file.'
			return False
			
		outputFolder = os.path.dirname(testProject) + '\\bin\\Release\\'
		dll =  outputFolder + match.groups()[0] + '.dll'
		resultFile = outputFolder + 'testResults.trx'
		if os.path.isfile(resultFile):
			os.remove(resultFile)
			
		# execute the tests in the container
		arg1 = '/testcontainer:' + dll
		arg2 = '/resultsfile:' + resultFile
		p = subprocess.call([self.mstest, arg1, arg2])
		
		# convert the results file
		if os.path.isfile(self.trx2html):
			subprocess.call([self.trx2html, resultFile])
		else:
			print 'TRX to HTML converter not found. path=' + self.trx2html
		
		if p==1: return False # exit early
			
		return True
		
	def pack(self, packageSpec, version = '0.0.0.0'):
		if not os.path.isfile(self.nuget):
			raise Exception('Nuget.exe not found. path=' + self.nuget)
			
		outputFolder = os.path.dirname(packageSpec) + '\\artifacts\\'
		if not os.path.exists(outputFolder):
			os.makedirs(outputFolder)
			
		p = subprocess.call([self.nuget, 'pack', packageSpec, '-Version', version, '-Symbols', '-o', outputFolder])
			
		if p==1: return False #exit early
		
		return True

		
	def validate(self, projectPath):
		packFile = os.path.dirname(projectPath) + '\\packages.config'
		if os.path.isfile(packFile):
			f = open(packFile)
			xml = f.read()
			f.close()
			print xml
			match = re.search(r'version="0.0.0.0"', xml)
			if match:
				# Found a non-versioned package being used by this project
				return False
		else:
			print 'No "packages.config" file was found. path=' + packFile
			
		return True
		
	def run(self, proj=None, test=None, nuspec=None):
		summary = '';
		
		# File header	
		start = datetime.datetime.now()
		print '\n'*5
		summary += self.log('STARTED BUILD - ' + start.strftime("%Y-%m-%d %H:%M:%S"))

		# Build the project
		if proj is not None:
			buildOk = self.build(proj)
			if not buildOk:
				self.log('BUILD: FAILED', start)
				sys.exit(100)
			summary += self.log('BUILD: SUCCEEDED', start)
		else:
			summary += self.log('BUILD: NOT SPECIFIED')
			
		# Build the tests and run them
		if test is not None:
			testOk = self.test(test)
			if not testOk:
				print self.log('TESTS: FAILED', start)
				sys.exit(100)
			summary += self.log('TESTS: PASSED', start)
		else:
			summary += self.log('TESTS: NOT SPECIFIED')

		# Package up the artifacts
		if nuspec is not None:
			packOk = self.pack(nuspec, '0.0.0.0')
			if not packOk:
				print self.log('NUGET PACK: FAILED', start)
				sys.exit(100)
			summary += self.log('NUGET PACK: SUCCEEDED', start)
		else:
			summary += self.log('NUGET PACK: NOT SPECIFIED')
			
		# Validate dependencies
		if not self.validate(proj):
			print self.log('DEPENDENCIES: NOT VALIDATED - DETECTED UNVERSIONED DEPENDENCY', start)
			sys.exit(100)
		summary += self.log('DEPENDENCIES: VALIDATED', start)

		# Build footer
		stop = datetime.datetime.now()
		diff = stop - start
		summary += self.log('FINISHED BUILD', start)
		
		# Build summary
		print '\n\n' + '-'*80
		print summary
		print '-'*80
		
	def log(self, message, start=None):
		timestamp = ''
		numsecs = ''
		if start is not None:
			split = datetime.datetime.now()
			diff = split - start
			timestamp = split.strftime("%Y-%m-%d %H:%M:%S") + '\t'
			numsecs = ' (' + str(diff.seconds) + ' seconds)'
		msg = timestamp + message + numsecs + '\n\n'
		print '='*10 + '> ' + msg
		return msg