import argparse, getpass
import coms_layer as messenger
import Crypto as cryptoTool
import make


def main():

    parser = argparse.ArgumentParser(description='Short sample app')

    parser.add_argument('--encrypt', '-e', action="store_true", default=False, help="used to start encrypt mode")
    parser.add_argument('--decrypt', '-d', action="store_true", default=False, help="used to start decrypt mode")

    parser.add_argument('--send', '-s', action="store_true", default=False, help="used to send a file")
    parser.add_argument('--receive', '-r', action="store_true", default=False, help="used to receive a file")

    parser.add_argument('--password', '-p', action="store", required=False, type=str, help="password for decrypting or encrypting file")

    parser.add_argument('--file', '-f', action="store", type=str, help="used to define a file preform actions on")

    parser.add_argument('--destination', '-des', action="store", help="used to define a destination for send mode")
    parser.add_argument('--port', '-pt', action="store", type=int, help="used to define a destination port for send mode")

    parser.add_argument('--makeKey', '-mK', action="store_true", default=False, help="used to create a PGP key")
    parser.add_argument('--makeCert', '-mC', action="store_true", default=False, help="used to create a X.509 certificate")
    args = parser.parse_args()

    if args.makeCert:
        make.cert(args)

    else:

        while args.password is None or args.password is "":
            args.password = getpass.getpass("Enter passphrase: ")
            if args.password is None or args.password is "":
                print("Cannot be blank")

    if args.makeKey:
        make.key(args)
    elif args.encrypt and args.send:
        messenger.send(cryptoTool.enc(args), args)
    elif args.encrypt:
        cryptoTool.enc(args)
    elif args.decrypt and args.receive:
        messenger.receive(cryptoTool.dec(args), args)
    elif args.decrypt:
        cryptoTool.dec(args)
    elif args.receive:
        messenger.receive("receivedMessage.text", args)
    elif args.receive:
        messenger.receive(args.file, args)
    else:
        print("no valid arguments see -h or -help")


if __name__ == '__main__':
    main()
