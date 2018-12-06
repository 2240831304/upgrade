from django.urls import path

from package.views import IndexView, ReadersView, RVersionAddView, RVersionEditView, ReaderVersionsView, ReaderRVersionsView, RVersionStateView, PackagesView, PackagesInfoView, PackageAddView, PackageEditView

app_name='package'
urlpatterns = [
    # 主页
    path('index', IndexView.as_view(), name='index'),
    # 添加阅读器号，以及返回所有的阅读器号信息
    path('readers', ReadersView.as_view(), name='readers'),
    # 添加阅读器新版本
    path('rversion', RVersionAddView.as_view(), name='rversion_add'),
    # 修改阅读器版本
    path('rversion/rv_<str:rv_id>', RVersionEditView.as_view(), name='rversion_edit' ),
    # 同步更新阅读器版本
    path('rversion/state', RVersionStateView.as_view(), name='rv_state'),
    # 返回当前阅读器所有的已同步更新的版本号，依赖版本
    path('rv_<str:reader_id>/rversions/versions', ReaderVersionsView.as_view(), name='versions'),
    # 返回当前阅读器所有的已同步更新的所有版本的所有信息，历史版本
    path('rv_<str:reader_id>/rversions', ReaderRVersionsView.as_view(), name='rversions'),

    # 所有的升级包展示
    path('pid_<str:pid>/packages', PackagesView.as_view(), name='packages'),
    # 添加升级包版本
    path('pid_<str:pid>/package', PackageAddView.as_view(), name='pack_add'),
    # 对某个版本升级包的处理
    path('pid_<str:pid>/package/pack_<str:pack_id>', PackageEditView.as_view(), name='pack_edit'),
    # 提供对应rversion所有的包
    path('packages', PackagesInfoView.as_view(), name='packages_info'),
]
