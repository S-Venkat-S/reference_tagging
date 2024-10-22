import xml.etree.ElementTree as ET
import calendar
from bs4 import BeautifulSoup
import requests

id = "1"
xml_text = "Polit, D. G., & Beck, C. T. (2021). Nursing research: Generating and assessing evidence for nursing practice (11th ed.). Wolters Kluwer."
style = "ieee"

# references_data = {
#     "references": [
#         {
#             "id": id,
#             "reference": xml_text,
#             "style" : style
#         }
#     ]
# }

# api_endpoint = 'http://127.0.0.1:8001/'  #API url endpoint
# references_json = ''
# try:
#     #Sending a POST request to the API endpoint with JSON data
#     response = requests.post(api_endpoint, json=references_data)
        
#     #Checking if the request was successful (status code 200)
#     if response.status_code == 200:
#         references_json = response.json()  #Assuming the response is JSON
#         print(references_json)
#     else:
#         print({'error': f'API Error: {response.status_code}'})
    
# except requests.exceptions.RequestException as e:
#     # pass
#     print({'error': f'Request Exception: {str(e)}'})
    
from index import res

references_json = res


from configparser import ConfigParser
config = ConfigParser()
config.read("config.ini")
con = config["ieee"]
# print(config.sections())
# print(config["ieee"]["title"])
# print(list(config["ieee"]))
# print(len((references_json)))
xml_text = ''
if references_json:
    doi = references_json[0]["doi_metadata"]

    if doi:
        ref = references_json[0]["doi_metadata"]
    else:
        ref = references_json[0]["parsed"]

    tag_list = config.get('ieee', 'order').split(', ')

    soup = BeautifulSoup(features='xml')
    reference = soup.new_tag(con["ref"], **{con['ref_att']: references_json[0]["id"]})
    soup.append(reference)
    label = soup.new_tag(con["label"])
    label.string = references_json[0]["id"]
    reference.append(label)
    mix = soup.new_tag(con["mix_cit"], **{con['mix_att']: "journal"})
    reference.append(mix)

    #Loop through the tag order
    for i in tag_list:
        #Loop through parsed text in json
        for j in ref:
            #Find author name
            if j==i=="author":
                per_grp = soup.new_tag(con["per_grp"], **{con['per_grp_att']: "author"})
                mix.append(per_grp)
                for k in ref["author"]:
                    if len(k)>1:
                        str_name = soup.new_tag(con["str_name"])
                        per_grp.append(str_name)
                        sur_name = soup.new_tag(con["sur_name"])
                        sur_name.string = k["family"]
                        str_name.append(sur_name)
                        giv_name = soup.new_tag(con["giv_name"])
                        giv_name.string = k["given"]
                        str_name.append(giv_name)
                    else:
                        str_name = soup.new_tag(con["str_name"])
                        mix.append(str_name)
                        sur_name = soup.new_tag(con["sur_name"])
                        sur_name.string = k["family"]
                        str_name.append(sur_name)
                        str_name.append(per_grp)
            #Find article title
            elif j==i=="title":
                title = soup.new_tag(con["alt_title"])
                title.string = ref["title"]
                mix.append(title)
            #Find source
            elif j==i=="container-title":
                con_title = soup.new_tag(con["source"])
                con_title.string = ref["container-title"]
                mix.append(con_title)
                # con_title = ET.SubElement(mix, f'{con["source"]}')
                # con_title.text = ref["container-title"]
                # xml_text += f'<{con["source"]}>{ref["container-title"]}</{con["source"]}>'
            #Find Volume
            elif j==i=="volume":
                vol = soup.new_tag(con["volume"])
                vol.string = ref["volume"]
                mix.append(vol)
            #Find issue
            elif j==i=="issue":
                issue = soup.new_tag(con["issue"])
                issue.string = ref["issue"]
                mix.append(issue)
            # Find page number
            elif j==i=="page":
                if "-" in ref["page"]:
                    split_page = ref["page"].split("-")
                    fpage = soup.new_tag(con["fpage"])
                    fpage.string = split_page[0]
                    mix.append(fpage)
                    lpage = soup.new_tag(con["lpage"])
                    lpage.string = split_page[1]
                    mix.append(lpage)
                else:
                    fpage = soup.new_tag(con["fpage"])
                    fpage.string = ref["page"]
                    mix.append(fpage)
            #Find Year
            elif j==i=="year":
                year = soup.new_tag(con["year"])
                year.string = ref["year"]
                mix.append(year)
            #Find DOI
            elif j==i=="DOI":
                doi = soup.new_tag(con["pub_id"], **{con['ext_type']: "uri"}, **{con['break']: "Y"}, **{con['xlink_href']: f"https://doi.org/{ref['DOI']}"})
                doi.string = ref["DOI"]
                mix.append(doi)
            #Find publisher
            elif j==i=="publisher":
                publish = soup.new_tag(con["publish"])
                publish.string = ref["publisher"]
                mix.append(publish)
            #Find doi_url
            elif j==i=="doi_url":
                doi_url = soup.new_tag(con["doi_url"])
                doi_url.string = ref["doi_url"]
                mix.append(doi_url)
            #Find year
            elif j==i=="issued":
                for d_name in ref["issued"]:
                    if d_name=="date-parts":
                        date = ref["issued"][d_name][0]
                    else:
                        date = []
                        date.append(ref["issued"][d_name])
                
                if len(date)>1:
                    dates = calendar.month_name[date[1]]
                    date[1] = ","+dates[:3]+"."
                    year = soup.new_tag(con["year"])
                    year.string = " ".join(map(str, date))
                    mix.append(year)
                else:
                    year = soup.new_tag(con["year"])
                    year.string = str(date[0])
                    mix.append(year)

    # print(soup.prettify(),"++++")





    # def json_to_html(json_data, style):
    #     html_data = ""
    #     config = styles_config[style]

    #     # root = config['root_element']
    #     # reference = config['reference_element']
    #     reference = ET.Element(config['reference_element'])

    #     title = ET.SubElement(reference, config['title_element'])
    #     title.text = json_data['parsed']['title']

    #     author = ET.SubElement(reference, config['title_element'])
    #     author.text = json_data['parsed']['title']

    #     return(ET.tostring(reference, encoding='unicode'))
    

    # html_output = ""
    # json_list = references_json
    # for json_data in json_list:
    #     xml_output = json_to_html(json_data, "ieee")
    #     # html_output += f"<p>{html_data}</p>"

    #     print(xml_output)
