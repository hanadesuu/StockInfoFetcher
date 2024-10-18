import requests
import json
import asyncio
import random
import pandas as pd
import asyncio
from requests.exceptions import ConnectTimeout

# 设置请求 URL 和 Headers
url = "https://gyl.scm121.com/api/goods/buyer/supplier/queryDisErpGoodsDataV2"

headers = {
    "accept": "application/json",
    "accept-language": "zh-CN,zh;q=0.9,ja-JP;q=0.8,ja;q=0.7",
    "app-version": "CHANNEL_20240924205607",
    "authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX25hbWUiOiIxNTgyMTg0NzA4MyIsImN1cnJlbnRfdXNlcl9vcmdfaWQiOiIiLCJjb0lkIjoiMTExODg2MDUiLCJhdXRob3JpdGllcyI6WyJKU1QtY2hhbm5lbCIsIm11bHRpTG9naW4iLCJKU1Qtc3VwcGxpZXIiXSwiY3VycmVudF91c2VyX29yZ19jb2RlIjoiLTEiLCJjbGllbnRfaWQiOiJwYyIsInVpZCI6IjEzNTE3ODc2Iiwicm9sZUlkcyI6WyJDNjM3QjBBOTM3QUQ0NzUxQTEwNzIwMjUxRjZGNzlERCIsIkFBOTA5NEU0MjBGMTRBMTU4REMxNzY1OEQ3NTcyNTREIiwiMzJCNzVERUY4OEU5NDJBNzg5N0I2ODY1QThCMDMyREQiXSwic2NvcGUiOlsidHJ1c3QiXSwiZXhwaXJhdGlvbiI6MTcyODExMzE2MjE2NSwiZXhwIjoxNzI4MTEzMTYyLCJ1c2VyIjp7ImNvSWQiOiIxMTE4ODYwNSIsInVpZCI6IjEzNTE3ODc2IiwibG9naW5OYW1lIjoiMTU4MjE4NDcwODMiLCJuaWNrTmFtZSI6Iui0neiSgiAiLCJjb05hbWUiOiLlv4PpgIkt5b-D5Yqo572R57ucIiwicHJveHlMb2dpbk5hbWUiOm51bGwsImxvZ2luV2F5IjoiVVNFUk5BTUUiLCJyb2xlSWRzIjoiMTEsMTIsMTMsMTQsMTUsMTYsMTcsMTgsMjIsMjMsMjcsMjgsMjksMzAsMzEsMzIsMzMsMzQsMzUsMzYsMzksNDAsNDEsNTEsNTIsNTMsNTQsNjEsNjIsNjQsNjUsNzAsNzEsNzIsNzMsNzYsMTAxLDEwMiwxMDMsMTA0LDEwNSwxMDYsMTA3LDEwOCwxMDkifSwianRpIjoiMzZmNDI4ODEtODcwYy00N2MxLWJiMDctNGYzMGJlOTE1NTU0In0.VAJ8kkfYdRIKiq6gp3k6APlRGv7GRCsaFSjaUEEs_U0",
    "content-type": "application/json;charset=UTF-8",
    "gwfp": "2cc869129839187f25474da36846ab47",
    "is-agent": "false",
    "priority": "u=1, i",
    "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\""
}

# 设置请求体数据
payload = {
    "supplierCoId": "10301064",  # 替换为实际的供应商ID
    "stockStart": "",  # 库存起始范围
    "stockEnd": "",  # 库存结束范围
    "brandName": "",  # 品牌名，可为空
    "pageNum": 1,  # 当前页码
    "pageSize": 50,  # 每页记录数
    "searchType": 1,  # 查询类型
    "itemCodeVague": "0",  # 是否模糊查询
    "itemCodes": "6972884342672"  # 商品编码
}



# 模拟异步获取库存数量的方法
async def get_stock_count(style_code, product_code):
    if not (pd.isna(product_code) or product_code == ''):
        payload["itemCodes"] = product_code
        try:
            # 发起 POST 请求
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)  # 增加超时限制
            # 解析返回的 JSON 数据
            if response.status_code == 200:
                data = response.json().get('data')
                code = response.json().get('code')
                if code == '1016':
                    print('重试')
                print("查询结果：", data)
                if isinstance(data, list) and len(data) > 0:
                    stock = data[0].get('stock', '库存信息不可用')
                    print('库存为', stock)
                    return stock
                else:
                    print("未找到库存信息", data, response.json())
                    return '未找到库存信息'
            else:
                print(f"请求失败，状态码: {response.status_code}, 返回内容: {response.text}")
                return '请求失败'
                
        except ConnectTimeout:
            print("请求超时，无法连接到服务器。")
            return '连接超时'
        except Exception as e:
            print(f"发生错误: {e}")
            return '发生错误'
    else:
        return '商品编号为空'

# 异步更新库存的函数
async def update_stock_for_excel(file_path, output_file_path):
    # 读取 Excel 文件
    df = pd.read_excel(file_path)

    # 获取 款式编码 和 商品编码 列
    style_codes = df['款式编码']
    product_codes = df['商品编码']

    # 如果文件中数据超过 max_rows 行，只处理前 max_rows 行
    # df = df.head(max_rows)

    # 创建一个新列用于存储库存数据
    df['产品当前库存'] = 0

    # 任务队列，用于存储所有异步任务
    tasks = []

    # 遍历每一行，获取款式编码和商品编码
    for index, row in df.iterrows():
        style_code = row['款式编码']
        product_code = row['商品编码']

        # 异步任务，获取库存并更新库存列
        tasks.append(fetch_and_update_stock(df, index, style_code, product_code))

    # 等待所有任务完成
    await asyncio.gather(*tasks)

    # 将结果写回 Excel
    df.to_excel(output_file_path, index=False)

# 异步函数，更新单行库存
async def fetch_and_update_stock(df, index, style_code, product_code):

    # 调用异步获取库存的方法
    stock_count = await get_stock_count(style_code, product_code)
    
    # 将库存数量写入到对应的行
    df.at[index, '产品当前库存'] = stock_count

# 运行异步任务
if __name__ == "__main__":
    # 输入文件路径和输出文件路径
    input_file = 'input.xlsx'    # 输入的 Excel 文件
    output_file = 'output.xlsx'  # 输出的 Excel 文件

    # 执行异步任务，处理前 5 行的数据
    asyncio.run(update_stock_for_excel(input_file, output_file))
