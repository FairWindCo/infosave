from django.shortcuts import render


# Create your views here.
def view_test(request):
    return render(request, 'vue_utils/vue_base_template.html', context={})
