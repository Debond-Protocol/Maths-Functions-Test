pragma solidity ^0.8.0;

// SPDX-License-Identifier: apache 2.0
/*
    Copyright 2022 Debond Protocol <info@debond.org>
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
*/

import "@prb-math/contracts/PRBMathSD59x18.sol";

contract MathFunctions {
    uint256 private constant NUMBER_OF_SECONDS_IN_YEAR = 31536000;

    /**
     * @dev calculate the sigmoid function for given params
     * @param _x the sigmoid argument (input parameter)
     * @param _c the sigmoid parameter c (see the white papaer)
     * @param result the output of sigmoid function for given _x and _c
     */
    function sigmoid(uint256 _x, uint256 _c)
        public
        pure
        returns (uint256 result)
    {
        if (_x == 0) {
            result = 0;
        } else if (_x == 1) {
            result = 1;
        } else {
            int256 temp1;
            int256 temp2;

            assembly {
                temp1 := sub(_c, 1000000000000000000)
                temp2 := sub(_x, 1000000000000000000)
            }

            temp1 = PRBMathSD59x18.mul(temp1, int256(_x));
            temp2 = PRBMathSD59x18.mul(temp2, int256(_c));

            temp1 = PRBMathSD59x18.inv(temp1);
            temp2 = PRBMathSD59x18.inv(temp2);

            temp1 = PRBMathSD59x18.exp2(temp1); //because temp1 = exp2(mul(temp2,log2(2)), with log2(2)=1
            temp2 = PRBMathSD59x18.exp2(temp2);

            result = uint256(PRBMathSD59x18.div(temp1, temp1 + temp2));
        }
    }

    function inv(uint256 x) public pure returns (uint256 result) {
        return uint256(PRBMathSD59x18.inv(int256(x)));
    }

    function div(uint256 x, uint256 y) public pure returns (uint256 result) {
        return uint256(PRBMathSD59x18.div(int256(x), int256(y)));
    }

    function mul(uint256 x, uint256 y) public pure returns (uint256 result) {
        return uint256(PRBMathSD59x18.mul(int256(x), int256(y)));
    }

    function pow(uint256 x, uint256 y) public pure returns (uint256 result) {
        return uint256(PRBMathSD59x18.pow(int256(x), int256(y)));
    }

    function log2(uint256 x) public pure returns (uint256 result) {
        return uint256(PRBMathSD59x18.log2(int256(x)));
    }

    /**
     * @dev calculate the floatting interest rate
     * @param _fixRateBond fixed rate bond
     * @param _floatingRateBond rate bond
     * @param _benchmarkIR benchmark interest rate
     * @param floatingRate floatting rate interest rate
     */
    function floatingInterestRate(
        uint256 _fixRateBond,
        uint256 _floatingRateBond,
        uint256 _benchmarkIR
    ) public pure returns (uint256 floatingRate) {
        uint256 x = (_fixRateBond * 1 ether) /
            (_fixRateBond + _floatingRateBond);
        uint256 c = 200000000000000000; // c = 1/5
        uint256 sig = sigmoid(x, c);

        floatingRate = (2 * _benchmarkIR * sig) / 1 ether;
    }

    /**
     * @dev calculate the fixed interest rate
     * @param _fixRateBond fixed rate bond
     * @param _floatingRateBond rate bond
     * @param _benchmarkIR benchmark interest rate
     * @param fixedRate fixed rate interest rate
     */

    function fixedInterestRate(
        uint256 _fixRateBond,
        uint256 _floatingRateBond,
        uint256 _benchmarkIR
    ) external pure returns (uint256 fixedRate) {
        uint256 floatingRate = floatingInterestRate(
            _fixRateBond,
            _floatingRateBond,
            _benchmarkIR
        );

        return 2 * _benchmarkIR - floatingRate;
    }

    /**
     * @dev calculate the interest earned in DBIT
     * @param _duration the satking duration
     * @param _interestRate Annual percentage rate (APR)
     * @param interest interest earned for the given duration
     */
    function calculateInterestRate(uint256 _duration, uint256 _interestRate)
        public
        pure
        returns (uint256 interest)
    {
        interest = (_interestRate * _duration) / NUMBER_OF_SECONDS_IN_YEAR;
    }

    /**
     * @dev Estimate how much Interest the user has gained since he staked dGoV
     * @param _amount the amount of DBIT staked
     * @param _duration staking duration to estimate interest from
     * @param interest the estimated interest earned so far
     */
    function estimateInterestEarned(
        uint256 _amount,
        uint256 _duration,
        uint256 _interestRate
    ) external pure returns (uint256 interest) {
        uint256 rate = calculateInterestRate(_duration, _interestRate);
        interest = (_amount * rate) / 1 ether;
    }

    /**
     * @dev calculate the average liquidity flow
     * @param _sumOfLiquidityFlow total liquidity flow for a given nonce
     * @param _benchmarkIR benchmark interest rate
     * @param averageFlow average liquidity flow
     */
    function lastMonthAverageLiquidityFlow(
        uint256 _sumOfLiquidityFlow,
        uint256 _benchmarkIR
    ) public pure returns (uint256 averageFlow) {
        averageFlow =
            (_sumOfLiquidityFlow * (1 ether + _benchmarkIR)) /
            1 ether;
    }

    function floatingETA(
        uint256 _maturityTime,
        uint256 _sumOfLiquidityFlow,
        uint256 _benchmarkIR,
        uint256 _sumOfLiquidityOfLastNonce,
        uint256 _nonceDuration,
        uint256 _lastMonthLiquidityFlow
    ) external pure returns (uint256 redemptionTime) {
        int256 deficit = _deficitOfBond(
            _sumOfLiquidityFlow,
            _benchmarkIR,
            _sumOfLiquidityOfLastNonce
        );

        int256 sumOverLastMonth = PRBMathSD59x18.div(
            deficit,
            int256(_lastMonthLiquidityFlow)
        ) * int256(_nonceDuration);

        redemptionTime =
            uint256(int256(_maturityTime * 1 ether) + sumOverLastMonth) /
            1 ether;
    }

    /**
     * @dev calculate the deficit of a bond
     * @param _sumOfLiquidityFlow total liquidity flow for a given nonce
     * @param _benchmarkIR benchmark interest rate
     * @param _sumOfLiquidityOfLastNonce sum of liquidity flow for last month
     * @param deficit bond deficit
     */
    function _deficitOfBond(
        uint256 _sumOfLiquidityFlow,
        uint256 _benchmarkIR,
        uint256 _sumOfLiquidityOfLastNonce
    ) public pure returns (int256 deficit) {
        deficit =
            (int256(_sumOfLiquidityFlow) * (1 ether + int256(_benchmarkIR))) /
            1 ether -
            int256(_sumOfLiquidityOfLastNonce);
    }

    /**
     * @dev check if in crisis or not
     * @param _sumOfLiquidityFlow total liquidity flow for a given nonce
     * @param _benchmarkIR benchmark interest rate
     * @param _sumOfLiquidityOfLastNonce sum of liquidity flow for last month
     * @param crisis true if in crisis, false otherwise
     */
    function inCrisis(
        uint256 _sumOfLiquidityFlow,
        uint256 _benchmarkIR,
        uint256 _sumOfLiquidityOfLastNonce
    ) public pure returns (bool crisis) {
        int256 deficit = _deficitOfBond(
            _sumOfLiquidityFlow,
            _benchmarkIR,
            _sumOfLiquidityOfLastNonce
        );

        crisis = deficit > 0;
    }

    // Token Contract
    function getLockedBalance(
        uint256 _collateralisedSupply,
        uint256 _airdropSupply,
        uint256 _airdropBalance
    ) public pure returns (uint256 _lockedBalance) {
        // max 5% of collateralised supply can be transferred
        uint256 _maxUnlockable = _collateralisedSupply * 5;
        // multiplying by 100, since _maxUnlockable isn't divided by 100
        uint256 _currentAirdropSupply = _airdropSupply * 100;

        _lockedBalance = 0;
        if (_currentAirdropSupply > _maxUnlockable) {
            _lockedBalance =
                ((100 - (_maxUnlockable * 100) / _currentAirdropSupply) *
                    _airdropBalance) /
                100;
        }
        return _lockedBalance;
    }

    //Bank Contract
    function _cdpUsdToDBIT(uint256 _sCollateralised)
        public
        pure
        returns (uint256 amountDBIT)
    {
        amountDBIT = 1 ether;
        if (_sCollateralised >= 1000 ether) {
            amountDBIT = 1.05 ether;
            uint256 logCollateral = log2(_sCollateralised / 1000);
            amountDBIT = pow(amountDBIT, logCollateral);
        }
    }

    function _cdpDbitToDgov(uint256 _sCollateralised)
        public
        pure
        returns (uint256 amountDGOV)
    {
        amountDGOV = inv(
            100 ether + ((_sCollateralised * 1e9) / 33333 / 1e18)**2
        );
    }

    //helper_function
    function getBlockTimestamp() public view returns (uint256) {
        return block.timestamp;
    }

    function getProgress(uint256 _maturityDate, uint256 _periodTimestamp)
        public
        view
        returns (uint256 progressAchieved, uint256 progressRemaining)
    {
        progressRemaining = _maturityDate <= block.timestamp
            ? 0
            : ((_maturityDate - block.timestamp) * 100) / _periodTimestamp;
        progressAchieved = 100 - progressRemaining;
        return (progressAchieved, progressRemaining);
    }

    function getProgress2(
        uint256 _tokenTotalSupply,
        uint256 _tokenTotalSupplyAtNonce
    )
        public
        pure
        returns (uint256 progressAchieved, uint256 progressRemaining)
    {
        uint256 BsumNL = _tokenTotalSupply;
        uint256 BsumN = _tokenTotalSupplyAtNonce;
        uint256 BsumNInterest = BsumN + mul(BsumN, 5 * 10**16);

        progressRemaining = BsumNInterest < BsumNL ? 0 : 100;
        progressAchieved = 100 - progressRemaining;
    }

    //Automated Pair Maker
    function entriesAfterAddingLiq(
        uint256 oldEntries,
        uint256 amount,
        uint256 totalEntriesToken,
        uint256 totalReserveToken
    ) public pure returns (uint256 newEntries) {
        newEntries =
            oldEntries +
            (amount * totalEntriesToken) /
            totalReserveToken;
    }

    function entriesAfterRemovingLiq(
        uint256 oldEntries,
        uint256 amount,
        uint256 totalEntriesToken,
        uint256 totalReserveToken
    ) public pure returns (uint256 newEntries) {
        newEntries =
            oldEntries -
            (amount * totalEntriesToken) /
            totalReserveToken;
    }

    function getAmountOut(
        uint256 amountIn,
        uint256 reserveIn,
        uint256 reserveOut
    ) public pure returns (uint256 amountOut) {
        require(amountIn > 0, "APM: INSUFFICIENT_INPUT_AMOUNT");
        require(reserveIn > 0 && reserveOut > 0, "APM: INSUFFICIENT_LIQUIDITY");
        uint256 numerator = amountIn * reserveOut;
        uint256 denominator = reserveIn + amountIn;
        amountOut = numerator / denominator;
    }

    //Exchange
    function currentPrice(
        uint256 startingTime,
        uint256 duration,
        bool curvingPrice,
        uint256 maxCurrencyAmount,
        uint256 minCurrencyAmount
    ) public view returns (uint256 auctionPrice) {
        uint256 time_passed = block.timestamp - startingTime;
        require(time_passed < duration, "auction ended,equal to faceValue");
        if (!curvingPrice) {
            // for fixed rate , there will be using the straight line fixed price decreasing mechanism.
            auctionPrice =
                maxCurrencyAmount -
                ((maxCurrencyAmount - minCurrencyAmount) * time_passed) /
                duration;
        }
        // else  if  its the floating rate, there will be decreasing parabolic curve as function of
        else {
            auctionPrice =
                maxCurrencyAmount -
                ((maxCurrencyAmount - minCurrencyAmount) * (time_passed**2)) /
                (duration**2);
        }
    }
}
