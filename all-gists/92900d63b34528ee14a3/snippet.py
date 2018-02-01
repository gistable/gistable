#   THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
#   FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.

# XL Deploy CLI script to create a DAR from artifacts defined in properties. Optionally also deploy to an env
# 2014-05-28 - 1 - Tom Batchelor
# 2014-05-29 - 2 - Tom Batchelor - Update to support properties files, also some refactoring thing into functions
# 2014-06-05 - 3 - Tom Batchelor - Update to support getting CLASSLOADER_MODE, CLASSLOADER_POLICY, SHARED_LIBRARIES and TAGS from XL Deploy
#                               dictionaries. Also creates ATPCO properties file copy tasks. Added wait for deployment with full status
#                               output
# 2014-06-10 - 4 - Tom Batchelor - Update to enable creatation of muliple artifact packages based on the properties file. Note this breaks
#                               changes made to version 3. Now items such as tags are set using the standard properties mechanism.
# 2015-09-18 - 5 - Tom Batchelor - Change to auto detect windows and Unix paths. Added functionality to auto-create zip files when a fileLocation
#                               for a binary artifact is a folder
#
# Version 5
#
# Usage:
#
# cli.sh -host <XLDeployHost> -username <username> -password <password> -f $PWD/createDar.py -- -n <appName> -b <buildID> -p <propertiesFile> -a <autoDeploy true|false> -e <deployEnv> -x <extraProperties>
#
# Properties file is in the format artifactID.key=value where artifactID is used to separate
# properties for different artifacts. Note that artifactID.type and artifactID.name always needs to be speced
# extraProperties need to be in Python literal dictionary format, e.g:
#    "{'webContent.type':'www.WebContent','webContent.name':'myWebContent','webContent.fileLocation':'/Users/tom/scratch/PetPortal_pages.zip'}"
#
# This script can also pull properties from a dictionary, and will search for a dictionary in the location:
# /Environments/AppDictionaries/<appName>
#
# Sample properties, note that lists need to be in Python list literal format:
#
# artifact.type=was.War
# artifact.fileLocation=/Users/tom/qb_repo/builds/17/artifacts/dist/Cars_Sample_App.war
# artifact.name=Cars_Sample_App
# artifact.tags=['WAR']
# datasource.type=jbossas.NonTransactionalDatasourceSpec
# datasource.name=Tom_Datasource
# datasource.jndiName=jndi/tomsds
# datasource.userName={{DB_USERNAME}}
# datasource.password={{DB_PASSWORD}}
# datasource.connectionUrl={{DB_CONNECTION_URL}}
#
# Example command execution (using above props file):
#
# cli.sh -username admin -password deploy -source /Users/tom/Documents/CreateDARCLI/createDAR.py -- -n TestApp -b 1.0-6 -p /Users/tom/builds/propertiesSample.properties -a true -e "WAS/WAS8ND"
#
# App name: TestApp
# Build ID: 1.0-6
# File location: /Users/tom/builds/Cars_Sample_App.war
# Properties File: /Users/tom/builds/propertiesSample.properties
# Auto deploy: true
# Environment: WAS/WAS8ND
#
# Properties are:
# {'datasource.jndiName': 'jndi/tomsds', 'datasource.userName': '{{DB_USERNAME}}', 'artifact.type': 'was.War', 'artifact.name': 'Cars_Sample_App', 'datasource.type': 'jbossas.NonTransactionalDatasourceSpec', 'artifact.fileLocation': '/Users/tom/qb_repo/builds/17/artifacts/dist/Cars_Sample_App.war', 'datasource.password': '{{DB_PASSWORD}}', 'datasource.name': 'Tom_Datasource', 'datasource.connectionUrl': '{{DB_CONNECTION_URL}}'}
#
# Performing initial deployment
# Deploying with task ID: 1333ef80-c07a-4366-96b1-64dc1e743bf6


import getopt, sys, time, ast, os, zipfile


##############################################################
#
# Prints output from all steps of a task, either running or complete
# to the console
#
# Param - taskInfo - TaskInfo - TaskInfo object
# Param - verbose - boolean - Verbose output or not
#
# Returns - No return value
#
##############################################################
def printSteps(taskInfo, verbose=True):
    for i in range(taskInfo.nrOfSteps):
        info = tasks.step(taskInfo.id, i+1)
        if info.state == 'PENDING':
            print "%s: %s %s [NOT EXECUTED]" % (str(i+1), info.description, info.state)
        else:
            print "%s: %s %s %s %s" % (str(i+1), info.description, info.state, info.startDate, info.completionDate)
            if verbose:
                print info.log
        print

##############################################################
#
# Safely read a CI from XL Deploy. Return None if the ci does
# no exist
#
# Param - id - string - Repository path to the CI
#
# Returns - ci - ConfigurationItem - CI or None if doesn't exist
#
##############################################################
def readCi(id):
    try:
        return repository.read(id)
    except:
        return None

##############################################################
#
# Returns the Application Name from a package path
#
# Param - package - string - Repository path to the package
#
# Returns - appName - string - Application name
#
##############################################################
def getAppFromPackagePath(package):
    return package.rpartition('/')[0].rpartition('/')[2]

##############################################################
#
# Synchronously deploys an application to a target environment.
# This will determin if this is an intial or an upgrade deployment
# and will perform the correct on as appropriate. This will output
# deployment steps as the compelete and print a summary on
# deployment completion
#
# Param - deployEnv - string - Repository path to the deployment
#                           environment
# Param - package - string - Repository path to the deployment
#                           package
#
# Returns - taskID - string -  Task ID for the executed task
# Returns - success - boolean - Indicates deployment end status
#
##############################################################
def syncDeployUpdate(deployEnv, package):
    appName = getAppFromPackagePath(package)
    
    # Read Environment
    environment = repository.read('Environments/' + deployEnv)
    
    # Deployment
    existingDeployment = readCi("%s/%s" % (environment.id, appName))
    if existingDeployment is not None:
        # Upgrade
        print 'Performing upgrade'
        deploymentRef = deployment.prepareUpgrade(package, existingDeployment.id)
        deploymentRef = deployment.prepareAutoDeployeds(deploymentRef)
    else:
        # Initial
        print 'Performing initial deployment'
        deploymentRef = deployment.prepareInitial(package,environment.id)
        deploymentRef = deployment.generateAllDeployeds(deploymentRef)
    deploymenyRef = deployment.validate(deploymentRef)
    taskID = deployment.deploy(deploymentRef).id
    print "Deploying with task ID: " + taskID
    deployit.startTask(taskID)

    taskState = 'EXECUTING'
    while taskState == 'EXECUTING':
        time.sleep(5)
        taskInfo = deployit.retrieveTaskInfo(taskID)
        taskState = taskInfo.state
        currentStep = taskInfo.currentStepNr
        print "Task now at step %s of %s. State: %s" % (currentStep, taskInfo.nrOfSteps, taskState)

    taskInfo = deployit.retrieveTaskInfo(taskID)
    print "Final task state: %s after %s of %s steps" % (taskInfo.state, min(currentStep + 1, taskInfo.nrOfSteps), taskInfo.nrOfSteps)
    printSteps(taskInfo, True)
    success = True
    if taskInfo.state != 'EXECUTED':
        print "WARN: Deployment was not completed successfully. Please log in to Deployit to review the deployment or contact a Deployit administrator"
        print "INFO: Cancelling task"
        tasks.cancel(taskInfo.id)
        success = False
    else:
        tasks.archive(taskInfo.id)
    return taskID, success

##############################################################
#
# Reads a properties file from the file system and creates a
# dictionary of key/value pairs. '=' is used as a the separator
# and exmaple line is:
#
#      key=value
#
# Param - propertiesFile - string - Path to the properties file
#
# Returns - propertiesMap - dict - Dictionary of properties
#                           from the file
#
##############################################################
def parsePropertiesFile(propertiesFile):
    propertiesMap = {}
    for line in open(propertiesFile):
        key, sep, val = line.strip().partition('=')
        propertiesMap[key] = val
    return propertiesMap

##############################################################
#
# Creates a list of artifacts from a properties dictionary
# properties keys should be in the format:
#      identifier.property
#
# For example:
#      artifact1.name=MyArtifactName
#
# Param - propertiesMap - dict - Dictionary of properties
#
# Returns - artifactList - list - List of artifact identifiers
#
##############################################################
def createArtifactList(propertiesMap):
    artifactIDs = []
    for key, val in propertiesMap.items():
        type, sep, subkey = key.strip().partition('.')
        if not type in artifactIDs:
            artifactIDs.append(type)
    return artifactIDs

##############################################################
#
# NOTE: Untested
#
# Creates a WebSphere session manager spec as a child of the parent,
# commonly this parent is  was.Ear.
#
# Param - parent - string - Parent to hold the spec, e.g. a was.Ear
# Param - props - - dict Session Manager Spec specific properties,
#               note that these should alredy be subsetted by
#               subsetProps
#
# Returns - No return value
#
##############################################################
def createSessionManager(parent, propertiesMap):
    sessionProps = subsetProps('session',propertiesMap)
    if len(sessionProps) != 0:
        name = sessionProps['name']
        del sessionProps['name']
        sessionManager = factory.configurationItem(parent + '/' + name,'was.SessionManagerSpec',sessionProps)
        repository.create(sessionManager)

##############################################################
#
# Will take a dictionary and return a subset based on the 'parent'
# element in the key. Keys should be in the format
#   parent.item
#
# The value of 'parent' above will be used to subset the dictionary
# and the return dictionary would use 'item' as the key for this entry
#
# Param - parent - string - Parent value to select enties for
# Param - propertiesMap - dict - Dictionary of properties
#
# Returns - dictionary - dict - Dictionary subset with keys made
#                       of just the 'item' property from the above
#                       example
#
##############################################################
def subsetProps(parent, propertiesMap):
    subset = {}
    for key, val in propertiesMap.items():
        type, sep, subkey = key.strip().partition('.')
        if type == parent:
            subset[subkey] = val
    return subset

##############################################################
#
# Returns a XL Deploy dictionary as a Python dictionary if
# the XL Deploy dictionart doesn't exist, returns "None"
#
# Param - dictionaryPath - string - Xl Dictionary to retrieve
#
# Returns - dictionary - dict -XL Dictionary as a Python
#                       Dictionary, None if it doesn't exist
#
##############################################################
def getDictionaryEntries(dictionaryPath):
    if repository.exists('Environments/' + dictionaryPath):
        dictionary = repository.read('Environments/' + dictionaryPath)
        return dictionary.entries
    else:
        return None

##############################################################
#
# Returns the value associated with the key. If the key does
# not exist, returns "None"
#
# Param - dictionary - dict - Dictionary to query
# Param - key - string - Key to get
#
# Returns - value - not-specified - Value for the key, None if
#                               it doesn't exist
#
##############################################################
def safeGetValue(dictionary, key):
    try:
        return dictionary[key]
    except:
        return None

##############################################################
#
# Iterates over a properties dictionary and converts list items
# form strings to list, if the string looks like
#      ['string1','string2']
#
# Detection for this is based on opening and closing square braces
#
# For example:
#      artifact1.name=MyArtifactName
#
# Param - propertiesMap - dict - Dictionary of properties
#
# Returns - propertiesMap - dict - Dictionary of properties,
#                               with lists as list type
#
##############################################################
def convertLists(propertiesMap):
    for key, value in propertiesMap.items():
        if value.startswith('[') and value.endswith(']'):
            value = ast.literal_eval(value)
            propertiesMap[key] = value
    return propertiesMap

##############################################################
#
# Creates a zip to upload from a directory. For example if
# the fileLocation is /a/b/stuff it will create
# /a/b/stuff/stuff.zip with the contents of /a/b/stuff/
# as the root of the zip
#
# Param - dirLocation - string - path to the folder
#
# Returns - fileLocation - string - path to the zip
#
##############################################################

def createZipFromFolder(dirLocation):
    dirName = ''
    fileLocation = ''
    unix = '/' in dirLocation
    # Figure out zip file name
    if unix:
        dirName = dirLocation.rpartition('/')[2]
        fileLocation = dirLocation + '/' + dirName + '.zip'
    else:
        # Assume Windows
        dirName = dirLocation.rpartition('\\')[2]
        fileLocation = dirLocation + '\\' + dirName + '.zip'
    os.chdir(dirLocation)
    if os.path.exists(fileLocation):
        os.remove(fileLocation)
    # Create zip file, loop over and add stuff.
    zipf = zipfile.ZipFile(fileLocation, 'w')
    for root, dirs, files in os.walk(dirLocation):
        if len(root) == len(dirLocation):
            root = ""
        else:
            root = root[len(dirLocation) + 1:]
        print root
        for file in files:
            if file != dirName + '.zip':
                print os.path.join(root, file)
                zipf.write(str(os.path.join(root, file)))
    zipf.close()
    return fileLocation


##############################################################
#
# Main
#
##############################################################

# vars
buildID = None
appName = None
propertiesFile = None
autoDeploy = None
deployEnv = None
commandLineProps = None

success = True

# Parse out the arguments
try:
    opts, args = getopt.getopt(sys.argv[1:],'hn:b:p:a:e:x:',['appName=','buildID=','propertiesFile=','autoDeploy=','deployEnv=','extraProperties='])
except getopt.GetoptError:
    print 'cli.sh -host <XLDeployHost> -username <username> -password <password> -f $PWD/createDar.py -- -n <appName> -b <buildID> -p <propertiesFile> -a <autoDeploy true|false> -e <deployEnv> -x <extraProperties>'
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print 'cli.sh -host <XLDeployHost> -username <username> -password <password> -f $PWD/createDar.py -- -n <appName> -b <buildID> -p <propertiesFile>  -a <autoDeploy true|false> -e <deployEnv> -x <extraProperties>'
        sys.exit(-1)
    elif opt in ('-n', '--appName'):
        appName = arg
    elif opt in ('-b', '--buildID'):
        buildID = arg
    elif opt in ('-p', '--propertiesFile'):
        propertiesFile = arg
    elif opt in ('-a', '--autoDeploy'):
        autoDeploy = arg
    elif opt in ('-e', '--deployEnv'):
        deployEnv = arg
    elif opt in ('-x', '--extraProperties'):
        commandLineProps = ast.literal_eval(arg)

if buildID == None or appName == None:
    print 'ERROR: appName and buildID are mandatory on the command line'
    print 'cli.sh -host <XLDeployHost> -username <username> -password <password> -f $PWD/createDar.py -- -n <appName> -b <buildID> -p <propertiesFile> -a <autoDeploy true|false> -e <deployEnv> -x <extraProperties>'
    sys.exit(-1)

if autoDeploy == None:
    autoDeploy = 'false'

if autoDeploy == 'true':
    if deployEnv == None:
        print 'ERROR: When autoDeploy is \'true\' deployEnv is mandatory on the command line'
        print 'cli.sh -host <XLDeployHost> -username <username> -password <password> -f $PWD/createDar.py -- -n <appName> -b <buildID> -p <propertiesFile> -a <autoDeploy true|false> -e <deployEnv> -x <extraProperties>'
        sys.exit(-1)

# Print Vars
print 'App name: ' + appName
print 'Build ID: ' + buildID
print 'Auto deploy: ' + autoDeploy
if propertiesFile != None:
    print 'Properties File: ' + propertiesFile
else:
    print 'Properties File: '
if autoDeploy == 'true':
    print 'Environment: ' + deployEnv

# Create Properties Map
if propertiesFile != None:
    propertiesMap = parsePropertiesFile(propertiesFile)
else:
    #Just a dummy map
    propertiesMap = {}

# Combine in properties pass with -x on the command line if present
if commandLineProps is not None:
    propertiesMap.update(commandLineProps)

# Read app specific dictionary
dictionaryEntries = getDictionaryEntries('AppDictionaries/' + appName)
if dictionaryEntries is not None:
    propertiesMap.update(dictionaryEntries)
artifactIDs = createArtifactList(propertiesMap)

# Make lists actual list instread of strings
convertLists(propertiesMap)

# Get Application
if (repository.exists('Applications/' + appName)):
    print 'Application ' + appName + ' exists'
else:
    application = factory.configurationItem('Applications/' + appName, 'udm.Application')
    repository.create(application)
newApplication = repository.read('Applications/' + appName)

# Create a new package
if (repository.exists('Applications/' + appName + '/' + buildID)):
     print 'Deployment package: ' + appName + '/' + buildID + ' already exists'
     sys.exit(0)
newPackage = factory.configurationItem('Applications/' + appName + '/' + buildID,'udm.DeploymentPackage')
repository.create(newPackage)

print
print 'Properties are:'
print propertiesMap

# Loop over each artifact ID and add an artifact to the package for each
for artifactID in artifactIDs:
    # Get a subset of the props for this artifact, figure out names and type.
    props = subsetProps(artifactID, propertiesMap)
    artifactName = 'Applications/' + appName + '/' + buildID + '/' + props['name']
    del props['name']
    artifactType = props['type']
    del props['type']
    
    # Create the artifact, 2 routes, one for file artifacts, and one for non-file artifacts
    fileLocation = safeGetValue(props, 'fileLocation')
    if fileLocation is not None:
        # Case where its a file artifact
        # If the fileLocation point to a directory, zip that up
        if os.path.isdir(fileLocation):
            fileLocation = createZipFromFolder(fileLocation)

        fileName = ''
        if '/' in fileLocation:
            # Unix
            fileName = fileLocation.rpartition('/')[2]
        else:
            # Assume Windows
            fileName = fileLocation.rpartition('\\')[2]
        artifactFile = open(fileLocation, 'rb').read()
        newArtifact = factory.artifact(artifactName, artifactType, props, artifactFile)
        newArtifact.filename = fileName
        repository.create(newArtifact)
    else:
        newArtifact = factory.configurationItem(artifactName, artifactType, props)
        repository.create(newArtifact)

# Deploy step
if autoDeploy == 'true':
    taskID, success = syncDeployUpdate(deployEnv, newPackage.id)

if success:
    sys.exit(0)
else:
    sys.exit(1)

