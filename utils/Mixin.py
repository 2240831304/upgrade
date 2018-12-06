from django.contrib.auth.decorators import login_required


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        # 调用View类中as_view方法
        view = super().as_view(**initkwargs)

        # 进行登录验证
        return login_required(view)