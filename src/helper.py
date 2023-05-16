from wikidataintegrator import wdi_core, wdi_login
from login import *


wikibase_prefix = "nounsdev"
wikibase = f"https://{wikibase_prefix}.wikibase.cloud"
sparql = f"https://{wikibase_prefix}.wikibase.cloud/query/sparql"
api_url = f"https://{wikibase_prefix}.wikibase.cloud/w/api.php"


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


def get_items_on_wikibase():
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


# Get existing properties and items in wikibase
properties_in_wikibase = get_properties_in_wikibase()
items_on_wikibase = get_items_on_wikibase()


# Wikibase properties categorized by datatype
item_properties = {"Proposal Type", "Transfer To", "Proposer", "Status"}

# Mapping of relations to their corresponding range
relation_to_range_mapping = {
    "Proposal Type": "Proposal Type",
    "Transfer To": "Individual",
    "Proposer": "Individual",
    "Status": "Status",
}

string_properties = {"Label", "Summary", "Team Name"}
quantity_properties = {
    "Transfer Value",
    "Proposal Budget",
    "Supporter Count",
    "Opposer Count",
    "Quorumvotes",
    "Id",
}
