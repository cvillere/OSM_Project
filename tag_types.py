# Tag Types

def key_type(element, keys):
    if element.tag == "tag":
        k = element.attrib["k"]
        if re.search(lower, k):
            keys["lower"] += 1
        elif re.search(lower_colon, k):
            keys["lower_colon"] += 1
        elif re.search(problemchars, k):
            keys["problemchars"] += 1
        else:
            keys["other"] += 1
        
        pass
    return keys