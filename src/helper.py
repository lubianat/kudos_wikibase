from wikidataintegrator import wdi_core, wdi_login
from login import *


wikibase = "https://kudos.wikibase.cloud"
sparql = "https://kudos.wikibase.cloud/query/sparql"
api_url = "https://kudos.wikibase.cloud/w/api.php"


def createProperty(
    login,
    api_url=api_url,
    sparql_url=sparql,
    label="",
    description="",
    property_datatype="",
):
    localEntityEngine = wdi_core.WDItemEngine.wikibase_item_engine_factory(
        api_url, sparql_url
    )
    item = localEntityEngine(data=[])
    item.set_label(label)
    item.set_description(description)
    new_property = item.write(
        login, entity_type="property", property_datatype=property_datatype
    )
    return new_property


def get_properties_in_wikibase():
    property_lookup = {}

    query = """
    SELECT ?property ?label
    WHERE {
        ?property a wikibase:Property .
        ?property rdfs:label ?label .
        FILTER (LANG(?label) = "en" )
    }"""

    results = wdi_core.WDItemEngine.execute_sparql_query(query=query, endpoint=sparql)

    for result in results["results"]["bindings"]:
        label = result["label"]["value"].split("/")[-1]
        property_lookup[label] = result["property"]["value"].split("/")[-1]

    return property_lookup


def get_nodes_on_kudos_wikibase():
    item_lookup = {}

    query = """
    SELECT ?item ?label WHERE {
      ?item rdfs:label ?label.
      FILTER((LANG(?label)) = "en")
      MINUS { ?item a wikibase:Property } 
    }"""

    results = wdi_core.WDItemEngine.execute_sparql_query(query=query, endpoint=sparql)

    for result in results["results"]["bindings"]:
        label = result["label"]["value"].split("/")[-1]
        item_lookup[label] = result["item"]["value"].split("/")[-1]

    return item_lookup


def get_docs_on_wikibase():
    item_lookup = {}

    query = """
    SELECT ?item ?label WHERE {
      ?item rdfs:label ?label.
      ?item   <https://kudos.wikibase.cloud/prop/direct/P31> <https://kudos.wikibase.cloud/entity/Q1490> . 
      FILTER((LANG(?label)) = "en")
    }"""

    results = wdi_core.WDItemEngine.execute_sparql_query(query=query, endpoint=sparql)

    for result in results["results"]["bindings"]:
        label = result["label"]["value"].split("/")[-1]
        item_lookup[label] = result["item"]["value"].split("/")[-1]

    return item_lookup


def get_doc_id2proposals_dict():
    item_lookup = {}

    query = """
    SELECT ?item ?label ?doc_id WHERE {
      ?item rdfs:label ?label.
      <https://kudos.wikibase.cloud/entity/P31> wikibase:directClaim ?p . 
      ?item ?p <https://kudos.wikibase.cloud/entity/Q1488> . 
      ?item   <https://kudos.wikibase.cloud/prop/direct/P610> ?doc_item . 
       ?doc_item   <https://kudos.wikibase.cloud/prop/direct/P594> ?doc_id . 
      FILTER((LANG(?label)) = "en")
    }"""

    results = wdi_core.WDItemEngine.execute_sparql_query(query=query, endpoint=sparql)

    for result in results["results"]["bindings"]:
        doc_id = result["doc_id"]["value"]
        item_lookup[doc_id] = result["item"]["value"].split("/")[-1]

    return item_lookup
