# A python script to turn annotated data in standoff format (brat annotation tool) to the formats expected by Stanford NER and Relation Extractor models
# - NER format based on: http://nlp.stanford.edu/software/crf-faq.html#a
# - RE format based on: http://nlp.stanford.edu/software/relationExtractor.html#training

# Usage:
# 1) Install the pycorenlp package
# 2) Run CoreNLP server (change CORENLP_SERVER_ADDRESS if needed)
# 3) Place .ann and .txt files from brat in the location specified in DATA_DIRECTORY
# 4) Run this script

# Cross-sentence annotation is not supported

from pycorenlp import StanfordCoreNLP
import os
from os import listdir
from os.path import isfile, join

DEFAULT_OTHER_ANNO = 'O'
STANDOFF_ENTITY_PREFIX = 'T'
STANDOFF_RELATION_PREFIX = 'R'
DATA_DIRECTORY = 'data'
OUTPUT_DIRECTORY = 'output'
CORENLP_SERVER_ADDRESS = 'http://localhost:9000'

NER_TRAINING_DATA_OUTPUT_PATH = join(OUTPUT_DIRECTORY, 'ner-crf-training-data.tsv')
RE_TRAINING_DATA_OUTPUT_PATH = join(OUTPUT_DIRECTORY, 're-training-data.corp')

if os.path.exists(OUTPUT_DIRECTORY):
	if os.path.exists(NER_TRAINING_DATA_OUTPUT_PATH):
		os.remove(NER_TRAINING_DATA_OUTPUT_PATH)
	if os.path.exists(RE_TRAINING_DATA_OUTPUT_PATH):
		os.remove(RE_TRAINING_DATA_OUTPUT_PATH)
else:
    os.makedirs(OUTPUT_DIRECTORY)

sentence_count = 0
nlp = StanfordCoreNLP(CORENLP_SERVER_ADDRESS)

# looping through .ann files in the data directory
ann_data_files = [f for f in listdir(DATA_DIRECTORY) if isfile(join(DATA_DIRECTORY, f)) and f.split('.')[1] == 'ann']

for file in ann_data_files:
	entities = []
	relations = []

	# process .ann file - place entities and relations into 2 seperate lists of tuples
	with open(join(DATA_DIRECTORY, file), 'r') as document_anno_file:
		lines = document_anno_file.readlines()
		for line in lines:
			standoff_line = line.split()
			if standoff_line[0][0] == STANDOFF_ENTITY_PREFIX:
				entity = {}
				entity['standoff_id'] = int(standoff_line[0][1:])
				entity['entity_type'] = standoff_line[1].capitalize()
				entity['offset_start'] = int(standoff_line[2])
				entity['offset_end'] = int(standoff_line[3])
				entity['word'] = standoff_line[4]
				entities.append(entity)

			elif standoff_line[0][0] == STANDOFF_RELATION_PREFIX:
				relation = {}
				relation['standoff_id'] = int(standoff_line[0][1:])
				relation['name'] = standoff_line[1]
				relation['standoff_entity1_id'] = int(standoff_line[2].split(':')[1][1:])
				relation['standoff_entity2_id'] = int(standoff_line[3].split(':')[1][1:])
				relations.append(relation)
				# relations.append((standoff_id, relation_name, standoff_entity1_id, standoff_entity2_id))

	# read the .ann's matching .txt file and tokenize its text using stanford corenlp
	with open(join(DATA_DIRECTORY, file.replace('.ann', '.txt')), 'r') as document_text_file:
		document_text = document_text_file.read()

	output = nlp.annotate(document_text, properties={
	  'annotators': 'tokenize,ssplit,pos',
	  'outputFormat': 'json'
	})

	# write text and annotations into NER and RE output files
	with open(NER_TRAINING_DATA_OUTPUT_PATH, 'a') as ner_training_data, open(RE_TRAINING_DATA_OUTPUT_PATH, 'a') as re_training_data:
		for sentence in output['sentences']:
			entities_in_sentence = {}
			sentence_re_rows = []

			for token in sentence['tokens']:
				offset_start = int(token['characterOffsetBegin'])
				offset_end = int(token['characterOffsetEnd'])

				re_row = {}
				entity_found = False
				ner_anno = DEFAULT_OTHER_ANNO

				# searching for token in annotated entities
				for entity in entities:
					if offset_start >= entity['offset_start'] and offset_end <= entity['offset_end']:
						ner_anno = entity['entity_type']

					# multi-token entities for RE need to be handled differently than NER
					if offset_start == entity['offset_start'] and offset_end <= entity['offset_end']:
						entities_in_sentence[entity['standoff_id']] = len(sentence_re_rows)
						re_row['entity_type'] = entity['entity_type']
						re_row['pos_tag'] = token['pos']
						re_row['word'] = token['word']

						sentence_re_rows.append(re_row)
						entity_found = True
						break
					elif offset_start > entity['offset_start'] and offset_end <= entity['offset_end'] and len(sentence_re_rows) > 0:
						sentence_re_rows[-1]['pos_tag'] += '/{}'.format(token['pos'])
						sentence_re_rows[-1]['word'] += '/{}'.format(token['word'])
						entity_found = True
						break
					
				if not entity_found:
					re_row['entity_type'] = DEFAULT_OTHER_ANNO
					re_row['pos_tag'] = token['pos']
					re_row['word'] = token['word']

					sentence_re_rows.append(re_row)

				# writing tagged tokens to NER training data
				ner_training_data.write('{}\t{}\n'.format(token['word'], ner_anno))

			# writing tagged tokens to RE training data
			token_count = 0
			for sentence_row in sentence_re_rows:
				re_training_data.write('{}\t{}\t{}\tO\t{}\t{}\tO\tO\tO\n'.format(str(sentence_count), sentence_row['entity_type'], str(token_count), sentence_row['pos_tag'], sentence_row['word']))
				token_count += 1

			re_training_data.write('\n')

			# writing relations to RE training data
			for relation in relations:
				if relation['standoff_entity1_id'] in entities_in_sentence and relation['standoff_entity2_id'] in entities_in_sentence:
					entity1 = str(entities_in_sentence[relation['standoff_entity1_id']])
					entity2 = str(entities_in_sentence[relation['standoff_entity2_id']])
					relation_name = relation['name']
					re_training_data.write('{}\t{}\t{}\n'.format(entity1, entity2, relation_name))

			re_training_data.write('\n')

			sentence_count += 1

		ner_training_data.write('\n')

	print('Processed file pair: {} and {}'.format(file, file.replace('.ann', '.txt')))
