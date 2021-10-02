import requests
from django.conf import settings

def get_token(): # iampoet에서 (API키랑 시크릿키를 가지고 로그인 역할 수행)
    access_data = {
        'imp_key':settings.IAMPORT_KEY,#imp_key,imp_secret 는 iamport에서 요구하는사항
        'imp_secret':settings.IAMPORT_SECRET
    }
    url = "https://api.iamport.kr/users/getToken"
    # 데이터를 넣어줄때 딕셔너리형태로 넣어주는건 request 모듈의 문법형태
    req = requests.post(url, data=access_data)
    access_res = req.json()# req를 json방식으로해석

    if access_res['code'] is 0:# 여기서 code는 iamport에서 제공하는것
        return access_res['response']['access_token']
    else:# 응답코드가 제대로 오지않을경우
        return None

# 어떤 order아이디로 얼마만큼 금액으로결제를 요청할지 iamport에 미리 등록
def payments_prepare(order_id,amount, **kwargs):
    access_token = get_token()
    if access_token:
        access_data = {
            'merchant':order_id,
            'amount':amount,
        }
        url = 'https://api.iamport.kr/payments/prepare'
        headers = {
            'Authorization':access_token
        }
        req = requests.post(url, data=access_data,headers=headers)
        res = req.json()
        if res['code'] != 0:
            raise ValueError('API 통신 오류')
    else:
        raise ValueError('토큰 오류')

# 사기방지를위해 고객이요청한 주문번호에 담겨있는 주문금액만큼 제대로 결제가 됬는지 확인하는과정
def find_transaction(order_id,*args, **kwargs):
    access_token = get_token()
    if access_token:
        url = 'https://api.iamport.kr/payments/find/'+order_id
        headers = {
            'Authorization':access_token
        }
        req = requests.post(url,headers=headers)
        res = req.json()
        if res['code'] == 0:
            context = {
                'imp_id':res['response']['imp_uid'],
                'merchant_order_id':res['response']['merchant_uid'],
                'amount':res['response']['amount'],
                'status':res['response']['status'],
                'type':res['response']['pay_method'],
                'receipt_url':res['response']['receipt_url']
            }
            return context
        else:
            return None
    else:
        raise ValueError('token error')