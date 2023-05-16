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

proposals = set(kg["subject"])

for proposal in proposals:
    if proposal != "Proposal 280":
        continue
    kg_subset = kg[kg["subject"] == proposal]
    proposal_qid = items_on_wikibase[proposal]
    item = wdi_core.WDItemEngine(
        wd_item_id=proposal_qid,
        new_item=False,
        mediawiki_api_url=api_url,
        sparql_endpoint_url=sparql,
    )
    item.get_wd_json_representation()

    data = []
    for i, row in kg_subset.iterrows():
        property_name = row["relation"]
        object_name = row["object"]

        if property_name in item_properties:
            data.append(
                wdi_core.WDItemID(
                    value=items_on_wikibase[object_name],
                    prop_nr=properties_in_wikibase[property_name],
                )
            )

        elif property_name in string_properties:
            data.append(
                wdi_core.WDString(
                    value=object_name, prop_nr=properties_in_wikibase[property_name]
                )
            )
        elif property_name in quantity_properties:
            if property_name in {
                "Supporter Count",
                "Opposer Count",
                "Quorumvotes",
                "Id",
            }:
                data.append(
                    wdi_core.WDQuantity(
                        value=int(object_name),
                        prop_nr=properties_in_wikibase[property_name],
                    )
                )
            if property_name == "Id":
                data.append(
                    wdi_core.WDUrl(
                        value=f"https://nouns.wtf/vote/{str(object_name)}",
                        prop_nr="P21",  # Nouns URL property
                    )
                )

        else:
            print(property_name)
        continue
    item.update(data)
    item.write(login=wd_login)
