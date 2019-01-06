
from django.urls import path
from django.conf.urls import include, url

from . import views
from . import models

app_name = 'croll'
urlpatterns = [
    path('', views.index, name='index'),
    path('createfinance', models.createfinance, name='index'),
    path('updatefinance', models.updatefinance, name='index'),
    path('financewindow', views.financewindow, name='index'),
    path('financeinfo', views.financeinfo, name='financeinfo'),
    path('createprice', models.createprice, name='createprice'),
    path('updateprice', models.updateprice, name='updateprice'),
    path('createcompany', models.createcompany, name='createcompany'),
    path('testview', views.testview, name='testview'),
    path('pbrwindow', views.pbrwindow, name='pbrwindow'),
    path('enteringwindow', views.enteringwindow, name='enteringwindow'),
    # path('remove', models.remove_letter, name='remove'),
    # url(r'whatever^$', 'croll.views.financeinfo',name='view_financeinfo'),
]