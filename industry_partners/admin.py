from django.contrib import admin
from .models import Industry, Internship, Training, Job, Mentorship
# Register your models here.


admin.site.register(Industry)
admin.site.register(Internship)
admin.site.register(Job)
admin.site.register(Training)
admin.site.register(Mentorship)