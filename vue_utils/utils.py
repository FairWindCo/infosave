from django.core import serializers
from django.core.paginator import Paginator


def get_from_request(request, request_param_name, default_value=None, raise_exception=False):
    if request_param_name and request:
        if request.GET and request_param_name in request.GET:
            return request.GET.get(request_param_name)
        elif request.POST and request_param_name in request.POST:
            return request.POST.get(request_param_name)
        elif raise_exception:
            raise ValueError(f'Param {request_param_name} not found in request')
        else:
            return default_value
    else:
        return None


def todict(obj, classkey=None):
    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = todict(v, classkey)
        return data
    elif hasattr(obj, "_ast"):
        return todict(obj._ast())
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [todict(v, classkey) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = dict([(key, todict(value, classkey))
                     for key, value in obj.__dict__.items()
                     if not callable(value) and not key.startswith('_')])
        if classkey is not None and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    else:
        return obj


def standart_serializer(list_object):
    return serializers.serialize('json', list_object)


def dict_serializer(list_object):
    return [todict(obj) for obj in list_object]


def process_paging(request, objects, default_page_size='25', serializer=dict_serializer):
    page_number = get_from_request(request, 'page', '0')
    page_size = get_from_request(request, 'per_page', default_page_size)
    paginator = Paginator(objects, page_size)

    return {
        'list': serializer(paginator.get_page(page_number).object_list),
        'page_number': page_number,
        'per_page': page_size,
        'count': paginator.count
    }
