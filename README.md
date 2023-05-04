this project can only use for some simple methods or transaction

if you want to get more professional and complex methods or programmable transaction

please move here and use [pysui](https://github.com/FrankC01/pysui)


-------------

Python SDK to interact with Sui Blockchain 

forked from georgelombardi97/sui_python_sdk

remove some api witch has not include in sui json api list

add more json api

fix signing transactions signature method 


Supports creating wallets, fetching data, signing transactions 
# Install
``
pip install suiutils-py
``

Todo: 
- Better type checking
- Use objects instead of json or dict models 
- More functions & helpers   
- Add more examples 
- Add websocket support & event subscription 
- Add support for publishing move packages 

# How to Use 
### Import required objects

```python
from suiutils_py.wallet import SuiWallet
from suiutils_py.provider import SuiJsonRpcProvider
from suiutils_py.rpc_tx_data_serializer import RpcTxDataSerializer
from suiutils_py.signer_with_provider import SignerWithProvider
from suiutils_py.models import TransferObjectTransaction, TransferSuiTransaction, MoveCallTransaction
```

### Wallet 
```python
# Create wallet using a mnemonic
mnemonic = "all all all all all all all all all all all all"
my_wallet = SuiWallet(mnemonic=mnemonic)
# Create a new wallet with random address
random_wallet = SuiWallet.create_random_wallet()
```
```python
# Get address of your wallet 
my_wallet.get_address()
> '0xbb98ad0ae2f72677c6526d66ca3d3669c280c25a'
```
```python
random_wallet.get_address()
>'0x97534f7d430793fa4ff4619a5431c3d72fe8397d'
```

### Providers
```python
# Setup Providers
rpc_url = "https://fullnode.devnet.sui.io"
faucet_url ="https://faucet.devnet.sui.io/gas"

provider = SuiJsonRpcProvider(rpc_url=rpc_url, faucet_url=faucet_url)
serializer = RpcTxDataSerializer(rpc_url=rpc_url)
signer = SignerWithProvider(provider=provider, serializer=serializer, signer_wallet=my_wallet)
```

```python
# Request tokens to your wallet 
provider.request_tokens_from_faucet(my_wallet.get_address())
```

```python
# Create a move call transaction
tmp_move_call = MoveCallTransaction(
            package_object_id='0xe220547c8a45080146d09cbb22578996628779890d70bd38ee4cf2eb05a4777d',
            module="bluemove_x_testnet",
            function="mint_with_quantity",
            type_arguments=[

            ],
            arguments=[
                '0x9269c5575b5a949fe094723e600eb0835193c207916442b8ae2162ae838d4ab2',
                '1'
            ],
            gas_budget='10000000',
            gas_payment=None,
        )

# Sign and execute the transaction
tx_digest = signer.execute_move_call(tx_move_call=tmp_move_call)['result']['digest']
```

#### Fetch the Transaction
```python
# Get the transaction 
provider.get_transaction_block(tx_digest)
```
