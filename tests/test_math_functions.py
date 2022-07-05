from brownie import MathFunctions, accounts, config
from scripts.helpful_scripts import get_account
import pytest


@pytest.fixture(scope="module")
def math_function_contract():
    account = get_account()
    return MathFunctions.deploy({"from": account})


def test_locked_balance(math_function_contract):
    test_cases = [
        # coll.sup. | air.sup. | air.bal.
        (100, 100, 100),
        (100, 4, 4),
        (100, 5, 5),
        (100, 6, 6),
        (100, 50, 100),
        (1000, 50, 50),
        (1000, 51, 51),
    ]
    expected_output = [95, 0, 0, 1, 90, 0, 1]

    output = []
    for case in test_cases:
        output.append(
            math_function_contract.getLockedBalance(case[0], case[1], case[2])
        )
    assert expected_output == output


def test_cdp_dbit(math_function_contract):
    test_cases = [
        # collateralized supply
        1,
        10,
        100,
        1000,
        10000,
        100000,
        1000000,
        10000000,
        100000000,
        1000000000,
        10000000000,
    ]
    expected_output = [1, 1, 1, 1, 1.176, 1.383, 1.626, 1.912, 2.249, 2.644, 3.110]

    output = []
    for case in test_cases:
        output.append(
            round(math_function_contract._cdpUsdToDBIT(case * (10**18)) / 10**18, 3)
        )

    assert expected_output == output


def test_cdp_dgov(math_function_contract):
    test_cases = [
        # collateralized supply
        1,
        10,
        100,
        1000,
        10000,
        100000,
        1000000,
        10000000,
        100000000,
        1000000000,
        10000000000,
    ]

    expected_output = []
    for case in test_cases:
        expected_output.append(round(1 / (100 + (case / 33333) ** 2), 3))

    output = []
    for case in test_cases:
        output.append(
            round(
                math_function_contract._cdpDbitToDgov(case * (10**18)) / 10**18, 3
            )
        )

    assert expected_output == output
