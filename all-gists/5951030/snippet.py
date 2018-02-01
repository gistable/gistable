import urllib.request as request
import re
import os
import copy
import json

outputprefix = "schemas/"
outputsuffix = '.json'
urlprefix = "http://json-schema.org/schemas/"
urlsuffix = '.json'
relprefix = 'http://schema.org/'

if not os.path.exists(outputprefix):
	os.makedirs(outputprefix)

def schemaToJson(schema, indent="\t"):
	"Schema-specific pretty printing"
	propertyTexts = []
	# List properties in this order (where defined)
	properties = ['id', 'title', 'description', 'allOf', 'oneOf', 'anyOf', 'not', 'type', 'format', 'items', 'additionalItems', 'properties', 'additionalProperties', 'definitions']
	schemaProperties = ['items', 'not', 'additionalProperties', 'additionalItems']
	schemaMapProperties = ['properties', 'definitions']
	schemaListProperties = ['allOf', 'oneOf', 'anyOf', 'items']
	for key in properties:
		if key in schema:
			if key in schemaProperties and isinstance(schema[key], object):
				propertyTexts.append(json.dumps(key) + ': ' + schemaToJson(schema[key], indent))
			elif key in schemaMapProperties and isinstance(schema[key], object) and len(schema[key]):
				innerTexts = []
				subKeys = list(schema[key].keys())
				subKeys.sort()
				for subKey in subKeys:
					innerTexts.append(json.dumps(subKey) + ": " + schemaToJson(schema[key][subKey], indent))
				propertyTexts.append(json.dumps(key) + ": {\n" + indent + (",\n" + indent).join([x.replace("\n", "\n" + indent) for x in innerTexts]) + "\n}")
			elif key in schemaListProperties and isinstance(schema[key], list) and len(schema[key]):
				innerTexts = []
				for subSchema in schema[key]:
					innerTexts.append(schemaToJson(subSchema, indent))
				propertyTexts.append(json.dumps(key) + ": [\n" + indent + (",\n" + indent).join([x.replace("\n", "\n" + indent) for x in innerTexts]) + "\n]")
			else:
				propertyTexts.append(json.dumps(key) + ': ' + json.dumps(schema[key], sort_keys=True, indent=indent))
	# Any property not covered
	keys = list(schema.keys())
	keys.sort()
	for key in keys:
		if key not in properties:
			propertyTexts.append(json.dumps(key) + ': ' + json.dumps(schema[key], sort_keys=True, indent=indent))
	# Assemble into JSON (including indent)
	jsonText = "{\n" + indent + (",\n" + indent).join([x.replace("\n", "\n" + indent) for x in propertyTexts]) + "\n}"
	# Compact things for readability
	jsonText = re.sub(r"\{[^\{,}]*\}", compactJson, jsonText) # Objects with only one property
	jsonText = re.sub(r"\[[^\[,\]]*\]", compactJson, jsonText) # Lists containing a single simple entry
	jsonText = re.sub(r"\[[^\{\[\}\]]*\]", compactJson, jsonText) # Lists containing only scalar types
	return jsonText

def compactJson(refObjMatch):
	refObjString = refObjMatch.group(0)
	try:
		jsonText = json.dumps(json.loads(refObjString))
		return jsonText
	except:
		return refObjString

response = request.urlopen("http://schema.rdfs.org/all.json")
jsonText = response.read()
spec = json.loads(jsonText.decode('ascii'))

# (Data)Types for which there is an ideomatic JSON Schema representation
hardCodedSchemas = {
	'Boolean': {'type': 'boolean'},
	'Date': {'type': 'string', 'format': 'http://schema.org/Date'},
	'DateTime': {'type': 'string', 'format': 'http://schema.org/DateTime'},
	'Float': {'type': 'number', 'format': 'http://schema.org/Float'},
	'Integer': {'type': 'integer'},
	'Number': {'type': 'number'},
	'Text': {'type': 'string'},
	'Time': {'type': 'string', 'format': 'time'},
	'URL': {'type': 'string', 'format': 'uri'}
}

for entry in spec['types'].values():
	filename = outputprefix + entry['id'] + outputsuffix
	schema = {
		'id': urlprefix + entry['id'] + urlsuffix,
		'title': entry['label'],
		'description': entry['comment_plain'],
		'format': entry['url'],
		'definitions': {}
	}
	if 'instances' in entry:
		schema['oneOf'] = [
			{
				'type': 'string',
				'enum': entry['instances']
			},
			{
				'type': 'array',
				'items': {'$ref': '#'}
			}
		]
	else:
		schema['type'] = 'object'
		schema['allOf'] = []
		for supertype in entry['supertypes']:
			schema['allOf'].append({
				'$ref': supertype + urlsuffix
			})
		schema['properties'] = {}
		for property in entry['specific_properties']:
			propertyInfo = spec['properties'][property]
			options = []
			for option in propertyInfo['ranges']:
				if (option in hardCodedSchemas):
					subSchema = copy.deepcopy(hardCodedSchemas[option])
					options.append(subSchema)
				else:
					options.append({'$ref': option + urlsuffix})
			if len(options) == 1:
				if 'format' in options[0] and options[0]['format'] == 'uri':
					options[0]['links'] = [
						{
							'rel': 'full',
							'href': '{$}'
						}
					]
				schema['properties'][property] = options[0]
			else:
				schema['properties'][property] = {
					'anyOf': options
				}
			if '$ref' not in schema['properties'][property]:
				subSchema = schema['properties'][property]
				subSchema['title'] = propertyInfo['label']
				subSchema['description'] = propertyInfo['comment_plain']
				schema['definitions'][property] = subSchema
				schema['properties'][property] = {'$ref': '#/definitions/' + property}
			schema['properties'][property] = {
				"oneOf": [
					schema['properties'][property],
					{
						"type": "array",
						"items": schema['properties'][property]
					}
				]
			}
	with open(filename, 'w') as handle:
		jsonText = schemaToJson(schema)
		handle.write(jsonText)