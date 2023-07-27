# en
python demo for izumiswap(zksync-era) exchange token，supprt eth->usdc,usdc->eth,eth->usdt,usdt->eth  swap
# cn
zksync-era链上izumiswap的兑换代币的python示例，支持 eth->usdc,usdc->eth,eth->usdt,usdt->eth  兑换

# pip install -r requirements.txt 安装依赖包
# code
```bash
from main import Izumi
# 你的私钥或者助记词，会自动判断
# your account pravite key or 12words mnemonic seeds, auto check
you_account_key = ''
# etherscan apikey not nessasary
# https://etherscan.io/register 注册获取, 此脚本非必须
you_ether_scan_key = ''
# splipage default 0.5%, if get "too much request" error, plz incry it, etc 0.01
# 交易滑点，默认千5，如果报了 “too much request” 错误，可以提升这个值，比如0.01，或者等主网gasfee比较低的时候，也能成功
splipage = 0.005
# coin_from交换的数量，如coin_from是eth，coin_to是usdc，则代表是用0.0001的eth兑换成等值的usdc，具体能兑换多少看当前eth价格
swap_amount = 0.0001
# 使用的代币
coin_from = 'eth'
# 兑换成的目标代币
coin_to = 'usdc'
# 想换回本币，对调coin_from和coin_to 即可
izm = Izumi(coin_from=coin_from,
            coin_to=coin_to,
            amount=swap_amount,
            account_key=you_account_key,
            scan_key=you_ether_scan_key,
            splipage=splipage
            )
izm.swap()
```
# 声明：看的懂代码的请小额测试一下，上来就全量兑换而导致财产损失本人概不负责
