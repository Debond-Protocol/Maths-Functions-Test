pragma solidity ^0.8.0;

// SPDX-License-Identifier: apache 2.0
/*
    Copyright 2021 Debond Protocol <info@debond.org>
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

contract MathFunctions {
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
}
