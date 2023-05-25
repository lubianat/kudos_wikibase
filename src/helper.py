from login import *
from wikibaseintegrator import wbi_login, WikibaseIntegrator
from wikibaseintegrator.wbi_config import config as wbi_config
from wikibaseintegrator import wbi_helpers
from wikibaseintegrator.datatypes import Item
from wikibaseintegrator.wbi_exceptions import ModificationFailed

wikibase_prefix = "nounsdev"
wbi_config["MEDIAWIKI_API_URL"] = f"https://{wikibase_prefix}.wikibase.cloud/w/api.php"
wbi_config[
    "SPARQL_ENDPOINT_URL"
] = f"https://{wikibase_prefix}.wikibase.cloud/query/sparql"
wbi_config["WIKIBASE_URL"] = f"https://{wikibase_prefix}.wikibase.cloud"

wbi_config["USER_AGENT"] = "NounsWikibaseBot"


login_instance = wbi_login.Clientlogin(user=WD_USER, password=WD_PASS)


def createProperty(
    label="",
    description="",
    property_datatype="",
):
    wbi = WikibaseIntegrator(login=login_instance)
    prop = wbi.property.new(datatype=property_datatype)
    prop.labels.set(language="en", value=label)
    prop.descriptions.set(language="en", value=description)
    new_property = prop.write()

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

    results = wbi_helpers.execute_sparql_query(
        query=query, endpoint=wbi_config["SPARQL_ENDPOINT_URL"]
    )

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

    results = wbi_helpers.execute_sparql_query(
        query=query, endpoint=wbi_config["SPARQL_ENDPOINT_URL"]
    )

    for result in results["results"]["bindings"]:
        label = result["label"]["value"].split("/")[-1]
        item_lookup[label] = result["item"]["value"].split("/")[-1]

    return item_lookup


# Get existing properties and items in wikibase
properties_in_wikibase = get_properties_in_wikibase()
items_on_wikibase = get_items_on_wikibase()


# Wikibase properties categorized by datatype
item_properties = {
    "Proposal Type",
    "Transfer To",
    "Proposer",
    "Status",
    "Previous Proposal",
    "Supported By",
    "Opposed By",
}

# Mapping of relations to their corresponding range
relation_to_range_mapping = {
    "Proposal Type": "Proposal Type",
    "Transfer To": "Individual",
    "Proposer": "Individual",
    "Supported By": "Individual",
    "Opposed By": "Individual",
    "Previous Proposal": "Proposal",
    "Status": "Status",
}

date_properties = {"ExecutionETA", "Proposal Submission Date"}
string_properties = {"Label", "Summary", "Team Name"}
quantity_properties = {
    "Transfer Value",
    "Proposal Duration in Months",
    "Proposal Budget",
    "Supporter Count",
    "Opposer Count",
    "Quorumvotes",
    "Id",
    "Team Size",
}


# Create property in wikibase if it doesn't exist
def create_property_if_not_exists(property_name):
    if property_name not in properties_in_wikibase.keys():
        property_datatype = ""
        if property_name in item_properties:
            property_datatype = "wikibase-item"
        if property_name in string_properties:
            property_datatype = "string"
        if property_name in quantity_properties:
            property_datatype = "quantity"
        if property_name in date_properties:
            property_datatype = "time"
        if property_datatype == "":
            print(f"{property_name} not in any list")
            return None
        new_property = createProperty(
            label=property_name,
            description="machine-generated property",
            property_datatype=property_datatype,
        )
        print(f"Property {new_property} created successfully.")
        return new_property
    else:
        return None


# Create item in wikibase if it doesn't exist
def create_item_if_not_exists(
    item_name, item_label, item_description, wd_item_id_value, item_aliases=None
):
    if item_name not in items_on_wikibase.keys():
        wbi = WikibaseIntegrator(login=login_instance)

        data = [Item(value=wd_item_id_value, prop_nr="P6")]
        # Create a new item
        item = wbi.item.new()
        item.labels.set(language="en", value=item_label)
        item.descriptions.set(language="en", value=item_description)
        if item_aliases:
            item.aliases.set(language="en", values=[item_aliases])
        item.claims.add(data)
        try:
            item.write()
        except ModificationFailed as e:
            print(e)
            pass
    else:
        return None
