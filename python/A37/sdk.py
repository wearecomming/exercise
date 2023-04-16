# coding=utf-8
import os
import time
import json
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
def get_sdk():
# 创建AcsClient实例
    client = AcsClient(
    "LTAI5tMpq1bfR6YwU97G1XY5",
    "UY6Dfu2KxN1gmp7nz3V5jLwvLA6lZQ",
    "cn-shanghai"
    )

    # 创建request，并设置参数。
    request = CommonRequest()
    request.set_method('POST')
    request.set_domain('nls-meta.cn-shanghai.aliyuncs.com')
    request.set_version('2019-02-28')
    request.set_action_name('CreateToken')

    try : 
        response = client.do_action_with_exception(request)
        #print(response)

        jss = json.loads(response)
        if 'Token' in jss and 'Id' in jss['Token']:
            token = jss['Token']['Id']
        expireTime = jss['Token']['ExpireTime']
        #print("token = " + token)
        #print("expireTime = " + str(expireTime))
        return token
    except Exception as e:
        print(e)