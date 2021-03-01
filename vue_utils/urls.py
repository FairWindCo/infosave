from django.urls import path

from vue_utils.views import view_test

urlpatterns = [
    path('test/', view_test, name='test_base_vue'),
]
