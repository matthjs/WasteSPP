from typing import List, Dict, Tuple
import requests
def print_structure(repo_url: str):
    """
    Print the structure of a GitHub repository.

    Args:
        repo_url (str): The URL of the GitHub repository.
    """
    # Parse the GitHub repository URL to extract owner and repo name
    _, _, _, owner, repo_name = repo_url.rstrip('/').split('/')
    contents_url = f"https://api.github.com/repos/{owner}/{repo_name}"
    response = requests.get(contents_url)

    if response.status_code == 200:
        contents = response.json()

        # Print the structure (you can process it further as needed)
        print("Repository Structure:")
        print(contents)
    else:
        response.raise_for_status()


class ProjectExtractor(object):
    """
    Uses GitHub REST API to get GitHub repositories deemed abandoned.
    """
    def __init__(self, min_stars: int, last_pushed_date: str, language: str = "java",
                 exclude_archived: bool = False):
        """
        Initializes the ProjectExtractor instance.

        Args:
            min_stars (int): The minimum number of stars a repository should have to be considered.
            last_pushed_date (str): The date until which repositories are considered for abandonment.
            language (str, optional): The programming language of the repositories (default is "java").
            exclude_archived (bool, optional): Flag to exclude archived repositories (default is False).
        """
        self.base_url = "https://api.github.com/search/repositories"
        self.min_stars = min_stars
        self.last_pushed_date = last_pushed_date
        self.language = language
        self.exclude_archived = exclude_archived

    def find_abandoned_projects(self, amount: int = 10) -> List[Dict]:
        """
        Retrieves abandoned projects.

        Args:
            amount (int): The number of abandoned projects to retrieve (default is 10).

        Returns:
            List[Dict]: A list of dictionaries representing abandoned projects.
        """
        params, headers = self._create_request(amount)

        response = requests.get(self.base_url, params=params, headers=headers)

        if response.status_code == 200:
            return response.json().get("items", [])
        else:
            response.raise_for_status()

    def _create_request(self, amount: int) -> Tuple[Dict, Dict]:
        """
        Create request parameters and headers for GitHub repository search.

        Args:
            amount (int): The number of results to retrieve.

        Returns:
            Tuple[Dict, Dict]: A tuple containing request parameters and headers.
        TODO: See if search by topics is relevant.
        """
        query = f"language:{self.language} stars:>={self.min_stars} pushed:<{self.last_pushed_date}"
        if self.exclude_archived:
            query += " archived:false"

        # If above max results per page, adjust page num.
        page_num = 1
        if amount > 100:
            page_num = int(amount / 100)

        params = {"q": query, "per_page" : amount, "page" : page_num}
        headers = {"Accept": "application/vnd.github+json",
                   "X-GitHub-Api-Version" : "2022-11-28"}

        return params, headers



