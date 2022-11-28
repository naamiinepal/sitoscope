from django.contrib import admin
from .models import Province, District, Municipality, Ward

# Register your models here.
admin.site.register(Province)
admin.site.register(District)
admin.site.register(Municipality)
admin.site.register(Ward)
