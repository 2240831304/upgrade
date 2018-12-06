from utils.db.base_db import BaseModel
from django.db import models
from tinymce.models import HTMLField

state = (
    (0, "未删除"),
    (1, "已删除")
)


class FAQ(BaseModel):
    question = models.CharField(max_length=124, verbose_name='问题')
    answer = HTMLField(verbose_name='解答')
    state = models.IntegerField(choices=state, default=0, verbose_name='问题状态')

    class Meta:
        db_table = 'faq'
        verbose_name = '问题'
        verbose_name_plural = verbose_name
