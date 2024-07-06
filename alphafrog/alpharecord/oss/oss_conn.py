# -*- coding: utf-8 -*-
import oss2
from alibabacloud_credentials.client import Client
from alibabacloud_credentials.models import Config
from oss2 import CredentialsProvider
from oss2.credentials import Credentials
import os


class CredentialProviderWrapper(CredentialsProvider):
    def __init__(self, client):
        self.client = client

    def get_credentials(self):
        credential = self.get_credentials()
        access_key_id = credential.get_access_key_id()
        access_key_secret = credential.get_access_key_secret()
        security_token = credential.get_access_key_secret()
        return Credentials(access_key_id, access_key_secret, security_token)


def establish_connection():
    config = Config(
        type='ram_role_arn',
        # 从环境变量中获取RAM用户的访问密钥（AccessKey ID和AccessKey Secret）。
        access_key_id=os.getenv('OSS_ACCESS_KEY_ID'),
        access_key_secret=os.getenv('OSS_ACCESS_KEY_SECRET'),
        # 从环境变量中获取RAM角色的RamRoleArn。
        role_arn=os.getenv('OSS_STS_ROLE_ARN'),
        # 填写RAM角色的会话名称。
        role_session_name='roleSessionName'
    )

    cred = Client(config)

    credentials_provider = CredentialProviderWrapper(cred)

    # 使用环境变量中获取的RAM用户的访问密钥和RAM角色的RamRoleArn配置访问凭证。
    auth = oss2.ProviderAuth(credentials_provider)

    return auth