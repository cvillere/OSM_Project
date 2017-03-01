# Iterative Parsing

import xml.etree.cElementTree as ET
import pprint

def count_tags(filename):
    TagList = []
    Tag_Dictionary = {}
    for event, elem in ET.iterparse(filename):
        TagList.append(elem.tag)
    for item in TagList:
        if item not in Tag_Dictionary:
            count = 0
            for item_tag in Tag_List:
                if item_tag == item:
                    count = count + 1
                Tag_Dictionary[item] = count
    return Tag_Dictionary

