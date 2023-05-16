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

# Login to Wikidata
wd_login = wdi_login.WDLogin(user=WD_USER, pwd=WD_PASS, mediawiki_api_url=api_url)


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
        if property_datatype == "":
            return None
        new_property = createProperty(
            login=wd_login,
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
        data = [wdi_core.WDItemID(value=wd_item_id_value, prop_nr="P6")]
        wd_item = wdi_core.WDItemEngine(
            wd_item_id="",
            new_item=True,
            data=data,
            mediawiki_api_url=api_url,
            sparql_endpoint_url=sparql,
        )
        wd_item.set_label(label=item_label)
        if item_aliases:
            wd_item.set_aliases(item_aliases, lang="en", append=True)
        wd_item.set_description(description=item_description)
        qid = wd_item.write(wd_login)
        items_on_wikibase[item_label] = qid
        return wd_item
    else:
        return None

    # Create all relation types for wikibase items


for relation_type in set(kg["relation"]):
    create_property_if_not_exists(relation_type)

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

    # Add range types to Wikibase
    for range_type in set(relation_to_range_mapping.values()):
        create_item_if_not_exists(range_type, range_type, "A node type.", "Q1")

    # Add currencies to the Wikibase.
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
