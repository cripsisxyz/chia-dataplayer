import logging
from binascii import unhexlify, hexlify
from cose.messages import Mac0Message, CoseMessage
from cose.keys import CoseKey
from cose.algorithms import HMAC256
from cose.headers import Algorithm, KID
from cose.keys.keyparam import KpKty, SymKpK, KpKeyOps
from cose.keys.keytype import KtySymmetric
from cose.keys.keyops import MacCreateOp, MacVerifyOp

class Serializer():

    def __init__(self, cose_key=str):
        
        self.cose_key = CoseKey.from_dict({
            KpKty: KtySymmetric,
            SymKpK: unhexlify(bytes(cose_key, encoding='utf-8')),
            KpKeyOps: [MacCreateOp, MacVerifyOp]
        })

    def cose_encode(self, message, protected_headers={}, unprotected_headers={}):
        msg = Mac0Message(
            phdr = {Algorithm: HMAC256, **protected_headers},
            uhdr = {**unprotected_headers},
            payload = message.encode('utf-8')
            )
      
        msg.key = self.cose_key
        encoded = msg.encode()
        
        return hexlify(encoded).hex()

    def cose_decode(self, message):
        message = unhexlify(message)
        
        try:
            decoded = CoseMessage.decode(message)
        except AttributeError as e:
            logging.error(f"Cannot decode COSE message, are you sure you are using the correct codec? Desc: {str(e)}")
            exit(1)

        decoded.key = self.cose_key

        if decoded.verify_tag():
            ph = decoded.phdr
            for k, v in ph.items():
                if "abc.ABCMeta" in str(type(k)):
                    del ph[k]
                    break
            return({"payload": str(decoded.payload.decode('ascii')), "protected_headers": ph, "unprotected_headers": decoded.uhdr})
        else:
            pass
            
    def hex_encode(self, message):
        return(hexlify(message.encode()).decode())
    
    def hex_decode(self, message):
        return(unhexlify(message).decode())