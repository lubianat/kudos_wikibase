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
    for proposal in proposals:
        kg_subset = kg[kg["subject"] == proposal]

        proposal_qid = items_on_wikibase[proposal]
        wbi = WikibaseIntegrator(login=login_instance)

        item = wbi.item.get(entity_id=proposal_qid)

        data = []
        for i, row in kg_subset.iterrows():
            property_name = row["relation"]
            object_name = row["object"]
            if pd.isna(object_name):
                continue

            if property_name in item_properties:
                if property_name in {"Supported By", "Opposed By"}:
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
                            prop_nr=properties_in_wikibase[property_name],
                            qualifiers=new_qualifiers,
                        )
                    )
                else:
                    data.append(
                        Item(
                            value=items_on_wikibase[object_name],
                            prop_nr=properties_in_wikibase[property_name],
                        )
                    )

            elif property_name in string_properties:
                if "\n" in object_name:
                    object_name = object_name.replace("\n", " --- ")
                data.append(
                    String(
                        value=object_name, prop_nr=properties_in_wikibase[property_name]
                    )
                )
            elif property_name in date_properties:
                time_struct = strptime(row["object"], "%Y-%m-%d")

                wikidata_time = strftime("+%Y-%m-%dT00:00:00Z", time_struct)
                data.append(Time(wikidata_time, prop_nr="P23"))
            elif property_name in quantity_properties:
                if property_name in {
                    "Supporter Count",
                    "Opposer Count",
                    "Quorumvotes",
                    "Id",
                }:
                    data.append(
                        Quantity(
                            amount=int(object_name),
                            prop_nr=properties_in_wikibase[property_name],
                        )
                    )
                if property_name == "Id":
                    data.append(
                        URL(
                            value=f"https://nouns.wtf/vote/{str(object_name)}",
                            prop_nr="P21",  # Nouns URL property
                        )
                    )

            else:
                print(property_name)
            continue
        item.claims.add(data, action_if_exists=ActionIfExists.REPLACE_ALL)
        item.write()
