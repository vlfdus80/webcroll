
from django.urls import path
from django.conf.urls import include, url

from . import views
from . import models
from . import getfromxing

app_name = 'croll'
urlpatterns = [
    path('', views.index, name='indexwindow'),
    path('indexwindow', views.index, name='indexwindow'),
    path('createfinance', models.createfinance, name='createfinance'),
    path('updatefinance', models.updatefinance, name='updatefinance'),
    path('financewindow', views.financewindow, name='financewindow'),
    path('financeinfo', views.financeinfo, name='financeinfo'),
    path('createprice', models.createprice, name='createprice'),
    path('updateprice', models.updateprice, name='updateprice'),
    path('createcompany', models.createcompany, name='createcompany'),
    path('testview', views.testview, name='testview'),
    path('pbrwindow', views.pbrwindow, name='pbrwindow'),
    path('perwindow', views.perwindow, name='perwindow'),
    path('enteringwindow', views.enteringwindow, name='enteringwindow'),
    path('graphtest', views.graphtest, name='graphtest'),
    path('updateperiodprice', getfromxing.updateperiodprice, name='updateperiodprice'),

    # path('remove', models.remove_letter, name='remove'),
    # url(r'whatever^$', 'croll.views.financeinfo',name='view_financeinfo'),
]