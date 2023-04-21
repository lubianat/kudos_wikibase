import json
import time
from pathlib import Path
from helper import *
from login import *


class KnowledgeGraph:
    def __init__(self):
        self.base_kg = self.load_knowledge_graph()
        self.kg = self.base_kg["index_struct"]["__data__"]["rel_map"]
        self.table_of_doc_ids = self.base_kg["index_struct"]["__data__"]["table"]
        self.properties_in_wikibase = get_properties_in_wikibase()
        self.wd_login = wdi_login.WDLogin(
            user=WD_USER, pwd=WD_PASS, mediawiki_api_url=api_url
        )
        self.nodes_on_wikibase = get_nodes_on_kudos_wikibase()
        self.docs_on_wikibase = get_docs_on_wikibase()
        self.doc_id2proposal = get_doc_id2proposals_dict()

    @staticmethod
    def load_knowledge_graph():
        HERE = Path(__file__).parent.resolve()
        DATA = HERE.parent.joinpath("data").resolve()
        base_kg = json.loads(
            DATA.joinpath("gpt_4_test.json_no_dubli_mini.json").read_text()
        )
        return base_kg

    def update_wikibase_item(self, subject, value, prop_nr, references):
        item = wdi_core.WDItemEngine(
            wd_item_id=subject,
            new_item=False,
            mediawiki_api_url=api_url,
            sparql_endpoint_url=sparql,
        )
        item.get_wd_json_representation()
        relation_statement = wdi_core.WDItemID(
            value=value, prop_nr=prop_nr, references=references
        )
        item.update([relation_statement])
        item.write(login=self.wd_login)
        print("ok")
        time.sleep(0.2)

    def process_kg_entities(self):
        for entity in self.kg:
            try:
                subject = self.nodes_on_wikibase[entity]

                for relation in self.kg[entity]:
                    value = self.nodes_on_wikibase[relation[0]]

                    for doc_id in self.docs_on_wikibase:
                        subject_doc_ids = self.table_of_doc_ids[entity] --
                        object_doc_ids = self.table_of_doc_ids[relation[0]]

                        if doc_id in subject_doc_ids and doc_id in object_doc_ids:
                            reference_doc = wdi_core.WDItemID(
                                value=self.docs_on_wikibase[doc_id],
                                prop_nr="P609",
                                is_reference=True,
                            )
                            reference_proposal = wdi_core.WDItemID(
                                value=self.doc_id2proposal[doc_id],
                                prop_nr="P612",
                                is_reference=True,
                            )
                            prop_nr = self.properties_in_wikibase[relation[1]]
                            references = [[reference_doc, reference_proposal]]
                            self.update_wikibase_item(
                                subject, value, prop_nr, references
                            )
            except KeyError as e:
                print(f"KeyError: {e}")


def main():
    kg = KnowledgeGraph()
    kg.process_kg_entities()


if __name__ == "__main__":
    main()
