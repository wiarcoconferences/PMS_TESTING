from django.contrib import admin

from mastermodule.models import *

admin.site.register(Work_Type)
admin.site.register(Modules)
admin.site.register(Task_Statuses)
admin.site.register(Task_priorities)
#admin.site.register(Default_invoicing)
admin.site.register(Generalinfo)
admin.site.register(Project_categorization)
admin.site.register(Resource_Categorization)

# Register your models here.
