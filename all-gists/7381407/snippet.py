import sys
import re
class mysql_to_mssql_converter:
	"""	
		Python script for converting MySQL dump into MSSQL compatible scripts
		Based on my project, I know the following points need to be converted
		1. 		` need to be removed
		2.		ENGINE=InnoDB etc need to be removed
		3.		int(size), (size) is not supported for int, need to be removed. 
		4. 		AUTO_INCREMENT need to be changed to IDENTITY(1,1)
		5. 		UNSIGNED need to be removed
		6. 		\n in text/varchar need to be changed to CHAR(13)+CHAR(10)
		7. 		SET SQL_MODE need to be removed
		8. 		SET time_zone need to be removed
		9. 		If AUTO_INCREMENT is used, need to SET IDENTITY_INSERT ON before inserting
				records into the table. Then set it to OFF after insersion. 
		10. 		tinyint need to be changed into int
		11. 		Remove 'IF NOT EXISTS'
		12.		There are some keywords in MSSQL like 'index' and 'file'. I'm not going to cover
				them here. You need to watch out.
	"""	
	def __init__(self,filename,output='output.sql'):
		if filename is None:
			exit('Please specify the file to be converted')
		
		isIdentity = False
		tableName = ''
		infile=open(filename)
		outfile=open(output,'w')
		outputLines=[]
		for line in infile.readlines():

			# remove `
			line=line.replace('`','')

			# remove 'IF NOT EXISTS'
			line=self.genPattern('IF NOT EXISTS').sub('',line)

			# replace tinyint to int
			line=self.genPattern('TINYNIT').sub('INT',line)

			# replace int(size) into int
			line=self.genPattern('int\(\d+\)').sub('INT',line)

			# remove UNSIGNED
			line=self.genPattern('UNSIGNED').sub('',line)


			# check if the table as AUTO_INCREMENT/IDENTITY
			if self.genPattern('AUTO_INCREMENT').search(line):
				isIdentity=True
				# replace AUTO_INCREMENT with IDENTITY
				line=self.genPattern('AUTO_INCREMENT').sub('IDENTITY(1,1)',line)


			# replace \n to  CHAR(13)+CHAR(10)
			line=line.replace('\\n','\' + CHAR(13)+CHAR(10) + \'')
			
			#remove  SET SQL_MODE line
			if self.genPattern('SET SQL_MODE').match(line):
				continue
			#remove SET time_zone line
			elif self.genPattern('SET time_zone').match(line):
				continue
			#remove ENGINE=XXXX etc
			elif line.find('ENGINE=') !=-1:
				line= ')\n'
			# turn on IDENTITY_INSERT if table uses AUTO_INCREMENT
			elif self.genPattern('INSERT INTO').match(line) and isIdentity:
				line='SET IDENTITY_INSERT %s ON;\n%s' % (tableName, line)
			# detect table name
			elif self.genPattern('CREATE TABLE').match(line):
				# turn off IDENTITY_INSERT
				if isIdentity:
					line='SET IDENTITY_INSERT %s OFF;\n%s' % (tableName, line)
					isIdentity = False
				# save table name
				tableName=line.split(' ')[-2]
				line='DROP TABLE %s;\n%s' % (tableName, line)
			pass

			outputLines.append(line)
		#print(outputLines)
		outfile.writelines(outputLines)

	def genPattern(self,patternStr,ignoreCase=True):
		"""
		Shortcut to generate a pattern with IGNORECASE on
		"""
		if ignoreCase:
			return re.compile(patternStr,re.IGNORECASE)
		else:
			return re.compile(patternStr)

if __name__ == "__main__":
	if len(sys.argv)<2:
		exit('!!!Error!!!Please specify the file to be converted')
	else:
		mysql_to_mssql_converter(sys.argv[1])