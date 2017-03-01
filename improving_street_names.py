# Improving Street Names

def update_name(name, mapping):
    name_object = street_type_re.search(name)
    if name_object:
        if name_object.group() in mapping.keys():
            name = re.sub(street_type_re, mapping[name_object.group()], name)
            
    return name