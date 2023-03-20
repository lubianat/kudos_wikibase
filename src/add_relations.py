from cmath import exp
import json
from pathlib import Path
from helper import *
from login import *
import time

HERE = Path(__file__).parent.resolve()
DATA = HERE.parent.joinpath("data").resolve()

# Define the knowledge graph
base_kg = json.loads(DATA.joinpath("index_kg.json").read_text())
kg = base_kg["docstore"]["docs"]["a7ac82a6-f7e8-4435-9622-f1bca3fe2315"]["rel_map"]

properties_in_wikibase = get_properties_in_wikibase()
wd_login = wdi_login.WDLogin(user=WD_USER, pwd=WD_PASS, mediawiki_api_url=api_url)

nodes_on_wikibase = get_nodes_on_kudos_wikibase()

# loop through each entity in the KG
for entity in kg:
    try:
        # get the Wikibase ID of the subject node
        subject = nodes_on_wikibase[entity]
        # loop through each relation for the current entity
        for relation in kg[entity]:
            # get the Wikibase ID of the object node
            value = nodes_on_wikibase[relation[0]]
            # get the property ID of the current relation
            prop_nr = properties_in_wikibase[relation[1]]
            # create a statement for the current relation
            relation_statement = wdi_core.WDItemID(value=value, prop_nr=prop_nr)
            # get the existing data for the item
            item = wdi_core.WDItemEngine(
                wd_item_id=subject,
                new_item=False,
                mediawiki_api_url=api_url,
                sparql_endpoint_url=sparql,
            )
            item.get_wd_json_representation()
            # add the statement to the item
            item.update([relation_statement])
            item.write(login=wd_login)
            time.sleep(0.2)
    except KeyError as e:
        print(e)
        pass
