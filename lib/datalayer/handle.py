import os, json, logging
from lib.datalayer.serial import Serializer

class Handler():
    
    def __init__(self, rpc_datalayer_instance):
        if os.getenv('COSE_KEY') is None:
            logging.warning("COSE_KEY environment variable not defined, USING A DEFAULT KEY for hex encodings")
            cose_key = "03d4f7f0611f28563a318c64f8b0852b"
        else:
            logging.info("COSE_KEY environment variable defined, using it")
            cose_key = os.getenv('COSE_KEY')
            
        self.serial = Serializer(cose_key=cose_key)
        self.rpc_instance = rpc_datalayer_instance

    def cose_push_data(self, store_id=str, store_key=str, msg_store_value=str, msg_protected_headers={}, msg_unprotected_headers={}):
        encoded_message = self.serial.cose_encode(message=msg_store_value, protected_headers=msg_protected_headers, unprotected_headers=msg_unprotected_headers)
        rpc_changelist = [{"action":"insert", "key": self.serial.hex_encode(store_key), "value": encoded_message}]
        return(json.dumps(self.rpc_instance.datalayer_update_owned_store(store_id=store_id, change_list=rpc_changelist), sort_keys=True, indent=2))

    def cose_read_data(self, store_id=str, store_key=str, return_value_object_only=False):
        key_value = self.rpc_instance.datalayer_get_value(store_id=store_id, key=self.serial.hex_encode(message=store_key))
        if not key_value:
            exit(1)
        key_value_hex = self.serial.hex_decode(message=key_value['value'])
        key_value['value'] = self.serial.cose_decode(message=key_value_hex)
        if return_value_object_only:
            return(key_value['value']['payload'])
        else:
            return(json.dumps(key_value, sort_keys=True, indent=2))

    def hex_push_data(self, store_id=str, store_key=str, msg_store_value=str):
        encoded_message = self.serial.hex_encode(message=msg_store_value)
        rpc_changelist = [{"action":"insert", "key": self.serial.hex_encode(store_key), "value": encoded_message}]
        return(json.dumps(self.rpc_instance.datalayer_update_owned_store(store_id=store_id, change_list=rpc_changelist), sort_keys=True, indent=2))
    
    def hex_read_data(self, store_id=str, store_key=str):
        key_value = self.rpc_instance.datalayer_get_value(store_id=store_id, key=self.serial.hex_encode(message=store_key))
        if not key_value:
            exit(1)
        key_value_hex = self.serial.hex_decode(message=key_value['value'])
        key_value['value'] = key_value_hex
        return(json.dumps(key_value, sort_keys=True, indent=2))
    
    def datastore_list_keys(self, store_id=str):
        keys = self.rpc_instance.datalayer_get_keys(store_id=store_id)
        keys_ascii = []
        for key in keys['keys']:
            if key.startswith('0x'):
                key = key[2:]
            try:
                ak = self.serial.hex_decode(message=key)
            except:
                ak = "UNKNOWN_CODING"
            keys_ascii.append(ak)
        keys["keys"] = keys_ascii
        return(json.dumps(keys, sort_keys=True, indent=2))

    def read_local_file(self, filepath=str):
        with open(filepath, mode="rb") as rawfile:
            b64_file = self.serial.base64_bencode(message=rawfile.read())
        return(b64_file)
    
    def write_local_file(self, filepath=str, filecontent=str):
        with open(filepath, mode="wb") as rawfile:
            rawfile.write(self.serial.base64_bdecode(filecontent))
        return(True)