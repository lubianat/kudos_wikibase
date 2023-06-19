import pandas as pd
from pathlib import Path
from helper import *
from login import *

# Resolve path to the data
HERE = Path(__file__).parent.resolve()
DATA = HERE.parent.joinpath("data").resolve()


def add_property_if_not_exists(properties_in_wikibase, label, description, datatype):
    if label not in properties_in_wikibase.keys():
        new_property = createProperty(
            label=label, description=description, property_datatype=datatype
        )


def add_node_types():
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


def add_relation_types(kg):
    relations = set(kg["relation"])
    for relation_type in relations:
        create_property_if_not_exists(relation_type)


def add_range_types(relation_to_range_mapping):
    for range_type in set(relation_to_range_mapping.values()):
        create_item_if_not_exists(range_type, range_type, "A node type.", "Q1")


def add_proposals(kg, items_on_wikibase):
    proposals = set(kg["subject"])
    for proposal in proposals:
        if proposal not in items_on_wikibase.keys():
            create_item_if_not_exists(
                proposal, proposal, "A Nouns proposal.", items_on_wikibase["Proposal"]
            )


def add_objects(kg, relation_to_range_mapping, items_on_wikibase):
    for property, range in relation_to_range_mapping.items():
        print(property)
        kg_subset = kg[kg["relation"] == property]
        objects = set(kg_subset["object"])
        for object in objects:
            if object not in items_on_wikibase.keys():
                create_item_if_not_exists(
                    object, object, range, items_on_wikibase[range]
                )


def add_inverse_properties(inverse_properties, properties_in_wikibase, login_instance):
    properties_in_wikibase["Inverse Property"] = "P61"
    properties_in_wikibase["Abstained By"] = "P58"
    for relation_type, inverse in inverse_properties.items():
        if inverse not in properties_in_wikibase.keys():
            wbi = WikibaseIntegrator(login=login_instance)
            prop = wbi.property.new(datatype="wikibase-item")
            prop.labels.set(language="en", value=inverse)
            prop.descriptions.set(language="en", value=f"inverse of {relation_type}")
            data = [
                Property(
                    value=properties_in_wikibase[relation_type],
                    prop_nr=properties_in_wikibase["Inverse Property"],
                )
            ]
            prop.claims.add(data)
            new_property = prop.write()


def main():
    # Read the KG data

    add_property_if_not_exists(
        properties_in_wikibase,
        "Vote Weight",
        "Qualifier for 'Supported By' and 'Opposed By' properties. ",
        "quantity",
    )
    add_property_if_not_exists(
        properties_in_wikibase,
        "Inverse Property",
        "The inverse property in the graph. ",
        "property",
    )

    kg = pd.read_csv(DATA.joinpath("KG_view1.csv"))

    add_node_types()
    add_relation_types(kg)
    add_range_types(relation_to_range_mapping)
    add_proposals(kg, items_on_wikibase)
    add_objects(kg, relation_to_range_mapping, items_on_wikibase)
    add_inverse_properties(inverse_properties, properties_in_wikibase, login_instance)

    kg = pd.read_csv(DATA.joinpath("KG_view2.csv"))

    add_node_types()
    add_relation_types(kg)
    add_range_types(relation_to_range_mapping)
    add_proposals(kg, items_on_wikibase)
    add_objects(kg, relation_to_range_mapping, items_on_wikibase)
    add_inverse_properties(inverse_properties, properties_in_wikibase, login_instance)


if __name__ == "__main__":
    main()
