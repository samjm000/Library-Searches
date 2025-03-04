import requests
import xml.etree.ElementTree as ET
import pandas as pd

# Base API URL
base_URL = "http://export.arxiv.org/api/query?"

#update, 
# Modify search query to match ArXiv API requirements
search_query = (
    '(all:"large language model" OR all:"LLM" OR all:"GPT" OR all:"transformer model" OR all:"BERT")'
    'AND (all:"knowledge graph" OR all:"QLoRA" OR all:"retrieval augmented generation" OR all:"RAG" OR all:"chain of thought" OR all:"prompt" OR all:"engineering")'
    'AND (all:"EHR" OR all:"electronic health record" OR all:"EMR" OR all:"electronic medical record" OR all:"clinical" OR all:"unstructured data")'
    'AND (all:"cancer" OR all:"oncology" OR all:"medical")'
)
def fetch_arxiv_results(search_query, base_URL):
    try:
        # Encode the search query
        encoded_query = requests.utils.quote(search_query)
        
        # Construct full URL
        full_url = f"{base_URL}search_query={encoded_query}&start=0&max_results=500"
        
        # Fetch results
        all_results = requests.get(full_url)
        root_element_tree = ET.fromstring(all_results.content)

        entries = root_element_tree.findall("{http://www.w3.org/2005/Atom}entry")
        data = []

        for entry in entries:
            # Add error handling for missing elements
            title = entry.find("{http://www.w3.org/2005/Atom}title").text if entry.find("{http://www.w3.org/2005/Atom}title") is not None else "No Title"
            summary = entry.find("{http://www.w3.org/2005/Atom}summary").text if entry.find("{http://www.w3.org/2005/Atom}summary") is not None else "No Summary"
            published = entry.find("{http://www.w3.org/2005/Atom}published").text if entry.find("{http://www.w3.org/2005/Atom}published") is not None else "No Date"
            
            author_list = entry.findall("{http://www.w3.org/2005/Atom}author")
            authors = ", ".join([author.find("{http://www.w3.org/2005/Atom}name").text for author in author_list]) if author_list else "No Authors"

            # Add link to the paper
            link = entry.find("{http://www.w3.org/2005/Atom}link[@title='pdf']")
            pdf_link = link.get('href') if link is not None else "No PDF Link"

            data.append([title, summary, published, authors, pdf_link])

        return data

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def save_to_csv(data, filename="arxiv_results.csv"):
    df = pd.DataFrame(data, columns=["Title", "Summary", "Published Date", "Authors", "PDF Link"])
    df.to_csv(filename, index=False)
    print(f"Exported {len(df)} papers to {filename}")

# Export to BibTeX for Zotero
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

# Run the fetch and save process
arxiv_data = fetch_arxiv_results(search_query, base_URL)
save_to_csv(arxiv_data)
save_to_bibtex(arxiv_data)