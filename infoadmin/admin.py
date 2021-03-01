from django.contrib import admin
from django.utils.html import format_html

from infoadmin.models import Machines, Rolls, Defects, Batch

# Register your models here.
from infosave import settings


@admin.register(Defects)
class DefectAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'defect',
                    'image_tag_defect_1', 'image_tag_defect_2'
                    ]

    def image_tag_defect_1(self, obj):
        print(obj)
        return format_html('<img src="{}" />'.format(obj.defect_image_1.url)) if obj.defect_image_1 else ''

    def image_tag_defect_2(self, obj):
        return format_html('<img src="{}" />'.format(obj.defect_image_2.url))  if obj.defect_image_2 else ''

    image_tag_defect_1.short_description = 'Defect Image'
    image_tag_defect_2.short_description = 'Defect Image'


admin.site.register(Machines)
admin.site.register(Rolls)
admin.site.register(Batch)
