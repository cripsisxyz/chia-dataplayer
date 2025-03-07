
## Description

Welcome to Chia DataPlayer API, a RESTful service that simplifies interaction with Chia DataLayer, allowing seamless data management and encryption with COSE (CBOR Object Signing and Encryption). Developed and tested with the official [chia-blockchain](https://github.com/Chia-Network/chia-blockchain) project.

If you find this project useful, consider donating to my Chia wallet:

`xch1vt3g694eclvcjmrj8mq83vtgrva9sw0qdz34muxrqjh5y5fzq6vq89n605` | `cripsis.xch`

Presentation page: [Chia DataPlayer](https://www.cripsis.xyz/chia-dataplayer-trabaja-como-un-humano/)

## Requirements

-   Python 3

-   `pipenv` for managing virtual environments

-   Chia Node with DataLayer enabled


### Installation

1.  Clone the repository:

    ```
    git clone https://github.com/yourrepo/chia-dataplayer-api.git
    cd chia-dataplayer-api
    ```

2.  Install dependencies:

    ```
    pipenv install
    ```

3.  Start the API server:

    ```
    pipenv run python app.py
    ```


## Configuration

The `config.yaml` file is used for API settings. Example:

```
---
rpc_connector:
  host: "localhost"
  private_wallet_cert_path: "~/.chia/mainnet/config/ssl/wallet/private_wallet.crt"
  private_wallet_key_path: "~/.chia/mainnet/config/ssl/wallet/private_wallet.key"
  service_ports:
    wallet: 9256
    datalayer: 8562
  service_wallets:
    chia: 1
    datalayer: 2

log_level: "WARNING"
```

If running the API on a different machine than your Chia node, modify the `host` accordingly.

## API Endpoints

### Check Status

**GET**  `/check`

Response:

```
{
  "status": "OK - all the checks are completed successfully!"
}
```

### List Datastores

**GET**  `/datastore/list`

Response:

```
[
  "store_id_1",
  "store_id_2"
]
```

### Create Datastore

**GET**  `/datastore/create`

Response:

```
{
  "store_id": "new_store_id"
}
```

### List Keys

**GET**  `/datastore/key/list?store_id={store_id}`

Response:

```
{
  "keys": ["key1", "key2", "key3"]
}
```

### Read Key

**GET**  `/datastore/key/read?store_id={store_id}&key={key}&codec={codec}`

Response:

```
{
  "success": true,
  "value": "hello world"
}
```

### Write Key

**POST**  `/datastore/key/update`

Request body:

```
{
  "store_id": "store_id",
  "key": "humanized_key",
  "value": "hello world",
  "codec": "hex"
}
```

Response:

```
{
  "success": true
}
```

### Delete Key

**DELETE**  `/datastore/key/delete?store_id={store_id}&key={key}`

Response:

```
{
  "success": true
}
```

## COSE Encryption

To store or read encrypted data, set the correct HMAC KEY in the `.env` file:

```
COSE_KEY=your_secret_key
```

Currently, only MAC0 (authenticated COSE message with one recipient) is supported.
