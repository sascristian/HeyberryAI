import gnupg
from os.path import dirname, exists
from os import makedirs
import logging
gpglog = logging.getLogger("gnupg")
gpglog.setLevel("WARNING")

# use own gpg home directory
gpg_home_dir = dirname(__file__)+"/gpg"
if not exists(gpg_home_dir):
    makedirs(gpg_home_dir)
gpg = gnupg.GPG(gnupghome=gpg_home_dir, options=["--always-trust"])


def list_keys():
    # list keys
    public_keys = gpg.list_keys()
    private_keys = gpg.list_keys(True)
    return public_keys, private_keys


def gen_key(user, passwd, key_lenght=1024, text="jarbas client key", name_real="MiniJarbas"):
    # gen key
    input_data = gpg.gen_key_input(key_type="RSA", key_length=key_lenght, name_email=user,
        passphrase=passwd, name_comment=text, name_real=name_real)
    key = gpg.gen_key(input_data)
    print key.fingerprint
    return key


def export_key(key_fingerprint, passwd=None, path=None, private=False, save=True):
    # export key
    if key_fingerprint is None:
        print "bad fingerprint"
        return None
    ascii_armored_public_keys = gpg.export_keys(key_fingerprint)
    if private:
        ascii_armored_private_keys = gpg.export_keys(key_fingerprint, True, passphrase=passwd)
    if save:
        if path is None:
            path = gpg_home_dir + '/mykeyfile.asc'
        with open(path, 'w') as f:
            f.write(ascii_armored_public_keys)
            if private:
                f.write(ascii_armored_private_keys)
    return ascii_armored_public_keys


def import_key(path=None):
    if path is None:
        path = gpg_home_dir + '/mykeyfile.asc'
    # import key
    key_data = open(path).read()
    import_result = gpg.import_keys(key_data)
    return import_result


def import_key_from_ascii(string):
    import_result = gpg.import_keys(string)
    return import_result


def delete_key(fingerprint):
    gpg.delete_keys(fingerprint, True)
    gpg.delete_keys(fingerprint)


def encrypt_string(user, string='Who are you? How did you get in my house?', verbose=False):
    # encrypt
    encrypted_data = gpg.encrypt(string, user, always_trust=True)
    encrypted_string = str(encrypted_data)
    if verbose:
        print 'ok: ', encrypted_data.ok
        print 'status: ', encrypted_data.status
        print 'stderr: ', encrypted_data.stderr
        print 'unencrypted_string: ', string
        print 'encrypted_string: ', encrypted_string
    return encrypted_data


def decrypt_string(encrypted_string, passwd, verbose=False):
    decrypted_data = gpg.decrypt(str(encrypted_string), passphrase=passwd)
    if verbose:
        print 'ok: ', decrypted_data.ok
        print 'status: ', decrypted_data.status
        print 'stderr: ', decrypted_data.stderr
        print 'decrypted string: ', decrypted_data.data
    return decrypted_data


def get_own_keys(user):
    public_keys, private_keys = list_keys()

    my_public_keys = []
    my_private_keys = []
    for key in public_keys:
        if user in key['uids'][0]:
            key = {"keyid": key["keyid"], "length": key["length"], "fingerprint": key["fingerprint"], "expires": key["expires"]}
            my_public_keys.append(key)

    for key in private_keys:
        if user in key['uids']:
            key = {"keyid": key["keyid"], "length": key["length"], "fingerprint": key["fingerprint"],
                   "expires": key["expires"]}
            my_private_keys.append(key)

    return public_keys, private_keys


def generate_client_key(user, passwd):
    print "generating client key"
    key = gen_key(user, passwd)

    print "exporting client key"
    #export_key(key.fingerprint, path=gpg_home_dir + '/client_private.asc', passwd=passwd, private=True)
    export_key(key.fingerprint, path=gpg_home_dir + '/client_public.asc', passwd=passwd, private=False)
    return key