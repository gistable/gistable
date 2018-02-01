# This small script shows how to use AllenNLP Semantic Role Labeling (http://allennlp.org/) with SpaCy 2.0 (http://spacy.io) components and extensions
# Script installs allennlp default model
# Important: Install allennlp form source and replace the spacy requirement with spacy-nightly in the requirements.txt
# Developed for SpaCy 2.0.0a18

from allennlp.commands import DEFAULT_MODELS
from allennlp.common.file_utils import cached_path
from allennlp.service.predictors import SemanticRoleLabelerPredictor
from allennlp.models.archival import load_archive

import spacy
from spacy.tokens import Token

class SRLComponent(object):
    '''
    A SpaCy pipeline component for SRL
    '''
    
    name = 'Semantic Role Labeler'

    def __init__(self):
        archive = load_archive(self._get_srl_model())
        self.predictor = SemanticRoleLabelerPredictor.from_archive(archive, "semantic-role-labeling")
        Token.set_extension('srl_arg0')
        Token.set_extension('srl_arg1')
        
    def __call__(self, doc):
        # See https://github.com/allenai/allennlp/blob/master/allennlp/service/predictors/semantic_role_labeler.py#L74
        words = [token.text for token in doc]
        for i, word in enumerate(doc):
            if word.pos_ == "VERB":
                verb = word.text
                verb_labels = [0 for _ in words]
                verb_labels[i] = 1
                instance = self.predictor._dataset_reader.text_to_instance(doc, verb_labels)
                output = self.predictor._model.forward_on_instance(instance, -1)
                tags = output['tags']

                # TODO: Tagging/dependencies can be done more elegant 
                if "B-ARG0" in tags:
                    start = tags.index("B-ARG0")
                    end = max([i for i, x in enumerate(tags) if x == "I-ARG0"] + [start]) + 1
                    word._.set("srl_arg0", doc[start:end])

                if "B-ARG1" in tags:
                    start = tags.index("B-ARG1")
                    end = max([i for i, x in enumerate(tags) if x == "I-ARG1"] + [start]) + 1
                    word._.set("srl_arg1", doc[start:end])
        
        return doc
    
    def _get_srl_model(self):
        return cached_path(DEFAULT_MODELS['semantic-role-labeling'])

    
def demo():
    nlp = spacy.load("en")
    nlp.add_pipe(SRLComponent(), after='ner')
    doc = nlp("Apple sold 1 million Plumbuses this month.")
    for w in doc:
        if w.pos_ == "VERB":
            print("('{}', '{}', '{}')".format(w._.srl_arg0, w, w._.srl_arg1)) 
            # ('Apple', 'sold', '1 million Plumbuses)
            