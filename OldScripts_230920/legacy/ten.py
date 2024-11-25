import json
import time

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models


# https://stackoverflow.com/questions/30069846/how-to-find-out-chinese-or-japanese-character-in-a-string-in-python
def is_cjk(character):
    """
    Checks whether character is CJK.

        >>> is_cjk(u'\u33fe')
        True
        >>> is_cjk(u'\uFE5F')
        False

    :param character: The character that needs to be checked.
    :type character: char
    :return: bool
    """
    return any([start <= ord(character) <= end for start, end in
                [(4352, 4607), (11904, 42191), (43072, 43135), (44032, 55215),
                 (63744, 64255), (65072, 65103), (65381, 65500),
                 (131072, 196607)]
                ])


def is_cjk_str(s):
    for c in s:
        if is_cjk(c):
            return True
    return False


f = open('ManualTransFile.json', encoding='utf8')
raw_data = json.load(f)
i = 0
raw_data_subscript_dict = {}
for key in raw_data:
    raw_data_subscript_dict[i] = key
    i = i + 1


i = 0
dlen = len(raw_data)


MAX_LEN = 5900

req_i = 0

raw_data_replace_dict = {}

while True:

    try:
        # 实例化一个认证对象，入参需要传入腾讯云账户 SecretId 和 SecretKey，此处还需注意密钥对的保密
        # 代码泄露可能会导致 SecretId 和 SecretKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考，建议采用更安全的方式来使用密钥，请参见：https://cloud.tencent.com/document/product/1278/85305
        # 密钥可前往官网控制台 https://console.cloud.tencent.com/cam/capi 进行获取

        cred = credential.Credential("xxxxxx", "xxxxxx")
        # 实例化一个http选项，可选的，没有特殊需求可以跳过
        httpProfile = HttpProfile()
        httpProfile.endpoint = "tmt.tencentcloudapi.com"

        # 实例化一个client选项，可选的，没有特殊需求可以跳过
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        # 实例化要请求产品的client对象,clientProfile是可选的
        client = tmt_client.TmtClient(cred, "ap-beijing", clientProfile)

        # 实例化一个请求对象,每个接口都会对应一个request对象
        req = models.TextTranslateBatchRequest()
        params = {
            "Source": "ja",
            "Target": "zh",
            "ProjectId": 0,
            "SourceTextList": []
        }


        req_to_global_seqn_dict = {}
        cnt_len = 0
        j = 0
        while True:
            while i < dlen and is_cjk_str(raw_data[raw_data_subscript_dict[i]]) == False:
                i = i + 1
            if i >= dlen:
                break
            cnt_s_len = len(raw_data[raw_data_subscript_dict[i]])
            if cnt_len + cnt_s_len > MAX_LEN or i >= dlen:
                break
            cnt_len += cnt_s_len
            params['SourceTextList'].append(raw_data[raw_data_subscript_dict[i]])
            req_to_global_seqn_dict[j] = i
            i = i + 1
            j = j + 1




        req.from_json_string(json.dumps(params))

        resp = {}
        while True:
            try:
                # 返回的resp是一个TextTranslateBatchResponse的实例，与请求对象对应
                resp = client.TextTranslateBatch(req)
                # resp = {}
                # 输出json格式的字符串回包
                # print(resp.to_json_string())
                break
            except TencentCloudSDKException as err:
                print(err)
                print('retrying')
                continue


        ret = {}

        # text_list = []
        text_list = resp.TargetTextList

        for j in range(len(text_list)):
            ret[j] = text_list[j]
            raw_data[raw_data_subscript_dict[req_to_global_seqn_dict[j]]] = text_list[j]
            # raw_data_replace_dict[req_to_global_seqn_dict[j]] = text_list[j]

        f2_name = 'r/' + str(req_i) + '_raw.txt'
        with open(f2_name, 'w', encoding='utf8') as f2:
            f2.writelines(resp.to_json_string())

        f2_name = 'r/' + str(req_i) + '_seqn.txt'
        with open(f2_name, 'w', encoding='utf8') as f2:
            f2.writelines(json.dumps(req_to_global_seqn_dict))

        print(str(req_i) + ', g_p = ' + str(i) + '')

        req_i = req_i + 1

        # break

        if i >= dlen:
            break

        # time.sleep(100)

    except TencentCloudSDKException as err:
        print(err)


with open('r/rr.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(raw_data, ensure_ascii=False))
with open('r/rp.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(raw_data, ensure_ascii=False, indent=4))


