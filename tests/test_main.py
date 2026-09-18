import unittest
from unittest.mock import patch

import main


class FakeResponse:
    def __init__(self, *, json_data=None, text="", headers=None, status_code=200):
        self._json_data = json_data
        self.text = text
        self.headers = headers or {"content-type": "application/json"}
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        if self._json_data is None:
            raise ValueError("No JSON payload")
        return self._json_data


class EloverblikMcpTests(unittest.TestCase):
    def setUp(self):
        main.fetch_access_token.cache_clear()
        main.get_access_token.cache_clear()

    @patch.dict("os.environ", {"METERING_POINT_ID": "571313180400002957", "API_REFRESH_TOKEN": "refresh"})
    @patch("main.get_access_token", return_value="access-token")
    @patch("main.requests.request")
    def test_metering_point_details_uses_default_metering_point(self, mock_request, _mock_token):
        mock_request.return_value = FakeResponse(json_data={"result": "ok"})

        result = main.eloverblik_metering_point_details()

        self.assertEqual(result, {"result": "ok"})
        request_kwargs = mock_request.call_args.kwargs
        self.assertEqual(request_kwargs["method"], "POST")
        self.assertEqual(
            request_kwargs["url"],
            "https://api.eloverblik.dk/customerapi/api/meteringpoints/meteringpoint/getdetails",
        )
        self.assertEqual(
            request_kwargs["json"],
            {"meteringPoints": {"meteringPoint": ["571313180400002957"]}},
        )

    @patch("main.get_access_token", return_value="access-token")
    @patch("main.requests.request")
    def test_relation_add_with_web_access_code_encodes_path(self, mock_request, _mock_token):
        mock_request.return_value = FakeResponse(json_data={"result": True})

        main.eloverblik_metering_point_relation_add_with_web_access_code(
            "571313180400002957",
            "ab/cd 12",
        )

        self.assertEqual(
            mock_request.call_args.kwargs["url"],
            "https://api.eloverblik.dk/customerapi/api/meteringpoints/meteringpoint/relation/add/571313180400002957/ab%2Fcd%2012",
        )

    @patch.dict("os.environ", {"METERING_POINT_ID": "571313180400002957", "API_REFRESH_TOKEN": "refresh"})
    @patch("main.get_access_token", return_value="access-token")
    @patch("main.requests.request")
    def test_meter_readings_uses_expected_endpoint(self, mock_request, _mock_token):
        mock_request.return_value = FakeResponse(json_data={"result": []})

        main.eloverblik_meter_readings("2024-01-01", "2024-01-31")

        self.assertEqual(
            mock_request.call_args.kwargs["url"],
            "https://api.eloverblik.dk/customerapi/api/meterdata/getmeterreadings/2024-01-01/2024-01-31",
        )

    @patch.dict("os.environ", {"METERING_POINT_ID": "571313180400002957", "API_REFRESH_TOKEN": "refresh"})
    @patch("main.get_access_token", return_value="access-token")
    @patch("main.requests.request")
    def test_timeseries_keeps_existing_end_date_adjustment(self, mock_request, _mock_token):
        mock_request.return_value = FakeResponse(json_data={"result": []})

        main.eloverblik_timeseries("2024-01-01", "2024-01-31", main.Aggregation.DAY)

        self.assertEqual(
            mock_request.call_args.kwargs["url"],
            "https://api.eloverblik.dk/customerapi/api/meterdata/gettimeseries/2024-01-01/2024-02-01/Day",
        )

    @patch.dict("os.environ", {"METERING_POINT_ID": "571313180400002957", "API_REFRESH_TOKEN": "refresh"})
    @patch("main.get_access_token", return_value="access-token")
    @patch("main.requests.request")
    def test_timeseries_export_returns_csv_content(self, mock_request, _mock_token):
        mock_request.return_value = FakeResponse(
            text="a,b\n1,2\n",
            headers={
                "content-type": "text/csv",
                "content-disposition": 'attachment; filename="timeseries.csv"',
            },
        )

        result = main.eloverblik_timeseries_export("2024-01-01", "2024-01-31")

        self.assertEqual(result["filename"], "timeseries.csv")
        self.assertEqual(result["content_type"], "text/csv")
        self.assertEqual(result["content"], "a,b\n1,2\n")


if __name__ == "__main__":
    unittest.main()
