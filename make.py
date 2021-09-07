from OpenSSL import crypto
import gnupg

def cert(args):
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 4096)

    cert = crypto.X509()
    cert.get_subject().C = "GB"#countryCode
    cert.get_subject().ST = "Scotland"#stateOrProvinceName
    cert.get_subject().L = "Edinburgh"#localityName
    cert.get_subject().O = "Heriot Watt University"#organizationName
    cert.get_subject().OU = "MACS"#organizationUnitName
    cert.get_subject().CN = "Test Name"#commonName
    cert.get_subject().emailAddress = "Test@test.net"#email
    cert.set_serial_number(0)#serialNumber
    cert.gmtime_adj_notBefore(0)#validityStartInSeconds
    cert.gmtime_adj_notAfter(320000000)#validityEndInSeconds
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(key, "sha512")

    with open("py.crt", "wt") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8"))
    with open("py.key", "wt") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key).decode("utf-8"))

def key(args):
    gpg = gnupg.GPG()
    gpg.encoding = 'utf-8'


    input_data = gpg.gen_key_input(
        name_real='Test Name',
        name_email='Test@test.net',
        expire_date='2021-03-01',
        key_type='RSA',
        key_length=4096,
        key_usage='encrypt,sign,auth',
        passphrase=args.password
    )

    key = gpg.gen_key(input_data)

    print("key = ", key)