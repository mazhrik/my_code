
from rest_framework.response import Response
from .models import Log, Log_history
import json
from rest_framework.authtoken.models import Token

def log_middleware(get_response):
    print("Middleware Log")

    def my_function(request):
        print("-----before------",request)
        print("=---------ip---------",request.META.get('REMOTE_ADDR'))
        # print(request.headers.get('User-Agent'))

        # try:
        #     token = request.headers.get("Authorization").split(' ')[1]
        #     user_t = Token.objects.filter(key=token)
        #     if user_t[0].user.is_active == False:
        #         return Response({"message":"the user is block"})

        # except:
        #     pass
        # print(request.headers.get('User-Agent'))
        try:
            # print(type(request.body))
            request_d = json.loads(request.body)
            # print(request_d)
        except Exception as e:
            request_d = {}
            # print("Middleware Exception before  ",e)
            pass
        
        # try:
        #     token = request.headers.get("Authorization").split(' ')[1]
        #     user_t = Token.objects.filter(key=token)
        #     if user_t[0].user.is_active == False:
        #         return Response({"message":"the user is block"})
        #     response = get_response(request)
        # except:
        #     pass

        response = get_response(request)

        # check  if the user is inactive request should not be comple


        if request.get_full_path() != "/Log/":
            # print("-----after------",request)

            try:                
                response_d = json.loads(response.content)
                ignore_url = [
                    '/v1/portfolio/group/',
                    '/v1/core/all_user_notification/',
                    '/v1/core/get_user_log/',
                    '/v1/target/social/view/',
                    '/v1/target/generic/view/',
                    '/v1/portfolio/event/',
                    '/v1/portfolio/individual/',
                    '/v1/target/keybase/view/',
                    '/v1/target/generic/view/',
                    '/v1/target/periodic_targets/',
                    '/v1/target/get/response/',
                    '/v1/target/query/',
                    '/v1/portfolio/event/'
                    '/v1/avatar/dashboard/',
                    '/v1/target/updatestatus/',
                    '/v1/core/get_all_ml_models/',
                ]


                for_history_url = [

                ]
                user = request.user
                method = request.method
                url = request.get_full_path()
                ip = request.META.get('REMOTE_ADDR')

                if request.method == "POST":
                    if url in for_history_url:
                        Log_history.objects.create(request_username=user, request_method = method, request_url= url, request_data= request_d, response_data= response_d, ip = ip).save()

                if request.method == "GET" or request.method == "POST":
                    if url not in ignore_url:
                        print("save logs\n\n")
                        Log.objects.create(request_username=user, request_method = method, request_url= url, request_data= request_d).save()
                else:
                    print("save logs\n\n")
                    Log.objects.create(request_username=user, request_method = method, request_url= url, request_data= request_d).save()
            except Exception as e:

                # print("Middleware Exception after", e)
                pass
                
        return response

    return my_function