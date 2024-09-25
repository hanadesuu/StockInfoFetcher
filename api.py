from collections import OrderedDict
import requests
import hashlib
import time
import json



#请求客户端
class open_client(object):
    
    app_key = None
    app_secret = None
    sandbox = False
    access_token = None

    sandbox_url = 'https://dev-api.jushuitan.com'
    url = 'https://openapi.jushuitan.com/'
    
    #初始化 sandbox: 是否是测试环境
    def __init__(self, app_key, app_secret, access_token, sandbox = True) -> None:

        self.app_key = app_key
        self.app_secret = app_secret
        self.sandbox = sandbox
        self.access_token = access_token

    #sign 计算
    def get_sign(self, data):
        list_data = list(data.keys())
        string_sign = self.app_secret
        sort_list = sorted(list_data)

        for item in sort_list:
            string_sign += str(item)
            string_sign += str(data[item])
        sign = hashlib.md5(string_sign.encode('utf-8')).hexdigest()
        return sign


    #请求接口
    def call(self, api, request_model)-> None:

        params = OrderedDict()
        params['app_key'] = self.app_key
        params['access_token'] = self.access_token
        params['timestamp'] = int(time.time())
        params['version'] = '2'
        params['charset'] = 'utf-8'
        params['biz'] =  json.dumps(request_model)
        params['sign'] = self.get_sign(params)

        headers = {'content-type': 'application/x-www-form-urlencoded;charset=UTF-8'}

        try:
            request_url = self.sandbox_url if self.sandbox else self.url 
            result = requests.post(request_url+api, data=params, headers=headers)
            if result.status_code == 200:
                return json.loads(result.text)

            return None
        except:
            return None


from collections import OrderedDict




if __name__ == '__main__':

    #查询店铺接口示例
    shop_request = OrderedDict()
    shop_request['page_index'] = 1
    shop_request['page_size'] = 10

    instance = open_client('b0b7d1db226d4216a3d58df9ffa2dde5', '99c4cef262f34ca882975a7064de0b87', 'b7e3b1e24e174593af8ca5c397e53dad', sandbox = True)
    result = instance.call('/open/shops/query', shop_request)
    print(result)

    