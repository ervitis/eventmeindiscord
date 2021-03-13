# -*- coding: utf-8 -*-
import base64
import logging
import os


class SecretManager(object):

    __sec_folder = 'c2VjcmV0'.encode('ascii')
    __sec_file_name = 'Y2xpZW50LXNlY3JldC5qc29u'.encode('ascii')
    __env_discord = 'RElTQ09SRF9UT0tFTg=='.encode('ascii')
    __env_gcp_n = 'R0NQX0NSRUQ='.encode('ascii')

    __logger = logging.getLogger(__name__)

    def __try_save_sec_tofile(self):
        _p = os.path.join(
            '.',
            base64.b64decode(self.__sec_folder).decode('ascii')
        )
        _v = os.getenv(base64.b64decode(self.__env_gcp_n).decode('ascii'), None)
        if not _v:
            raise ValueError('I will not connect...')

        try:
            _sf = os.path.join(_p, base64.b64decode(self.__sec_file_name).decode('ascii'))
            if not os.path.exists(_sf):
                os.mkdir(_p)
                with open(_sf, 'w') as f:
                    f.write(_v)
        except Exception as e:
            raise e

    def __get_discord(self):
        return base64.b64decode(os.getenv(base64.b64decode(self.__env_discord).decode('ascii'))).decode('ascii')

    @classmethod
    def discord(cls) -> str:
        self = cls
        return cls.__get_discord(self)

    def save(self):
        try:
            self.__try_save_sec_tofile()
        except Exception as e:
            self.__logger.error(f'Something happened trying to save in file: {e}')
            raise e
