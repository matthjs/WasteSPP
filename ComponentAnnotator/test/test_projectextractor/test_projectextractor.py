import unittest
from unittest.mock import Mock, patch
from projectextractor.projectextractor import ProjectExtractor


class TestProjectExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = ProjectExtractor(min_stars=100, last_pushed_date="2022-01-01", language="java")

    @patch("requests.get")
    def test_find_abandoned_projects_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"name": "repo1"}, {"name": "repo2"}]}
        mock_get.return_value = mock_response

        result = self.extractor.find_abandoned_projects(amount=2)

        self.assertEqual(result, [{"name": "repo1"}, {"name": "repo2"}])

    def test_create_request(self):
        params, headers = self.extractor._create_request(amount=10)

        expected_params = {
            "q": "language:java stars:>=100 pushed:<2022-01-01 archived:true",
            "per_page": 10,
            "page": 1
        }

        expected_headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}

        self.assertEqual(params, expected_params)
        self.assertEqual(headers, expected_headers)

if __name__ == '__main__':
    unittest.main()
