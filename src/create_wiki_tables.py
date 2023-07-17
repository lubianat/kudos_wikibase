from wikibaseintegrator import wbi_helpers
from datetime import datetime


def create_wiki_table(wikibase_prefix, query):
    # Run the query
    results = wbi_helpers.execute_sparql_query(
        query, endpoint=f"https://{wikibase_prefix}.wikibase.cloud/query/sparql"
    )

    # Retrieve the header names from the results
    headers = results["head"]["vars"]

    # Begin the table in wiki markup
    wiki_table = '{| class="wikitable"\n|-\n! ' + " !! ".join(
        [f"{header.capitalize()}" for header in headers]
    )

    for result in results["results"]["bindings"]:
        # For each row, add a line to the table
        wiki_table += f"\n|-\n" + " ".join(
            [f"|| {result[header]['value']}" for header in headers]
        )

    # End the table in wiki markup
    wiki_table += "\n|}"

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # Begin the table in wiki markup, including the time of last update
    wiki_table = f"''This table was last updated on {now} (UTC).''\n" + wiki_table
    return wiki_table


wikibase_prefix = "nounsdev"
query = """
    SELECT ?item ?itemLabel ?nouns_url WHERE {
        ?item <https://nounsdev.wikibase.cloud/prop/direct/P6> <https://nounsdev.wikibase.cloud/entity/Q2> . 
        ?item <https://nounsdev.wikibase.cloud/prop/direct/P15> ?id . 
        ?item <https://nounsdev.wikibase.cloud/prop/direct/P21> ?nouns_url . 
        ?item rdfs:label ?itemLabel
    }
    ORDER BY ?id
"""
# Create wiki table
wiki_table = create_wiki_table(wikibase_prefix, query)

# Write wiki table to file
with open("proposals.txt", "w") as f:
    f.write(wiki_table)

query = """
SELECT ?item ?itemLabel WHERE {
    <https://nounsdev.wikibase.cloud/entity/P6> wikibase:directClaim ?p .
    ?item ?p <https://nounsdev.wikibase.cloud/entity/Q8> . 
    ?item rdfs:label ?itemLabel
}
ORDER BY ?itemLabel
"""
# Create wiki table
wiki_table = create_wiki_table(wikibase_prefix, query)

# Write wiki table to file
with open("individuals.txt", "w") as f:
    f.write(wiki_table)
