from configparser import ConfigParser
from bs4 import BeautifulSoup
import json
import jmespath
# ieee_config = json.load(open("config_ieee.json"))
# csl_json = json.load(open("inp.json"))

def Add_tag(res, style):
    file = "styles_json/config_" + "ieee" + ".json"
    # print(file)
    ieee_config = json.load(open(file))
    doi = res[0]["doi_metadata"]

    if doi:
        ref = res[0]["doi_metadata"]
    else:
        ref = res[0]["parsed"]

    csl_json = ref
    def func(k, author_index=None):
        xml_tag = list(k.keys())[0]
        mix = soup.new_tag(xml_tag)
        if "child" in k[xml_tag]:
            for child_item in k[xml_tag]["child"]:
                if xml_tag == "person-group":
                    authors = csl_json.get("author", [])
                    for i,author in enumerate(authors):
                        child_tag = func(child_item, author_index=i)
                        if child_tag:
                            mix.append(child_tag)
                else:
                    child_tag = func(child_item, author_index=author_index)
                    if child_tag:
                        mix.append(child_tag)

        #Set value if "value" exists
        if "value" in k[xml_tag]:
            csl_value = k[xml_tag]["value"]
            if csl_value:
                if "." in csl_value or "[" in csl_value:  # For jmespath expressions
                    if author_index is not None:
                        csl_value = csl_value.replace("[0]", f"[{author_index}]")
                    xml_text = jmespath.search(csl_value, csl_json)
                    if xml_text is not None:
                        # print(xml_text)
                        mix.string = str(xml_text)
                        # print(mix,"===")

                else:
                    if author_index is not None:
                        csl_value = csl_value.replace("[0]", f"[{author_index}]")
                    xml_text = csl_json.get(csl_value)
                    if xml_text is not None:
                        # print(xml_text,"----")
                        sou = BeautifulSoup(xml_text, 'html.parser')
                        # print(sou,"****")
                        # for item in sou:
                        #     # print(item,"????")
                        #     mix.append(item)
                        # for item in sou:
                        #     if isinstance(item, str):  # If it's a string (text node)
                        #         mix.append(item)
                        #     else:  # If it's a tag, append it
                        #         mix.append(item)
                        mix.append(BeautifulSoup(str(sou), 'html.parser'))

                        # print(mix,")))")
                        # mix.string = str(xml_text)

        #Add attributes if present
        if "attributes" in k[xml_tag]:
            for attribute in k[xml_tag]["attributes"]:
                for attr_key, attr_value in attribute.items():
                    if attr_value["value"] == "URL":
                        if attr_value["value"] in csl_json:
                            mix[attr_key] = csl_json.get(attr_value["value"])
                    else:
                        mix[attr_key] = attr_value["value"]
        
        if mix.string or mix.contents:
            return mix
        else:
            return None  

    soup = BeautifulSoup(features='xml')
    for k in ieee_config:
        root_tag = func(k)
        if root_tag:
            soup.append(root_tag)

    # print(soup.prettify())

    # soup_str = str(soup)
    # print(soup_str)
    # adds = {
    #     "<volume>": ", vol. <volume>",
    #     "</sur-name>": "</sur-name>, ",
    #     "</string-name><string": "</string-name>, <string",
    #     "</article-title>": "</article-title>.",
    #     "<issue>": "<italic>(</italic><issue>",
    #     "</issue>": "</issue><italic>),</italic>",
    #     "<year>": "(<year>",
    #     "</year>": "</year>). ",
    #     "</lpage>": "</lpage>. "
    #   }

    # for key,value in adds.items():
    #     if key in soup_str:
    #         soup_str = soup_str.replace(key, value)
    # sou = BeautifulSoup(soup_str, "xml")
    # print(sou.prettify())
    return str(soup)
# res = [{'parsed': {'type': 'book', 'title': 'The Pocket Guide to Neurocritical Care: A concise reference for the evaluation and management of neurologic emergencies', 'author': [{'family': 'Darsie', 'given': 'M. D.'}, {'family': 'Moheet', 'given': 'A. M.'}], 'issued': {'year': 2017}, 'publisher': 'Neurocritical Care Society', 'place': 'Chicago, IL'}, 'doi_metadata': False}]
# Add_tag(res, "ieee")