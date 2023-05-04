import base64

from .provider import SuiJsonRpcProvider
from .rpc_tx_data_serializer import RpcTxDataSerializer
from .wallet import SuiWallet
from .models import MoveCallTransaction
from typing import Optional, List
from .signer import TxnMetaData


class SignerWithProvider:

    def __init__(self,
                 provider: SuiJsonRpcProvider,
                 serializer: RpcTxDataSerializer,
                 signer_wallet: SuiWallet,
                 ):
        self.provider = provider
        self.serializer = serializer
        self.signer_wallet = signer_wallet

        self._rpc_minor_version: Optional[int] = None
        self._rpc_major_version: Optional[int] = None

    def get_address(self):
        return self.signer_wallet.get_address()

    def sign_data(self, data: bytes):
        return self.signer_wallet.sign_data(data)

    def request_sui_from_faucet(self):
        return self.provider.request_tokens_from_faucet(self.get_address())

    def sign_and_execute_transaction(self, tx_bytes: bytes):
        tx = TxnMetaData(tx_bytes)
        signer = tx.SignSerializedSigWith(self.signer_wallet.private_key)
        return self.provider.execute_transaction(signer)

    def split_sui_coin(self, amount: str):
        object_id = self.get_coin_object()
        res = self.provider.split_coins(self.signer_wallet.get_address(), object_id, [amount], None, "100000000")
        tx = res['result']['txBytes']
        res = self.sign_and_execute_transaction(tx)
        new_object_id = res['result']['effects']['created'][0]['reference']['objectId']
        return new_object_id

    def execute_move_call(self, tx_move_call: MoveCallTransaction):
        res = self.serializer.new_move_call(
            signer_addr=self.signer_wallet.get_address(),
            tx=tx_move_call)
        tx_bytes = res["result"]["txBytes"]

        res = self.provider.get_dry_run_transaction_block(tx_bytes)
        dry_run_status_map = res['result']['effects']['status']
        # check can execute by dry run but not real run, may fail by blow reason
        # 1, gas budget( solve: incr your gas budget)
        # 2, function limit , some nft one account can only mint once ( solve: check is it has mint before)
        # 3, no enough sui gas to execute the transaction
        # etc... see error msg
        if dry_run_status_map['status'] == 'failure':
            raise Exception(dry_run_status_map['error'])

        return self.sign_and_execute_transaction(tx_bytes)

    def _fetch_and_update_rpc_version(self):
        rpc_version_res = self.provider.get_rpc_version()
        version_str = rpc_version_res["result"]["info"]["version"]
        if isinstance(version_str, str) and len(version_str.split(".")) == 3:
            version_split = version_str.split(".")
            self._rpc_major_version = int(version_split[0])
            self._rpc_minor_version = int(version_split[1])

    def get_coin_object(self, transfer_coin_type: str = '0x2::sui::SUI') -> str:
        cursor = None
        limit = 10
        while 1:
            res = self.provider.get_all_coins(self.signer_wallet.get_address(), cursor, limit)
            object_list = res['result']['data']

            for obj_item in object_list:
                if obj_item['coinType'] != transfer_coin_type:
                    continue
                obj_id = obj_item['coinObjectId']
                return obj_id
            if res['result']['hasNextPage']:
                cursor = res['nextCursor']
            else:
                break

        return ''