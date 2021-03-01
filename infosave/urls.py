"""infosave URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path

from infoadmin.views import get_machine_list, update_rolls, get_active_machine_list, end_roll, fix_defects_roll, \
    get_active_branches, update_batch, index, list_full_batches, test
from infosave import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    url('machines', get_machine_list),
    url('actives', get_active_machine_list),
    url('rolls_update', update_rolls),
    url('rolls_end', end_roll),
    url('fix_defects', fix_defects_roll),
    url('create_batch', update_batch),
    url('all_batches', list_full_batches, name='full_batches'),
    url('batches', get_active_branches),
    url('test', test, name='test_vue'),
    url('', index, name='index'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()

