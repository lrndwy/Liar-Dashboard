from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Table)
admin.site.register(Column)
admin.site.register(Row)
admin.site.register(Data)
admin.site.register(Relation)
admin.site.register(CustomUser)

