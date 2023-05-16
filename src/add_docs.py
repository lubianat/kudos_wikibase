import json
from pathlib import Path
from helper import *
from login import *

HERE = Path(__file__).parent.resolve()
DATA = HERE.parent.joinpath("data").resolve()

# Define the knowledge graph
base_kg = json.loads(DATA.joinpath("gpt_4_test.json_no_dubli_mini.json").read_text())
docs = base_kg["docstore"]["docs"]
wd_login = wdi_login.WDLogin(user=WD_USER, pwd=WD_PASS, mediawiki_api_url=api_url)


docs_on_wikibase = get_docs_on_wikibase()
instance_of_doc_statement = wdi_core.WDItemID(value="Q1490", prop_nr="P31")


proposals = {}
proposal2date = {}
for doc in docs:
    print(doc)
    doc_info = docs[doc]

    doc_proposal_number = doc_info["extra_info"]["doc_src"]
    date = doc_info["extra_info"]["date"]
    if doc_proposal_number not in proposals.keys():
        proposals[doc_proposal_number] = []
        proposal2date[doc_proposal_number] = date
    proposals[doc_proposal_number].append(doc)
    if doc not in docs_on_wikibase.keys():
        data = []

        doc_number_statement = wdi_core.WDString(
            value=doc_proposal_number, prop_nr="P592"
        )
        date_of_doc_statement = wdi_core.WDEDTF(value=date, prop_nr="P593")
        doc_id_statement = wdi_core.WDString(value=doc, prop_nr="P594")

        doc_id = doc
        data.extend(
            [
                instance_of_doc_statement,
                doc_number_statement,
                date_of_doc_statement,
                doc_id_statement,
            ]
        )

        try:
            new_item = wd_item.write(wd_login)
            print(new_item)
        except Exception as e:  # Handle the exception here
            print(f"Error: {e}")


docs_on_wikibase = get_docs_on_wikibase()

instance_of_proposal_statement = wdi_core.WDItemID(value="Q1488", prop_nr="P31")

for proposal, values in proposals.items():
    data = []

    date_of_proposal_statement = wdi_core.WDEDTF(
        value=proposal2date[proposal], prop_nr="P611"
    )

    data.extend(
        [
            instance_of_proposal_statement,
            date_of_proposal_statement,
        ]
    )
    for doc_id in values:
        doc_item = docs_on_wikibase[doc_id]
        proposal_doc_id_statement = wdi_core.WDItemID(value=doc_item, prop_nr="P610")
        data.append(proposal_doc_id_statement)

    wd_item = wdi_core.WDItemEngine(
        wd_item_id="",
        new_item=True,
        data=data,
        mediawiki_api_url=api_url,
        sparql_endpoint_url=sparql,
    )
    wd_item.set_label(label=doc_proposal_number)
    wd_item.set_description(description="proposal")
    try:
        new_item = wd_item.write(wd_login)
        print(new_item)
    except Exception as e:  # Handle the exception here
        print(f"Error: {e}")
