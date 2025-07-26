# # from django.db import models

# # # Create your models here.
# # class Room(models.Model):
# #     name = models.CharField(max_length=100, unique=True)
# #     columns = models.IntegerField(default=4)
# #     benches_per_column = models.IntegerField(default=6)
# #     students_per_bench = models.IntegerField(default=3)

# #     def __str__(self):
# #         return self.name

# # class Student(models.Model):
# #     student_id = models.CharField(max_length=20, unique=True)
# #     batch = models.CharField(max_length=50, default='General') # New field

# #     def __str__(self):
# #         return f"{self.student_id} ({self.batch})"

# # class Bench(models.Model):
# #     room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='benches')
# #     row_num = models.IntegerField()
# #     col_num = models.IntegerField()
# #     students = models.ManyToManyField(Student, blank=True)

# #     class Meta:
# #         unique_together = ('room', 'row_num', 'col_num')
# #         ordering = ['col_num', 'row_num'] # Order benches by column, then row

# #     def __str__(self):
# #         return f"{self.room.name} - Col {self.col_num}, Row {self.row_num}"

# # class Absentee(models.Model):
# #     room = models.ForeignKey(Room, on_delete=models.CASCADE)
# #     student = models.ForeignKey(Student, on_delete=models.CASCADE)
# #     timestamp = models.DateTimeField(auto_now_add=True)

# #     def __str__(self):
# #         return f"{self.student.student_id} in {self.room.name}"











# # attendance/models.py
# from django.db import models

# class Room(models.Model):
#     name = models.CharField(max_length=100, unique=True)
#     columns = models.IntegerField(default=4)
#     benches_per_column = models.IntegerField(default=6)
#     students_per_bench = models.IntegerField(default=3)

#     def __str__(self):
#         return self.name

# class Student(models.Model):
#     student_id = models.CharField(max_length=20, unique=True)
#     batch = models.CharField(max_length=50, default='General')

#     def __str__(self):
#         return f"{self.student_id} ({self.batch})"

# class Bench(models.Model):
#     room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='benches')
#     row_num = models.IntegerField()
#     col_num = models.IntegerField()
#     # Updated ManyToManyField to use a 'through' model to preserve order
#     students = models.ManyToManyField(Student, through='SeatingAssignment', blank=True)

#     class Meta:
#         unique_together = ('room', 'row_num', 'col_num')
#         ordering = ['col_num', 'row_num']

#     def __str__(self):
#         return f"{self.room.name} - Col {self.col_num}, Row {self.row_num}"

# class SeatingAssignment(models.Model):
#     """This 'through' model ensures student order is preserved on a bench."""
#     student = models.ForeignKey(Student, on_delete=models.CASCADE)
#     bench = models.ForeignKey(Bench, on_delete=models.CASCADE)
#     # The default ordering by creation time is crucial.
#     assignment_time = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['assignment_time']

# class Absentee(models.Model):
#     room = models.ForeignKey(Room, on_delete=models.CASCADE)
#     student = models.ForeignKey(Student, on_delete=models.CASCADE)
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.student.student_id} in {self.room.name}"




















# attendance/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Room(models.Model):
    name = models.CharField(max_length=100, unique=True)
    columns = models.IntegerField(default=4)
    benches_per_column = models.IntegerField(default=6)
    students_per_bench = models.IntegerField(default=3)

    def __str__(self):
        return self.name

class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    batch = models.CharField(max_length=50, default='General')

    def __str__(self):
        return f"{self.student_id} ({self.batch})"

class Bench(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='benches')
    row_num = models.IntegerField()
    col_num = models.IntegerField()
    students = models.ManyToManyField(Student, through='SeatingAssignment', blank=True)

    class Meta:
        unique_together = ('room', 'row_num', 'col_num')
        ordering = ['col_num', 'row_num']

    def __str__(self):
        return f"{self.room.name} - Col {self.col_num}, Row {self.row_num}"

class SeatingAssignment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    bench = models.ForeignKey(Bench, on_delete=models.CASCADE)
    assignment_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['assignment_time']

class Absentee(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.student_id} in {self.room.name}"

class InvigilatorAssignment(models.Model):
    invigilator = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_staff': False})
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_column = models.IntegerField()
    end_column = models.IntegerField()

    def __str__(self):
        return f"{self.invigilator.username} assigned to {self.room.name} (Cols {self.start_column}-{self.end_column})"

    class Meta:
        unique_together = ('invigilator', 'room')
