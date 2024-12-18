# from googleapi import google
# num_page = 3
import ordering
import calendar
from queue import Queue
from threading import Thread, Lock
from typing import List, Union
from fastapi import FastAPI
import re
import time
import requests
import json
import google.generativeai as genai
from pydantic import BaseModel  # AIzaSyCHmvQi4G7jWTWy6ojYCt67lIxPt36w-Mo
genai.configure(api_key="AIzaSyD4WMOaLJdZ8lVB3vAUh80rWsavImtV1b4")

# def TSP_ref(id, xml_text, style):
app = FastAPI()
DEBUG = True


def debug(message):
    if DEBUG:
        print(message)


def doi_metadata_api(doi_url):

    try:
        url = doi_url
        headers = {
            # "Accept": "application/json"
            "Accept": "application/vnd.citationstyles.csl+json"
        }

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            metadata = json.loads(response.text)
            metadata["user_doi"] = doi_url
            return metadata
        else:
            print(
                f"Error retrieving DOI metadata for DOI {doi_url}: {response.status_code}")
            return None
    except Exception as e:
        print(e)
        return False


def clean_up_doi(doi):
    doi = doi.strip().lower()
    if doi.endswith(".") or doi.endswith(","):
        doi = doi[:-1]
    if "doi:" in doi:
        doi = doi.replace("doi:", "")
    if "org:" in doi:
        doi = doi.replace("org:", "org/")
    if not doi.startswith("doi.org") and not doi.startswith("http"):
        doi = "doi.org/"+doi
    if doi.startswith("doi.org"):
        doi = "https://"+doi
    return doi


def find_doi_in_reference(reference):
    words = reference.split(" ")
    ref = None
    for word in words:
        if "doi" in word.lower() and len(word) > 5:
            ref = word
        elif re.match("\d{2}\.\d{3,}\/", word):
            ref = word
    if ref != None:
        return clean_up_doi(word)
    return False


def ask_google(reference):
    for i in range(3):
        try:
            time.sleep(1)
            generation_config = genai.types.GenerationConfig(temperature=0)
            model = genai.GenerativeModel(
                'gemini-pro', generation_config=generation_config)
            prompt = f"""Parse the below references text in detailed csl-JSON format and also search for DOI in google and add key "doi_url" in the result wherever applicable and give result in JSON Format.
            {reference}
            """
            response = model.generate_content(prompt)
            # matches = re.search(r'(\{.*\})', response.text, re.DOTALL)

            # if matches:
            #     text = matches.group(1)
            #     return json.loads(text)
            # else:
            #     print("No match found")
            response = re.sub(r'```json', '', response.text,
                              flags=re.IGNORECASE)

            return json.loads(response.replace('`', ''))
        except json.JSONDecodeError as decode_err:
            print("Error in decoder.", decode_err)
            continue
        except Exception as e:
            if "429" in str(e):
                wait_time = 2 ** i  # Exponential backoff
                print(
                    f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print("Exception ", e)
                continue
    return False


def ask_crossref(reference):
    error_email = "vapt@transforma.in"
    url = f"https://api.crossref.org/works?filter=has-full-text:true&mailto={error_email}&query={reference}&select=DOI,score&rows=1&sort=score"
    response = requests.get(url)
    if response.status_code == 200:
        metadata = json.loads(response.text)
        if metadata["message"]["items"][0]["score"] > 100:
            return "http://doi.org/" + metadata["message"]["items"][0]["DOI"]
    return False


def ask_duckduckgo(reference):
    from duckduckgo_search import DDGS
    with DDGS() as ddgs:
        for r in ddgs.text(f"{reference}", region='in-en', safesearch='off', max_results=3, backend='html'):
            print(r)


def get_doi_metadata(reference):
    doi_in_reference = find_doi_in_reference(reference)
    if doi_in_reference:
        debug("DOI Found in Reference")
        return doi_metadata_api(doi_in_reference)
    cross_ref = ask_crossref(reference)
    if cross_ref:
        debug("DOI Found in Crossref")
        return doi_metadata_api(cross_ref)
    return False


class Reference(BaseModel):
    id: str
    reference: str
    style: str


class Item(BaseModel):
    references: List[Reference]

# Define the worker function for threads
def worker(work_queue, lock, output_queue):
    while True:
        # Acquire lock before accessing the queue
        lock.acquire()
        if not work_queue or len(work_queue) == 0:
            # Queue is empty, break the loop
            lock.release()
            break
        # Get the next work item from the queue
        work_item = work_queue.pop(0)
        lock.release()
        # Do the work and capture the output
        output = process_reference(work_item)
        # Place the output in the output queue
        output_queue.put(output)


def process_reference(reference):
    res = {"id": reference.id}
    doi_metadata = get_doi_metadata(reference.reference)
    if doi_metadata:
        res["doi_metadata"] = doi_metadata
    else:
        debug("DOI Found in Google")
        parsed = ask_google(reference.reference)
        res["parsed"] = parsed
        res["doi_metadata"] = False
    return res


def process_requests(references):

    # Create a shared lock, work queue, and a queue to store outputs
    lock = Lock()
    work_queue = references
    output_queue = Queue()

    # Define the number of threads
    num_threads = 4

    # Create and start worker threads
    threads = []
    for i in range(num_threads):
        thread = Thread(target=worker, args=(work_queue, lock, output_queue))
        thread.start()
        threads.append(thread)

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    # Print the collected results from the output queue
    # print("All work completed. Results:")
    output = []
    while not output_queue.empty():
        output.append(output_queue.get())

    return output


def preprocess(res):

    if not res:
        return ""
    doi = res["doi_metadata"]

    if doi:
        ref = res["doi_metadata"]
    else:
        ref = res["parsed"]

    if not ref:
        return ""
    
    try:
        #Initialize the correct page value
        page_value = ref.get("page") or ref.get("first-page") or ref.get("fpage")
        f_page = ref.get("page-first")
        l_page = ref.get("page-last")

        # Separate the page number and add first, last tag
        if page_value:
            split_page = [part for part in page_value.replace(
                "–", "-").replace("--", "-").split("-") if part.isdigit()]
            if len(split_page) > 1:
                ref["fpage"], ref["lpage"] = split_page
            else:
                ref["fpage"] = page_value
        if f_page:
            ref["fpage"] = f_page
        if l_page:
            ref["lpage"] = l_page

        #Initialize the correct year value
        issued = ref.get("issued", {})
        date_parts = issued.get("date-parts", [])
        if date_parts:
            year = str(date_parts[0][0])
            if len(date_parts[0]) > 1:
                month_index = date_parts[0][1]
                if 1 <= month_index <= 12:
                    month_name = calendar.month_name[month_index][:3]
                    ref["year"] = f"{year}, {month_name}."
                else:
                    ref["year"] = year
            else:
                ref["year"] = year
                
        #Initialize the correct given name
        author = ref.get("author", {})
        if author:
            for given in author:
                given["given_initial"] = "".join(initial[0] for initial in given["given"].split())
    except Exception as e:
        print(f"Error in preprocess (index.py)-file {e}")

    return ordering.add_tag(res, "vancouver")


@app.post("/")
def read_root(inp: Item):
    ress = process_requests(inp.references)
    refe = []
    for res in ress:
        check_id = {}
        check_id["id"] = res["id"]
        check_id["value"] = preprocess(res)
        refe.append(check_id)
    return refe
