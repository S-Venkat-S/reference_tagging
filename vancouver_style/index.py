from configparser import ConfigParser
from bs4 import BeautifulSoup
from bs4.element import NavigableString
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


# res = {'doi_metadata': {'indexed': {'date-parts': [[2023, 10, 7]], 'date-time': '2023-10-07T10:11:59Z', 'timestamp': 1696673519006}, 'reference-count': 46, 'publisher': 'Institute of Electrical and Electronics Engineers (IEEE)', 'issue': '7', 'license': [{'start': {'date-parts': [[2023, 7, 1]], 'date-time': '2023-07-01T00:00:00Z', 'timestamp': 1688169600000}, 'content-version': 'vor', 'delay-in-days': 0, 'URL': 'https://ieeexplore.ieee.org/Xplorehelp/downloads/license-information/IEEE.html'}, {'start': {'date-parts': [[2023, 7, 1]], 'date-time': '2023-07-01T00:00:00Z', 'timestamp': 1688169600000}, 'content-version': 'stm-asf', 'delay-in-days': 0, 'URL': 'https://doi.org/10.15223/policy-029'}, {'start': {'date-parts': [[2023, 7, 1]], 'date-time': '2023-07-01T00:00:00Z', 'timestamp': 1688169600000}, 'content-version': 'stm-asf', 'delay-in-days': 0, 'URL': 'https://doi.org/10.15223/policy-037'}], 'funder': [{'DOI': '10.13039/501100012166', 'name': 'National Key Research and Development Program of China', 'doi-asserted-by': 'publisher', 'award': ['2019YFB1405702'], 'id': [{'id': '10.13039/501100012166', 'id-type': 'DOI', 'asserted-by': 'publisher'}]}], 'content-domain': {'domain': [], 'crossmark-restriction': False}, 'published-print': {'date-parts': [[2023, 7]]}, 'DOI': '10.1109/tnnls.2021.3114378', 'type': 'journal-article', 'created': {'date-parts': [[2021, 10, 6]], 'date-time': '2021-10-06T02:08:08Z', 'timestamp': 1633486088000}, 'page': '3727-3736', 'source': 'Crossref', 'is-referenced-by-count': 18, 'title': 'Enhancing Chinese Character Representation With Lattice-Aligned Attention', 'prefix': '10.1109', 'volume': '34', 'author': [{'ORCID': 'http://orcid.org/0000-0003-4503-8259', 'authenticated-orcid': False, 'given': 'Shan', 'family': 'Zhao', 'sequence': 'first', 'affiliation': [{'name': 'School of Design, Hunan University, Changsha, China'}]}, {'ORCID': 'http://orcid.org/0000-0002-5002-3724', 'authenticated-orcid': False, 'given': 'Minghao', 'family': 'Hu', 'sequence': 'additional', 'affiliation': [{'name': 'PLA Academy of Military Science, Beijing, China'}]}, {'ORCID': 'http://orcid.org/0000-0001-5726-833X', 'authenticated-orcid': False, 'given': 'Zhiping', 'family': 'Cai', 'sequence': 'additional', 'affiliation': [{'name': 'College of Computer, National University of Defense Technology, Changsha, Hunan, China'}]}, {'given': 'Zhanjun', 'family': 'Zhang', 'sequence': 'additional', 'affiliation': [{'name': 'College of Computer, National University of Defense Technology, Changsha, Hunan, China'}]}, {'ORCID': 'http://orcid.org/0000-0002-6620-1898', 'authenticated-orcid': False, 'given': 'Tongqing', 'family': 'Zhou', 'sequence': 'additional', 'affiliation': [{'name': 'College of Computer, National University of Defense Technology, Changsha, Hunan, China'}]}, {'ORCID': 'http://orcid.org/0000-0001-8753-3878', 'authenticated-orcid': False, 'given': 'Fang', 'family': 'Liu', 'sequence': 'additional', 'affiliation': [{'name': 'School of Design, Hunan University, Changsha, Hunan, China'}]}], 'member': '263', 'reference': [{'key': 'ref13', 'doi-asserted-by': 'publisher', 'DOI': '10.18653/v1/P18-1144'}, {'key': 'ref35', 'article-title': 'Layer normalization', 'author': 'lei ba', 'year': '2016', 'journal-title': 'arXiv 1607 06450'}, {'key': 'ref12', 'doi-asserted-by': 'publisher', 'DOI': '10.1609/aaai.v35i16.17706'}, {'key': 'ref34', 'doi-asserted-by': 'publisher', 'DOI': '10.1109/CVPR.2016.90'}, {'key': 'ref15', 'doi-asserted-by': 'publisher', 'DOI': '10.18653/v1/P19-1430'}, {'key': 'ref37', 'first-page': '108', 'article-title': 'The third international Chinese language processing bakeoff: Word segmentation and named entity recognition', 'author': 'levow', 'year': '2006', 'journal-title': 'Proc 5th SIGHAN Workshop Chin Lang Process'}, {'key': 'ref14', 'first-page': '2379', 'article-title': 'An encoding strategy based word-character LSTM for Chinese NER', 'volume': '1', 'author': 'liu', 'year': '2019', 'journal-title': 'Proc Conf North Amer Chapter Assoc Comput Linguistics Hum Lang Technol'}, {'key': 'ref36', 'doi-asserted-by': 'publisher', 'DOI': '10.18653/v1/D15-1064'}, {'key': 'ref31', 'doi-asserted-by': 'publisher', 'DOI': '10.1109/CVPR.2018.00637'}, {'key': 'ref30', 'doi-asserted-by': 'publisher', 'DOI': '10.1109/TNNLS.2018.2856253'}, {'key': 'ref11', 'doi-asserted-by': 'publisher', 'DOI': '10.1016/j.jbi.2019.103290'}, {'key': 'ref33', 'doi-asserted-by': 'publisher', 'DOI': '10.18653/v1/P19-1656'}, {'key': 'ref10', 'doi-asserted-by': 'publisher', 'DOI': '10.12783/dtcse/wcne2017/19833'}, {'key': 'ref32', 'first-page': '2335', 'article-title': 'Relation classification via convolutional deep neural network', 'author': 'zeng', 'year': '2014', 'journal-title': 'Proc 25th Int Conf Comput Linguistics (COLING)'}, {'key': 'ref2', 'doi-asserted-by': 'publisher', 'DOI': '10.18653/v1/P19-1024'}, {'key': 'ref1', 'doi-asserted-by': 'publisher', 'DOI': '10.1109/TNNLS.2016.2603784'}, {'key': 'ref17', 'doi-asserted-by': 'publisher', 'DOI': '10.1109/CVPR.2019.00680'}, {'key': 'ref39', 'article-title': 'A concise model for multi-criteria Chinese word segmentation with transformer encoder', 'author': 'qiu', 'year': '2019', 'journal-title': 'arXiv 1906 12035'}, {'key': 'ref16', 'first-page': '2720', 'article-title': 'Subword encoding in lattice LSTM for Chinese word segmentation', 'volume': '1', 'author': 'yang', 'year': '2019', 'journal-title': 'Proc Conf North Amer Chapter Assoc Comput Linguistics Hum Lang Technol'}, {'key': 'ref38', 'first-page': '2335', 'article-title': 'The second international Chinese word segmentation bakeoff', 'author': 'emerson', 'year': '2005', 'journal-title': 'Proc 4th SIGHAN Workshop Chin Lang Process'}, {'key': 'ref19', 'doi-asserted-by': 'publisher', 'DOI': '10.18653/v1/2020.acl-main.528'}, {'key': 'ref18', 'doi-asserted-by': 'publisher', 'DOI': '10.1109/CVPR.2019.00644'}, {'key': 'ref24', 'doi-asserted-by': 'publisher', 'DOI': '10.24963/ijcai.2019/692'}, {'key': 'ref46', 'doi-asserted-by': 'publisher', 'DOI': '10.18653/v1/P17-1110'}, {'key': 'ref23', 'doi-asserted-by': 'publisher', 'DOI': '10.18653/v1/2020.acl-main.735'}, {'key': 'ref45', 'doi-asserted-by': 'publisher', 'DOI': '10.1609/aaai.v33i01.33016457'}, {'key': 'ref26', 'doi-asserted-by': 'publisher', 'DOI': '10.18653/v1/D19-1396'}, {'key': 'ref25', 'doi-asserted-by': 'publisher', 'DOI': '10.18653/v1/D19-1096'}, {'key': 'ref20', 'doi-asserted-by': 'publisher', 'DOI': '10.18653/v1/D17-1145'}, {'key': 'ref42', 'doi-asserted-by': 'publisher', 'DOI': '10.18653/v1/D15-1203'}, {'key': 'ref41', 'doi-asserted-by': 'publisher', 'DOI': '10.18653/v1/N18-2028'}, {'key': 'ref22', 'doi-asserted-by': 'publisher', 'DOI': '10.18653/v1/2020.acl-main.734'}, {'key': 'ref44', 'article-title': 'Relation classification via recurrent neural network', 'author': 'zhang', 'year': '2015', 'journal-title': 'arXiv 1508 01006'}, {'key': 'ref21', 'article-title': 'Lattice-based recurrent neural network encoders for neural machine translation', 'author': 'su', 'year': '2016', 'journal-title': 'arXiv 1609 07730'}, {'key': 'ref43', 'doi-asserted-by': 'publisher', 'DOI': '10.18653/v1/P16-1200'}, {'key': 'ref28', 'doi-asserted-by': 'publisher', 'DOI': '10.18653/v1/2020.acl-main.611'}, {'key': 'ref27', 'article-title': 'TENER: Adapting transformer encoder for named entity recognition', 'author': 'yan', 'year': '2019', 'journal-title': 'arXiv 1911 04474'}, {'key': 'ref29', 'doi-asserted-by': 'publisher', 'DOI': '10.1109/ICCV.2015.279'}, {'key': 'ref8', 'article-title': 'A discourse-level named entity recognition and relation extraction dataset for Chinese literature text', 'author': 'xu', 'year': '2017', 'journal-title': 'arXiv 1711 07010'}, {'key': 'ref7', 'doi-asserted-by': 'publisher', 'DOI': '10.18653/v1/N16-1030'}, {'key': 'ref9', 'article-title': 'F-score driven max margin neural network for named entity recognition in Chinese social media', 'author': 'he', 'year': '2016', 'journal-title': 'arXiv 1611 04234'}, {'key': 'ref4', 'doi-asserted-by': 'publisher', 'DOI': '10.1007/s10115-017-1100-y'}, {'key': 'ref3', 'article-title': 'Dynamic modeling cross-modal interactions in two-phase prediction for entity-relation extraction', 'author': 'zhao', 'year': '2021', 'journal-title': 'IEEE Trans Neural Netw Learn Syst'}, {'key': 'ref6', 'doi-asserted-by': 'publisher', 'DOI': '10.18653/v1/P17-1078'}, {'key': 'ref5', 'doi-asserted-by': 'publisher', 'DOI': '10.1109/TNNLS.2018.2884540'}, {'key': 'ref40', 'article-title': 'Pre-training with whole word masking for Chinese BERT', 'author': 'cui', 'year': '2019', 'journal-title': 'arXiv 1906 08101'}], 'container-title': 'IEEE Transactions on Neural Networks and Learning Systems', 'original-title': [], 'link': [{'URL': 'http://xplorestaging.ieee.org/ielx7/5962385/10175014/09559723.pdf?arnumber=9559723', 'content-type': 'unspecified', 'content-version': 'vor', 'intended-application': 'similarity-checking'}], 'deposited': {'date-parts': [[2023, 7, 31]], 'date-time': '2023-07-31T17:33:28Z', 'timestamp': 1690824808000}, 'score': 1, 'resource': {'primary': {'URL': 'https://ieeexplore.ieee.org/document/9559723/'}}, 'subtitle': [], 'short-title': [], 'issued': {'date-parts': [[2023, 7]]}, 'references-count': 46, 'journal-issue': {'issue': '7'}, 'URL': 'http://dx.doi.org/10.1109/tnnls.2021.3114378', 'relation': {}, 'ISSN': ['2162-237X', '2162-2388'], 'subject': [], 'container-title-short': 'IEEE Trans. Neural Netw. Learning Syst.', 'published': {'date-parts': [[2023, 7]]}, 'user_doi': 'https://doi.org/10.1109/tnnls.2021.3114378', 'fpage': '3727', 'lpage': '3736', 'year': '2023, Jul.'}}
# add_tag(res, "vancouver")
