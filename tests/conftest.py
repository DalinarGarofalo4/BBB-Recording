from typing import Any, Dict

import pytest
from faker import Faker

faker = Faker()
ShadowState = Dict[str, Any]
ShadowReported = Dict[str, Any]


@pytest.fixture()
def get_token_with_algorithm_wrong():
    """
    Get fake bearer token.
    - Algorithm used: HS384
    """
    return 'eyJhbGciOiJIUzM4NCIsInR5cCI6IkpXVCJ9.e30.7lW5XpYN-zolV19W8NYwsiJDc9e6-QOccCmoO7SrZMc9I_OGwJ4LwnDji1D8yGIu'
