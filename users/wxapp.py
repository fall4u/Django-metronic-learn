import requests
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from requests.exceptions import RequestException
from rest_framework.authtoken.models import Token

from .WXBizDataCrypt import WXBizDataCrypt


class WXAppData:
    def __init__(self, appId, secret):
        self.appId = appId
        self.secret = secret

    def get_token(self, code, encrypt_data='', iv=''):
        url = 'https://api.weixin.qq.com/sns/jscode2session?appid=%s&secret=%s&js_code=%s&grant_type=authorization_code'\
              % (self.appId, self.secret, code)
        try:
            response = requests.get(url)
            r = response.json()
            print "encrypt_data = %s"%encrypt_data
            print "iv = %s"%iv
            print r
            if r['openid'] and len(r['openid']) > 8 and r['session_key'] and len(r['session_key'])>2 :
                # check user existed ?
                openid = r['openid']
                session_key = r['session_key']
                user =  authenticate(username=openid, password=openid)
                if user is None:
                    # create user
                    print "incoming a new user"
                    user = User.objects.create_user(username = openid , password = openid)
                    user.save()

                    if encrypt_data and iv and len(encrypt_data) > 50 and len(iv) > 5:
                        pc = WXBizDataCrypt(self.appId, session_key)
                        user_info = pc.decrypt(encrypt_data,iv)
                        print user_info

                        user.profile.province = user_info['province']
                        user.profile.language = user_info['language']
                        user.profile.nickName = user_info['nickName']
                        user.profile.country  = user_info['country']
                        user.profile.gender   = user_info['gender']
                        user.profile.city     = user_info['city']
                        user.profile.avatarUrl     = user_info['avatarUrl']
                        user.save()



                    else:
                        print "encrypt_data and iv not valid"
                else:
                    print "user is existed"

                token, created = Token.objects.get_or_create(user=user)
                return token


                # u_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, str(time.time()))
                # skey = uuid.uuid3(uuid.NAMESPACE_DNS, str(time.time()))
                # create_time = datetime.datetime.now()
                # last_vist_time = datetime.datetime.now()
                # openid = r['openid']
                # session_key = r['session_key']
                # user_info = ''
                # if encrypt_data and iv and len(encrypt_data) > 50 and len(iv)> 5:
                #     pc = WXBizDataCrypt(self.appId, session_key)
                #     user_info = pc.decrypt(encrypt_data, iv)
                return {
                    'ok': 'success',
                    # 'session': {
                    #     'uuid': u_uuid,
                    #     'skey': skey,
                    #     'create_time': create_time,
                    #     'last_vist_time': last_vist_time,
                    #     'openid': openid,
                    #     'session_key': session_key,
                    #     'user_info': user_info,
                    #     'expires_in': r['expires_in']
                    # }
                }
            elif r['errcode'] and r['errmsg']:
                return {
                    'ok': 'fail',
                    'msg': r['errmsg']
                }
            else:
                return {
                    'ok': 'fail',
                    'msg': 'wechat return value error'
                }
        except RequestException:
            return {
                'ok': 'fail',
                'msg': 'network error'
            }