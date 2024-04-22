import pytest

import requests


def test_passing():
    assert (1, 2, 3) == (1, 2, 3)


def test_failing():
    with pytest.raises(AssertionError):
        assert (1, 2, 3) == (3, 2, 1)


def multiply_by_two(a):
    return a * 2


@pytest.mark.parametrize("input, expected", [(1, 2), (2, 4), (3, 6)])
def test_multiply_by_two(input, expected):
    result = multiply_by_two(input)
    assert result == expected


@pytest.fixture
def setup_data():
    data = {'username': 'test_user', 'password': 'test_pass'}
    return data


def login(u, p):
    return 'success'


def test_login(setup_data):
    result = login(setup_data['username'], setup_data['password'])
    assert result == 'success'


def test_api_response():
    response = requests.get('https://google.com')
    assert response.status_code == 200 or response.status_code == 301
