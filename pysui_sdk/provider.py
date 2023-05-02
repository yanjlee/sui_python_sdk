import uuid
import base64
from typing import Dict, Optional, Union
from .signer import SignedTransactionSerializedSig
import requests as rq


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

        def get_check_points(self, cursor: str = None, limit: int = 10, order: bool = False):
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
        def get_all_coins(self, address: str, cursor: str = None, limit: int = 10):
            return self.send_request_to_rpc(method="suix_getAllCoins", params=[address, cursor, limit])

        def get_coin_metadata(self, coin_type: str):
            return self.send_request_to_rpc(method="suix_getCoinMetadata", params=[coin_type])

        def get_coins(self, address: str, coin_type: str = '0x2::sui::SUI', cursor: str = None, limit: int = 10):
            return self.send_request_to_rpc(method="suix_getCoins", params=[address, coin_type, cursor, limit])

        # example epoch="5000"
        def get_committee_info(self, epoch: str = None):
            return self.send_request_to_rpc(method="suix_getCommitteeInfo", params=[epoch])

        def get_dynamic_field_object(self, parent_object_id: str, dynamic_field_name: str):
            return self.send_request_to_rpc(method="suix_getDynamicFieldObject", params=[parent_object_id, dynamic_field_name])

        def get_dynamic_fields(self, parent_object_id: str, cursor: str = None, limit: int = 10):
            return self.send_request_to_rpc(method="suix_getDynamicFields", params=[parent_object_id, cursor, limit])

        def split_coins(self, address: str, coin_object_id: str, split_amount: list[str], gas=None, gas_budget="100000"):
            return self.send_request_to_rpc(method="unsafe_splitCoin", params=[
                address,
                coin_object_id,
                split_amount,
                gas,
                gas_budget
            ])

        def transfer_objects(self, address: str, transfer_object_id: str, recipient: str, gas=None, gas_budget="100000"):
            return self.send_request_to_rpc(method="unsafe_transferObject", params=[
                address,
                transfer_object_id,
                gas,
                gas_budget,
                recipient
            ])

        def pay_all_sui(self, address: str, sui_object_ids: list[str], recipient: str, gas_budget="100000"):
            return self.send_request_to_rpc(method="unsafe_payAllSui", params=[
                address,
                sui_object_ids,
                recipient,
                gas_budget,
            ])

        def pay_sui(self, address: str, sui_object_ids: list[str], recipients: list[str], amounts: list[str], gas_budget="100000"):
            return self.send_request_to_rpc(method="unsafe_paySui", params=[
                address,
                sui_object_ids,
                recipients,
                amounts,
                gas_budget,
            ])

        def get_latest_sui_system_state(self):
            return self.send_request_to_rpc(method="suix_getLatestSuiSystemState", params=[])

        def get_owned_objects(self, address: str, query: str, cursor: str = None, limit: int = 10):
            return self.send_request_to_rpc(method="suix_getOwnedObjects", params=[
                address,
                query,
                cursor,
                limit
            ])

        def get_reference_gas_price(self):
            return self.send_request_to_rpc(method="suix_getReferenceGasPrice", params=[])

        def get_stakes(self, address: str):
            return self.send_request_to_rpc(method="suix_getStakes", params=[
                address
            ])

        def get_stakes_by_ids(self, staked_sui_ids: list[str]):
            return self.send_request_to_rpc(method="suix_getStakesByIds", params=[
                staked_sui_ids
            ])

        def get_total_supply(self, coin_type: str = '0x2:sui:SUI'):
            return self.send_request_to_rpc(method="suix_getTotalSupply", params=[
                coin_type
            ])

        def get_validators_apy(self):
            return self.send_request_to_rpc(method="suix_getValidatorsApy", params=[])

        def query_transaction_blocks(self, query: dict, cursor: str = None, limit: int = 10, order: bool = False):
            return self.send_request_to_rpc(method="suix_queryTransactionBlocks", params=[
                query,
                cursor,
                limit,
                order
            ])

        def resolve_name_service_address(self, name: str):
            return self.send_request_to_rpc(method="suix_resolveNameServiceNames", params=[
                name
            ])

        # this is a websocket stream
        def subscribe_event(self):
            pass

        # this is a websocket stream
        def subscribe_transaction(self):
            pass

        def batch_transaction(self,
                              address: str,
                              single_transaction_params: list[str],
                              gas: str = None,
                              gas_budget: str = "10000",
                              txn_builder_mode: str = None
                              ):
            return self.send_request_to_rpc(method="unsafe_batchTransaction", params=[
                address,
                single_transaction_params,
                gas,
                gas_budget,
                txn_builder_mode
            ])

        def merge_coin(self,
                       address: str,
                       primary_coin: str,
                       coin_to_merge: str,
                       gas: str = None,
                       gas_budget: str = "10000"):
            return self.send_request_to_rpc(method="unsafe_mergeCoins", params=[
                address,
                primary_coin,
                coin_to_merge,
                gas,
                gas_budget
            ])

        def pay(self,
                address: str,
                input_coins: list[str],
                recipients: list[str],
                amounts: list[str],
                gas: str = None,
                gas_budget: str = "10000"
                ):
            return self.send_request_to_rpc(method="unsafe_Pay", params=[
                address,
                input_coins,
                recipients,
                amounts,
                gas,
                gas_budget
            ])

        def publish(self,
                    address: str,
                    compiled_modules: list[base64],
                    dependencies: list[str],
                    gas: str = None,
                    gas_budget: str = "10000"
                    ):

            return self.send_request_to_rpc(method="unsafe_publish", params=[
                address,
                compiled_modules,
                dependencies,
                gas,
                gas_budget
            ])

        def request_add_stack(self,
                              address: str,
                              coins: list[str],
                              amount: int,
                              validator: str, #  the validator's Sui address
                              gas: str = None,
                              gas_budget: str = "10000"
                              ):
            return self.send_request_to_rpc(method="unsafe_requestAddStake", params=[
                address,
                coins,
                amount,
                validator,
                gas,
                gas_budget
            ])

        def request_withdraw_stake(self, address: str, staked_sui: str, gas: str = None, gas_budget: str = "10000"):
            return self.send_request_to_rpc(method="unsafe_requestWithdrawStake", params=[
                address,
                staked_sui,
                gas,
                gas_budget
            ])

        def split_coin_equal(self, address: str, coin_object_id: str, split_count: int, gas: str = None, gas_budget: str = "10000"):
            return self.send_request_to_rpc(method="unsafe_splitCoinEqual", params=[
                address,
                coin_object_id,
                split_count,
                gas,
                gas_budget
            ])

        def transfer_sui(self, address: str, sui_object_id: str, recipient: str, amount: str, gas_budget: str = "10000"):
            return self.send_request_to_rpc(method="unsafe_transferSui", params=[
                address,
                sui_object_id,
                gas_budget,
                recipient,
                amount,
            ])