from pub_oapi_tools_common.osti_gov_api import OstiGovApi
import json

# Get the API
osti_api = OstiGovApi(verbose=True)

# url = "https://www.osti.gov/servlets/purl/3008748"
url = "https://www.osti.gov/servlets/purl/1963892"
osti_api.download_fulltext(
    fulltext_url=url, output_dir="pdf-test")

exit()

# Test the DOI endpoint
dois = ["10.1109/tasc.2025.3628585",
        "10.1038/s41586-021-04349-7",
        "10.1103/prxquantum.4.040337",
        "10.1103/physrevlett.127.050501"]

for doi in dois:
    response = osti_api.get_doi(doi)
    print(response.headers)
    print(response.json())
    print()

exit()


# Test a records search with multiple pages
# See docs for search params: https://www.osti.gov/api/v1/docs
lbl_pubs_after_fy_2025 = {'research_org': 'LBNL',
                          'publication_date_start': '10/01/2024'}

response = osti_api.query_records(lbl_pubs_after_fy_2025)

with open("./records_search_test.json", 'w') as f:
    json.dump(response, f, indent=4)


# Test getting PDFs
