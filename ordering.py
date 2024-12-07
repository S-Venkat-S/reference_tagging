from configparser import ConfigParser
from bs4 import BeautifulSoup
import json
import jmespath


def add_tag(res, style="vancouver"):
    file = "styles_json/config_" + style + ".json"

    ieee_config = json.load(open(file))

    csl_json = res["doi_metadata"] if res["doi_metadata"] else res["parsed"]

    def func(k, author_index=None):
        xml_tag = list(k.keys())[0]
        mix = soup.new_tag(xml_tag)
        if "child" in k[xml_tag]:
            for child_item in k[xml_tag]["child"]:
                child_tag = func(child_item, author_index=author_index)
                if child_tag:
                    mix.append(child_tag)

        if "children" in k[xml_tag]:
            for child_item in k[xml_tag]["children"]:
                authors = csl_json.get("author", [])
                for i, author in enumerate(authors):
                    child_tag = func(child_item, author_index=i)
                    if child_tag:
                        mix.append(child_tag)

        # Set value if "value" exists
        if "value" in k[xml_tag]:

            csl_value = k[xml_tag]["value"].replace(
                "[?]", f"[{author_index}]" if author_index is not None else "")
            xml_text = jmespath.search(
                csl_value, csl_json) if "." in csl_value or "[" in csl_value else csl_json.get(csl_value)
            if xml_text:
                mix.string = str(xml_text) if not isinstance(
                    xml_text, BeautifulSoup) else xml_text

        # Add attributes if present
        if "attributes" in k[xml_tag]:
            for attribute in k[xml_tag]["attributes"]:
                for attr_key, attr_value in attribute.items():
                    if attr_value["value"] == "URL" or attr_value["value"] == "doi_url" or attr_value["value"] == "type":
                        if attr_value["value"] in csl_json:
                            mix[attr_key] = csl_json.get(attr_value["value"])
                        else:
                            mix[attr_key] = "journal"
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

    # Remove the wrapper tags
    for wrapper in soup.find_all("wrapper"):
        wrapper.unwrap()

    return str(soup)