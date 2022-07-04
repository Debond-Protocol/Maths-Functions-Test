from brownie import MathFunctions, accounts, config
from scripts.helpful_scripts import get_account
import pytest


@pytest.fixture(scope="module")
def math_function_contract():
    account = get_account()
    return MathFunctions.deploy({"from": account})


def test_read_contract(math_function_contract):
    # pp = MathFunctions[-1]
    output = math_function_contract.getLockedBalance(100, 100, 100)
    assert output == 95
