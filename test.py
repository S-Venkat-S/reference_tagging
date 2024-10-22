from scholarly import scholarly

# Retrieve the author's data, fill-in, and print
# Get an iterator for the author results
search_query = scholarly.search_keyword('Zhao, X. (2021). Challenges and barriers in intercultural communication between patients with immigration backgrounds and health professionals: a systematic literature review. Health Communication, 38(4), 824-833.')
# Retrieve the first result from the iterator
print(dir(search_query))
print(next(search_query))
