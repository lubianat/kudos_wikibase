import json
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON
from pathlib import Path

HERE = Path(__file__).parent.resolve()
DATA = HERE.parent.joinpath("data").resolve()


# Set up the query
endpoint_url = "https://kudos.wikibase.cloud/query/sparql"
query = """
SELECT ?subject_label ?property_label ?object_label WHERE {
  ?a rdfs:label ?subject_label .
  ?b rdfs:label ?property_label .
  ?c rdfs:label ?object_label .

  ?b wikibase:directClaim ?direct_b .
  ?a ?direct_b ?c .

  FILTER(LANG(?subject_label) = 'en' && LANG(?property_label) = 'en' && LANG(?object_label) = 'en')
}
"""

# Send the request and get the response as JSON
sparql = SPARQLWrapper(endpoint_url)
sparql.setQuery(query)
sparql.setReturnFormat(JSON)
result = sparql.query().convert()

# Extract the data and create a dictionary
data = {}
for binding in result["results"]["bindings"]:
    subject = binding["subject_label"]["value"]
    prop = binding["property_label"]["value"]
    obj = binding["object_label"]["value"]
    if prop != "instance of":
        if subject not in data:
            data[subject] = []
        data[subject].append([obj, prop])

# Save the dictionary as a JSON file
with open(DATA.joinpath("rel_map_from_kudos_wikibase.json"), "w") as f:
    json.dump(data, f, indent=4)
