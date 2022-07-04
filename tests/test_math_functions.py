from brownie import MathFunctions, accounts, config
from scripts.helpful_scripts import get_account
import pytest


@pytest.fixture(scope="module")
def math_function_contract():
    account = get_account()
    return MathFunctions.deploy({"from": account})


def test_read_contract(math_function_contract):
    o1 = math_function_contract.getLockedBalance(100, 100, 100)
    o2 = math_function_contract.getLockedBalance(100, 4, 4)
    o3 = math_function_contract.getLockedBalance(100, 5, 5)
    o4 = math_function_contract.getLockedBalance(100, 6, 6)
    o5 = math_function_contract.getLockedBalance(100, 50, 100)
    o6 = math_function_contract.getLockedBalance(1000, 50, 50)
    o7 = math_function_contract.getLockedBalance(1000, 51, 51)

    assert [o1, o2, o3, o4, o5, o6, o7] == [95, 0, 0, 1, 90, 0, 1]
