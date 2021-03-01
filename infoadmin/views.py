import base64
import os
import shutil
import tempfile

from django.core.exceptions import ViewDoesNotExist
from django.db.models import F
from django.http import JsonResponse, HttpResponse
from django.middleware import csrf
# Create your views here.
from django.shortcuts import render
from django.utils.datetime_safe import datetime

from infoadmin.models import Machines, barcode_images_path, Rolls, Defects, Batch
from vue_utils.utils import process_paging


def get_machine_list(request):
    list_machines = Machines.objects.filter(is_use_roll__exact=False).values('pk', 'name')
    token = csrf.get_token(request)
    data = {
        'machines_list': list(list_machines),  # serialize('json', list_machines),
        'count': len(list_machines),
        'token': token
    }
    print(data, request)
    return JsonResponse(data, safe=False)


def get_active_machine_list(request):
    list_machines = Machines.objects.filter(is_use_roll__exact=True).values('pk', 'name')
    token = csrf.get_token(request)
    data = {
        'machines_list': list(list_machines),  # serialize('json', list_machines),
        'count': len(list_machines),
        'token': token
    }
    print(data, request)
    return JsonResponse(data, safe=False)


def get_active_branches(request):
    list_machines = Batch.objects.filter(rolls_count__gt=F('rolls_processed')).values('pk', 'code_number')
    token = csrf.get_token(request)
    data = {
        'branch_list': list(list_machines),  # serialize('json', list_machines),
        'count': len(list_machines),
        'token': token
    }
    print(data, request)
    return JsonResponse(data, safe=False)


def copy_file(file_path, dest=barcode_images_path()):
    head, tail = os.path.split(file_path)
    print('COPY', tail, file_path, dest)
    shutil.copy(file_path, dest)
    os.remove(file_path)
    return tail


def parse_files(request):
    file_name_1 = None
    file_name_2 = None
    if 'file_1' in request.POST and request.POST['file_1']:
        with tempfile.NamedTemporaryFile(delete=False) as file:
            file.write(base64.urlsafe_b64decode(request.POST['file_1']))
            file_name_1 = file.name
        file_name_1 = copy_file(file_name_1)
    if 'file_2' in request.POST and request.POST['file_2']:
        with tempfile.NamedTemporaryFile(delete=False) as file:
            file.write(base64.urlsafe_b64decode(request.POST['file_2']))
            file_name_2 = file.name
        file_name_2 = copy_file(file_name_2)
    if request.FILES:
        if file_name_1 is None and 'file_1' in request.FILES:
            file_name_1 = request.FILES['file_1']
        if file_name_2 is None and 'file_2' in request.FILES:
            file_name_2 = request.FILES['file_2']
    return file_name_1, file_name_2


def parse_request_worker(request):
    if 'worker_id' in request.POST and request.POST['worker_id']:
        worker = Machines.objects.get(id=request.POST['worker_id'])
    else:
        raise ViewDoesNotExist()
    if 'batch_id' in request.POST and request.POST['batch_id'] and request.POST['batch_id'] is not None:
        batch = Batch.objects.get(id=request.POST['batch_id'])
    else:
        batch = None
    file_name_1, file_name_2 = parse_files(request)

    value = request.POST['value'] if 'value' in request.POST and request.POST['value'] else ''
    return worker, file_name_1, file_name_2, value, batch


def parse_request_branch(request):
    file_name_1, file_name_2 = parse_files(request)
    branch = request.POST['branch'] if 'branch' in request.POST and request.POST['branch'] else ''
    value = request.POST['value'] if 'value' in request.POST and request.POST['value'] else ''
    return branch, file_name_1, file_name_2, value


def update_rolls(request):
    if request.method == 'POST':
        file_name_1 = None
        file_name_2 = None
        worker = None
        if request.POST:
            worker, file_name_1, file_name_2, value, batch = parse_request_worker(request)
        if worker:
            rolls = Rolls(machine=worker, batch=batch)
            if batch:
                batch.rolls_processed = batch.rolls_processed + 1
                batch.save()
            if file_name_1:
                rolls.bar_code_1 = file_name_1
            if file_name_2:
                rolls.bar_code_2 = file_name_2
            worker.is_use_roll = True
            rolls.code_number = value
            rolls.save()
            worker.save()
        return HttpResponse('OK', content_type="text/plain")
    else:
        raise ViewDoesNotExist()


def end_roll(request):
    if request.method == 'POST':
        worker = None
        if request.POST:
            worker, file_name_1, file_name_2, value, _ = parse_request_worker(request)
        if worker:
            rolls = worker.rolls_set.filter(timestamp_end_process__isnull=True).order_by(
                '-timestamp_start_process').all()
            if rolls:
                roll = rolls[0]
                roll.cycles = value
                worker.is_use_roll = False
                worker.save()
                roll.timestamp_end_process = datetime.now()
                roll.save()
            return HttpResponse('OK', content_type="text/plain")
        raise ViewDoesNotExist()
    else:
        raise ViewDoesNotExist()


def fix_defects_roll(request):
    if request.method == 'POST':
        print('FIXING...')
        worker = None
        print(request.POST)
        if request.POST:
            worker, file_name_1, file_name_2, value, _ = parse_request_worker(request)
        if worker:
            rolls = worker.rolls_set.filter(timestamp_end_process__isnull=True).order_by(
                '-timestamp_start_process').all()
            if rolls:
                roll = rolls[0]
                defect = Defects(roll=roll)
                if file_name_1:
                    defect.defect_image_1 = file_name_1
                if file_name_2:
                    defect.defect_image_2 = file_name_2
                defect.defect = value
                defect.save()

            return HttpResponse('OK', content_type="text/plain")
        raise ViewDoesNotExist()
    else:
        raise ViewDoesNotExist()


def update_batch(request):
    if request.method == 'POST' and request.POST:
        file_name_1, file_name_2 = parse_files(request)
        batch = Batch()
        batch.bar_code_1 = file_name_1
        batch.bar_code_2 = file_name_2
        batch.rolls_count = request.POST.get('rolls_count', 0)
        batch.code_number = request.POST.get('value', batch.id)
        batch.save()
        return JsonResponse({
            'batch_id': batch.id
        })
    else:
        raise ViewDoesNotExist()


def list_full_batches(request):
    objects = Batch.objects.all().order_by('pk')
    result = process_paging(request, objects)
    return JsonResponse(result, safe=False)

def index(request):
    return render(request, 'infoadmin/main_vue_app.html', {})


def test(request):
    print('TEST')
    return render(request, 'infoadmin/main_primevue_app.html', {})