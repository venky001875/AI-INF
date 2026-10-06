import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import main


class InfluencerSearchTests(unittest.TestCase):
    def run_search_with_response(self, content):
        with patch.object(
            type(main.search_tool),
            "invoke",
            return_value="Search evidence for named creators",
        ), patch.object(
            main,
            "llm",
            SimpleNamespace(
                invoke=lambda prompt: SimpleNamespace(content=content)
            ),
        ):
            result = main.influencer_search("robotics", "India", "All", 3)
        return json.loads(result)

    def test_accepts_markdown_json_and_skips_invalid_names(self):
        content = '''Here is the result:
```json
{"influencers":[{"name":"Asha Rao","platform":"YouTube"},{"name":null,"username":"creator_x"},{"name":"creator_x","username":"creator_x"}]}
```
Thanks'''

        result = self.run_search_with_response(content)

        self.assertEqual(
            [person["name"] for person in result["influencers"]],
            ["Asha Rao", "creator_x", "creator_x"],
        )

    def test_empty_response_returns_readable_error(self):
        result = self.run_search_with_response("")

        self.assertIn("error", result)
        self.assertIn("empty response", result["message"])

    def test_unexpected_text_returns_readable_error(self):
        result = self.run_search_with_response("not JSON")

        self.assertIn("error", result)
        self.assertIn("valid JSON", result["message"])

    def test_accepts_dict_response_and_dict_search_results(self):
        with patch.object(
            type(main.search_tool),
            "invoke",
            return_value={"title": "Asha Rao", "snippet": "Robotics educator in India"},
        ), patch.object(
            main,
            "llm",
            SimpleNamespace(
                invoke=lambda prompt: SimpleNamespace(
                    content={"influencers": [{"name": "Asha Rao", "platform": "YouTube"}]}
                )
            ),
        ):
            result = main.influencer_search("robotics", "India", "All", "2")

        data = json.loads(result)
        self.assertEqual(data["influencers"][0]["name"], "Asha Rao")


if __name__ == "__main__":
    unittest.main()