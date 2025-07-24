from django.contrib import admin

# Register your models here.
from .models import Room, Student, Bench, Absentee, SeatingAssignment

admin.site.register(Room)
admin.site.register(Student)
admin.site.register(Bench)
admin.site.register(Absentee)
admin.site.register(SeatingAssignment) # Register the new model