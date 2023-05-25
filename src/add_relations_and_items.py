# KEY ASSUMPTION OF LABEL UNIQUENESS

import pandas as pd
from pathlib import Path
from helper import *
from login import *

# Resolve path to the data
HERE = Path(__file__).parent.resolve()
DATA = HERE.parent.joinpath("data").resolve()

# Read the KG data
kg = pd.read_csv(DATA.joinpath("KG_view1.csv"))
# kg["object"] = [a.split("-")[0].strip() for a in kg["object"]]


# Add the vote weight property to be used as qualifier
if "Vote Weight" not in properties_in_wikibase.keys():
    new_property = createProperty(
        label="Vote Weight",
        description="Qualifier for 'Supported By' and 'Opposed By' properties. ",
        property_datatype="quantity",
    )
# Add node types to Wikibase
create_item_if_not_exists(
    "Proposal",
    "Proposal",
    "The concept of a proposal in the Nouns platform.",
    "Q1",
    ["Nouns Proposal"],
)
create_item_if_not_exists(
    "Currency",
    "Currency",
    "A currency used for transactions and/or proposals in Nouns Includes ETH, USDC and USD.",
    "Q1",
    ["monetary standard"],
)

relations = set(kg["relation"])

for relation_type in relations:
    create_property_if_not_exists(relation_type)

    # Add range types to Wikibase
    for range_type in set(relation_to_range_mapping.values()):
        create_item_if_not_exists(range_type, range_type, "A node type.", "Q1")

    proposals = set(kg["subject"])
    for proposal in proposals:
        try:
            if proposal not in items_on_wikibase.keys():
                create_item_if_not_exists(
                    proposal,
                    proposal,
                    "A Nouns proposal.",
                    items_on_wikibase["Proposal"],
                )
        except:
            continue

    # Add items that play the role of objects in the Wikibase.
    for property, range in relation_to_range_mapping.items():
        kg_subset = kg[kg["relation"] == property]
        objects = set(kg_subset["object"])
        for object in objects:
            if object not in items_on_wikibase.keys():
                create_item_if_not_exists(
                    object, object, range, items_on_wikibase[range]
                )

    # Add currencies to the Wikibase.
    currency_list = ["ETH", "USDC", "USD"]
    for currency in currency_list:
        if currency not in items_on_wikibase.keys():
            create_item_if_not_exists(
                currency, currency, "A currency.", items_on_wikibase["Currency"]
            )
