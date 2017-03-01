import csv
import codecs
import re
import xml.etree.cElementTree as ET
import cerberus
import schema


#Regular Expression used to detect the first colon in an expression
LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')

#Regular Expression used to detect if there are any 
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

#Regular Expression created to remove underscores to normalize/clean the data
UNDER_SCORE = re.compile(r'([a-zA-Z0-9_])_([a-zA-Z0-9_])', re.IGNORECASE)

#Regular Expression created to remove semi colons
SEMI_COLON = re.compile(r'([a-zA-Z0-9_ \t\n\r\f\v]);([a-zA-Z0-9_ \t\n\r\f\v])')

#Regular Expression used to clean phone numbers
phone_number = re.compile('(?:\D?\d?(?:\s?|\D?))?\D?(\d{3})\D?(?:\s?|\D?)(\d{3})(?:\s?|\D?)(\d{4})')

SCHEMA = schema.schema


'''This is a function utilized in the shape element function to remove underscores from the k and v attributes of tag 
elements

UNDER_SCORE regular expression is used to search the input and stored in variable v_under_score.
if condition tests if v_under_score has a matching object. 
else condition simply returns the input. 

function will take any type of input as an argument
'''

def remove_underscores(input):
    v_under_score = UNDER_SCORE.search(input)
    if v_under_score:
        k_value_replace = input.replace('_',' ')
        return k_value_replace
    else:
	return input


'''This is a function utilized in the shape element function to remove semi colons from the k and v attributes of tag 
elements

SEMI_COLON regular expression is used to search the input and stored in variable v_under_score.
if condition tests if v_under_score has a matching object.
returns only the part of the input preceding its semi colon
else condition simply returns the input. 

function will take any type of input as an argument
''' 

def remove_semicolons(input):
    v_semi_colon = SEMI_COLON.search(input)
    if v_semi_colon:
        k_value_split = input.split(";")
        k_value_final = k_value_split[0]
        return k_value_final
    else:
        return input


"""Function to clean phone numbers using RE module

phone_number is the variable in which I have stored the RE I created to clean the phone numbers.
audited_number creates a list of tuples from the child.attrib['v'] value. 
clean_number used to to store the list of tuples in proper telephone number form

the function returns the clean_number varible

the function takes any type of input as an argument

"""

def clean_phone_number(input):
    
    if input == 'phone':
    
        phone_number = re.compile('(?:\D?\d?(?:\s?|\D?))?\D?(\d{3})\D?(?:\s?|\D?)(\d{3})(?:\s?|\D?)(\d{4})')
        audited_number = re.findall(phone_number, child.attrib['v'])
        clean_number = audited_number[0][0] + "-" + audited_number[0][1] + "-" + audited_number[0][2]
        
        return clean_number

    else:
        pass

#This cell is used to clean the street names for both the node and way elements

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

# UPDATE THIS VARIABLE
mapping = { "St" : "Street",
            "St." : "Street",
            "Rd.": "Road",
            "Ave" : "Avenue",
            "st" : "Street",
            "st." : "Street",
            "Blvd." : "Boulevard",
            "Blvd" : "Boulevard",
            "street" : "Street",
            "avenue" : "Avenue",
            "parkway" : "Parkway"}


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()

    return street_types


def update_name(name, mapping):
    
    
    name_object = street_type_re.search(name)
    if name_object:
    # YOUR CODE HERE
        if name_object.group() in mapping.keys():
            name = re.sub(street_type_re, mapping[name_object.group()], name)
        
            
    return name


#Below function used to execute the cleaning of the street names
def test():
    st_types = audit(OSM_FILE)
    #print st_types
    #assert len(st_types) == 3
    #pprint.pprint(dict(st_types))

    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)


NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"



# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements
    

    # YOUR CODE HERE
    if element.tag == 'node':
        for item in NODE_FIELDS:
        '''try/except statement necessary due to missing values in file. Statement added
        to pass validation.'''
        
            try:
                node_attribs[item] = element.attrib[item]
            except:
                node_attribs[item] = "9999999"
        
        for child in element:
                
            k_problems = PROBLEMCHARS.search(child.attrib['k'])
            k_semi_colon = LOWER_COLON.search(child.attrib['k'])
            v_problems = PROBLEMCHARS.search(child.attrib['v'])
            
            clean_phone_number(child.attrib['k'])
 
            
            if k_problems or v_problems: #will omit key/value if either key or value has problem chars
                pass
            
                
            elif k_semi_colon:
                node_tags_dict = {}
                
                '''removes underscores and semi-colons from child.attrib['v'] and appends it to the 
                node_tags_dict dictionary with "value" as its key.'''
                
                v_value = remove_underscores(child.attrib["v"])
                v_value_semicolon = remove_semicolons(v_value)
                node_tags_dict["value"] = v_value_semicolon
                
                '''Appends 'id' value of element to the node_tags_dict dictionary.
                Removes underscores and semi-colons from child.attrib['k'] and appends it to the 
                node_tags_dict dictionary with "key" as its key.'''
                
                node_tags_dict["id"] = node_attribs["id"]
                k_value = remove_underscores(child.attrib['k'])
                k_value_semicolon = remove_semicolons(k_value)
                
                k_value_split = k_value_semicolon.split(":")
                
                
                if len(k_value_split) <= 2:
                    node_tags_dict["key"] = k_value_split[1]
                    node_tags_dict["type"] = k_value_split[0]
                if len(k_value_split) > 2:
                    node_tags_dict["key"] = k_value_split[1] + ":" + k_value_split[2]
                    node_tags_dict["type"] = k_value_split[0]
        
                tags.append(node_tags_dict)
            
            else:
                node_tags_dict = {}
                
                 '''removes underscores and semi-colons from child.attrib['k'] and appends it to the 
                node_tags_dict dictionary with "key" as its key.'''
                    
                k_value = remove_underscores(child.attrib['k'])
                k_value_semicolon = remove_semicolons(k_value)
                node_tags_dict["key"] = k_value_semicolon
                
                '''removes underscores and semi-colons from child.attrib['v'] and appends it to the 
                node_tags_dict dictionary with "value" as its key.'''
                
                v_value = remove_underscores(child.attrib["v"])
                v_value_semicolon = remove_semicolons(v_value)
                node_tags_dict["value"] = v_value_semicolon
                
                '''Appends 'id' value of element to the node_tags_dict dictionary.
                Appends 'type' to the node_tags_dict dictionary.'''
                
                node_tags_dict["id"] = node_attribs["id"] 
                node_tags_dict["type"] = default_tag_type
                
                tags.append(node_tags_dict)
            

        return {'node': node_attribs, 'node_tags': tags}
    
    elif element.tag == 'way':
        for item in WAY_FIELDS:
            try:
                way_attribs[item] = element.attrib[item]
            except:
                way_attribs[item] = "9999999"
                
        count = 0
        for child in element:
            if child.tag == "nd":
                way_nodes_dict = {}
                way_nodes_dict['id'] = way_attribs['id'] 
                if child.get("ref"):
                    way_nodes_dict["node_id"] = child.attrib['ref']
                    way_nodes_dict['position'] = count
                    count = count + 1
                way_nodes.append(way_nodes_dict)
            
            elif child.tag == "tag":
                
                k_problems = PROBLEMCHARS.search(child.attrib['k'])
                k_semi_colon = LOWER_COLON.search(child.attrib['k'])
                v_problems = PROBLEMCHARS.search(child.attrib['v'])
                
                clean_phone_number(child.attrib['k'])
                
                
                if k_problems or v_problems: #will omit key/value if either key or value has problem chars
                    pass
                
          
                elif k_semi_colon:
                    way_tags_dict = {}
                    
                '''removes underscores and semi-colons from child.attrib['v'] and appends it to the 
                node_tags_dict dictionary with "value" as its key.'''
                
                    v_value = remove_underscores(child.attrib["v"])
                    v_value_semicolon = remove_semicolons(v_value)
                    way_tags_dict["value"] = v_value_semicolon
                    
                '''Appends 'id' value of element to the node_tags_dict dictionary.
                Removes underscores and semi-colons from child.attrib['k'] and appends it to the 
                node_tags_dict dictionary with "key" as its key.'''
                    
                    way_tags_dict["id"] = way_attribs["id"]
                    k_value = remove_underscores(child.attrib['k'])
                    k_value_semicolon = remove_semicolons(k_value)
                    
                    k_value_split = k_value_semicolon.split(":")
                
                    if len(k_value_split) <= 2:
                        way_tags_dict["key"] = k_value_split[1]
                        way_tags_dict["type"] = k_value_split[0]
                    if len(k_value_split) > 2:
                        way_tags_dict["key"] = k_value_split[1] + ":" + k_value_split[2]
                        way_tags_dict["type"] = k_value_split[0]
                    
                    tags.append(way_tags_dict)
                    
                else:
                    way_tags_dict = {}
                    
                '''removes underscores and semi-colons from child.attrib['k'] and appends it to the 
                node_tags_dict dictionary with "key" as its key.'''
                    
                    k_value = remove_underscores(child.attrib['k'])
                    k_value_semicolon = remove_semicolons(k_value)
                    way_tags_dict["key"] = k_value_semicolon
                    
                '''removes underscores and semi-colons from child.attrib['v'] and appends it to the 
                node_tags_dict dictionary with "value" as its key.'''
                    
                    v_value = remove_underscores(child.attrib["v"])
                    v_value_semicolon = remove_semicolons(v_value)
                    way_tags_dict["value"] = v_value_semicolon
                    
                '''Appends 'id' value of element to the node_tags_dict dictionary.
                Appends 'type' to the node_tags_dict dictionary.'''     
                    
                    way_tags_dict["id"] = way_attribs["id"]
                    way_tags_dict["type"] = default_tag_type

                    tags.append(way_tags_dict)
            
                
            
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_strings = (
            "{0}: {1}".format(k, v if isinstance(v, str) else ", ".join(v))
            for k, v in errors.iteritems()
        )
        raise cerberus.ValidationError(
            message_string.format(field, "\n".join(error_strings))
        )


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_FILE, validate=True)  


from collections import defaultdict

#Functions used to audit the data

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

def jb_unique_k_and_v(osmfile, tagtype):
    """Creates a default dictionary of key values as the keys and value values as the values.
    Function takes two arguments. First argument is an XML file. The second argument is 
    tagtypes in the OSM file corresponding to node, way, or relation. Node, way, and
    relation are all elements types in the XML file."""  

    osm_file = open(osmfile, "r")
    unique_k_and_v = defaultdict(set)
    for i, element in enumerate(get_element(osm_file)):
        if element.tag == tagtype:                         
            for tag in element.iter("tag"):
                    unique_k_and_v[tag.attrib['k']].add(tag.attrib['v'])    
    print len(unique_k_and_v.keys())  # this is a check
    print "--------------------"
    return unique_k_and_v
      