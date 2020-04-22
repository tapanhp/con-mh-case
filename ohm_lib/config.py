import ConfigParser
import cStringIO
import os
import stat


class Config(dict):
    def __init__(self, passed_filenames=None):
        super(Config, self).__init__()
        self._read_config_files(passed_filenames)

    def deep_get(self, *keys):
        value = self.__dict__
        for key in keys:
            try:
                value = value[key]
            except KeyError:
                return None

        return value

    # Copied from /System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/ConfigParser.py
    _boolean_states = {'1': True, 'yes': True, 'true': True, 'on': True,
                       '0': False, 'no': False, 'false': False, 'off': False}

    def getboolean(self, section, option):
        v = self.deep_get(section, option)
        if v.lower() not in self._boolean_states:
            raise ValueError, 'Not a boolean: %s' % v
        return self._boolean_states[v.lower()]

    def base_url(self):
        return self.deep_get('custom', 'base_url')

    def oem_equals(self, test_oem):
        return self.oem() == test_oem.lower()

    def oem(self):
        config_oem = self.deep_get('custom', 'oem')
        if not config_oem:
            return ''
        else:
            return config_oem.lower()

    def email_image_base_url(self):
        '''
        OL-7740 Pull from the production server, even in development mode, so we can see the
        images which would otherwise be blocked by the GMail image proxy when testing emails locally
        '''
        return self.deep_get('custom', 'email_image_base_url')

    def redirect_url(self):
        return self.deep_get('custom', 'redirect_url')

    def reduction_event(self):
        return self.deep_get('company', 'reduction_event')

    def get_config_default(self, section, option, value=None, default=None, asbool=False):
        '''
        Get a config value from config file.  If value is not None, returns value passed in.
        If value is None and no option found, returns default
        '''
        if value is not None:
            return value

        opt = self.deep_get(section, option)
        if opt:
            if asbool:
                return opt in {'True', '1', 'yes', 'on'}
            else:
                return opt

        return default

    # ---- Private ----

    def _read_config_files(self, passed_filenames=None):
        if passed_filenames:
            filenames = passed_filenames
        else:
            from environment import environment
            filenames = (
                'config/my_main.cnf',
                'config/my_common.cnf',
                'config/my_host.cnf',
                'config/my_%s.cnf' % environment
            )

        vault_password = os.environ.get('VAULT_PASSWORD')
        if not vault_password:
            filename = os.environ.get('ANSIBLE_VAULT_PASSWORD_FILE') or '~/.vault_pass.txt'
            filepath = os.path.expanduser(filename)
            if os.path.exists(filepath):
                if stat.S_IMODE(os.stat(filepath).st_mode) & 0077:
                    print("The Vault Password file %s is readable by others! Please fix this." % filename)
                    exit(1)
                vault_password = open(filepath).readline().strip()

        vault = vault_password

        internal_config = ConfigParser.RawConfigParser()

        for filename in filenames:
            self._read_config(filename, vault, internal_config)

        # OEM configs get read in after the other config files so that we know which oem is currently running.
        if not passed_filenames:
            filename = "config/oem/%s.cnf" % internal_config.get('custom', 'oem').lower()
            self._read_config(filename, vault, internal_config)

        settings = self._convert_config_to_dict(internal_config)

        self.__dict__.update(settings)
        self.update(settings)

    # ---- Static Methods ----

    @staticmethod
    def _read_config(filepath, vault, internal_config):
        if not filepath.startswith('/'):
            from environment import APP_ROOT
            filepath = os.path.join(APP_ROOT, filepath)

        if not os.path.exists(filepath):
            return

        with open(filepath) as f:
            data = f.read()
            if data[:14] == "$ANSIBLE_VAULT":
                if vault is None:
                    print("Encrypted config file %s but no password." % filepath)
                    exit(1)
                data = vault.decrypt(data)
            secret_file = cStringIO.StringIO(data)
            internal_config.readfp(secret_file)
            del secret_file
            del data

    @staticmethod
    def _convert_config_to_dict(config):
        config_dict = {}
        for section in config.sections():
            config_dict[section] = {}
            for item in config.items(section):
                config_dict[section][item[0]] = item[1]

        return config_dict

    @staticmethod
    def _cleanup_plain_text_keys(data):
        plain_text_keys = Config._plain_text_keys(data)
        Config._remove_plain_text_keys(data, plain_text_keys)

    @staticmethod
    def _plain_text_keys(data):
        plain_text_keys = []
        for key, value in data.iteritems():
            if type(value) == dict:
                plain_text_keys = plain_text_keys + Config._plain_text_keys(value)

            elif key.endswith('_enc'):
                truncated_key = key[:-4]
                plain_text_keys.append(truncated_key)

        return plain_text_keys

    @staticmethod
    def _remove_plain_text_keys(data, keys_to_remove):
        for key in data.keys():
            value = data[key]
            if type(value) == dict:
                Config._remove_plain_text_keys(value, keys_to_remove)

            elif key in keys_to_remove:
                data.pop(key)


internal_config = None


def config(reset=False):
    global internal_config

    if reset or not internal_config:
        internal_config = Config()

    return internal_config


if __name__ == "__main__":
    import pprint
    from environment import environment

    print()
    print("Environment=%s" % environment)
    print("--------------------------------")
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(config())



