#!/usr/bin/python

apiVersion = 'v5'
apiURL = 'https://api.thousandeyes.com'
urlBase = apiURL + '/' + apiVersion + '/'

logLevel = 3
requestCount = 0
uploadLimit = 10000

import json, base64, requests, urllib3, time, datetime, sys, threading
from sys import setrecursionlimit


me = threading.currentThread() 

#---------------------------------------------------
# switching from default ASCII encoding to UTF8
#---------------------------------------------------
reload(sys)
sys.setdefaultencoding('UTF8')

def _printDebugMessage(debugLevel, debugMessage):
    if debugLevel == 'debug':
        intLogLevel = 4
    elif debugLevel == 'info':
        intLogLevel = 3
    elif debugLevel == 'warn':
        intLogLevel = 2
    elif debugLevel == 'error':
        intLogLevel = 1
    else:
        debugLevel = 'unset'
        intLogLevel = 4
    if logLevel >= intLogLevel:
        debugTime = datetime.datetime.now()
        dateStamp = debugTime.strftime("%Y-%m-%d %H:%M:%S")
        print dateStamp + ' (' + debugLevel + ') ' + debugMessage
    if debugLevel == 'error':
        quit()

def getElapsedTime(t1,t2):
    if t1 > t2:
        #reverse the order if t1 is bigger
        t3=t1
        t1=t2
        t2=t3
    hours,remainder = divmod((t2-t1).seconds, 3600)
    minutes,seconds = divmod(remainder, 60)
    return str(hours) +'h ' + str(minutes) + 'm ' + str(seconds) + 's'

def _getRequestHeaders(theUser, thePass):
    if theUser <> '' and thePass <> '':
        authorization = base64.b64encode(theUser + ':' + thePass)
        headers = {'accept': 'application/json', 'content-type': 'application/json',
                      'Authorization': 'Basic ' + authorization}
        return headers
    else:
        _printDebugMessage('error', 'Username/password must be specified.')

def _makeGetRequest(requestURI, theUser, thePass):
    global requestCount
    requestCount += 1
    _printDebugMessage('info', '(#' + str(requestCount) + ') Requesting GET data ' + requestURI)
    requestHeaders = _getRequestHeaders(theUser, thePass)
    if requestHeaders <> '':
        teResponse = requests.get(requestURI, headers=requestHeaders)
        if teResponse.status_code == 429:  #429 means "too many requests"
            for power in (0, 1, 2, 3, 4, 5):
                _printDebugMessage('info',
                                  '429 Too Many Requests received.  Sleeping for ' + str(2 ** power) + ' minutes.')
                time.sleep(60 * 2 ^ power)
                _printDebugMessage('info', '(#' + str(requestCount) + ') Requesting data ' + requestURI)
                teResponse = requests.get(requestURI, headers=requestHeaders)
                if teResponse.status_code == 200:
                    break;
                elif teResponse.status_code <> 429:
                    _printDebugMessage('error', 'Non-429 response received after a sleep.  Exiting. ')
        jsonResponse = json.loads(teResponse.content)
    else:
        _printDebugMessage('error', 'Empty headers: ' + teResponse.headers)
        jsonResponse = ''
    return jsonResponse

def _makePostRequest(requestURI, postData, expectedStatusCode, theUser, thePass):
    global requestCount
    requestCount += 1
    _printDebugMessage('info', '(#' + str(requestCount) + ') Sending POST data ' + requestURI)
    requestHeaders = _getRequestHeaders(theUser, thePass)
    if requestHeaders <> '':
        teResponse = requests.post(requestURI, headers=requestHeaders, data=json.dumps(postData))
        if _getContentType(teResponse, expectedStatusCode) == 'json':
            if teResponse.content == '': #this is done to handle empty content teResponse that cannot be used with json.load(teReponse.content)
                return ''
            else:
                jsonResponse = json.loads(teResponse.content)
                return jsonResponse
        else:
            _printDebugMessage('error','POST request came back empty, or in currently unsupported format: ' + requestURI)
    else:
        _printDebugMessage('error', 'Empty headers: ' + teResponse.headers)

def _getContentType(responseObject, expectedStatusCode):
    if (responseObject.status_code == expectedStatusCode):
        if responseObject.headers['content-type'].split(';')[0] == 'application/json':
            return 'json'
        else:
            _printDebugMessage('warn', 'Unexpected format returned: XML')
            return ''
    else:
        jsonResponse = json.loads(responseObject.content)
        _printDebugMessage('warn', 'Unexpected status code returned: ' + str(responseObject.status_code) + ' '  + jsonResponse['errorMessage'])
        return ''

def countPoints(theData, elementToCount):
    _printDebugMessage('debug', 'Validating result count for dataDog upload...')
    resultCount = 0
    _printDebugMessage('debug', 'Data has ' + str(len(theData.keys())) + ' tests.')
    for test in theData.keys():
        testResultCount = 0
        _printDebugMessage('debug', 'Test ' + test + ' has ' + str(len(theData[test].keys())) + ' metric series.')
        for metric in theData[test].keys():
            if metric == elementToCount:
                _printDebugMessage('debug', 'Metric ' + metric + ' has ' + str(len(theData[test][metric].keys())) + ' agent series.')
                for agent in theData[test][metric].keys():
                    _printDebugMessage('debug', 'Agent ' + agent + ' has ' + str(len(theData[test][metric][agent])) + ' datapoints.')
                    testResultCount += len(theData[test][metric][agent]);
        resultCount += testResultCount
        _printDebugMessage('debug', 'Test ' + test + ' has ' + str(testResultCount) + ' datapoints. (' + str(resultCount) + ' total)')
    _printDebugMessage('debug', 'Data series upload has ' + str(resultCount) + ' datapoints.')
    return resultCount

def _dataDogUploadSeries(theData, appKey, apiKey, resultCount):
    #print '=========================='
    #_printDebugMessage('error','Dumping data: ' + json.dumps(theData))
    #print '=========================='
    from datadog import initialize, api
    options = {
        'api_key': apiKey,
        'app_key': appKey
    }

    initialize(**options)
    _printDebugMessage('info', 'Uploading data for tag [' + str(theData[0]['tags'][1]) + '] to DataDog (' + str(resultCount) + ' dataPoints)...')
    _printDebugMessage('error', json.dumps(theData))
    ddApiResponse = api.Metric.send(theData)
    _printDebugMessage('info', 'DataDog upload is complete....')
    if ddApiResponse['status'] == 'ok':
        return 1
    else: 
        _printDebugMessage('error','Errors were received when uploading DD metrics')

def _getPrimaryTestMetrics(testType):
    #make a call, get primary metrics
    if testType == 'http-server':
        metricsList = ['redirectTime','dnsTime','connectTime','waitTime','receiveTime','responseTime','fetchTime']
    elif testType == 'page-load':
        metricsList = ['domLoadTime','pageLoadTime']
    elif testType == 'transactions':
        metricsList = ['stepsCompleted','totalSteps','transactionTime']
    elif testType == 'network':
        metricsList = ['loss','avgLatency','jitter']
    elif testType == 'agent-to-server':
        metricsList = ['loss','avgLatency','jitter']
    elif testType == 'agent-to-agent':
        metricsList = ['loss','avgLatency','jitter']
    elif testType == 'bgp':
        metricsList = ['reachability','updates','pathChanges']
    elif testType == 'dns-server':
        metricsList = ['resolutionTime']
    elif testType == 'dns-trace':
        metricsList = ['queries','finalQueryTime']
    elif testType == 'dnssec':
        metricsList = ['valid']
    else:
        metricsList = []
    return metricsList

def _getEndpointForTest(testId, apiUser, apiPass):
    testDetails = _makeGetRequest(urlBase + 'tests/' + str(testId), apiUser, apiPass)
    testType = testDetails['test'][0]['type']
    metricsList = _getPrimaryTestMetrics(testType)

    if testType == 'http-server':
        endpoint = 'web/http-server/'
        dataElements = ['web','httpServer']
        dataSource = 'agent'
    elif testType == 'page-load':
        endpoint = 'web/page-load/'
        dataElements = ['web','pageLoad']
        dataSource = 'agent'
    elif testType == 'transactions':
        endpoint = 'web/transactions/'
        dataElements = ['web','transaction']
        dataSource = 'agent'
    elif testType == 'network':
        endpoint = 'net/metrics/'
        dataElements = ['net','metrics']
        dataSource = 'agent'
    elif testType == 'agent-to-server':
        endpoint = 'net/metrics/'
        dataElements = ['net','metrics']
        dataSource = 'agent'
    elif testType == 'agent-to-agent':
        endpoint = 'net/metrics/'
        dataElements = ['net','metrics']
        dataSource = 'agent'
    elif testType == 'bgp':
        endpoint = 'net/bgp-metrics/'
        dataElements = ['net','bgpMetrics']
        dataSource = 'monitor'
    elif testType == 'dns-server':
        endpoint = 'dns/server/'
        dataElements = ['dns','server']
        dataSource = 'agent'
    elif testType == 'dns-trace':
        endpoint = 'dns/trace/'
        dataElements = ['dns','trace']
        dataSource = 'agent'
    elif testType == 'dnssec':
        endpoint = 'dns/dnssec/'
        dataElements = ['dns','dnssec']
        dataSource = 'agent'
    else:
        endpoint = []
        dataElements = []

    endpointData = dict()
    endpointData['endpoint'] = endpoint
    endpointData['metricsList'] = metricsList
    endpointData['dataElements'] = dataElements
    endpointData['dataSource'] = dataSource
    return endpointData

def getAgentIPList(onlyAgentsOnTests, apiUser, apiPass):
    responseData = _makeGetRequest(urlBase + '/agents' , apiUser, apiPass)
    agentList = responseData['agents']
    for agent in agentList:
        addressString = ''
        if agent['agentType'] == 'Enterprise Cluster':
            for clusterMember in agent['clusterMembers']:
                if 'publicIpAddresses' in agent.keys():
                    for address in agent['publicIpAddresses']:
                        if address not in addressString:
                            if addressString <> '':
                                addressString += ',' + address
                            else:
                                addressString += address
                else:
                    for address in agent['ipAddresses']:
                        if address not in addressString:
                            if addressString <> '':
                                addressString += ',' + address
                            else:
                                addressString += address
        else:
            if 'publicIpAddresses' in agent.keys():
                for address in agent['publicIpAddresses']:
                    if address not in addressString:
                        if addressString <> '':
                            addressString += ',' + address
                        else:
                            addressString += address
            else:
                for address in agent['ipAddresses']:
                    if address not in addressString:
                        if addressString <> '':
                            addressString += ',' + address
                        else:
                            addressString += address
        print agent['agentName'] + ':' + addressString

def parseArguments():
    import getpass, argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', action='store', dest='te_apiUser', help='ThousandEyes Username')
    parser.add_argument('-p', action='store', dest='te_apiPass', help='ThousandEyes API Token')
    parser.add_argument('-d', action='store', dest='dd_apiKey', help='Datadog API key')
    parser.add_argument('-a', action='store', dest='dd_appKey', help='Datadog APP key')
    parser.add_argument('-t', action='store', dest='testList', help='comma-separated list of testIds')
    parser.add_argument('-w', action='store', dest='windowSize', help='api query window size')
    parser.add_argument('-f', action='store', dest='fromTo', help='specific from/to string')
    
    argResults = parser.parse_args()

    if argResults.te_apiUser == '' or argResults.te_apiUser == None:
        while argResults.te_apiUser == None or argResults.te_apiUser == '':
            argResults.te_apiUser = str(raw_input("Enter ThousandEyes username: "))
    if argResults.te_apiPass == '' or argResults.te_apiPass == None:
        while argResults.te_apiPass == None or argResults.te_apiPass == '':
            argResults.te_apiPass = getpass.getpass("Enter API token for " + argResults.te_apiUser + ": ")
    if argResults.dd_apiKey == '' or argResults.dd_apiKey == None:
        while argResults.dd_apiKey == None or argResults.dd_apiKey == '':
            argResults.dd_apiKey = getpass.getpass("Enter datadog API key: ")
    if argResults.dd_appKey == '' or argResults.dd_appKey == None:
        while argResults.dd_appKey == None or argResults.dd_appKey == '':
            argResults.dd_appKey = getpass.getpass("Enter datadog APP key: ")
    if argResults.testList == '' or argResults.testList == None:
        while argResults.testList == None or argResults.testList == '':
            argResults.testList = str(raw_input("Enter test list (comma-separated): "))
    if (argResults.windowSize == '' or argResults.windowSize == None) and (argResults.fromTo == None or argResults.fromTo == None):
        while argResults.windowSize == None or argResults.windowSize == '':
            argResults.windowSize = str(raw_input("Enter window size: "))
    elif (argResults.windowSize <> '' and argResults.windowSize <> None) and (argResults.fromTo <> '' and argResults.fromTo <> None):
        windowSize = None
        while argResults.windowSize == None or argResults.windowSize == '':
            argResults.windowSize = str(raw_input("Window and From/To are mutually exclusive.  Enter new window size: "))
    elif argResults.windowSize <> None:
        argResults.windowSize = 'window=' + argResults.windowSize
    else:
        argResults.windowSize = 'from=' + argResults.fromTo
    rawList = argResults.testList.split(',')
    testList = list()
    for entry in rawList:
        testList.append(int(entry.strip()))
    argResults.testList = testList
    return argResults

def parsePageOfResults(testData, endpointData):
    metricSeriesList = dict()
    local_dpCount = 0
    local_errorCount = 0
    for dataPoint in testData[endpointData['dataElements'][0]][endpointData['dataElements'][1]]:
        #iterate through thousandEyes result objects
        for metric in endpointData['metricsList']:
            #do for each metric
            local_dpCount += 1
            if 'te.' + metric not in metricSeriesList.keys():
                metricSeriesList['te.' + metric] = dict()
            metricSeries = metricSeriesList['te.' + metric]

            if endpointData['dataSource'] == 'agent':
                dataSource = 'agentName'
            else:
                dataSource = 'monitorName'

            if dataPoint[dataSource] not in metricSeries.keys():
                metricSeries[dataPoint[dataSource]] = list()
            agentSeries = metricSeries[dataPoint[dataSource]]

            if metric in dataPoint.keys():
                point = (dataPoint['roundId'], dataPoint[metric])
                agentSeries.append(point)
                metricSeriesList['te.' + metric][dataPoint[dataSource]] = agentSeries
            else:
                local_errorCount += 1
#                print 'metric: ' + metric + ' data: ' + json.dumps(dataPoint)
    _printDebugMessage('debug', 'This page has ' + str(local_dpCount) + ' results, ' + str(local_errorCount) + ' errors.')
    return {'data': metricSeriesList.copy(), 'stats': {'testDataPoints': local_dpCount, 'testErrors': local_errorCount}}

def merge(a, b, path=None):
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass # same leaf value
            else:
                a[key] += b[key]
        else:
            a[key] = b[key]
    return a

def parseTestResultsForDataDog(testList, apiUser, apiPass, window, ddAppKey, ddApiKey):
    ddData = dict()
    stats = {'dataPoints': 0, 'errorCount': 0, 'dataPoints.uploaded': 0}
    _printDebugMessage('info','Downloading test results from the ThousandEyes API')
    startTimeStamp = datetime.datetime.now()
    for testId in testList:
        testResults = 0
        endpointData = _getEndpointForTest(testId, apiUser, apiPass)
        testData = _makeGetRequest(urlBase + endpointData['endpoint'] + str(testId) + '?' + window , apiUser, apiPass)
        hostLabel = 'te.' + testData[endpointData['dataElements'][0]]['test']['type'] + '.' + testData[endpointData['dataElements'][0]]['test']['testName']
        metricSeriesList = dict()
        while 'next' in testData['pages']:
            pageData = parsePageOfResults(testData, endpointData)
            metricSeriesList = merge(metricSeriesList, pageData['data'])
            stats['dataPoints'] += pageData['stats']['testDataPoints']
            stats['errorCount'] += pageData['stats']['testErrors']
            testResults += pageData['stats']['testDataPoints'] - pageData['stats']['testErrors']
            if stats['dataPoints'] - stats['errorCount'] >= uploadLimit:
                stats['dataPoints.uploaded'] += stats['dataPoints']
                _printDebugMessage('debug','inside the while loop')
                _dataDogUploadSeries(convertToDataDogUploadFormat(metricSeriesList, 'test', hostLabel, '', ''), ddAppKey, ddApiKey, stats['dataPoints'])
                stats['dataPoints'] = 0
            testData = _makeGetRequest(testData['pages']['next'], apiUser, apiPass)

        pageData = parsePageOfResults(testData, endpointData)
        metricSeriesList = merge(metricSeriesList, pageData['data'])
        stats['dataPoints'] += pageData['stats']['testDataPoints']
        stats['errorCount'] += pageData['stats']['testErrors']
        testResults += pageData['stats']['testDataPoints'] - pageData['stats']['testErrors']

        #upload each test independently, regardless of whether the limit was reached
        if stats['dataPoints'] > 0:
            stats['dataPoints.uploaded'] += stats['dataPoints']
            _printDebugMessage('debug','inside the last page condition')
            _dataDogUploadSeries(convertToDataDogUploadFormat(metricSeriesList, 'test', hostLabel, '', ''), ddAppKey, ddApiKey, stats['dataPoints'])
            stats['dataPoints'] = 0

    endTimeStamp = datetime.datetime.now()
    _printDebugMessage('info','Completed processing of test results; Processed ' + str(testResults) + ' entries for test ' + str(testId) + ', resulting in a total of ' + str(stats['dataPoints']-stats['errorCount']+stats['dataPoints.uploaded']) + ' dataPoints.')
    _printDebugMessage('info','Total elapsed processing time: ' + getElapsedTime(endTimeStamp,startTimeStamp))

def convertToDataDogUploadFormat(theData, topLevel, testName, metricName, agentName):
    _printDebugMessage('debug','Converting data to dd, topLevel = [' + topLevel + '], testName = [' + testName + '], metricName = [' + metricName + '], agentName = [' + agentName + ']')
    if topLevel == 'test':
        if testName in theData:
            metricSeries = theData[testName]
            testMetrics = list()
            for metric in metricSeries.keys():
                testMetrics += convertToDataDogUploadFormat(metricSeries[metric], 'metric', testName, metric, '')
            return testMetrics
        else:
            metricSeries = theData
            testMetrics = list()
            for metric in metricSeries.keys():
                testMetrics += convertToDataDogUploadFormat(metricSeries[metric], 'metric', testName, metric, '')
            return testMetrics
    elif topLevel == 'metric':
        agentMetrics = list()
        for agent in theData.keys():
            agentMetrics.append(convertToDataDogUploadFormat(theData[agent], 'agent', testName, metricName, agent))
        return agentMetrics
    elif topLevel == 'agent':
        seriesData = dict()
        seriesData['host'] = 'ThousandEyes'
        seriesData['metric'] = metricName
        seriesData['tags'] = ['agent:' + agentName, 'test:' + testName]
        seriesData['points'] = theData
        return seriesData
    else:
        _printDebugMessage('error','Unknown topLevel variable [' + topLevel + '] passed to recursive function.  Expected [test, agent, metric]')
    return ddUpload

args = parseArguments()
parseTestResultsForDataDog(args.testList, args.te_apiUser, args.te_apiPass, args.windowSize, args.dd_appKey, args.dd_apiKey)
