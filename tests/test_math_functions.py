from brownie import MathFunctions
from scripts.helpful_scripts import get_account
import pytest, random, datetime


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

    for _ in range(10):

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


def test_sigmoid(math_function_contract):
    test_cases = []
    expected_output = []
    for _ in range(10):
        x = random.random()
        c = random.random()

        test_cases.append((x, c))

        num = 2 ** (-1 / ((1 - c) * x))
        den = num + 2 ** (-1 / ((1 - x) * c))

        expected_output.append(round(num / den, 5))

    output = []
    for case in test_cases:
        output.append(
            round(
                math_function_contract.sigmoid(
                    case[0] * (10**18), case[1] * (10**18)
                )
                / (10**18),
                5,
            )
        )

    for i in range(len(expected_output)):
        if expected_output[i] != output[i]:
            print(expected_output[i], output[i])

    assert expected_output == output


def test_floating_interest_rate(math_function_contract):
    test_cases = []
    expected_output = []

    for _ in range(10):
        _fixRateBond = random.randint(1, 10000000000)
        _floatingRateBond = random.randint(1, 10000000000)
        _benchmarkIR = random.random()

        test_cases.append((_fixRateBond, _floatingRateBond, _benchmarkIR))

        x = (_fixRateBond) / (_fixRateBond + _floatingRateBond)
        c = 1 / 5
        num = 2 ** (-1 / ((1 - c) * x))
        den = num + 2 ** (-1 / ((1 - x) * c))

        floatingRate = 2 * _benchmarkIR * num / den
        expected_output.append(round(floatingRate, 3))

    output = []
    for case in test_cases:
        output.append(
            round(
                math_function_contract.floatingInterestRate(
                    case[0] * (10**18),
                    case[1] * (10**18),
                    case[2] * (10**18),
                )
                / (10**18),
                3,
            )
        )

    assert expected_output == output


def test_fixed_interest_rate(math_function_contract):
    test_cases = []
    expected_output = []

    for _ in range(10):
        _fixRateBond = random.randint(1, 10000000000)
        _floatingRateBond = random.randint(1, 10000000000)
        _benchmarkIR = random.random()

        test_cases.append((_fixRateBond, _floatingRateBond, _benchmarkIR))

        x = (_fixRateBond) / (_fixRateBond + _floatingRateBond)
        c = 1 / 5
        num = 2 ** (-1 / ((1 - c) * x))
        den = num + 2 ** (-1 / ((1 - x) * c))

        floatingRate = 2 * _benchmarkIR * num / den
        fixedRate = 2 * _benchmarkIR - floatingRate

        expected_output.append(round(fixedRate, 3))

    output = []
    for case in test_cases:
        output.append(
            round(
                math_function_contract.fixedInterestRate(
                    case[0] * (10**18),
                    case[1] * (10**18),
                    case[2] * (10**18),
                )
                / (10**18),
                3,
            )
        )

    assert expected_output == output


def test_calculate_interest_rate(math_function_contract):
    test_cases = []
    expected_output = []

    for _ in range(10):
        _duration = random.randint(1, 31536000)
        _interestRate = random.random()

        test_cases.append((_duration, _interestRate))
        equivalent_interest_rate = _interestRate * (_duration / 31536000)
        expected_output.append(round(equivalent_interest_rate, 3))

    output = []
    for case in test_cases:
        output.append(
            round(
                math_function_contract.calculateInterestRate(
                    case[0],
                    case[1] * (10**18),
                )
                / (10**18),
                3,
            )
        )

    assert expected_output == output


def test_estimate_interest(math_function_contract):
    test_cases = []
    expected_output = []

    for _ in range(10):
        _amount = random.randint(1, 10000000000)
        _duration = random.randint(1, 31536000)
        _interestRate = random.random()

        test_cases.append((_amount, _duration, _interestRate))
        equivalent_interest_rate = _interestRate * (_duration / 31536000)
        interest = _amount * equivalent_interest_rate
        expected_output.append(round(interest, 3))

    output = []
    for case in test_cases:
        output.append(
            round(
                math_function_contract.estimateInterestEarned(
                    case[0] * (10**18),
                    case[1],
                    case[2] * (10**18),
                )
                / (10**18),
                3,
            )
        )

    assert expected_output == output


def test_average_liquidity_flow(math_function_contract):
    test_cases = []
    expected_output = []

    for _ in range(10):
        _sumOfLiquidityFlow = random.randint(1, 10000000000)
        _benchmarkIR = random.random()

        test_cases.append((_sumOfLiquidityFlow, _benchmarkIR))

        average_liquidity_flow = _sumOfLiquidityFlow * (1 + _benchmarkIR)
        expected_output.append(round(average_liquidity_flow, 3))

    output = []
    for case in test_cases:
        output.append(
            round(
                math_function_contract.lastMonthAverageLiquidityFlow(
                    case[0] * (10**18),
                    case[1] * (10**18),
                )
                / (10**18),
                3,
            )
        )

    assert expected_output == output


def test_floating_eta(math_function_contract):
    test_cases = []
    expected_output = []
    current_time = math_function_contract.getBlockTimestamp()

    for _ in range(10):
        _maturityTime = random.randint(
            current_time, current_time + 15552000
        )  # anytime in next 180 days
        _sumOfLiquidityFlow = random.randint(1, 100000000)  # any value upto 100 mill
        _benchmarkIR = random.random()
        _sumOfLiquidityOfLastNonce = random.randint(
            1, 10000000000
        )  # any value upto 10 bill
        _nonceDuration = 86400  # 1 day
        _lastMonthLiquidityFlow = random.randint(1, _sumOfLiquidityFlow)

        test_cases.append(
            (
                _maturityTime,
                _sumOfLiquidityFlow,
                _benchmarkIR,
                _sumOfLiquidityOfLastNonce,
                _nonceDuration,
                _lastMonthLiquidityFlow,
            )
        )
        deficit = _sumOfLiquidityFlow * (1 + _benchmarkIR) - _sumOfLiquidityOfLastNonce
        sumOverLastMonth = (deficit / _lastMonthLiquidityFlow) * _nonceDuration
        redemptionTime = _maturityTime + sumOverLastMonth

        expected_output.append(
            datetime.datetime.fromtimestamp(redemptionTime).strftime("%c")
        )
    output = []
    for case in test_cases:
        new_maturity_time = round(
            math_function_contract.floatingETA(
                case[0],
                case[1] * (10**18),
                case[2] * (10**18),
                case[3] * (10**18),
                case[4],
                case[5] * (10**18),
            ),
            3,
        )
        output.append(datetime.datetime.fromtimestamp(new_maturity_time).strftime("%c"))
        # print(datetime.datetime.fromtimestamp(case[0]).strftime("%c"))

    assert expected_output == output


def test_deficit_of_bond(math_function_contract):
    test_cases = []
    expected_output = []

    for _ in range(10):
        _sumOfLiquidityFlow = random.randint(1, 10000000000)
        _benchmarkIR = random.random()
        _sumOfLiquidityOfLastNonce = random.randint(1, 10000000000)

        test_cases.append(
            (_sumOfLiquidityFlow, _benchmarkIR, _sumOfLiquidityOfLastNonce)
        )

        deficit = _sumOfLiquidityFlow * (1 + _benchmarkIR) - _sumOfLiquidityOfLastNonce
        expected_output.append(round(deficit, 3))

    output = []
    for case in test_cases:
        output.append(
            round(
                math_function_contract._deficitOfBond(
                    case[0] * (10**18),
                    case[1] * (10**18),
                    case[2] * (10**18),
                )
                / (10**18),
                3,
            )
        )

    assert expected_output == output


def test_in_crises(math_function_contract):
    test_cases = []
    expected_output = []

    for _ in range(10):
        _sumOfLiquidityFlow = random.randint(1, 10000000000)
        _benchmarkIR = random.random()
        _sumOfLiquidityOfLastNonce = random.randint(1, 10000000000)

        test_cases.append(
            (_sumOfLiquidityFlow, _benchmarkIR, _sumOfLiquidityOfLastNonce)
        )

        deficit = _sumOfLiquidityFlow * (1 + _benchmarkIR) - _sumOfLiquidityOfLastNonce
        expected_output.append(int(deficit > 0))

    output = []
    for case in test_cases:
        output.append(
            math_function_contract.inCrisis(
                case[0] * (10**18),
                case[1] * (10**18),
                case[2] * (10**18),
            )
        )

    assert expected_output == output
