from main import Izumi
# you private key or 12 words mnemonic seeds
# 你的私钥或者助记词，会自动判断
you_account_key = ''
# etherscan apikey, not nessasary
# https://etherscan.io/register 注册获取, 只调用获取eth 价格的接口的话，无需key
you_ether_scan_key = ''
swap_amount = 0.0001  # coin_from交换的数量，如coin_from是eth，coin_to是usdc，则代表是用0.0001的eth兑换成等值的usdc，具体能兑换多少看当前eth价格
coin_from = 'eth'
coin_to = 'usdc'

izm = Izumi(coin_from=coin_from,
            coin_to=coin_to,
            amount=swap_amount,
            account_key=you_account_key,
            scan_key=you_ether_scan_key
            )
izm.swap()
