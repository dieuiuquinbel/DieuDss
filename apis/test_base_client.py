import unittest
from unittest.mock import patch

from apis.base_client import get_json


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self) -> bytes:
        return b'{"ok": true}'


class BaseClientTest(unittest.TestCase):
    @patch("apis.base_client.urlopen", return_value=FakeResponse())
    def test_get_json_encodes_query_and_returns_json(self, mocked_urlopen) -> None:
        payload = get_json("https://example.test/search", {"query": "ức gà"}, timeout=7)

        self.assertEqual(payload, {"ok": True})
        request = mocked_urlopen.call_args.args[0]
        self.assertIn("query=%E1%BB%A9c+g%C3%A0", request.full_url)
        self.assertEqual(mocked_urlopen.call_args.kwargs["timeout"], 7)


if __name__ == "__main__":
    unittest.main()
