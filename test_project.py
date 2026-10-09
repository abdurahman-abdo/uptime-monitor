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
        
        http_error = requests.exceptions.HTTPError(msg, response=self)
        raise http_error
    
def test_check_url(monkeypatch):
    def get(url, timeout, allow_redirects=True):
        return RequestsMock(url, timeout, None).raise_for_status()
    
    monkeypatch.setattr(requests, "get", get)
    response = project.check_url("ftp://example.com", timeout=0.5, redirects=True)
    assert response["url"] == "ftp://example.com"
    assert response["status_code"] == None
    assert response["response_time_ms"] == None
    