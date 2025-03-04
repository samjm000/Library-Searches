import requests
import xml.etree.ElementTree as ET
import pandas as pd

base_URL = "http://export.arxiv.org/api/query?"

search_query = (
    '(all:"large language model" OR all:"LLM" OR all:"GPT" OR all:"transformer" OR all:"BERT")'
    'AND (all:"knowledge graph" OR all:"QLoRA" OR all:"retrieval augmented generation" OR all:"RAG" OR all:"chain of thought" OR all:"prompt" OR all:"engineering")'
    'AND (all:"EHR" OR all:"electronic health record" OR all:"EMR" OR all:"electronic medical record" OR all:"clinical" OR all:"unstructured data")'
    'AND (all:"cancer" OR all:"oncology" OR all:"medical")'
)

def fetch_arxiv_results(search_query, base_URL, max_results_per_query=100, total_results=500):
    data = []
    start = 0
    total_entries = 0

    while start < total_results:
        try:
            encoded_query = requests.utils.quote(search_query)
            full_url = f"{base_URL}search_query={encoded_query}&start={start}&max_results={max_results_per_query}"
            all_results = requests.get(full_url)
            print(f"Fetching results from: {full_url}")
            
            root_element_tree = ET.fromstring(all_results.content)
            entries = root_element_tree.findall("{http://www.w3.org/2005/Atom}entry")
            print(f"Entries found: {len(entries)}")

            if len(entries) == 0:
                print("No more entries found.")
                break

            for entry in entries:
                title = entry.find("{http://www.w3.org/2005/Atom}title").text if entry.find("{http://www.w3.org/2005/Atom}title") is not None else "No Title"
                summary = entry.find("{http://www.w3.org/2005/Atom}summary").text if entry.find("{http://www.w3.org/2005/Atom}summary") is not None else "No Summary"
                published = entry.find("{http://www.w3.org/2005/Atom}published").text if entry.find("{http://www.w3.org/2005/Atom}published") is not None else "No Date"

                author_list = entry.findall("{http://www.w3.org/2005/Atom}author")
                authors = ", ".join([author.find("{http://www.w3.org/2005/Atom}name").text for author in author_list]) if author_list else "No Authors"

                link = entry.find("{http://www.w3.org/2005/Atom}link[@title='pdf']")
                pdf_link = link.get('href') if link is not None else "No PDF Link"

                data.append([title, summary, published, authors, pdf_link])

            total_entries += len(entries)
            print(f"Fetched {total_entries} results so far.")
            save_to_csv(data, filename=f"arxiv_results_{total_entries}.csv")
            save_to_bibtex(data, filename=f"arxiv_results_{total_entries}.bib")

            start += max_results_per_query

        except Exception as e:
            print(f"An error occurred: {e}")
            break

    print(f"Total number of results found: {total_entries}")
    return data

def save_to_csv(data, filename="arxiv_results.csv"):
    df = pd.DataFrame(data, columns=["Title", "Summary", "Published Date", "Authors", "PDF Link"])
    df.to_csv(filename, index=False)
    print(f"Exported {len(df)} papers to {filename}")

def save_to_bibtex(data, filename="arxiv_results.bib"):
    with open(filename, 'w', encoding='utf-8') as f:
        for entry in data:
            bibtex_entry = f"""@article{{arxiv:{entry[0].replace(' ', '_')},
    title = {{{entry[0]}}},
    author = {{{entry[3]}}},
    abstract = {{{entry[1]}}},
    year = {{{entry[2][:4]}}},
    month = {{{entry[2][5:7]}}},
    url = {{{entry[4]}}},
    journal = {{arXiv preprint}}
}}

"""
            f.write(bibtex_entry)
    print(f"Exported {len(data)} papers to {filename}")

arxiv_data = fetch_arxiv_results(search_query, base_URL, max_results_per_query=100, total_results=500)
