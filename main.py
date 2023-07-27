# coding=utf8
import json
import requests
from web3 import Web3, Account
from web3.contract import Contract
from eth_typing import Address
from eth_typing import HexStr
from loguru import logger
import time
import random


class MyEtherUtils():

    zero_address = '0x'+''.zfill(40)

    def __init__(self, wb3: Web3):
        self.web3: Web3 = wb3

    def load_abi(self, name):
        abi_save_file = f'./{name}-abi.json'

        with open(abi_save_file, 'r') as f:
            json_data = json.load(f)
            return json_data

    def check_allowance(self, from_token_address: str, address_wallet: Address, spender: str) -> float:
        try:
            contract = self.web3.eth.contract(address=self.web3.to_checksum_address(from_token_address),
                                        abi=self.load_abi('erc20'))
            amount_approved = contract.functions.allowance(address_wallet, spender).call()
            return amount_approved

        except Exception as ex:
            logger.error(f'Something went wrong | {ex}')

    def get_contract(self, from_token_address: str) -> Contract:
        return self.web3.eth.contract(address=self.web3.to_checksum_address(from_token_address),
                             abi=self.load_abi('erc20'))

    def add_gas_price(self) -> int:
        try:
            gas_price = self.web3.eth.gas_price
            gas_price = int(gas_price * random.uniform(1.01, 1.02))
            return gas_price
        except Exception as ex:
            logger.error(f'Something went wrong | {ex}')

    def add_gas_limit(self, tx: dict) -> int:
        tx['value'] = 0
        gas_limit = self.web3.eth.estimate_gas(tx)

        return gas_limit

    def approve_token(self, amount: float, account, chain: str, from_token_address: str, spender: str) -> HexStr:
        try:
            spender = self.web3.to_checksum_address(spender)
            contract = self.get_contract(from_token_address)
            allowance_amount = self.check_allowance(from_token_address, account.address, spender)

            if amount > allowance_amount:
                tx = contract.functions.approve(
                    spender,
                    amount
                ).build_transaction(
                    {
                        'chainId': self.web3.eth.chain_id,
                        'from': account.address,
                        'nonce': self.web3.eth.get_transaction_count(account.address),
                        'gasPrice': 0,
                        'gas': 0,
                        'value': 0
                    }
                )
                if chain == 'bsc':
                    tx['gasPrice'] = random.randint(1000000000, 1050000000)
                else:
                    gas_price = self.add_gas_price()
                    tx['gasPrice'] = gas_price

                gas_limit = self.add_gas_limit(tx)
                tx['gas'] = gas_limit

                signed_tx = account.signTransaction(tx)
                raw_tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
                tx_receipt = self.web3.eth.wait_for_transaction_receipt(raw_tx_hash)
                while tx_receipt is None:
                    time.sleep(1)
                    tx_receipt = self.web3.eth.get_transaction_receipt(raw_tx_hash)
                tx_hash = self.web3.to_hex(raw_tx_hash)
                logger.info(f'Token approved | Tx hash: {tx_hash}')
                time.sleep(3)
                return tx_hash

        except Exception as ex:
            logger.error(f'Something went wrong | {ex}')


class Etherscan():

    def __init__(self, key, network='mainnet'):
        self.key = key
        if network == 'mainnet':
            self.host = f"https://cn.etherscan.io"
            self.api_host = 'https://api.etherscan.io'

        if network == 'goerli':
            self.host = f"https://cn.etherscan.io"
            self.api_host = 'https://api-goerli.etherscan.io'

        if network == 'sepolia':
            self.host = f"https://cn.etherscan.io"
            self.api_host = 'https://api-sepolia.etherscan.io'

    def get_ether_price(self):
        params = {
            'module': 'stats',
            'action': 'ethprice',
            'apikey': self.key
        }
        res = requests.get(f'{self.api_host}/api', params=params)
        if res.status_code == 200 and res.json()['status'] == '1':
            return float(res.json()['result']['ethusd'])

        return None

class Izumi():

    def __init__(self, coin_from, coin_to, amount, account_key, scan_key='', splipage=0.005):
        self.web3: Web3 = Web3(Web3.HTTPProvider('https://mainnet.era.zksync.io'))
        self.coin_from = coin_from
        self.coin_to = coin_to
        self.amount = amount
        self.account_key = account_key
        self.scan_key = scan_key
        self.splipage = splipage

    def get_path(self, token_chain: list, fee_chain: list):
        hex_str = token_chain[0]
        for i in range(len(fee_chain)):
            hex_str += self.fee_2_hex(fee_chain[i])
            hex_str += token_chain[i+1]

        return hex_str

    def fee_2_hex(self, fee: int):
        n0 = fee % 16
        n1 = (fee // 16) % 16
        n2 = (fee // 256) % 16
        n3 = (fee // 4096) % 16
        n4 = 0
        n5 = 0
        return '0x' + self.num_2_hex(n5) + self.num_2_hex(n4) + self.num_2_hex(n3) + self.num_2_hex(
            n2) + self.num_2_hex(n1) + self.num_2_hex(n0)

    def num_2_hex(self, num: int):

        if num < 10:
            return str(num)
        strs = 'ABCDEF'
        return strs[num - 10]

    def log(self, log_str):
        logger.info(log_str)

    def swap(self):
        Account.enable_unaudited_hdwallet_features()
        if len(self.account_key.split(' ')) == 12:
            # use 12words mnemonic seeds
            # 使用12个单次的助记词
            account = self.web3.eth.account.from_mnemonic(self.account_key)
        else:
            # use private key
            # 使用私钥
            account = self.web3.eth.account.from_key(self.account_key)

        utils = MyEtherUtils(self.web3)

        coin_map = {
            'eth': '0x5aea5775959fbc2557cc8789bc1bf90a239d9a91',
            'usdc': '0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4',
            'usdt': '0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4'
        }

        swap_contract_address               = '0x943ac2310D9BC703d6AB5e5e76876e212100f894'
        share_liquit_usdt_contract_address  = '0x496d88D1EFc3E145b7c12d53B78Ce5E7eda7a42c'
        router_contract_address             = '0x6C31035D62541ceba2Ac587ea09891d1645D6D07'

        izumi_contract = self.web3.eth.contract(
            address=Web3.to_checksum_address(swap_contract_address),
            abi=utils.load_abi('izumi-swap'))

        es = Etherscan(key=self.scan_key)
        eth_price = es.get_ether_price()
        # print(eth_price)
        # return
        if not eth_price:
            self.log('get mainnet eth price error,plz check!')
            return
        else:
            self.log(f'eth price {eth_price} usd')

        # if add other coin address for swap, get the coin decimal num and check the real swap value num
        # 如果加了其他的coin地址去swap，需要完善，自己获取coin的小数位，得到实际的交换值
        if self.coin_from.lower() == 'eth':
            value = int(self.amount*10e17)  # eth
        elif self.coin_from.lower() == 'usdt': # sludst
            value = int(self.amount*10e17)
        else: # usdc
            value = int(self.amount*10e5)  # stable coin


        deadline = int(self.web3.eth.get_block('latest').timestamp) + 1200
        if (self.coin_from == 'eth' and self.coin_to == 'usdc') or (self.coin_from == 'usdc' and self.coin_to == 'eth'):
            fee = 2000 # 0.2%
            token_chain = [
                self.web3.to_checksum_address(coin_map[self.coin_from]), 
                self.web3.to_checksum_address(coin_map[self.coin_to])
            ]
            fee_chain = [fee]
        if (self.coin_from == 'eth' and self.coin_to == 'usdt') or (self.coin_from == 'usdt' and self.coin_to == 'eth'):
            fee = 400 # 0.04%
            if self.coin_from == 'eth':
                token_chain = [
                    self.web3.to_checksum_address(coin_map[self.coin_from]),
                    self.web3.to_checksum_address(coin_map[self.coin_to]),
                    self.web3.to_checksum_address(share_liquit_usdt_contract_address)
                ]
            if self.coin_from == 'usdt': # 逆序
                token_chain = [
                    self.web3.to_checksum_address(share_liquit_usdt_contract_address),
                    self.web3.to_checksum_address(coin_map[self.coin_from]),
                    self.web3.to_checksum_address(coin_map[self.coin_to]),
                ]
            fee_chain = [fee, fee]
        path = self.get_path(token_chain, fee_chain)
        # 去掉字符串中的 '0x' 部分
        # remove “0x” part
        path = path.replace("0x", "")

        if self.coin_from == 'usdc':
            utils.approve_token(amount=value,
                                account=account,
                                chain='ERA',
                                from_token_address=coin_map[self.coin_from],
                                spender=swap_contract_address,
                                )
                                
        if self.coin_from == 'usdt':
            utils.approve_token(amount=value,
                                account=account,
                                chain='ERA',
                                from_token_address=share_liquit_usdt_contract_address,
                                spender=router_contract_address,
                                )

        if self.coin_from.lower() == 'eth':
            min_get = self.amount * eth_price * 10e5
        else:
            min_get = self.amount / eth_price * 10e17
        # 0.2% token fee, 0.5% splipage, min get 99.5%
        # 有千2的交易税费，考虑使用千5的滑点，计算最小的获得值，即千2的税已经包含在千5以内了
        # 所以交易滑点要大于千2，保险起见写千5，直接写千2会失败
        min_get = int(min_get * (1-self.splipage))
        args = [[
            Web3.to_bytes(hexstr=path),
            account.address if self.coin_from == 'eth' else Web3.to_checksum_address(utils.zero_address),
            value,
            min_get,
            deadline,
        ]]
        encode_data = izumi_contract.encodeABI(fn_name='swapAmount', args=args)
        # print(encode_data)
        if self.coin_from.lower() == 'eth':
            call_args = [
                encode_data,
                Web3.to_bytes(hexstr='0x12210e8a')  # refundETH 4bytes method-id
            ]
        else:
            call_args = [
                encode_data,
                izumi_contract.encodeABI(fn_name='unwrapWETH9', args=[
                    0,
                    account.address
                ])
            ]
        tx = izumi_contract.functions.multicall(call_args).build_transaction({
            'value': value if self.coin_from.lower() == 'eth' else 0,
            'nonce': self.web3.eth.get_transaction_count(account.address),
            'from': account.address,
            'maxFeePerGas': 0,
            'maxPriorityFeePerGas': 0,
            'gas': 0
        })

        tx.update({'maxFeePerGas': self.web3.eth.gas_price})
        tx.update({'maxPriorityFeePerGas': self.web3.eth.gas_price})

        gas_limit = self.web3.eth.estimate_gas(tx)
        tx.update({'gas': gas_limit})
        signed_tx = account.signTransaction(tx)
        raw_tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_hash = self.web3.to_hex(raw_tx_hash)
        self.log(f'Swapped success！ | TX: https://explorer.zksync.io/tx/{tx_hash}')


if __name__ == "__main__":
    pass