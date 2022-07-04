from brownie import network, config, MathFunctions
from scripts.helpful_scripts import get_account


def deploy_math_functions():
    account = get_account()
    pp = MathFunctions.deploy({"from": account})
    output = pp.getLockedBalance(100, 100, 100)
    print(output)


def main():
    deploy_math_functions()
