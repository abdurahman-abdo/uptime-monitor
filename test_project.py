import pytest
from datetime import timedelta
import requests
import project

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

    # test working url when timout is exceeded
    run_and_assert_url(monkeypatch, 
                        url="https://example.com/", 
                        status_code=200, 
                        expected_status=200, 
                        expected_is_ok=False,
                        timeout=0.5)