import pytest

from casingdesign.examples import onshore_horizontal_well


@pytest.fixture
def onshore_well():
    return onshore_horizontal_well()
