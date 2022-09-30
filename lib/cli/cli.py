import logging, argparse, sys, yaml
class Cli():
    
    @staticmethod
    def set_app_logger():
        root = logging.getLogger()
        root.propagate = True
        root.setLevel(eval(f"logging.{config['log_level']}"))
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(eval(f"logging.{config['log_level']}"))
        formatter = logging.Formatter('[%(levelname)s]|%(asctime)s|%(funcName)s|%(message)s')
        for handler in root.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setFormatter(formatter)
        handler.setFormatter(formatter)
        root.addHandler(handler)
        
    @staticmethod
    def argparse():
        global args_global
        
        def printText(args):
            print(args)
            
        parser = argparse.ArgumentParser(description='Interact with Chia DataLayer in a easy way')

        parser.add_argument('-f', '--config-file', type=str, help='YAML config file. If not specified use default config.yaml', required=False)
        parser.add_argument('-m', '--mode', type=str, choices=['check', 'execute'], default='execute', required=False, help='Check only mode or really execute actions (default execute)')
        
        subparser = parser.add_subparsers()
        datastores = subparser.add_parser('datastore')
        datastores.add_argument('--id', '-i', type=str, help='Datastore ID', required=True)
        datastores.add_argument('--codec', '-c', type=str, help='Encoding type for reading or updating (default hex)', choices=['hex', 'cbor'], default='hex', required=False)
        datastores.add_argument('--action', '-a', type=str, help='Action to execute over datastore (required)', choices=['update_key', 'read_key', 'list_keys'], required=True)
        datastores.add_argument('--key', '-k', type=str, help='Key of selection (required for read_key, update_key actions)', required=False)
        datastores.add_argument('--value', '-v', type=str, help='Value for update_key action (optional)', required=False)
        datastores.add_argument('--cbor-ph', '-cph', type=str, help='List of protected headers to store for update_key action and cbor codec (optional). Format: FOO=BAR ABC=XYZ', nargs='+', required=False)
        datastores.add_argument('--cbor-uh', '-cuh', type=str, help='List of unprotected headers to store for update_key action and cbor codec (optional). Format: FOO=BAR ABC=XYZ', nargs='+', required=False)
        
        datastores.set_defaults(func=printText)
        args_global = parser.parse_args()
        args_datastores, unknown = datastores.parse_known_args()
        
        if args_global.mode == "check" and args_datastores.id is None:
            parser.print_help()
            sys.exit(0)
            
        if args_datastores.action == "update_key":
            if args_datastores.key is None or args_datastores.value is None:
                logging.error("Key or value not specified for update_key action")
                exit(1)

            if args_datastores.codec == "cbor":
                if args_datastores.cbor_ph is not None:
                    try:
                        cbor_ph = dict()
                        for i in args_datastores.cbor_ph:
                            kv = i.split("=")
                            cbor_ph[kv[0]] = kv[1]
                    except Exception as e:
                        logging.error("Malformed k=v pair for cbor public headers")
                        exit(1)
                    else:
                        args_datastores.cbor_ph = cbor_ph
                else:
                    args_datastores.cbor_ph = {}
                        
                if args_datastores.cbor_uh is not None:
                    try:
                        cbor_uh = dict()
                        for i in args_datastores.cbor_uh:
                            kv = i.split("=")
                            cbor_uh[kv[0]] = kv[1]
                    except Exception as e:
                        logging.error("Malformed k=v pair for cbor public headers")
                        exit(1)
                    else:
                        args_datastores.cbor_uh = cbor_uh
                else:
                    args_datastores.cbor_uh = {}

        return(args_global, args_datastores)

    def load_config_file():
        global config
        
        if args_global.config_file is not None:
            filepath = args_global.config_file
        else:
            filepath = f"{sys.path[0]}/config.yaml"
        try:
            with open(filepath, 'r') as file:
                config = yaml.full_load(file)
        except Exception as e:
            logging.error(f"Cannot open config file {filepath}: {str(e)}")
            exit(1)
        else:
            logging.debug(f"Successfully loaded config file {filepath}")
            return(config)
