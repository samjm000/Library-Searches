import requests
import xml.etree.ElementTree as ET
import time

# Base API URL
base_URL = "http://export.arxiv.org/api/query?"

# Corrected search query
search_query = (
    '(all:"large language model" OR all:"LLM" OR all:"GPT" OR all:"transformer" OR all:"BERT")'
    'AND (all:"Knowledge Graph" OR all:"QLoRA" OR all:"retrieval augmented generation" OR all:"RAG" OR all:"Chain of Thought" OR all:"Prompt" OR all:"Engineering")'
    'AND (all:"EHR" OR all:"Electronic Health Record" OR all:"EMR" OR all:"Electronic Medical Record" OR all:"Clinical" OR all:"unstructured data")'
    'AND (all:"cancer" OR all:"oncology" OR all:"Medical")'
)


def fetch_arxiv_by_date(base_URL, search_query, start_date, end_date, max_results=1000):
    all_data = []
    start = 0
    total_results = 0
    date_query = f"submittedDate:[{start_date}+TO+{end_date}]"

    while len(all_data) < max_results:
        try:
            # Construct full URL with date filter and pagination
            full_url = f"{base_URL}search_query=({search_query})+AND+{date_query}&start={start}&max_results=1000"
            print(f"Full URL: {full_url}")

            
            print(f"Fetching results from {start_date} to {end_date}, start={start}")
            response = requests.get(full_url)
            root_element_tree = ET.fromstring(response.content)
            
            # Find total number of results (if not already found)
            if total_results == 0:
                total_results_elem = root_element_tree.find("{http://www.w3.org/2005/Atom}totalResults")
                if total_results_elem is not None:
                    total_results = int(total_results_elem.text)
                    print(f"Total results found for {start_date} to {end_date}: {total_results}")

            entries = root_element_tree.findall("{http://www.w3.org/2005/Atom}entry")
            
            if not entries:
                print("No more entries found.")
                break

            for entry in entries:
                # Extract paper details
                title = entry.find("{http://www.w3.org/2005/Atom}title").text if entry.find("{http://www.w3.org/2005/Atom}title") is not None else "No Title"
                summary = entry.find("{http://www.w3.org/2005/Atom}summary").text if entry.find("{http://www.w3.org/2005/Atom}summary") is not None else "No Summary"
                published = entry.find("{http://www.w3.org/2005/Atom}published").text if entry.find("{http://www.w3.org/2005/Atom}published") is not None else "No Date"
                
                author_list = entry.findall("{http://www.w3.org/2005/Atom}author")
                authors = ", ".join([author.find("{http://www.w3.org/2005/Atom}name").text for author in author_list]) if author_list else "No Authors"

                link = entry.find("{http://www.w3.org/2005/Atom}link[@title='pdf']")
                pdf_link = link.get('href') if link is not None else "No PDF Link"

                all_data.append([title, summary, published, authors, pdf_link])

            # Increment start for the next batch
            start += 100
            time.sleep(3)

            if len(all_data) >= max_results or len(all_data) >= total_results:
                print(f"Reached max results for {start_date} to {end_date}. Exported {len(all_data)} papers.")
                break

        except Exception as e:
            print(f"An error occurred: {e}")
            break

    return all_data[:max_results]

# Export to BibTeX with unique keys
def save_to_bibtex(data, filename="results.bib"):
    with open(filename, 'w', encoding='utf-8') as f:
        unique_keys = set()
        for i, entry in enumerate(data, 1):
            # Create a unique key
            base_key = entry[0].replace(' ', '_')[:20].replace('[', '').replace(']', '')
            key = base_key
            counter = 1
            while key in unique_keys:
                key = f"{base_key}_{counter}"
                counter += 1
            unique_keys.add(key)
            
            # Clean up title and authors to remove any LaTeX-unfriendly characters
            title = entry[0].replace('&', r'\&').replace('#', r'\#').replace('_', r'\_')
            authors = entry[3].replace('&', r'\&')
            
            bibtex_entry = f"""@article{{arxiv:{key},
    title = {{{title}}},
    author = {{{authors}}},
    abstract = {{{entry[1][:1000]}}},
    year = {{{entry[2][:4]}}},
    month = {{{entry[2][5:7]}}},
    url = {{{entry[4]}}},
    journal = {{arXiv preprint}}
}}

"""
            f.write(bibtex_entry)
    print(f"Exported {len(data)} papers to {filename}")

# Define date ranges for splitting
date_ranges = [("2022-01-01", "2022-12-31"), ("2023-01-01", "2023-12-31")]  # Example ranges
all_results = []

# Fetch results for each date range
for start_date, end_date in date_ranges:
    results = fetch_arxiv_by_date(base_URL, search_query, start_date, end_date, max_results=1000)
    all_results.extend(results)

# Export all results to a BibTeX file
save_to_bibtex(all_results)
print(f"Total results fetched: {len(all_results)}")
