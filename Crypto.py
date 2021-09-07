import gnupg
# import password_hash as hash


def dec(args):
    # hashpass = hash.password(args.password)
    gpg = gnupg.GPG()
    gpg.encoding = 'utf-8'

    with open(args.file, 'rb')as f:
        dec = gpg.decrypt_file(f, passphrase=args.password, output=args.file + ".dec")

    print(dec.ok)
    print(dec.stderr)


def enc(args):
    # hashpass = hash.password(args.password)
    gpg = gnupg.GPG()
    gpg.encoding = 'utf-8'

    with open(args.file, 'rb')as f:
        enc = gpg.encrypt_file(f, passphrase=args.password, recipients=["Test@test.net"], output=args.file + ".enc")

    # if args.verbose:
    print(enc.ok)
    print(enc.stderr)

    return args.file + ".enc"
