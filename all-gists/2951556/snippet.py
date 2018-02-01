'''
This is a quick reference example to get you started with yaml. Please review this,
but spend the time to fully read the wikipedia page on yaml:
http://en.wikipedia.org/wiki/Yaml

Note that the magic quote-less yaml parsing will still always strip values.
To avoid this you need to use quotes. Quotes can also force types to string type,
and are always valid (meaning omitting quotes is for convenience not necessity).
'''

# You will need to first do a "sudo pip install pyyaml"
import yaml

sample_yaml_as_dict = '''
first_dict_key: some value
second_dict_key: some other value
'''

sample_yaml_as_list = '''
# Notice here how i don't need quotes. Read the wikipedia page for more info!
- list item 1
- list item 2
'''

my_config_dict = yaml.load(sample_yaml_as_dict)
print my_config_dict
# Will print:
# {'second_dict_key': 'some other value', 'first_dict_key': 'some value'}

my_config_list = yaml.load(sample_yaml_as_list)
print my_config_list
# Will print:
# ['list item 1', 'list item 2']

# Load some external config file
with open('~/my_config.yaml') as fp:
    my_configuration = yaml.load(fp)

print my_configuration_dict