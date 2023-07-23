from http import HTTPStatus

invalid_signup_data = [
    (
        {
            'email': ('a' * 80) + '@example.com',
            'username': 'valid-username'
        },
        ((
            'Check email validation on {request_method} to `{url}`'
            'it should not exceed 80 ch'
        ),)
    ),
    (
        {
            'email': 'validemail@example.org',
            'username': ('a' * 51)
        },
        ((
            'Check username validation on {request_method} to `{url}`'
            'it should not exceed 50 ch'
        ),)
    ),
    (
        {
            'email': 'validemail@example.org',
            'username': '|-|aTa|_|_|a'
        },
        ((
            'Check username validation on {request_method} to `{url}`'
            'it should match the following pattern: ^[\\w.@+-]+\\z'
        ),)
    )
]


def assert_url_exists(response, url) -> bool:
    assert response.status_code != HTTPStatus.NOT_FOUND, (
        f"Endpoint {url} not found, check urls.py"
    )


def check_pagination(url, response_json, expected_count, post_data=None):
    expected_keys = ('count', 'next', 'previous', 'results')
    for key in expected_keys:
        assert key in response_json, (
            f"Make sure pagination for {url} is enabled and contains key {key}"
        )
    assert response_json['count'] == expected_count, (
        f"Make sure {url} is paginated and it's count contains correct value"
    )
    assert isinstance(response_json['results'], list), (
        f"{url} Response json should contain an array at 'results' key"
    )
    assert len(response_json['results']) == expected_count, (
        f"'results' key of {url}'s response json "
        "contains incorrect number of elements"
    )
    if post_data:
        for item in post_data.items():
            assert item in response_json['results'][0].items(), (
                f"Make sure the response json of {url} contains correct data"
            )
