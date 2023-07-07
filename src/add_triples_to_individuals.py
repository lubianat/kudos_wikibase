import pandas as pd
from pathlib import Path
from helper import *
from login import *
from time import strptime, strftime
from wikibaseintegrator.datatypes import Item, String, Time, Quantity, URL
from wikibaseintegrator.wbi_enums import ActionIfExists
from wikibaseintegrator.models import Qualifiers
from wikibaseintegrator.wbi_exceptions import MissingEntityException, ModificationFailed

# Resolve path to the data
HERE = Path(__file__).parent.resolve()
DATA = HERE.parent.joinpath("data").resolve()

# Read the KG data
kg1 = pd.read_csv(DATA.joinpath("KG_view1.csv"))
kg2 = pd.read_csv(DATA.joinpath("KG_view2.csv"))

kg_list = [kg1, kg2]
proposals = set(kg1["subject"])
properties_in_wikibase["Vote Reason"] = "P63"

for kg in kg_list:
    individuals = set([a for a in kg["object"] if str(a).startswith("0x")])

    for individual in individuals:
        if individual == "0xbobatea":
            continue
        kg_subset = kg[kg["object"] == individual]
        wbi = WikibaseIntegrator(login=login_instance)
        individual_qid = items_on_wikibase[individual]

        try:
            item = wbi.item.get(entity_id=individual_qid)
        except MissingEntityException as e:
            print(e)
            pass
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
                        if row["reason"] != "Reason not provided":
                            reason = row["reason"]
                            if len(reason) > 2499:
                                reason = reason[0:2400]
                            new_qualifiers.add(
                                String(
                                    prop_nr=properties_in_wikibase["Vote Reason"],
                                    value=reason.replace("\n", "-")
                                    .replace('"', "")
                                    .strip(),
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
        try:
            item.write()
        except ModificationFailed as e:
            print(e)
            pass
