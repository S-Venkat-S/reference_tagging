import json

def json_to_html(json_data):
    html_data = ""
    for key, value in json_data.items():
        if isinstance(value, list):
            html_data += f"<span class='{key}'>"
            for item in value:
                if isinstance(item, dict):
                    html_data += json_to_html(item)
                else:
                    html_data += f"<span class='item'>{item}</span>"
            html_data += "</span>"
        elif isinstance(value, dict):
            html_data += f"<span class='{key}'>"
            html_data += json_to_html(value)
            html_data += "</span>"
        else:
            html_data += f"<span class='{key}'>{value}</span>"
    return html_data

html_output = ""
json_list = json.load(open("References.json", "r"))
for json_data in json_list:
    html_data = json_to_html(json_data)
    html_output += f"<p>{html_data}</p>"

print(html_output)
