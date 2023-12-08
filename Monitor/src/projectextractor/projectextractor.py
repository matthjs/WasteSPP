from typing import List, Dict, Tuple

import requests

class ProjectExtractor(object):
    _instance = None

    """
    Uses GitHub REST API to get GitHub repositories deemed abandoned.
    """
    def __new__(cls, min_stars: int, last_pushed_date: str, language: str = "java",
                 exclude_archived: bool = False):
        if cls._instance is None:
            cls._instance = super(ProjectExtractor, cls).__new__(cls)
            cls.base_url = "https://api.github.com/search/repositories"
            cls.min_stars = min_stars
            cls.last_pushed_date = last_pushed_date
            cls.language = language
            cls.exclude_archived = exclude_archived

        return cls._instance

    def print_structure(self, repo_url: str):
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

    def find_abandoned_projects(self, amount: int = 10) -> List[Dict]:
        """
        Retrieves abandoned projects.
        """
        params, headers = self._create_request(amount)

        response = requests.get(self.base_url, params=params, headers=headers)

        if response.status_code == 200:
            return response.json().get("items", [])
        else:
            response.raise_for_status()

    def _create_request(self, amount: int) -> Tuple[Dict, Dict]:
        """
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


if __name__ == "__main__":
    extr = ProjectExtractor(min_stars=100, last_pushed_date="2022-01-01")

    abandoned_projects = extr.find_abandoned_projects()

    print("Abandoned Projects:")
    for project in abandoned_projects:
        print(f"- {project['name']} ({project['html_url']})")
        extr.print_structure(project['html_url'])



