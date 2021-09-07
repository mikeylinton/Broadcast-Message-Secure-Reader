# Broadcast Message Secure Reader

Project for paired work on Computer Network Security's second coursework. The project was completed with Andrew McGregor: [GitLab]( https://gitlab.com/Mcgregor381 ), [GitHub]( https://github.com/Mcgregor381  ). 

## Task 1

```bash
cat /dev/urandom  | xxd -ps | head -1
>$PASS
gpg --full-generate-key
#<KEYID>:Keypair
#<Name>:Real name
#<ID>@hw.ac.uk:Email
#<$PASS>:Passphrase

#Public Key
gpg --armor --export <KeyID>
#Private Key
gpg --armor --export-secret-key <KeyID>
```

## Task 2
```bash
gpgsm --generate-key > example.com.cert-req.pem
gpg --with-keygrip -k <ID>@hw.ac.uk

gpg --import <file name>
gpg -s <ID>@hw.ac.uk
```