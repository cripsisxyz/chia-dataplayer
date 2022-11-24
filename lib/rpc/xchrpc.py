import logging, requests, json
from os.path import expanduser
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from lib.dealermath.dealermath import DealerMath

class RemoteProcedureCall():

    def __init__(self, host="127.0.0.1", port=9256, private_wallet_cert_path="~/.chia/mainnet/config/ssl/wallet/private_wallet.crt", private_wallet_key_path="~/.chia/mainnet/config/ssl/wallet/private_wallet.key", network_fee=1000):
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        self.default_rpc_headers = {'Content-Type': 'application/json'}
        self.default_wallet_certs = (expanduser(private_wallet_cert_path), expanduser(private_wallet_key_path))
        self.host = host
        self.port = port
        self.network_fee = network_fee

        logging.debug(f"RPC connector set to {self.host}:{str(self.port)} using certs {str(self.default_wallet_certs)}")

    def check_available_wallets(self):
        logging.debug('Checking available RPC chia wallets')

        request_data = {"wallet_id": "*"}
        try:
            response = requests.post(f"https://{self.host}:{str(self.port)}/get_wallets", headers=self.default_rpc_headers, json=request_data, cert=self.default_wallet_certs, verify=False)
            response.raise_for_status()
        except Exception as e:
            logging.error(f"Cannot get available RPC chia wallets {str(e)}")
            return(False)
        else:
            available_wallets = json.loads(response.text)['wallets']
            logging.debug(f"Connection with chia RPC protocol sucessfull")
            logging.info(f"Available wallets: {available_wallets}")
            return(available_wallets)

    def check_wallets_synced(self):
        logging.debug(f"Checking chia wallets synced")

        request_data = {}
        try:
            response = requests.post(f"https://{self.host}:{str(self.port)}/get_sync_status", headers=self.default_rpc_headers, json=request_data, cert=self.default_wallet_certs, verify=False)
            response.raise_for_status()
        except Exception as e:
            logging.error(f"Cannot get RPC chia wallets sync status {str(e)}")
            return(False)
        else:
            loaded_json = json.loads(response.text)
            if loaded_json["syncing"]:
                logging.info(f"Wallets are syncing with network")

            if loaded_json["synced"]:
                logging.debug(f"Wallets are correctly synced with network")
            else:
                logging.warning(f"Wallets are NOT synced with network")
                return(False)

    def check_wallet_balance(self, wallet_id=int):
        logging.debug(f"Checking XCH balance on wallet id {str(wallet_id)}")

        request_data = {"wallet_id": wallet_id}
        try:
            response = requests.post(f"https://{self.host}:{str(self.port)}/get_wallet_balance", headers=self.default_rpc_headers, json=request_data, cert=self.default_wallet_certs, verify=False)
            response.raise_for_status()
        except Exception as e:
            logging.error(f"Cannot get available RPC chia wallets {str(e)}")
            return(False)
        else:
            max_send_amount_mojo = int(json.loads(response.text)["wallet_balance"]["max_send_amount"])
            max_send_amount_xch_str = DealerMath.mojo_to_xch_str(max_send_amount_mojo)
            logging.info(f"Available balance (max_send_amount): {str(max_send_amount_mojo)} MOJOs == {str(max_send_amount_xch_str)} XCH")

            return(max_send_amount_mojo, max_send_amount_xch_str)

    def datalayer_get_owned_stores(self):
        logging.debug(f"Getting owned stores")
        
        request_data = {}
        try:
            response = requests.post(f"https://{self.host}:{str(self.port)}/get_owned_stores", headers=self.default_rpc_headers, json=request_data, cert=self.default_wallet_certs, verify=False)
            response.raise_for_status()
        except Exception as e:
            logging.error(str(e))
            return(False)
        else:
            loaded_json = json.loads(response.text)
            if loaded_json["success"]:
                logging.info(f"Owned data stores: {loaded_json}")
                return(True)
            else:
                logging.error(f"Cannot found owned data stores {str(response.body)}")
            return(False)

    def datalayer_update_owned_store(self, store_id=str, change_list=list):
        logging.info(f"Updating Store: {store_id}")
        
        request_data = {
            "id": str(store_id),
            "changelist": list(change_list),
            "fee": int(self.network_fee)
        }
               
        try:
            response = requests.post(f"https://{self.host}:{str(self.port)}/batch_update", headers=self.default_rpc_headers, json=request_data, cert=self.default_wallet_certs, verify=False)
            response.raise_for_status()
        except Exception as e:
            logging.error(str(e))
            return(False)
        else:
            loaded_json = json.loads(response.text)
            if loaded_json["success"]:
                logging.info("Succesfull")
                return(loaded_json)
            else:
                logging.error(f"Cannot update Store: {str(response.text)}")
            return(False)
        
    def datalayer_get_value(self, store_id=str, key=str):
        logging.debug(f"Getting Key: {key} for Store: {store_id}")
        
        request_data = {
            "id": str(store_id),
            "key": str(key)
        }
        
        try:
            response = requests.post(f"https://{self.host}:{str(self.port)}/get_value", headers=self.default_rpc_headers, json=request_data, cert=self.default_wallet_certs, verify=False)
            response.raise_for_status()
        except Exception as e:
            logging.error(str(e))
            return(False)
        else:
            loaded_json = json.loads(response.text)
            if loaded_json["success"]:
                logging.info("Succesfull")
                return(loaded_json)
            else:
                logging.error(f"Cannot found Key. Desc: {str(loaded_json)}")
            return(False)
        
    def datalayer_delete_key(self, store_id=str, key=str):
        logging.debug(f"Deleting Key: {key} for Store: {store_id}")
        
        request_data = {
            "id": str(store_id),
            "key": str(key),
            "fee": int(self.network_fee)
        }
        
        try:
            response = requests.post(f"https://{self.host}:{str(self.port)}/delete_key", headers=self.default_rpc_headers, json=request_data, cert=self.default_wallet_certs, verify=False)
            response.raise_for_status()
        except Exception as e:
            logging.error(str(e))
            return(False)
        else:
            loaded_json = json.loads(response.text)
            print(loaded_json)
            if loaded_json["success"]:
                logging.info("Succesfull")
                return(loaded_json)
            else:
                logging.error(f"Cannot delete key. Desc: {str(loaded_json)}")
            return(False)
        
    def datalayer_get_keys(self, store_id=str):
        logging.debug(f"Listing Keys for Store: {store_id}")
        
        request_data = {
            "id": str(store_id)
        }
        
        try:
            response = requests.post(f"https://{self.host}:{str(self.port)}/get_keys", headers=self.default_rpc_headers, json=request_data, cert=self.default_wallet_certs, verify=False)
            response.raise_for_status()
        except Exception as e:
            logging.error(str(e))
            return(False)
        else:
            loaded_json = json.loads(response.text)
            if loaded_json["success"]:
                logging.info("Succesfull")
                return(loaded_json)
            else:
                logging.error(f"Cannot list keys. Desc: {str(loaded_json)}")
            return(False)