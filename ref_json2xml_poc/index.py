from configparser import ConfigParser
from bs4 import BeautifulSoup
import json
import jmespath
# ieee_config = json.load(open("config_ieee.json"))
# csl_json = json.load(open("inp.json"))

def Add_tag(res, style):
    file = "styles_json/config_" + style + ".json"
    # print(file)
    ieee_config = json.load(open(file))
    doi = res[0]["doi_metadata"]

    if doi:
        ref = res[0]["doi_metadata"]
    else:
        ref = res[0]["parsed"]
    
    # print(ref,"---")
    csl_json = ref
    def func(k):
        xml_tag = list(k.keys())[0]
        mix = soup.new_tag(xml_tag)
        if "child" in k[xml_tag]:
            for child_item in k[xml_tag]["child"]:
                child_tag = func(child_item)
                if child_tag:
                    mix.append(child_tag)

            # Set value if "value" exists
        if "value" in k[xml_tag]:
            csl_value = k[xml_tag]["value"]
            if csl_value:
                if "." in csl_value or "[" in csl_value:  # For jmespath expressions
                    xml_text = jmespath.search(csl_value, csl_json)
                    if xml_text is not None:
                        mix.string = str(xml_text)

                else:
                    xml_text = csl_json.get(csl_value)
                    if xml_text is not None:
                        mix.string = str(xml_text)

        # Add attributes if present
        if "attributes" in k[xml_tag]:
            for attribute in k[xml_tag]["attributes"]:
                for attr_key, attr_value in attribute.items():
                    # print(attr_value["value"])
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

    print(soup.prettify())
    # texted = ["<volume>", "<issue>", "<fpage>", ""]
    # sp = str(soup).split("<volume>")
    # change_ref = sp[0] + ", vol. <volume>" + sp[1]
    # print(change_ref)
    return str(soup)
        # tag = list(i.keys())[0]
        # # print(tag)
        # label = soup.new_tag(tag)
        # # label.string = references_json[0]["id"]
        # mix.append(label)
        # # print(tag)
        # # csl = i[tag]["value"]
        # for j in i[tag]:
        #     # print(j)
        #     if j == "value":
        #         csl = i[tag]["value"]
        #         if csl:
        #             if "." in csl or "[" in csl:
        #                 xml_text = jmespath.search(csl, csl_json)
        #                 label.string = str(xml_text)
        #             else:
        #                 xml_text = csl_json.get(csl)
        #                 label.string = xml_text

        #     if j == "child":
        #         for id, y in enumerate((i[tag][j])):
        #             in_tag = list(i[tag][j][id].keys())[0]
        #             label1 = soup.new_tag(in_tag)
        #             label.append(label1)
        #             csl = i[tag][j][id][in_tag]["value"]
        #             # print(csl,"--")
        #             # print(in_tag,"===")
        #             if csl:
        #                 if "." in csl or "[" in csl:
        #                     xml_text = jmespath.search(csl, csl_json)
        #                     label1.string = str(xml_text)
        #                 else:
        #                     xml_text = csl_json.get(csl)
        #                     label1.string = xml_text

        #     if j == "attributes":
        #         for id, y in enumerate((i[tag][j])):
        #             in_tag = list(i[tag][j][id].keys())[0]
        #             csl = i[tag][j][id][in_tag]["value"]
        #             label[in_tag] = csl

        # if i[tag]["child"]:
        #     print(i[tag]["child"])
        
        # if csl:
        #     if "." in csl or "[" in csl:
        #         xml_text = jmespath.search(csl, csl_json)
        #     else:
        #         xml_text = csl_json.get(csl)
        #         label.string = xml_text
        # for attribute in attributes:
    # print(soup.prettify())
        # print(tag, xml_text)