import pytest
from datetime import timedelta
import requests
import project

class RequestsMock:
    def __init__(self, url, elapsed, status_code, history=None):
        if not history:
            history = []
            
        self.url = url
        self.elapsed = timedelta(milliseconds=elapsed)
        self.status_code = status_code
        self.history = history
        
        try:
            self.raise_for_status()
            self.is_ok = True
        except Exception:
            self.is_ok = False
    
    def raise_for_status(self):
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

def test_ftp_url(monkeypatch):
    run_and_assert_url(monkeypatch, 
                    url="ftp://example.com", 
                    status_code=None, 
                    expected_status=None, 
                    expected_is_ok=False)

def test_not_found_url(monkeypatch):
    run_and_assert_url(monkeypatch, 
                    url="https://example.com/404", 
                    status_code=404, 
                    expected_status=404, 
                    expected_is_ok=False)

def test_server_error_url(monkeypatch):
    run_and_assert_url(monkeypatch, 
                    url="https://example.com/500", 
                    status_code=500, 
                    expected_status=500, 
                    expected_is_ok=False)

def test_working_url(monkeypatch):
    run_and_assert_url(monkeypatch, 
                    url="https://example.com/", 
                    status_code=200, 
                    expected_status=200, 
                    expected_is_ok=True,
                    expected_error=None)