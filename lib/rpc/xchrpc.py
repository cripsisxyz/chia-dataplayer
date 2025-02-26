import logging
import uvicorn
import requests
import json
from os.path import expanduser
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from lib.dealermath.dealermath import DealerMath

logger = logging.getLogger("uvicorn")

class RemoteProcedureCall:
    def __init__(self, host="127.0.0.1", port=9256,
                 private_wallet_cert_path="~/.chia/mainnet/config/ssl/wallet/private_wallet.crt",
                 private_wallet_key_path="~/.chia/mainnet/config/ssl/wallet/private_wallet.key",
                 network_fee=1000):
        """
        Initialize the RPC connection with default settings.
        """
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        self.host = host
        self.port = port
        self.network_fee = network_fee
        self.default_rpc_headers = {'Content-Type': 'application/json'}
        self.default_wallet_certs = (expanduser(private_wallet_cert_path), expanduser(private_wallet_key_path))

        logger.debug(f"RPC connector set to {self.host}:{self.port} using certs {self.default_wallet_certs}")

    def _send_request(self, endpoint, request_data):
        """
        Send a request to the Chia RPC endpoint.
        """
        url = f"https://{self.host}:{self.port}/{endpoint}"

        try:
            response = requests.post(url, headers=self.default_rpc_headers, json=request_data,
                                     cert=self.default_wallet_certs, verify=False)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            return {"error": f"HTTP error: {http_err}"}
        except requests.exceptions.ConnectionError as conn_err:
            logger.error(f"Connection error occurred: {conn_err}")
            return {"error": f"Connection error: {conn_err}"}
        except requests.exceptions.Timeout as timeout_err:
            logger.error(f"Timeout error occurred: {timeout_err}")
            return {"error": f"Timeout error: {timeout_err}"}
        except requests.exceptions.RequestException as req_err:
            logger.error(f"An error occurred: {req_err}")
            return {"error": f"Request error: {req_err}"}


    def check_available_wallets(self):
        """
        Check available wallets in Chia RPC.
        """
        logger.debug("Checking available RPC Chia wallets")
        response = self._send_request("get_wallets", {"wallet_id": "*"})
        if response and "error" not in response:
            wallets = response.get('wallets', [])
            logger.info(f"Available wallets: {wallets}")
            return wallets
        return {"error": "Failed to fetch wallets"}

    def check_wallets_synced(self):
        """
        Check if Chia wallets are synced with the network.
        """
        logger.debug("Checking Chia wallets sync status")
        response = self._send_request("get_sync_status", {})
        if response and "error" not in response:
            if response.get("syncing"):
                logger.info("Wallets are syncing with network")
            if response.get("synced"):
                logger.debug("Wallets are correctly synced with network")
                return True
            logger.warning("Wallets are NOT synced with network")
        return {"error": "Failed to check sync status"}

    def check_wallet_balance(self, wallet_id):
        """
        Retrieve the XCH balance for a given wallet ID.
        """
        logger.debug(f"Checking XCH balance for wallet ID {wallet_id}")
        response = self._send_request("get_wallet_balance", {"wallet_id": wallet_id})
        if response and "error" not in response:
            max_mojo = response.get("wallet_balance", {}).get("max_send_amount", 0)
            max_xch = DealerMath.mojo_to_xch_str(max_mojo)
            logger.info(f"Available balance: {max_mojo} MOJOs == {max_xch} XCH")
            return max_mojo, max_xch
        return {"error": "Failed to fetch wallet balance"}

    def datalayer_get_owned_stores(self):
        """
        Retrieve a list of owned stores in Chia Data Layer.
        """
        logger.debug("Getting owned stores")
        response = self._send_request("get_owned_stores", {})
        if response and "error" not in response and response.get("success"):
            logger.info(f"Owned data stores: {response}")
            return response
        logger.error("Failed to fetch owned stores")
        return {"error": "Failed to fetch owned stores"}

    def datalayer_update_owned_store(self, store_id, change_list):
        """
        Update an existing store in Chia Data Layer.
        """
        logger.info(f"Updating Store: {store_id}")

        response = None

        try:
            response = self._send_request("batch_update", {"id": store_id, "changelist": change_list, "fee": self.network_fee})
            if response and response.get("success"):
                logger.info("Update successful")
                return response
            logger.error(f"Failed to update store: {store_id}, Response: {response}")
        except Exception as e:
            logger.error(f"Exception in datalayer_update_owned_store: {e}")

        return None

    def datalayer_get_value(self, store_id, key):
        """
        Retrieve a specific key from a store in Chia Data Layer.
        """
        logger.debug(f"Fetching Key: {key} for Store: {store_id}")
        response = self._send_request("get_value", {"id": store_id, "key": key})
        if response and response.get("success"):
            logger.info("Fetch successful")
            return response
        logger.error(f"Failed to fetch key: {key}")
        return None

    def datalayer_delete_key(self, store_id, key):
        """
        Delete a specific key from a store in Chia Data Layer.
        """
        logger.debug(f"Deleting Key: {key} from Store: {store_id}")
        response = self._send_request("delete_key", {"id": store_id, "key": key, "fee": self.network_fee})
        if response and response.get("success"):
            logger.info("Deletion successful")
            return response
        logger.error(f"Failed to delete key: {key}")
        return None

    def datalayer_get_keys(self, store_id):
        """
        Retrieve all keys from a store in Chia Data Layer.
        """
        logger.debug(f"Listing keys for Store: {store_id}")
        response = self._send_request("get_keys", {"id": store_id})
        if response and response.get("success"):
            logger.info("Fetch successful")
            return response
        logger.error(f"Failed to list keys for store: {store_id}")
        return None

    def create_data_store(self, fee=None):
        """
        Create a new data store in Chia Data Layer.
        """
        logger.info("Creating new data store")
        request_data = {"fee": str(fee) if fee else str(self.network_fee)}
        response = self._send_request("create_data_store", request_data)
        if response and response.get("success"):
            logger.info("Data store created successfully")
            return response
        logger.error("Failed to create data store")
        return None
