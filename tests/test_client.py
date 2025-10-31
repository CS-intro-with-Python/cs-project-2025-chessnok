import requests


def test_request():
    res = requests.get('http://127.0.0.1:5000/')
    assert res.status_code == 200
