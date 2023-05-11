import json
from pathlib import Path
from helper import *
from login import *

HERE = Path(__file__).parent.resolve()
DATA = HERE.parent.joinpath("data").resolve()

import pandas as pd

kg = pd.read_csv(DATA.joinpath("KG_20230511.csv"))


relations = set(kg["relation"])

print(relations)

ignored_for_now = {
    "executioneta",
    "clone to",
    "clone value",
}

item_properties = {
    "proposal type",
    "transfer to",
    "deposit to",
    "status",
    "previous proposal",
    "proposer",
    "purchase to",
    "team",
}

string_properties = {"proposal summary", "proposal"}

quantity_properties = {
    "proposal number" "transfer value",
    "deposit value",
    "purchase value",
    "proposal budget" "opposed by",
    "voted by",
    "quorumvotes" "team size",
}
date_properties = {
    "proposal deadline",
}


# Define a set to hold the relation types and nodes
relation_types = set()
nodes = set()

# Loop through each entity in the knowledge graph
for entity in kg:
    # Loop through each relation in the entity's list of relations
    nodes.add(entity)
    for relation in kg[entity]:
        # Add the relation type to the set
        relation_types.add(relation[1])
        nodes.add(relation[0])

relation_types = list(set(relation_types))
nodes = list(set(nodes))


# Print the set of relation types and nodes
print("Relation types: ", relation_types)
print("Nodes: ", nodes)


properties_in_wikibase = get_properties_in_wikibase()
wd_login = wdi_login.WDLogin(user=WD_USER, pwd=WD_PASS, mediawiki_api_url=api_url)

for relation_type in relation_types:
    if relation_type not in properties_in_wikibase.keys():
        print(relation_type)
        new_property = createProperty(
            login=wd_login,
            label=relation_type,
            description="machine-generated property",
            property_datatype="wikibase-item",
        )
        print(f"Property {new_property} created successfully.")

    else:
        pass


instance_of_node_statement = wdi_core.WDItemID(value="Q1", prop_nr="P31")
nodes_on_wikibase = get_nodes_on_kudos_wikibase()

for node in nodes:
    if node not in nodes_on_wikibase.keys():
        data = []
        data.append(instance_of_node_statement)
        wd_item = wdi_core.WDItemEngine(
            wd_item_id="",
            new_item=True,
            data=data,
            mediawiki_api_url=api_url,
            sparql_endpoint_url=sparql,
        )
        wd_item.set_label(label=node)
        wd_item.set_description(description="machine-generated item")
        try:
            new_item = wd_item.write(wd_login)
            print(new_item)
        except Exception as e:  # Handle the exception here
            print(f"Error: {e}")
