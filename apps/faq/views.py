import logging

from django.shortcuts import render
from django.views import View
from django.http.response import JsonResponse
from django.http import QueryDict
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from utils.decorator import is_login
from ota.response_code import CODE
from faq.models import FAQ
from faq.constants import FAQ_STATE

logger = logging.getLogger('ota')


class FAQListView(View):
    @method_decorator(login_required)
    def get(self, request):
        # 获取所有的未删除的faq
        faq_objs = FAQ.objects.filter(state=FAQ_STATE['ADD'])

        context = {
            "faq_objs": faq_objs
        }

        return render(request, 'faqs.html', context)


class FAQAddView(View):
    @method_decorator(login_required)
    def get(self, request):
        return render(request, 'faqadd.html')

    @method_decorator(is_login)
    def post(self, request):
        # 获取数据
        question = request.POST.get('question')
        anwser = request.POST.get('answer')

        if not all([question, anwser]):
            content = {
                "code": CODE.PARAMERR,
                "msg": "缺少参数"
            }
            return JsonResponse(content)

        # 业务处理
        try:
            faq_obj = FAQ()
            faq_obj.question = question
            faq_obj.answer = anwser
            faq_obj.save()
        except Exception as e:
            logger.error("添加问题失败, detail:{}".format(e))
            content = {
                "code": CODE.DBERR,
                "msg": "添加失败"
            }
            return JsonResponse(content)

        content = {
            "code": CODE.OK,
            "msg": "添加成功"
        }
        return JsonResponse(content)


# FAQ edit
class FAQEditView(View):
    @method_decorator(login_required)
    def get(self, request, faq_id):
        # 获取数据
        faq_id = faq_id

        # 获取对应faq对象
        faq_obj = FAQ.objects.filter(id=faq_id).first()

        # 判断是否存在
        if not faq_obj:
            content = {
                "code": CODE.PARAMERR,
                "msg": "请求faq对象不存在"
            }
            return JsonResponse(content)

        context = {
            "faq_obj": faq_obj
        }

        return render(request, 'faqedit.html', context)

    @method_decorator(is_login)
    def put(self, request, faq_id):

        # 获取数据
        faq_id = faq_id
        PUT = QueryDict(request.body)
        question = PUT.get('question')
        answer = PUT.get('answer')
        print(answer)
        # 检验参数会否完整
        if not all([question]):
            content = {
                "code": CODE.PARAMERR,
                "msg": "缺少参数"
            }
            return JsonResponse(content)

        faq_obj = FAQ.objects.filter(id=faq_id).first()

        try:
            faq_obj.question = question
            faq_obj.answer = answer
            faq_obj.save()
        except Exception as e:
            logger.error("修改失败 detail：{}".format(e))
            content = {
                "code": CODE.DBERR,
                "msg": "修改失败"
            }
            return JsonResponse(content)

        content = {
            "code": CODE.OK,
            "msg": '修改成功'
        }
        return JsonResponse(content)

    @method_decorator(is_login)
    def delete(self, request, faq_id):
        faq_id = faq_id

        faq_obj = FAQ.objects.filter(id=faq_id).first()

        if not faq_obj:
            content = {
                "code": CODE.PARAMERR,
                "msg": "错误的请求"
            }
            return JsonResponse(content)

        try:
            faq_obj.state = FAQ_STATE['DELETE']
        except Exception as e:
            logger.error("faqid:{}删除失败, detail:{}".format(faq_id, e))
            content = {
                "code": CODE.DBERR,
                "msg": "删除失败"
            }
            return JsonResponse(content)

        content = {
            "code": CODE.OK,
            "msg": "删除成功"
        }
        return JsonResponse(content)
