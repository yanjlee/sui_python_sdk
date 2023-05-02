import requests as rq
import uuid
import base64
from typing import Dict, Optional, Union
from .signer import SignedTransactionSerializedSig


class ExecuteTransactionRequestType:
    ImmediateReturn = "ImmediateReturn"
    WaitForTxCert = "WaitForTxCert"
    WaitForEffectsCert = "WaitForEffectsCert"
    WaitForLocalExecution = "WaitForLocalExecution"


class SuiJsonRpcProvider:

    def __init__(self,
                 rpc_url: str,
                 faucet_url: str = None,
                 session_headers: Dict = None):
        self.session = rq.Session()
        self.session.headers.update(session_headers or {})

        self.rpc_url = rpc_url
        self.faucet_url = faucet_url

    def request_tokens_from_faucet(self, addr: str):
        return self.session.post(self.faucet_url, json={"FixedAmountRequest": {"recipient": addr}}).json()

    def send_request_to_rpc(self,
                            method: str,
                            params: list = None,
                            request_id: str = None):
        return self.session.post(self.rpc_url,
                                 json={
                                     "jsonrpc": "2.0",
                                     "method": method,
                                     "params": params or [],
                                     "id": request_id or str(uuid.uuid4()),
                                 }).json()

    def batch_send_request_to_rpc(self,
                                  methods: list,
                                  params: list = None,
                                  request_ids: list = None):
        return self.session.post(self.rpc_url,
                                 json=[{
                                     "jsonrpc": "2.0",
                                     "method": methods[i],
                                     "params": params[i] if (
                                             isinstance(params, list) and params[i] is not None) else [],
                                     "id": request_ids[i] if isinstance(request_ids, list) else str(uuid.uuid4()),
                                 } for i in range(len(methods))
                                 ]
                                 ).json()

    def get_dry_run_transaction_block(self, tx: str):
        return self.send_request_to_rpc(method="sui_dryRunTransactionBlock", params=[tx])

    def get_rpc_version(self):
        return self.send_request_to_rpc(method="rpc.discover")

    def get_balance_by_address_coin_type(self, addr: str, coin_type: str = '0x2::sui::SUI'):
        return self.send_request_to_rpc(method="suix_getBalance", params=[addr, coin_type])

    def get_all_balance_by_address(self, addr: str):
        return self.send_request_to_rpc(method="suix_getAllBalances", params=[addr])

    def get_object(self, object_id: str, options=None):
        if options is None:
            options = {
                "showType": True,
                "showOwner": True,
                "showPreviousTransaction": True,
                "showDisplay": False,
                "showContent": True,
                "showBcs": False,
                "showStorageRebate": True
            }
        return self.send_request_to_rpc(method="sui_getObject", params=[object_id, options])

    def get_move_function_arg_types(self, package_id: str, module_name: str, function_name: str):
        return self.send_request_to_rpc(method="sui_getMoveFunctionArgTypes",
                                        params=[package_id, module_name, function_name])

    def get_check_point(self, check_point_id: str = "1000"):
        return self.send_request_to_rpc(method="sui_getCheckpoint", params=[check_point_id])

    def get_check_points(self, cursor: str, limit: int = 10, order: bool = False):
        return self.send_request_to_rpc(method="sui_getCheckpoints", params=[cursor, limit, order])

    def get_events(self, tx_digest: str):
        return self.send_request_to_rpc(method="sui_getEvents", params=[tx_digest])

    def get_latest_checkpoint_sequence_number(self):
        return self.send_request_to_rpc(method="sui_getLatestCheckpointSequenceNumber")

    def get_loaded_child_objects(self, tx_digest: str):
        return self.send_request_to_rpc(method="sui_getLoadedChildObjects", params=[tx_digest])

    def get_normalized_move_module(self, package_id: str, module_name: str):
        return self.send_request_to_rpc(method="sui_getNormalizedMoveModule",
                                        params=[package_id, module_name])

    def get_normalized_move_function(self, package_id: str, module_name: str, function_name: str):
        return self.send_request_to_rpc(method="sui_getNormalizedMoveFunction",
                                        params=[package_id, module_name, function_name])

    def get_normalized_move_modules_by_package(self, package_id: str):
        return self.send_request_to_rpc(method="sui_getNormalizedMoveModulesByPackage",
                                        params=[package_id])

    def get_normalized_move_struct(self, package_id: str, module_name: str, struct_name: str):
        return self.send_request_to_rpc(method="sui_getNormalizedMoveStruct",
                                        params=[package_id, module_name, struct_name])

    # request_type is default to be `WaitForEffectsCert` unless options.show_events or options.show_effects is true
    # `request_type` must set to `None` or `WaitForLocalExecution`if effects is required in the response'
    def execute_transaction(self, signer: SignedTransactionSerializedSig):
        params = [
            signer.TxBytes,
            [signer.Signature],
            {
                "showInput": True,
                "showRawInput": True,
                "showEffects": True,
                "showEvents": True,
                "showObjectChanges": True,
                "showBalanceChanges": True
            },
            ExecuteTransactionRequestType.WaitForLocalExecution  # request_type
        ]
        # print(params)
        return self.send_request_to_rpc(method="sui_executeTransactionBlock",
                                        params=params)

    def get_total_transaction_number(self):
        return self.send_request_to_rpc(method="sui_getTotalTransactionBlocks")

    def get_transaction_block(self, tx_digest: str, options: dict = None):
        if options is None:
            options = {
                "showInput": True,
                "showRawInput": False,
                "showEffects": True,
                "showEvents": True,
                "showObjectChanges": False,
                "showBalanceChanges": False
            }

        return self.send_request_to_rpc(method="sui_getTransactionBlock", params=[tx_digest, options])

    def get_multi_get_objects(self, object_ids: list[str], options: dict = None):
        if options is None:
            pass  # todo test ...
        return self.send_request_to_rpc(method="sui_multiGetTransactionBlocks", params=[object_ids, options])

    def try_get_past_object(self, object_id: str, version: int = None, options: dict = None):
        if options is None:
            options = {
                "showType": True,
                "showOwner": True,
                "showPreviousTransaction": True,
                "showDisplay": False,
                "showContent": True,
                "showBcs": False,
                "showStorageRebate": True
            }
        return self.send_request_to_rpc(method="sui_tryGetPastObject", params=[object_id, version, options])

    def try_multi_get_past_objects(self, object_ids: list[str], options: dict = None):
        if options is None:
            options = {
                "showType": True,
                "showOwner": True,
                "showPreviousTransaction": True,
                "showDisplay": False,
                "showContent": True,
                "showBcs": False,
                "showStorageRebate": True
            }
        return self.send_request_to_rpc(method="sui_tryMultiGetPastObjects", params=[object_ids, options])

    # optional paging cursor, object_id
    def get_all_coins(self, address: str, cursor: str = '', limit: int = 10):
        return self.send_request_to_rpc(method="suix_getAllCoins", params=[address, cursor, limit])

    def get_coin_metadata(self, coin_type: str):
        return self.send_request_to_rpc(method="suix_getCoinMetadata", params=[coin_type])

    def get_coins(self, address: str, coin_type: str = '0x2::sui::SUI', cursor: str = '', limit: int = 10):
        return self.send_request_to_rpc(method="suix_getCoins", params=[address, coin_type, cursor, limit])

    # example epoch="5000"
    def get_committee_info(self, epoch: str = None):
        return self.send_request_to_rpc(method="suix_getCommitteeInfo", params=[epoch])

    def get_dynamic_field_object(self, parent_object_id: str, dynamic_field_name: str):
        return self.send_request_to_rpc(method="suix_getDynamicFieldObject", params=[parent_object_id, dynamic_field_name])

    def get_dynamic_fields(self, parent_object_id: str, cursor: str = '', limit: int = 10):
        return self.send_request_to_rpc(method="suix_getDynamicFields", params=[parent_object_id, cursor, limit])

    # def get_objects_owned_by_object(self, object_id: str):
    #     return self.send_request_to_rpc(method="sui_getObjectsOwnedByObject", params=[object_id])

    # def get_objects_owned_by_address(self, addr: str):
    #     return self.send_request_to_rpc(method="suix_getBalance", params=[addr])

    # def get_transactions(self,
    #                      query: Union[Dict, str] = None,
    #                      cursor: Optional[Union[Dict, str]] = None,
    #                      limit: Optional[int] = None,
    #                      order: str = "Descending"):
    #     return self.send_request_to_rpc(method="sui_getTransactions", params=[query, cursor, limit, order])

    # def get_transaction_with_effects(self, digest: str):
    #     return self.send_request_to_rpc(method="sui_getTransactionBlock", params=[digest])

    # def get_events_by_transaction(self, digest: str, limit: int = 100):
    #     return self.send_request_to_rpc(method="sui_getEventsByTransaction", params=[digest, limit])

    # def get_events_by_module(self, package: str, module: str, limit: int = 100, start_time: int = 0,
    #                          end_time: int = 2 ** 53 - 1):
    #     return self.send_request_to_rpc(method="sui_getEventsByModule",
    #                                     params=[package, module, limit, start_time, end_time])

    # def get_events_by_object(self, object_id: str, limit: int = 100, start_time: int = 0, end_time: int = 2 ** 53 - 1):
    #     return self.send_request_to_rpc(method="sui_getEventsByObject", params=[object_id, limit, start_time, end_time])

    # def get_total_transaction_in_range(self, start_of_range: int, end_of_range: int):
    #     return self.send_request_to_rpc(method="sui_getTransactionsInRange", params=[start_of_range, end_of_range])
