import pytest
from datetime import timedelta
import requests
import project
import json

@pytest.mark.parametrize("url", [
    "ftp://example.com",
    "file:///etc/passwd",
    "example.com",
    "htp://example.com",
    "mailto:user@domain.com",
    "http://",
])

def test_check_malformed_url(url):
    response = project.check_url(url)

    assert response["final_url"] == url
    assert response["status_code"] is None
    assert response["response_time_ms"] is None
    assert response["is_ok"] is False
    assert response["redirects"] is None
    assert response["error"] is not None

class RequestsMock:
    def __init__(self, url, timeout, status_code, history=None):
        if not history:
            history = []
            
        self.url = url
        self.timeout = timedelta(milliseconds=timeout)
        self.status_code = status_code
        self.history = history
        self.elapsed = timedelta(milliseconds=2)
        
        try:
            self.raise_for_status()
            self.is_ok = True
        except Exception:
            self.is_ok = False
    
    def raise_for_status(self):
        if self.elapsed > self.timeout:
            raise requests.exceptions.Timeout(response=self)

        if not self.status_code:
            raise requests.exceptions.InvalidSchema(response=self)
        
        if 400 <= self.status_code < 500:
            error_type = "Client Error"
        elif 500 <= self.status_code < 600:
            error_type = "Server Error"
        else:
            return
        
        msg = f"{self.status_code} {error_type} for url: {self.url}"
        
        raise requests.exceptions.HTTPError(msg, response=self)

def run_and_assert_url(monkeypatch, url, status_code, expected_status, expected_is_ok, expected_error=True, timeout=0.5):
    def get(url, timeout, allow_redirects=True):
        return RequestsMock(url, timeout, status_code)
    
    monkeypatch.setattr(requests, "get", get)
    response = project.check_url(url, timeout, redirects=True)
    
    print("\n--- DEBUG RESPONSE ---")
    print(response)
    print("----------------------")
    
    assert response["url"] == url
    assert response["status_code"] == expected_status
    assert response["is_ok"] == expected_is_ok
    if expected_error:
        assert response["error"] is not None
    else:
        assert response["error"] is None
    return response

def test_check_url(monkeypatch):

    # test url not found
    run_and_assert_url(monkeypatch, 
                    url="https://example.com/404", 
                    status_code=404, 
                    expected_status=404, 
                    expected_is_ok=False)

    # test server error
    run_and_assert_url(monkeypatch, 
                    url="https://example.com/500", 
                    status_code=500, 
                    expected_status=500, 
                    expected_is_ok=False)
    
    # test working url when timeout is not exceeded
    run_and_assert_url(monkeypatch, 
                    url="https://example.com/", 
                    status_code=200, 
                    expected_status=200, 
                    expected_is_ok=True,
                    expected_error=None,
                    timeout=2)

    # test working url when timeout is exceeded
    run_and_assert_url(monkeypatch, 
                        url="https://example.com/", 
                        status_code=200, 
                        expected_status=200, 
                        expected_is_ok=False,
                        timeout=0.5)
    
sample_mixed_response_dict = [
    {
        "url": "https://www.example.com",
        "status_code": 200,
        "response_time_ms": 120,
        "is_ok": True,
        "error": None
    },
    {
        "url": "https://www.github.com",
        "status_code": 200,
        "response_time_ms": 340,
        "is_ok": True,
        "error": None
    },
    {
        "url": "https://httpbin.org/status/404",
        "status_code": 404,
        "response_time_ms": 829.12,
        "is_ok": False,
        "error": 'Resource not found (404).'
    }
]

sample_down_response_dict = [
    {
        "url": "https://test.com",
        "status_code": None,
        "response_time_ms": None,
        "is_ok": False,
        "error": 'Failed to connect to the server.'
    },
    {
        "url": "ftp://example.com",
        "status_code": None,
        "response_time_ms": None,
        "is_ok": False,
        "error": "An unexpected requests error occurred: No connection adapters were found for 'ftp://example.com'"
    },
    {
        "url": "https://httpbin.org/status/404",
        "status_code": 404,
        "response_time_ms": 829.12,
        "is_ok": False,
        "error": 'Resource not found (404).'
    }
]

sample_up_response_dict = [
    {
        "url": "https://www.example.com",
        "status_code": 200,
        "response_time_ms": 120,
        "is_ok": True,
        "error": None
    },
    {
        "url": "https://www.github.com",
        "status_code": 200,
        "response_time_ms": 340,
        "is_ok": True,
        "error": None
    },
    {
        "url": "https://www.google.com",
        "status_code": 200,
        "response_time_ms": 1031.3,
        "is_ok": True,
        "error": None
    }
]

sample_corrupt_response_dict = [
    {
        "url": "https://www.example.com",
        "status_code": 200,
        "response_time_ms": None,
        "is_ok": True,
        "error": None
    },
    {
        "url": "https://www.github.com",
        "status_code": 200,
        "response_time_ms": 340,
        "is_ok": True,
        "error": None
    },
]

sample_empty_response = []

def test_summarize_results_mixed():
    summary = project.summarize_results(sample_mixed_response_dict)
    
    assert summary["total_checks"] == 3
    assert summary["number_up"] == 2
    assert summary["number_down"] == 1
    assert summary["uptime"] == 66.67
    assert summary["average_response_time"] == 230
    assert summary["failures"] == [
        {
            "url": 'https://httpbin.org/status/404',
            "status_code": 404,
            "error_message": 'Resource not found (404).'
        }
    ]

def test_summarize_results_up():
    summary = project.summarize_results(sample_up_response_dict)
    
    assert summary["total_checks"] == 3
    assert summary["number_up"] == 3
    assert summary["number_down"] == 0
    assert summary["uptime"] == 100
    assert summary["average_response_time"] == 497.1
    assert not summary["failures"]

def test_summarize_results_down():
    summary = project.summarize_results(sample_down_response_dict)
    
    assert summary["total_checks"] == 3
    assert summary["number_up"] == 0
    assert summary["number_down"] == 3
    assert summary["uptime"] == 0
    assert summary["average_response_time"] is None
    assert summary["failures"] == [
        {
            "url": 'https://test.com',
            "status_code": None,
            "error_message": 'Failed to connect to the server.'
        },
                {
            "url": 'ftp://example.com',
            "status_code": None,
            "error_message": "An unexpected requests error occurred: No connection adapters were found for 'ftp://example.com'"
        },
        {
            "url": 'https://httpbin.org/status/404',
            "status_code": 404,
            "error_message": 'Resource not found (404).'
        }
    ]

def test_summarize_results_empty():
    summary = project.summarize_results(sample_empty_response)
    
    assert summary["total_checks"] == 0
    assert summary["number_up"] == 0
    assert summary["number_down"] == 0
    assert summary["uptime"] is None
    assert summary["average_response_time"] is None
    assert not summary["failures"]

def test_summarize_results_failed():    
    with pytest.raises(TypeError):
            project.summarize_results(sample_corrupt_response_dict)

def test_json_loader(tmp_path):
    valid_data = [
        {"url": "https://example.com"},
        {"url": "https://www.github.com", "timeout": 10},
        {"url": "https://httpbin.org/status/404"},
        {"url": "https://httpbin.org/status/500"},
        {"url": "https://httpbin.org/delay/5", "timeout": 2},
        {"url": "https://httpbin.org/redirect/2", "redirects": True},
        {"url": "http://github.com", "redirects": False},
        {"url": "https://this-domain-does-not-exist-12345.com"},
        {"url": "ftp://example.com"},
        {"timeout": 5}
    ]

    test_dir = tmp_path / "debug"
    test_dir.mkdir(exist_ok=True)

    valid_filepath = test_dir / "valid.json"
    valid_filepath.write_text(json.dumps(valid_data, indent=2))
    
    non_json_filepath = test_dir / "invalid.txt"
    non_json_filepath.write_text("This is a test string.")
    
    empty_filepath = test_dir / "invalid.json"
    empty_filepath.write_text("")
    
    object_filepath = test_dir / "object_file.json"
    object_filepath.write_text(json.dumps({"url": "https://example.com"}, indent=2))
    
    list_filepath = test_dir / "list_file.json"
    list_filepath.write_text(json.dumps(["https://example.com", "https://github.com"], indent=2))
    
    empty_list_filepath = test_dir / "empty.json"
    empty_list_filepath.write_text(json.dumps([], indent=2))
    
    assert project.json_loader(valid_filepath)
    with pytest.raises(ValueError, match="The file nothing.json was not found!"):
        project.json_loader("nothing.json")
    with pytest.raises(ValueError, match="The JSON file is corrupted or empty!"):
        project.json_loader(non_json_filepath)
    with pytest.raises(ValueError, match="The JSON file is corrupted or empty!"):
        project.json_loader(empty_filepath)
    with pytest.raises(ValueError, match="The json format was invalid!"):
        project.json_loader(empty_list_filepath)
    with pytest.raises(ValueError, match="The json format was invalid!"):
        project.json_loader(object_filepath)
    with pytest.raises(ValueError, match="The json format was invalid!"):
        project.json_loader(list_filepath)
    
