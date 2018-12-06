from django.urls import path

from faq.views import FAQListView, FAQAddView, FAQEditView

app_name = 'faq'
urlpatterns = [
    path('faqs', FAQListView.as_view(), name='faqs'),
    path('faq', FAQAddView.as_view(), name='faq_add'),
    path('faq/<str:faq_id>', FAQEditView.as_view(), name='faq_edit'),
]
