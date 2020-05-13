from general_user.models import UpRVersion, UpPackage
from utils.common_func.package import get_pack


# 用户使用返回升级包信息
def get_package(request):
    return get_pack(request, False, UpRVersion, UpPackage)



