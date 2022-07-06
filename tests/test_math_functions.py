from brownie import MathFunctions, accounts, config
from scripts.helpful_scripts import get_account
import pytest
import random


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


def test_get_progress(math_function_contract):
    current_time = math_function_contract.getBlockTimestamp()
    test_cases = [
        # maturity_date | period
        (current_time, 1000),
        (current_time + 250, 1000),
        (current_time + 500, 1000),
        (current_time + 750, 1000),
        (current_time + 1000, 1000),
        (current_time + 15552000 * 0.1, 15552000),  # 15552000 = 180 days
        (current_time + 15552000 * 0.2, 15552000),
        (current_time + 15552000 * 0.3, 15552000),
        (current_time + 15552000 * 0.4, 15552000),
        (current_time + 15552000 * 0.5, 15552000),
        (current_time + 15552000 * 0.6, 15552000),
        (current_time + 15552000 * 0.7, 15552000),
        (current_time + 15552000 * 0.8, 15552000),
        (current_time + 15552000 * 0.9, 15552000),
    ]

    expected_output = [100, 75, 50, 25, 0, 90, 80, 70, 60, 50, 40, 30, 20, 10]

    output = []
    for case in test_cases:
        output.append(math_function_contract.getProgress(case[0], case[1])[0])

    assert expected_output == output


def test_get_progress2(math_function_contract):
    interest_rate = 0.05

    test_cases = [
        # current supply | supply at nonce
        (100, 100 / (1 + interest_rate) - 1),
        (1000, 1000 / (1 + interest_rate) + 1),
        (10000, 10000 / (1 + interest_rate) - 1),
        (100000, 100000 / (1 + interest_rate) + 1),
        (1000000, 1000000 / (1 + interest_rate) - 1),
        (10000000, 10000000 / (1 + interest_rate) + 1),
        (100000000, 100000000 / (1 + interest_rate) - 1),
        (1000000000, 1000000000 / (1 + interest_rate) + 1),
        (10000000000, 10000000000 / (1 + interest_rate) - 1),
    ]

    expected_output = [100, 0, 100, 0, 100, 0, 100, 0, 100]

    output = []
    for case in test_cases:
        output.append(
            math_function_contract.getProgress2(
                case[0] * (10**18), case[1] * (10**18)
            )[0]
        )
    assert expected_output == output


def test_add_entry(math_function_contract):

    test_cases = [
        # (old entries | amount to add | total entries | total balance)
    ]
    expected_output = []

    for _ in range(10):
        old_entries = random.randint(1, 10000000000)
        amount_to_add = random.randint(1, 10000000000)
        total_entries = random.randint(old_entries, 10000000000)
        total_balance = random.randint(1, 10000000000)
        test_cases.append((old_entries, amount_to_add, total_entries, total_balance))
        expected_output.append(
            round(old_entries + total_entries / total_balance * amount_to_add, 3)
        )

    output = []
    for case in test_cases:
        output.append(
            round(
                math_function_contract.amountToAddEntry(
                    case[0] * (10**18),
                    case[1] * (10**18),
                    case[2] * (10**18),
                    case[3] * (10**18),
                )
                / (10**18),
                3,
            )
        )
    assert expected_output == output


def test_remove_entry(math_function_contract):

    test_cases = [
        # (old entries | amount to remove | total entries | total balance)
    ]
    expected_output = []

    for _ in range(10):
        old_entries = random.randint(1, 10000000000)
        total_balance = random.randint(1, 10000000000)
        total_entries = random.randint(old_entries, 10000000000)
        amount_to_remove = random.randint(
            1, int(old_entries * total_balance / total_entries)
        )

        test_cases.append((old_entries, amount_to_remove, total_entries, total_balance))
        expected_output.append(
            round(old_entries - total_entries / total_balance * amount_to_remove, 3)
        )

    output = []
    for case in test_cases:
        output.append(
            round(
                math_function_contract.amountToRemoveEntry(
                    case[0] * (10**18),
                    case[1] * (10**18),
                    case[2] * (10**18),
                    case[3] * (10**18),
                )
                / (10**18),
                3,
            )
        )
    assert expected_output == output


def test_amount_out(math_function_contract):
    test_cases = [
        # (amount_in | reserve_in | reserve_out)
    ]
    expected_output = []

    for _ in range(10):
        amount_in = random.randint(1, 10000000000)
        reserve_in = random.randint(1, 10000000000)
        reserve_out = random.randint(1, 10000000000)

        test_cases.append((amount_in, reserve_in, reserve_out))
        expected_output.append(
            round(reserve_out - reserve_in * reserve_out / (reserve_in + amount_in), 3)
        )

    output = []
    for case in test_cases:
        output.append(
            round(
                math_function_contract.getAmountOut(
                    case[0] * (10**18),
                    case[1] * (10**18),
                    case[2] * (10**18),
                )
                / (10**18),
                3,
            )
        )
    assert expected_output == output


def test_current_price(math_function_contract):

    test_cases = []
    expected_output = []
    block_time = math_function_contract.getBlockTimestamp()

    for _ in range(3):

        # start time in the past 7 days
        startingTime = block_time - random.randint(1, 604800)

        # random duration from 1 to 2 weeks
        duration = random.randint(604800, 604800 * 2)

        maxCurrencyAmount = random.randint(1, 100000)
        minCurrencyAmount = random.randint(1, maxCurrencyAmount)

        test_cases.append(
            (startingTime, duration, maxCurrencyAmount, minCurrencyAmount)
        )

        # Linear
        expected_output.append(
            round(
                maxCurrencyAmount
                - (
                    (maxCurrencyAmount - minCurrencyAmount)
                    * (block_time - startingTime)
                )
                / duration,
                3,
            )
        )

        # Parabolic
        expected_output.append(
            round(
                maxCurrencyAmount
                - (
                    (maxCurrencyAmount - minCurrencyAmount)
                    * ((block_time - startingTime) ** 2)
                )
                / (duration**2),
                3,
            )
        )

    output = []
    for case in test_cases:
        # Linear
        output.append(
            round(
                math_function_contract.currentPrice(
                    case[0],
                    case[1],
                    False,
                    case[2] * (10**18),
                    case[3] * (10**18),
                )
                / (10**18),
                3,
            )
        )

        # Parabolic
        output.append(
            round(
                math_function_contract.currentPrice(
                    case[0],
                    case[1],
                    True,
                    case[2] * (10**18),
                    case[3] * (10**18),
                )
                / (10**18),
                3,
            )
        )

    assert expected_output == output
