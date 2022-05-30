from scripts.helpful_scripts import get_account, encode_function_data, upgrade
from brownie import (
    Box,
    network,
    Contract,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    BoxV2,
)


def main():
    account = get_account()
    print(f"Deploying to {network.show_active()}")
    box = Box.deploy({"from": account})
    print(box.retrieve())

    # Deploys the proxy admin contract that manages the TransparentUpgradeableProxy contract
    proxy_admin = ProxyAdmin.deploy({"from": account})

    # initializer = box.store, 1
    # box_encoded_initializer_function = encoude_function_data(initializer)
    box_encoded_initializer_function = encode_function_data()

    # The TransparentUpgradeableProxy takes 3 variables:
    # 1. The address of the contract that contains the logic (The Box contract in our case)
    # 2. The address of the admin that manages the implementations to the proxy
    # 3. The data that should be passed. This could be an initialization function (equal to a contructor),
    # given by the encode_function_data function to encode it to the bytes format, necessary for the compiler
    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from": account, "gas_limit": 1000000},
    )

    print(f"Proxy deployed to {proxy}, you can now upgrade to v2!")
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    proxy_box.store(1, {"from": account})
    print(proxy_box.retrieve())

    # Upgrade Box to BoxV2
    box_V2 = BoxV2.deploy({"from": account})
    upgrade_transaction = upgrade(account, proxy, box_V2.address, proxy_admin)
    upgrade_transaction.wait(1)
    print("Proxy has been upgraded!")
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    proxy_box.increment({"from": account})
    print(proxy_box.retrieve())
