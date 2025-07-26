from django.contrib import admin
from .models import Room, Student, Bench, Absentee, SeatingAssignment, InvigilatorAssignment

class InvigilatorAssignmentInline(admin.TabularInline):
    model = InvigilatorAssignment
    extra = 1 # Show one extra blank form for easy adding

class RoomAdmin(admin.ModelAdmin):
    inlines = [InvigilatorAssignmentInline]

admin.site.register(Room, RoomAdmin) # Register Room with the custom admin class
admin.site.register(Student)
admin.site.register(Bench)
admin.site.register(Absentee)
admin.site.register(SeatingAssignment)
admin.site.register(InvigilatorAssignment)