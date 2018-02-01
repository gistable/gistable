from xml.etree import cElementTree as elemtree
from datetime import date

"""
Use this to parse XML from MeSH (Medical Subject Headings). More information 
on the format at: http://www.ncbi.nlm.nih.gov/mesh

End users will primarily want to call the `parse_mesh` function and do something
with the output.
"""

def parse_mesh(filename):
    """Parse a mesh file, successively generating
    `DescriptorRecord` instance for subsequent processing."""
    for _evt, elem in elemtree.iterparse(filename):
        if elem.tag == 'DescriptorRecord':
            yield DescriptorRecord.from_xml_elem(elem)

def date_from_mesh_xml(xml_elem):
    year = xml_elem.find('./Year').text
    month = xml_elem.find('./Month').text
    day = xml_elem.find('./Day').text
    return date(int(year), int(month), int(day))

class PharmacologicalAction(object):
    """A pharmacological action, denoting the effects of a MeSH descriptor."""
    
    def __init__(self, descriptor_ui):
        self.descriptor_ui = descriptor_ui
    
    @classmethod
    def from_xml_elem(cls, elem):
        descriptor_ui = elem.find('./DescriptorReferredTo/DescriptorUI')
        return cls(descriptor_ui)

class SlotsToNoneMixin(object):
    def __init__(self, **kwargs):
        for attr in self.__slots__:
            setattr(self, attr, kwargs.get(attr, None))
    
    def __repr__(self):
        attrib_repr = ', '.join(u'%s=%r' % (attr, getattr(self, attr)) for attr in self.__slots__)
        return self.__class__.__name__ + '(' + attrib_repr + ')'

class Term(SlotsToNoneMixin):
    """A term from within a MeSH concept."""

    __slots__ = ('term_ui', 'string', 'is_concept_preferred', 'is_record_preferred',
      'is_permuted', 'lexical_tag', 'date_created', 'thesaurus_list')
    
    @classmethod
    def from_xml_elem(cls, elem):
        term = cls()
        term.is_concept_preferred = elem.get('ConceptPreferredYN', None) == 'Y'
        term.is_record_preferred = elem.get('RecordPreferredYN', None) == 'Y'
        term.is_permuted = elem.get('IsPermutedTermYN', None) == 'Y'
        term.lexical_tag = elem.get('LexicalTag')
        for child_elem in elem:
            if child_elem.tag == 'TermUI':
                term.ui = child_elem.text
            elif child_elem.tag == 'String':
                term.name = child_elem.text
            elif child_elem.tag == 'DateCreated':
                term.date_created = date_from_mesh_xml(child_elem)
            elif child_elem.tag == 'ThesaurusIDlist':
                term.thesaurus_list = [th_elem.text for th_elem in child_elem]
        return term

class SemanticType(SlotsToNoneMixin):
    __slots__ = ('ui', 'name')
    
    @classmethod
    def from_xml_elem(cls, elem):
        sem_type = cls()
        for child_elem in elem:
            if child_elem.tag == 'SemanticTypeUI':
                sem_type.ui = child_elem.text
            elif child_elem.tag == 'SemanticTypeName':
                sem_type.name = child_elem.text

class Concept(SlotsToNoneMixin):
    """A concept within a MeSH Descriptor."""
    __slots__ = ( 'ui', 'name', 'is_preferred', 'umls_ui', 'casn1_name', 'registry_num', 
      'scope_note', 'sem_types', 'terms')
    
    @classmethod
    def from_xml_elem(cls, elem):
        concept = cls()
        concept.is_preferred = elem.get('PreferredConceptYN', None) == 'Y'
        for child_elem in elem:
            if child_elem.tag == 'ConceptUI':
                concept.ui = child_elem.text
            elif child_elem.tag == 'ConceptName':
                concept.name = child_elem.find('./String').text
            elif child_elem.tag == 'ConceptUMLSUI':
                concept.umls_ui
            elif child_elem.tag == 'CASN1Name':
                concept.casn1_name = child_elem.text
            elif child_elem.tag == 'RegistryNumber':
                concept.registry_num = child_elem.text
            elif child_elem.tag == 'ScopeNote':
                concept.scope_note = child_elem.text
            elif child_elem.tag == 'SemanticTypeList':
                concept.sem_types = [SemanticType.from_xml_elem(st_elem)
                  for st_elem in child_elem.findall('SemanticType')]
            elif child_elem.tag == 'TermList':
                concept.terms = [Term.from_xml_elem(term_elem)
                  for term_elem in child_elem.findall('Term')]
        return concept

class DescriptorRecord(SlotsToNoneMixin):
    "A MeSH Descriptor Record."""
    
    __slots__ = ('ui', 'name', 'date_created', 'date_revised', 'pharm_actions', 
      'tree_numbers', 'concepts')
    
    @classmethod
    def from_xml_elem(cls, elem):
        rec = cls()
        for child_elem in elem:
            if child_elem.tag == 'DescriptorUI':
                rec.ui = child_elem.text
            elif child_elem.tag == 'DescriptorName':
                rec.name = child_elem.find('./String').text
            elif child_elem.tag == 'DateCreated':
                rec.date_created = date_from_mesh_xml(child_elem)
            elif child_elem.tag == 'DateRevised':
                rec.date_revised = date_from_mesh_xml(child_elem)
            elif child_elem.tag == 'TreeNumberList':
                rec.tree_numbers = [tn_elem.text
                  for tn_elem in child_elem.findall('TreeNumber')]
            elif child_elem.tag == 'ConceptList':
                rec.concepts = [Concept.from_xml_elem(c_elem) 
                  for c_elem in child_elem.findall('Concept')]
            elif child_elem.tag == 'PharmacologicalActionList':
                rec.pharm_actions = [PharmacologicalAction.from_xml_elem(pa_elem) 
                  for pa_elem in child_elem.findall('PharmacologicalAction')]
        return rec

                  
                  
