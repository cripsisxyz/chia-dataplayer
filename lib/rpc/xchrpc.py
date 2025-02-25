import logging
import requests
import json
from os.path import expanduser
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from lib.dealermath.dealermath import DealerMath

class RemoteProcedureCall:
    def __init__(self, host="127.0.0.1", port=9256,
                 private_wallet_cert_path="~/.chia/mainnet/config/ssl/wallet/private_wallet.crt",
                 private_wallet_key_path="~/.chia/mainnet/config/ssl/wallet/private_wallet.key",
                 network_fee=1000):
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        self.host = host
        self.port = port
        self.network_fee = network_fee
        self.default_rpc_headers = {'Content-Type': 'application/json'}
        self.default_wallet_certs = (expanduser(private_wallet_cert_path), expanduser(private_wallet_key_path))

        logging.debug(f"RPC connector set to {self.host}:{self.port} using certs {self.default_wallet_certs}")

    def _send_request(self, endpoint, request_data):
        url = f"https://{self.host}:{self.port}/{endpoint}"
        try:
            response = requests.post(url, headers=self.default_rpc_headers, json=request_data,
                                     cert=self.default_wallet_certs, verify=False)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"RPC request to {endpoint} failed: {e}")
            return None

    def check_available_wallets(self):
        logging.debug("Checking available RPC Chia wallets")
        response = self._send_request("get_wallets", {"wallet_id": "*"})
        if response:
            wallets = response.get('wallets', [])
            logging.info(f"Available wallets: {wallets}")
            return wallets
        return []

    def check_wallets_synced(self):
        logging.debug("Checking Chia wallets sync status")
        response = self._send_request("get_sync_status", {})
        if response:
            if response.get("syncing"):
                logging.info("Wallets are syncing with network")
            if response.get("synced"):
                logging.debug("Wallets are correctly synced with network")
                return True
            logging.warning("Wallets are NOT synced with network")
        return False

    def check_wallet_balance(self, wallet_id):
        logging.debug(f"Checking XCH balance for wallet ID {wallet_id}")
        response = self._send_request("get_wallet_balance", {"wallet_id": wallet_id})
        if response:
            max_mojo = response.get("wallet_balance", {}).get("max_send_amount", 0)
            max_xch = DealerMath.mojo_to_xch_str(max_mojo)
            logging.info(f"Available balance: {max_mojo} MOJOs == {max_xch} XCH")
            return max_mojo, max_xch
        return 0, "0"

    def datalayer_get_owned_stores(self):
        logging.debug("Getting owned stores")
        response = self._send_request("get_owned_stores", {})
        if response and response.get("success"):
            logging.info(f"Owned data stores: {response}")
            return response
        logging.error("Failed to fetch owned stores")
        return None

    def datalayer_update_owned_store(self, store_id, change_list):
        logging.info(f"Updating Store: {store_id}")
        response = self._send_request("batch_update", {"id": store_id, "changelist": change_list, "fee": self.network_fee})
        if response and response.get("success"):
            logging.info("Update successful")
            return response
        logging.error(f"Failed to update store: {store_id}")
        return None

    def datalayer_get_value(self, store_id, key):
        logging.debug(f"Fetching Key: {key} for Store: {store_id}")
        response = self._send_request("get_value", {"id": store_id, "key": key})
        if response and response.get("success"):
            logging.info("Fetch successful")
            return response
        logging.error(f"Failed to fetch key: {key}")
        return None

    def datalayer_delete_key(self, store_id, key):
        logging.debug(f"Deleting Key: {key} from Store: {store_id}")
        response = self._send_request("delete_key", {"id": store_id, "key": key, "fee": self.network_fee})
        if response and response.get("success"):
            logging.info("Deletion successful")
            return response
        logging.error(f"Failed to delete key: {key}")
        return None

    def datalayer_get_keys(self, store_id):
        logging.debug(f"Listing keys for Store: {store_id}")
        response = self._send_request("get_keys", {"id": store_id})
        if response and response.get("success"):
            logging.info("Fetch successful")
            return response
        logging.error(f"Failed to list keys for store: {store_id}")
        return None
