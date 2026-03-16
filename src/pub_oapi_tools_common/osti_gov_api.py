from pub_oapi_tools_common.misc import log
import requests
from math import ceil


class OstiGovApi:

    def __init__(self,
                 quiet: bool = False,
                 verbose: bool = False):
        """
        An interface for working with OSTI.GOV's bibliographic API.
        Documentation: https://www.osti.gov/api/v1/docs
        This is a public API that doesn't require authentication,
        however the headers indicate rate limiting may be applied.

        :param quiet: Suppresses non-error logging output.
        :param verbose: Prints extra debug info.
        """

        self.osti_gov_api = "https://www.osti.gov/api/v1"
        self.quiet = quiet
        self.verbose = verbose

    def query_records(self,
                      params: dict,
                      rows: int = 100) -> list:
        """
        Sends a search query to the /records endpoint.
        This function handles pagination and merging data from pages.

        :param params: Search params for the records enpoint
        :param rows: Number of rows per page
        :return: A list of records dicts, merged from
            all pages in the records search
        """

        # Session() is recommended for multi-req. pagination
        with requests.Session() as session:

            # A generator function that yields all pages sequentially
            def get_records_pages():
                params['rows'] = rows
                req_url = f"{self.osti_gov_api}/records"

                if not self.quiet:
                    log("INFO", __name__,
                        f"Quering OSTI.GOV API for pagination data and first page.")

                # Calculate the number of pages from total records found and row count
                first_response = session.get(req_url, params=params)
                total_rows = int(first_response.headers['X-Total-Count'])
                num_pages = ceil(total_rows / rows)

                if not self.quiet:
                    log("INFO", __name__,
                        f"{total_rows} total rows found / {rows} rows per page = "
                        f"{num_pages} total pages for this query.")

                # Yield the first page body json
                first_page = first_response.json()
                yield first_page

                # Loop through the pages, yielding page body jsons
                for page in range(2, num_pages + 1):
                    if not self.quiet:
                        log("INFO", __name__,
                            f"Querying OSTI.GOV API, page: {page} / {num_pages}")
                    params['page'] = page
                    next_page = session.get(req_url, params=params).json()
                    yield next_page

            # Use the generator to get response pages and merge them
            merged_pages = []
            for records_page in get_records_pages():
                merged_pages += records_page

        return merged_pages

    def get_doi(self, doi: str) -> dict:
        """
        Returns the OSTI record for a single DOI.
        NOTE! This is current case-sensitive, but they're
        working on making it insensitive.

        :param doi: A DOI, the "https://doi.org/" can be excluded.
        :return: A request response object
        """

        if not self.quiet:
            log("INFO", __name__,
                f"Querying OSTI.GOV API for DOI: {doi}")

        req_url = f"{self.osti_gov_api}/records"
        params = {'doi': doi}
        response = requests.get(req_url, params=params)

        return response

    def download_fulltext(self, fulltext_url: str, output_dir: str = "./"):
        if not self.quiet:
            log("INFO", __name__, f"Downloading PDF from: {fulltext_url}")

        with requests.session() as session:
            response = session.get(fulltext_url, headers=headers)
            file_type = response.headers['content-Type']
            osti_id = fulltext_url.split('/')[-1]

            if file_type == 'application/pdf':
                with open(f'{output_dir}/{osti_id}.pdf', 'wb') as f:
                    f.write(response.content)
