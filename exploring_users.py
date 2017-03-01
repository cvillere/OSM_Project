# Exploring Users

def get_user(element):
    if element.tag == "node":
        idu = element.attrib["uid"]
    elif element.tag == "way":
        idu = element.attrib["uid"]
    elif element.tag == "relation":
        idu = element.attrib["uid"]
    else:
        idu = None
    
    userid = idu
    
    return userid

def process_map(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        if get_user(element) == None:
            pass
        elif get_user(element) not in users:
            users.add(get_user(element))
        
        pass
    
    return users