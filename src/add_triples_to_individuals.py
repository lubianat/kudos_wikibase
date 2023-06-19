import pandas as pd
from pathlib import Path
from helper import *
from login import *
from time import strptime, strftime
from wikibaseintegrator.datatypes import Item, String, Time, Quantity, URL
from wikibaseintegrator.wbi_enums import ActionIfExists
from wikibaseintegrator.models import Qualifiers

# Resolve path to the data
HERE = Path(__file__).parent.resolve()
DATA = HERE.parent.joinpath("data").resolve()

# Read the KG data
kg1 = pd.read_csv(DATA.joinpath("KG_view1.csv"))
kg2 = pd.read_csv(DATA.joinpath("KG_view2.csv"))

kg_list = [kg1, kg2]
proposals = set(kg1["subject"])

for kg in kg_list:
    individuals = set([a for a in kg["object"] if str(a).startswith("0x")])

    for individual in individuals:
        kg_subset = kg[kg["object"] == individual]
        wbi = WikibaseIntegrator(login=login_instance)
        individual_qid = items_on_wikibase[individual]

        item = wbi.item.get(entity_id=individual_qid)

        data = []
        for i, row in kg_subset.iterrows():
            property_name = row["relation"]
            object_name = row["subject"]
            if property_name in item_properties:
                if property_name in inverse_properties.keys():
                    if property_name != "Proposer":
                        new_qualifiers = Qualifiers()
                        new_qualifiers.add(
                            Quantity(
                                prop_nr=properties_in_wikibase["Vote Weight"],
                                amount=int(row["weight"]),
                            )
                        )
                        data.append(
                            Item(
                                value=items_on_wikibase[object_name],
                                prop_nr=properties_in_wikibase[
                                    inverse_properties[property_name]
                                ],
                                qualifiers=new_qualifiers,
                            )
                        )
                    else:
                        data.append(
                            Item(
                                value=items_on_wikibase[object_name],
                                prop_nr=properties_in_wikibase[
                                    inverse_properties[property_name]
                                ],
                            )
                        )

            else:
                print(property_name)
            continue
        item.claims.add(data, action_if_exists=ActionIfExists.REPLACE_ALL)
        item.write()
