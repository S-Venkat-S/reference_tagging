from configparser import ConfigParser
from bs4 import BeautifulSoup
import json
import jmespath
# ieee_config = json.load(open("config_ieee.json"))
# csl_json = json.load(open("inp.json"))

def add_tag(res, style="ieee"):
    file = "styles_json/config_" + style + ".json"
    # print(file)
    ieee_config = json.load(open(file))
    # print((res))
    csl_json = res["doi_metadata"] if res["doi_metadata"] else res["parsed"]

    def func(k, author_index = None):
        xml_tag = list(k.keys())[0]
        mix = soup.new_tag(xml_tag)
        if "child" in k[xml_tag]:
            for child_item in k[xml_tag]["child"]:
                child_tag = func(child_item, author_index = author_index)
                if child_tag:
                    mix.append(child_tag)

        if "children" in k[xml_tag]:
            for child_item in k[xml_tag]["children"]:
                authors = csl_json.get("author", [])
                for i,author in enumerate(authors):
                    child_tag = func(child_item, author_index = i)
                    if child_tag:
                        mix.append(child_tag)

        #Set value if "value" exists
        if "value" in k[xml_tag]:

            csl_value = k[xml_tag]["value"].replace("[?]", f"[{author_index}]" if author_index is not None else "")
            xml_text = jmespath.search(csl_value, csl_json) if "." in csl_value or "[" in csl_value else csl_json.get(csl_value)
            if xml_text:
                mix.string = str(xml_text) if not isinstance(xml_text, BeautifulSoup) else xml_text
                
            # csl_value = k[xml_tag]["value"]
            # if csl_value:
            #     if "." in csl_value or "[" in csl_value:  # For jmespath expressions
            #         if author_index is not None:
            #             csl_value = csl_value.replace("[?]", f"[{author_index}]")
            #         xml_text = jmespath.search(csl_value, csl_json)
            #         if xml_text is not None:
            #             mix.string = str(xml_text)

            #     else:
            #         if author_index is not None:
            #             csl_value = csl_value.replace("[?]", f"[{author_index}]")
            #         xml_text = csl_json.get(csl_value)
            #         if xml_text is not None:
            #             sou = BeautifulSoup(xml_text, 'html.parser')
            #             mix.append(BeautifulSoup(str(sou), 'html.parser'))

        #Add attributes if present
        if "attributes" in k[xml_tag]:
            for attribute in k[xml_tag]["attributes"]:
                for attr_key, attr_value in attribute.items():
                    if attr_value["value"] == "URL" or attr_value["value"] == "doi_url":
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
# res = {'parsed': {'type': 'book', 'title': 'The Pocket Guide to Neurocritical Care: A concise reference for the evaluation and management of neurologic emergencies', 'author': [{'family': 'Darsie', 'given': 'M. D.'}, {'family': 'Moheet', 'given': 'A. M.'}], 'issued': {'year': 2017}, 'publisher': 'Neurocritical Care Society', 'place': 'Chicago, IL'}, 'doi_metadata': False}
# add_tag(res, "ieee")