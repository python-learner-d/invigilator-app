# # # # # # # # # # # # # # # # # # # # # attendance/views.py

# # # # # # # # # # # # # # # # # # # # from django.shortcuts import render, get_object_or_404, redirect
# # # # # # # # # # # # # # # # # # # # from django.http import JsonResponse
# # # # # # # # # # # # # # # # # # # # from django.views.decorators.csrf import csrf_exempt
# # # # # # # # # # # # # # # # # # # # from django.contrib import messages
# # # # # # # # # # # # # # # # # # # # import json
# # # # # # # # # # # # # # # # # # # # import pandas as pd

# # # # # # # # # # # # # # # # # # # # from .models import Room, Student, Bench, Absentee

# # # # # # # # # # # # # # # # # # # # def room_list(request):
# # # # # # # # # # # # # # # # # # # #     rooms = Room.objects.all()
# # # # # # # # # # # # # # # # # # # #     return render(request, 'attendance/room_list.html', {'rooms': rooms})

# # # # # # # # # # # # # # # # # # # # def seating_plan_view(request, room_id):
# # # # # # # # # # # # # # # # # # # #     room = get_object_or_404(Room, pk=room_id)
# # # # # # # # # # # # # # # # # # # #     benches = Bench.objects.filter(room=room).order_by('col_num', 'row_num')
# # # # # # # # # # # # # # # # # # # #     plan = [[] for _ in range(room.columns)]
# # # # # # # # # # # # # # # # # # # #     for bench in benches:
# # # # # # # # # # # # # # # # # # # #         # Ensure the student list on a bench is ordered by their ID for consistency
# # # # # # # # # # # # # # # # # # # #         bench.ordered_students = bench.students.order_by('id')
# # # # # # # # # # # # # # # # # # # #         plan[bench.col_num - 1].append(bench)
        
# # # # # # # # # # # # # # # # # # # #     return render(request, 'attendance/seating_plan.html', {'room': room, 'plan': plan})

# # # # # # # # # # # # # # # # # # # # @csrf_exempt
# # # # # # # # # # # # # # # # # # # # def mark_absent(request):
# # # # # # # # # # # # # # # # # # # #     # This view remains the same
# # # # # # # # # # # # # # # # # # # #     if request.method == 'POST':
# # # # # # # # # # # # # # # # # # # #         data = json.loads(request.body)
# # # # # # # # # # # # # # # # # # # #         student_id, room_id = data.get('student_id'), data.get('room_id')
# # # # # # # # # # # # # # # # # # # #         if not student_id or not room_id:
# # # # # # # # # # # # # # # # # # # #             return JsonResponse({'status': 'error', 'message': 'Missing data'}, status=400)
# # # # # # # # # # # # # # # # # # # #         try:
# # # # # # # # # # # # # # # # # # # #             student = Student.objects.get(student_id=student_id)
# # # # # # # # # # # # # # # # # # # #             room = Room.objects.get(id=room_id)
# # # # # # # # # # # # # # # # # # # #             Absentee.objects.get_or_create(room=room, student=student)
# # # # # # # # # # # # # # # # # # # #             return JsonResponse({'status': 'success', 'message': f'Student {student_id} marked absent.'})
# # # # # # # # # # # # # # # # # # # #         except (Student.DoesNotExist, Room.DoesNotExist):
# # # # # # # # # # # # # # # # # # # #             return JsonResponse({'status': 'error', 'message': 'Invalid ID'}, status=404)
# # # # # # # # # # # # # # # # # # # #     return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=405)

# # # # # # # # # # # # # # # # # # # # def upload_plan(request): # RENAMED FUNCTION
# # # # # # # # # # # # # # # # # # # #     if request.method == 'POST':
# # # # # # # # # # # # # # # # # # # #         excel_file = request.FILES.get('excel_file')
# # # # # # # # # # # # # # # # # # # #         if not excel_file or not excel_file.name.endswith('.xlsx'):
# # # # # # # # # # # # # # # # # # # #             messages.error(request, 'Please upload a valid .xlsx file.')
# # # # # # # # # # # # # # # # # # # #             return redirect('upload_plan') # UPDATED REDIRECT
        
# # # # # # # # # # # # # # # # # # # #         try:
# # # # # # # # # # # # # # # # # # # #             xls = pd.ExcelFile(excel_file)
# # # # # # # # # # # # # # # # # # # #             seated_count = 0
# # # # # # # # # # # # # # # # # # # #             # Clear all existing bench assignments before creating new ones
# # # # # # # # # # # # # # # # # # # #             Bench.objects.all().delete()

# # # # # # # # # # # # # # # # # # # #             for sheet_name in xls.sheet_names:
# # # # # # # # # # # # # # # # # # # #                 try:
# # # # # # # # # # # # # # # # # # # #                     room = Room.objects.get(name=sheet_name)
# # # # # # # # # # # # # # # # # # # #                     df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
                    
# # # # # # # # # # # # # # # # # # # #                     # Iterate through the dataframe (rows and columns of the excel sheet)
# # # # # # # # # # # # # # # # # # # #                     for r_idx, row in df.iterrows():
# # # # # # # # # # # # # # # # # # # #                         for c_idx, student_id in enumerate(row):
# # # # # # # # # # # # # # # # # # # #                             if pd.notna(student_id):
# # # # # # # # # # # # # # # # # # # #                                 student_id_str = str(student_id)
                                
# # # # # # # # # # # # # # # # # # # #                                 # Get or create the student
# # # # # # # # # # # # # # # # # # # #                                 student, _ = Student.objects.get_or_create(student_id=student_id_str)
                                
# # # # # # # # # # # # # # # # # # # #                                 # Determine the physical bench this student belongs to
# # # # # # # # # # # # # # # # # # # #                                 bench_col_num = (c_idx // room.students_per_bench) + 1
# # # # # # # # # # # # # # # # # # # #                                 bench_row_num = r_idx + 1
                                
# # # # # # # # # # # # # # # # # # # #                                 if bench_col_num <= room.columns and bench_row_num <= room.benches_per_column:
# # # # # # # # # # # # # # # # # # # #                                     bench, _ = Bench.objects.get_or_create(
# # # # # # # # # # # # # # # # # # # #                                         room=room,
# # # # # # # # # # # # # # # # # # # #                                         row_num=bench_row_num,
# # # # # # # # # # # # # # # # # # # #                                         col_num=bench_col_num
# # # # # # # # # # # # # # # # # # # #                                     )
# # # # # # # # # # # # # # # # # # # #                                     bench.students.add(student)
# # # # # # # # # # # # # # # # # # # #                                     seated_count += 1

# # # # # # # # # # # # # # # # # # # #                 except Room.DoesNotExist:
# # # # # # # # # # # # # # # # # # # #                     messages.warning(request, f'A room named "{sheet_name}" was found in the Excel file but does not exist in the database. It was ignored.')
# # # # # # # # # # # # # # # # # # # #                     continue

# # # # # # # # # # # # # # # # # # # #             messages.success(request, f'Successfully processed file and seated {seated_count} students.')
# # # # # # # # # # # # # # # # # # # #             return redirect('room_list')

# # # # # # # # # # # # # # # # # # # #         except Exception as e:
# # # # # # # # # # # # # # # # # # # #             messages.error(request, f'An error occurred: {e}')
# # # # # # # # # # # # # # # # # # # #             return redirect('upload_plan') # UPDATED REDIRECT

# # # # # # # # # # # # # # # # # # # #     return render(request, 'attendance/upload_plan.html') # RENAMED TEMPLATE

























# # # # # # # # # # # # # # # # # # # # attendance/views.py

# # # # # # # # # # # # # # # # # # # from django.shortcuts import render, get_object_or_404, redirect
# # # # # # # # # # # # # # # # # # # from django.http import JsonResponse
# # # # # # # # # # # # # # # # # # # from django.views.decorators.csrf import csrf_exempt
# # # # # # # # # # # # # # # # # # # from django.contrib import messages
# # # # # # # # # # # # # # # # # # # from collections import defaultdict
# # # # # # # # # # # # # # # # # # # import json
# # # # # # # # # # # # # # # # # # # import pandas as pd

# # # # # # # # # # # # # # # # # # # from .models import Room, Student, Bench, Absentee

# # # # # # # # # # # # # # # # # # # def room_list(request):
# # # # # # # # # # # # # # # # # # #     rooms = Room.objects.all()
# # # # # # # # # # # # # # # # # # #     return render(request, 'attendance/room_list.html', {'rooms': rooms})

# # # # # # # # # # # # # # # # # # # def seating_plan_view(request, room_id):
# # # # # # # # # # # # # # # # # # #     room = get_object_or_404(Room, pk=room_id)
# # # # # # # # # # # # # # # # # # #     benches = Bench.objects.filter(room=room).order_by('col_num', 'row_num')
# # # # # # # # # # # # # # # # # # #     plan = [[] for _ in range(room.columns)]
# # # # # # # # # # # # # # # # # # #     for bench in benches:
# # # # # # # # # # # # # # # # # # #         bench.ordered_students = bench.students.order_by('id')
# # # # # # # # # # # # # # # # # # #         plan[bench.col_num - 1].append(bench)
        
# # # # # # # # # # # # # # # # # # #     return render(request, 'attendance/seating_plan.html', {'room': room, 'plan': plan})

# # # # # # # # # # # # # # # # # # # @csrf_exempt
# # # # # # # # # # # # # # # # # # # def mark_absent(request):
# # # # # # # # # # # # # # # # # # #     if request.method == 'POST':
# # # # # # # # # # # # # # # # # # #         data = json.loads(request.body)
# # # # # # # # # # # # # # # # # # #         student_id, room_id = data.get('student_id'), data.get('room_id')
# # # # # # # # # # # # # # # # # # #         if not student_id or not room_id:
# # # # # # # # # # # # # # # # # # #             return JsonResponse({'status': 'error', 'message': 'Missing data'}, status=400)
# # # # # # # # # # # # # # # # # # #         try:
# # # # # # # # # # # # # # # # # # #             student = Student.objects.get(student_id=student_id)
# # # # # # # # # # # # # # # # # # #             room = Room.objects.get(id=room_id)
# # # # # # # # # # # # # # # # # # #             Absentee.objects.get_or_create(room=room, student=student)
# # # # # # # # # # # # # # # # # # #             return JsonResponse({'status': 'success', 'message': f'Student {student_id} marked absent.'})
# # # # # # # # # # # # # # # # # # #         except (Student.DoesNotExist, Room.DoesNotExist):
# # # # # # # # # # # # # # # # # # #             return JsonResponse({'status': 'error', 'message': 'Invalid ID'}, status=404)
# # # # # # # # # # # # # # # # # # #     return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=405)

# # # # # # # # # # # # # # # # # # # def upload_students(request):
# # # # # # # # # # # # # # # # # # #     if request.method == 'POST':
# # # # # # # # # # # # # # # # # # #         excel_file = request.FILES.get('excel_file')
# # # # # # # # # # # # # # # # # # #         if not excel_file or not excel_file.name.endswith('.xlsx'):
# # # # # # # # # # # # # # # # # # #             messages.error(request, 'Please upload a valid .xlsx file.')
# # # # # # # # # # # # # # # # # # #             return redirect('upload_students')
        
# # # # # # # # # # # # # # # # # # #         try:
# # # # # # # # # # # # # # # # # # #             df = pd.read_excel(excel_file)
# # # # # # # # # # # # # # # # # # #             required_cols = ['StudentID', 'Batch']
# # # # # # # # # # # # # # # # # # #             if not all(col in df.columns for col in required_cols):
# # # # # # # # # # # # # # # # # # #                 messages.error(request, "Excel file must have columns named 'StudentID' and 'Batch'.")
# # # # # # # # # # # # # # # # # # #                 return redirect('upload_students')

# # # # # # # # # # # # # # # # # # #             created_count = 0
# # # # # # # # # # # # # # # # # # #             for index, row in df.iterrows():
# # # # # # # # # # # # # # # # # # #                 sid = str(row['StudentID'])
# # # # # # # # # # # # # # # # # # #                 batch_name = str(row['Batch'])
                
# # # # # # # # # # # # # # # # # # #                 student, created = Student.objects.update_or_create(
# # # # # # # # # # # # # # # # # # #                     student_id=sid,
# # # # # # # # # # # # # # # # # # #                     defaults={'batch': batch_name}
# # # # # # # # # # # # # # # # # # #                 )
# # # # # # # # # # # # # # # # # # #                 if created:
# # # # # # # # # # # # # # # # # # #                     created_count += 1
            
# # # # # # # # # # # # # # # # # # #             messages.success(request, f'Successfully processed file. Added {created_count} new students.')
# # # # # # # # # # # # # # # # # # #             return redirect('room_list')

# # # # # # # # # # # # # # # # # # #         except Exception as e:
# # # # # # # # # # # # # # # # # # #             messages.error(request, f'An error occurred: {e}')
# # # # # # # # # # # # # # # # # # #             return redirect('upload_students')

# # # # # # # # # # # # # # # # # # #     return render(request, 'attendance/upload_students.html')

# # # # # # # # # # # # # # # # # # # def auto_arrange_seating(request, room_id):
# # # # # # # # # # # # # # # # # # #     room_to_arrange = get_object_or_404(Room, pk=room_id)
    
# # # # # # # # # # # # # # # # # # #     seated_students_ids = Bench.objects.values_list('students', flat=True)
# # # # # # # # # # # # # # # # # # #     students_to_seat = Student.objects.exclude(id__in=seated_students_ids).order_by('id')

# # # # # # # # # # # # # # # # # # #     if not students_to_seat:
# # # # # # # # # # # # # # # # # # #         messages.warning(request, 'No unseated students available to arrange.')
# # # # # # # # # # # # # # # # # # #         return redirect('room_list')

# # # # # # # # # # # # # # # # # # #     Bench.objects.filter(room=room_to_arrange).delete()

# # # # # # # # # # # # # # # # # # #     students_by_batch = defaultdict(list)
# # # # # # # # # # # # # # # # # # #     for student in students_to_seat:
# # # # # # # # # # # # # # # # # # #         students_by_batch[student.batch].append(student)

# # # # # # # # # # # # # # # # # # #     batch_names = sorted(students_by_batch.keys())
    
# # # # # # # # # # # # # # # # # # #     if len(batch_names) < 2:
# # # # # # # # # # # # # # # # # # #         messages.warning(request, 'Seating arrangement requires at least two batches of students.')
# # # # # # # # # # # # # # # # # # #         return redirect('room_list')
        
# # # # # # # # # # # # # # # # # # #     if room_to_arrange.id % 2 != 0:
# # # # # # # # # # # # # # # # # # #         batch_order = batch_names
# # # # # # # # # # # # # # # # # # #     else:
# # # # # # # # # # # # # # # # # # #         batch_order = list(reversed(batch_names))

# # # # # # # # # # # # # # # # # # #     seated_count = 0
# # # # # # # # # # # # # # # # # # #     total_virtual_columns = room_to_arrange.columns * room_to_arrange.students_per_bench

# # # # # # # # # # # # # # # # # # #     for virtual_col_idx in range(total_virtual_columns):
# # # # # # # # # # # # # # # # # # #         batch_to_pick_name = batch_order[virtual_col_idx % len(batch_order)]
        
# # # # # # # # # # # # # # # # # # #         real_bench_col = (virtual_col_idx // room_to_arrange.students_per_bench) + 1
        
# # # # # # # # # # # # # # # # # # #         for r in range(1, room_to_arrange.benches_per_column + 1):
# # # # # # # # # # # # # # # # # # #             if students_by_batch[batch_to_pick_name]:
# # # # # # # # # # # # # # # # # # #                 student = students_by_batch[batch_to_pick_name].pop(0)
                
# # # # # # # # # # # # # # # # # # #                 bench, _ = Bench.objects.get_or_create(room=room_to_arrange, row_num=r, col_num=real_bench_col)
# # # # # # # # # # # # # # # # # # #                 bench.students.add(student)
# # # # # # # # # # # # # # # # # # #                 seated_count += 1
# # # # # # # # # # # # # # # # # # #             else:
# # # # # # # # # # # # # # # # # # #                 break
            
# # # # # # # # # # # # # # # # # # #     messages.success(request, f'Successfully arranged {seated_count} students in {room_to_arrange.name}.')
# # # # # # # # # # # # # # # # # # #     return redirect('room_list')



















# # # # # # # # # # # # # # # # # # # attendance/views.py

# # # # # # # # # # # # # # # # # # from django.shortcuts import render, get_object_or_404, redirect
# # # # # # # # # # # # # # # # # # from django.http import JsonResponse
# # # # # # # # # # # # # # # # # # from django.views.decorators.csrf import csrf_exempt
# # # # # # # # # # # # # # # # # # from django.contrib import messages
# # # # # # # # # # # # # # # # # # from collections import defaultdict
# # # # # # # # # # # # # # # # # # import json
# # # # # # # # # # # # # # # # # # import pandas as pd

# # # # # # # # # # # # # # # # # # from .models import Room, Student, Bench, Absentee

# # # # # # # # # # # # # # # # # # def room_list(request):
# # # # # # # # # # # # # # # # # #     rooms = Room.objects.all()
# # # # # # # # # # # # # # # # # #     return render(request, 'attendance/room_list.html', {'rooms': rooms})

# # # # # # # # # # # # # # # # # # def seating_plan_view(request, room_id):
# # # # # # # # # # # # # # # # # #     room = get_object_or_404(Room, pk=room_id)
# # # # # # # # # # # # # # # # # #     benches = Bench.objects.filter(room=room).order_by('col_num', 'row_num')
# # # # # # # # # # # # # # # # # #     plan = [[] for _ in range(room.columns)]
    
# # # # # # # # # # # # # # # # # #     for bench in benches:
# # # # # # # # # # # # # # # # # #         # Prepare a list of seats, including placeholders for empty ones
# # # # # # # # # # # # # # # # # #         students_on_bench = list(bench.students.order_by('id'))
# # # # # # # # # # # # # # # # # #         seats = []
# # # # # # # # # # # # # # # # # #         for i in range(room.students_per_bench):
# # # # # # # # # # # # # # # # # #             if i < len(students_on_bench):
# # # # # # # # # # # # # # # # # #                 seats.append(students_on_bench[i])
# # # # # # # # # # # # # # # # # #             else:
# # # # # # # # # # # # # # # # # #                 seats.append(None) # Add a placeholder for an empty seat
# # # # # # # # # # # # # # # # # #         bench.seats = seats
# # # # # # # # # # # # # # # # # #         plan[bench.col_num - 1].append(bench)
        
# # # # # # # # # # # # # # # # # #     return render(request, 'attendance/seating_plan.html', {'room': room, 'plan': plan})

# # # # # # # # # # # # # # # # # # @csrf_exempt
# # # # # # # # # # # # # # # # # # def mark_absent(request):
# # # # # # # # # # # # # # # # # #     if request.method == 'POST':
# # # # # # # # # # # # # # # # # #         data = json.loads(request.body)
# # # # # # # # # # # # # # # # # #         student_id, room_id = data.get('student_id'), data.get('room_id')
# # # # # # # # # # # # # # # # # #         if not student_id or not room_id:
# # # # # # # # # # # # # # # # # #             return JsonResponse({'status': 'error', 'message': 'Missing data'}, status=400)
# # # # # # # # # # # # # # # # # #         try:
# # # # # # # # # # # # # # # # # #             student = Student.objects.get(student_id=student_id)
# # # # # # # # # # # # # # # # # #             room = Room.objects.get(id=room_id)
# # # # # # # # # # # # # # # # # #             Absentee.objects.get_or_create(room=room, student=student)
# # # # # # # # # # # # # # # # # #             return JsonResponse({'status': 'success', 'message': f'Student {student_id} marked absent.'})
# # # # # # # # # # # # # # # # # #         except (Student.DoesNotExist, Room.DoesNotExist):
# # # # # # # # # # # # # # # # # #             return JsonResponse({'status': 'error', 'message': 'Invalid ID'}, status=404)
# # # # # # # # # # # # # # # # # #     return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=405)

# # # # # # # # # # # # # # # # # # def upload_students(request):
# # # # # # # # # # # # # # # # # #     if request.method == 'POST':
# # # # # # # # # # # # # # # # # #         excel_file = request.FILES.get('excel_file')
# # # # # # # # # # # # # # # # # #         if not excel_file or not excel_file.name.endswith('.xlsx'):
# # # # # # # # # # # # # # # # # #             messages.error(request, 'Please upload a valid .xlsx file.')
# # # # # # # # # # # # # # # # # #             return redirect('upload_students')
        
# # # # # # # # # # # # # # # # # #         try:
# # # # # # # # # # # # # # # # # #             df = pd.read_excel(excel_file)
# # # # # # # # # # # # # # # # # #             required_cols = ['StudentID', 'Batch']
# # # # # # # # # # # # # # # # # #             if not all(col in df.columns for col in required_cols):
# # # # # # # # # # # # # # # # # #                 messages.error(request, "Excel file must have columns named 'StudentID' and 'Batch'.")
# # # # # # # # # # # # # # # # # #                 return redirect('upload_students')

# # # # # # # # # # # # # # # # # #             created_count = 0
# # # # # # # # # # # # # # # # # #             for index, row in df.iterrows():
# # # # # # # # # # # # # # # # # #                 sid = str(row['StudentID'])
# # # # # # # # # # # # # # # # # #                 batch_name = str(row['Batch'])
                
# # # # # # # # # # # # # # # # # #                 student, created = Student.objects.update_or_create(
# # # # # # # # # # # # # # # # # #                     student_id=sid,
# # # # # # # # # # # # # # # # # #                     defaults={'batch': batch_name}
# # # # # # # # # # # # # # # # # #                 )
# # # # # # # # # # # # # # # # # #                 if created:
# # # # # # # # # # # # # # # # # #                     created_count += 1
            
# # # # # # # # # # # # # # # # # #             messages.success(request, f'Successfully processed file. Added {created_count} new students.')
# # # # # # # # # # # # # # # # # #             return redirect('room_list')

# # # # # # # # # # # # # # # # # #         except Exception as e:
# # # # # # # # # # # # # # # # # #             messages.error(request, f'An error occurred: {e}')
# # # # # # # # # # # # # # # # # #             return redirect('upload_students')

# # # # # # # # # # # # # # # # # #     return render(request, 'attendance/upload_students.html')

# # # # # # # # # # # # # # # # # # def auto_arrange_seating(request, room_id):
# # # # # # # # # # # # # # # # # #     room_to_arrange = get_object_or_404(Room, pk=room_id)
    
# # # # # # # # # # # # # # # # # #     seated_students_ids = Bench.objects.values_list('students', flat=True)
# # # # # # # # # # # # # # # # # #     students_to_seat = Student.objects.exclude(id__in=seated_students_ids).order_by('id')

# # # # # # # # # # # # # # # # # #     if not students_to_seat:
# # # # # # # # # # # # # # # # # #         messages.warning(request, 'No unseated students available to arrange.')
# # # # # # # # # # # # # # # # # #         return redirect('room_list')

# # # # # # # # # # # # # # # # # #     Bench.objects.filter(room=room_to_arrange).delete()

# # # # # # # # # # # # # # # # # #     students_by_batch = defaultdict(list)
# # # # # # # # # # # # # # # # # #     for student in students_to_seat:
# # # # # # # # # # # # # # # # # #         students_by_batch[student.batch].append(student)

# # # # # # # # # # # # # # # # # #     batch_names = sorted(students_by_batch.keys())
    
# # # # # # # # # # # # # # # # # #     if len(batch_names) < 2:
# # # # # # # # # # # # # # # # # #         messages.warning(request, 'Seating arrangement requires at least two batches of students.')
# # # # # # # # # # # # # # # # # #         return redirect('room_list')
        
# # # # # # # # # # # # # # # # # #     if room_to_arrange.id % 2 != 0:
# # # # # # # # # # # # # # # # # #         batch_order = batch_names
# # # # # # # # # # # # # # # # # #     else:
# # # # # # # # # # # # # # # # # #         batch_order = list(reversed(batch_names))

# # # # # # # # # # # # # # # # # #     seated_count = 0
# # # # # # # # # # # # # # # # # #     total_virtual_columns = room_to_arrange.columns * room_to_arrange.students_per_bench

# # # # # # # # # # # # # # # # # #     for virtual_col_idx in range(total_virtual_columns):
# # # # # # # # # # # # # # # # # #         batch_to_pick_name = batch_order[virtual_col_idx % len(batch_order)]
        
# # # # # # # # # # # # # # # # # #         real_bench_col = (virtual_col_idx // room_to_arrange.students_per_bench) + 1
        
# # # # # # # # # # # # # # # # # #         for r in range(1, room_to_arrange.benches_per_column + 1):
# # # # # # # # # # # # # # # # # #             if students_by_batch[batch_to_pick_name]:
# # # # # # # # # # # # # # # # # #                 student = students_by_batch[batch_to_pick_name].pop(0)
                
# # # # # # # # # # # # # # # # # #                 bench, _ = Bench.objects.get_or_create(room=room_to_arrange, row_num=r, col_num=real_bench_col)
# # # # # # # # # # # # # # # # # #                 bench.students.add(student)
# # # # # # # # # # # # # # # # # #                 seated_count += 1
# # # # # # # # # # # # # # # # # #             else:
# # # # # # # # # # # # # # # # # #                 break
            
# # # # # # # # # # # # # # # # # #     messages.success(request, f'Successfully arranged {seated_count} students in {room_to_arrange.name}.')
# # # # # # # # # # # # # # # # # #     return redirect('room_list')


























# # # # # # # # # # # # # # # # # from django.shortcuts import render, get_object_or_404, redirect
# # # # # # # # # # # # # # # # # from django.http import JsonResponse
# # # # # # # # # # # # # # # # # from django.views.decorators.csrf import csrf_exempt
# # # # # # # # # # # # # # # # # from django.contrib import messages
# # # # # # # # # # # # # # # # # from collections import defaultdict
# # # # # # # # # # # # # # # # # import json
# # # # # # # # # # # # # # # # # import pandas as pd

# # # # # # # # # # # # # # # # # from .models import Room, Student, Bench, Absentee

# # # # # # # # # # # # # # # # # def room_list(request):
# # # # # # # # # # # # # # # # #     rooms = Room.objects.all()
# # # # # # # # # # # # # # # # #     return render(request, 'attendance/room_list.html', {'rooms': rooms})

# # # # # # # # # # # # # # # # # def seating_plan_view(request, room_id):
# # # # # # # # # # # # # # # # #     room = get_object_or_404(Room, pk=room_id)
# # # # # # # # # # # # # # # # #     benches = Bench.objects.filter(room=room).order_by('col_num', 'row_num')
# # # # # # # # # # # # # # # # #     plan = [[] for _ in range(room.columns)]
    
# # # # # # # # # # # # # # # # #     for bench in benches:
# # # # # # # # # # # # # # # # #         # Prepare a list of seats, including placeholders for empty ones
# # # # # # # # # # # # # # # # #         students_on_bench = list(bench.students.order_by('id'))
# # # # # # # # # # # # # # # # #         seats = []
# # # # # # # # # # # # # # # # #         for i in range(room.students_per_bench):
# # # # # # # # # # # # # # # # #             if i < len(students_on_bench):
# # # # # # # # # # # # # # # # #                 seats.append(students_on_bench[i])
# # # # # # # # # # # # # # # # #             else:
# # # # # # # # # # # # # # # # #                 seats.append(None) # Add a placeholder for an empty seat
# # # # # # # # # # # # # # # # #         bench.seats = seats
# # # # # # # # # # # # # # # # #         plan[bench.col_num - 1].append(bench)
        
# # # # # # # # # # # # # # # # #     return render(request, 'attendance/seating_plan.html', {'room': room, 'plan': plan})

# # # # # # # # # # # # # # # # # @csrf_exempt
# # # # # # # # # # # # # # # # # def mark_absent(request):
# # # # # # # # # # # # # # # # #     if request.method == 'POST':
# # # # # # # # # # # # # # # # #         data = json.loads(request.body)
# # # # # # # # # # # # # # # # #         student_id, room_id = data.get('student_id'), data.get('room_id')
# # # # # # # # # # # # # # # # #         if not student_id or not room_id:
# # # # # # # # # # # # # # # # #             return JsonResponse({'status': 'error', 'message': 'Missing data'}, status=400)
# # # # # # # # # # # # # # # # #         try:
# # # # # # # # # # # # # # # # #             student = Student.objects.get(student_id=student_id)
# # # # # # # # # # # # # # # # #             room = Room.objects.get(id=room_id)
# # # # # # # # # # # # # # # # #             Absentee.objects.get_or_create(room=room, student=student)
# # # # # # # # # # # # # # # # #             return JsonResponse({'status': 'success', 'message': f'Student {student_id} marked absent.'})
# # # # # # # # # # # # # # # # #         except (Student.DoesNotExist, Room.DoesNotExist):
# # # # # # # # # # # # # # # # #             return JsonResponse({'status': 'error', 'message': 'Invalid ID'}, status=404)
# # # # # # # # # # # # # # # # #     return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=405)

# # # # # # # # # # # # # # # # # def upload_students(request):
# # # # # # # # # # # # # # # # #     if request.method == 'POST':
# # # # # # # # # # # # # # # # #         excel_file = request.FILES.get('excel_file')
# # # # # # # # # # # # # # # # #         if not excel_file or not excel_file.name.endswith('.xlsx'):
# # # # # # # # # # # # # # # # #             messages.error(request, 'Please upload a valid .xlsx file.')
# # # # # # # # # # # # # # # # #             return redirect('upload_students')
        
# # # # # # # # # # # # # # # # #         try:
# # # # # # # # # # # # # # # # #             df = pd.read_excel(excel_file)
# # # # # # # # # # # # # # # # #             required_cols = ['StudentID', 'Batch']
# # # # # # # # # # # # # # # # #             if not all(col in df.columns for col in required_cols):
# # # # # # # # # # # # # # # # #                 messages.error(request, "Excel file must have columns named 'StudentID' and 'Batch'.")
# # # # # # # # # # # # # # # # #                 return redirect('upload_students')

# # # # # # # # # # # # # # # # #             created_count = 0
# # # # # # # # # # # # # # # # #             for index, row in df.iterrows():
# # # # # # # # # # # # # # # # #                 sid = str(row['StudentID'])
# # # # # # # # # # # # # # # # #                 batch_name = str(row['Batch'])
                
# # # # # # # # # # # # # # # # #                 student, created = Student.objects.update_or_create(
# # # # # # # # # # # # # # # # #                     student_id=sid,
# # # # # # # # # # # # # # # # #                     defaults={'batch': batch_name}
# # # # # # # # # # # # # # # # #                 )
# # # # # # # # # # # # # # # # #                 if created:
# # # # # # # # # # # # # # # # #                     created_count += 1
            
# # # # # # # # # # # # # # # # #             messages.success(request, f'Successfully processed file. Added {created_count} new students.')
# # # # # # # # # # # # # # # # #             return redirect('room_list')

# # # # # # # # # # # # # # # # #         except Exception as e:
# # # # # # # # # # # # # # # # #             messages.error(request, f'An error occurred: {e}')
# # # # # # # # # # # # # # # # #             return redirect('upload_students')

# # # # # # # # # # # # # # # # #     return render(request, 'attendance/upload_students.html')

# # # # # # # # # # # # # # # # # def auto_arrange_seating(request, room_id):
# # # # # # # # # # # # # # # # #     room_to_arrange = get_object_or_404(Room, pk=room_id)
    
# # # # # # # # # # # # # # # # #     seated_students_ids = Bench.objects.values_list('students', flat=True)
# # # # # # # # # # # # # # # # #     students_to_seat = Student.objects.exclude(id__in=seated_students_ids).order_by('id')

# # # # # # # # # # # # # # # # #     if not students_to_seat:
# # # # # # # # # # # # # # # # #         messages.warning(request, 'No unseated students available to arrange.')
# # # # # # # # # # # # # # # # #         return redirect('room_list')

# # # # # # # # # # # # # # # # #     Bench.objects.filter(room=room_to_arrange).delete()

# # # # # # # # # # # # # # # # #     students_by_batch = defaultdict(list)
# # # # # # # # # # # # # # # # #     for student in students_to_seat:
# # # # # # # # # # # # # # # # #         students_by_batch[student.batch].append(student)

# # # # # # # # # # # # # # # # #     batch_names = sorted(students_by_batch.keys())
    
# # # # # # # # # # # # # # # # #     if len(batch_names) < 2:
# # # # # # # # # # # # # # # # #         messages.warning(request, 'Seating arrangement requires at least two batches of students.')
# # # # # # # # # # # # # # # # #         return redirect('room_list')
        
# # # # # # # # # # # # # # # # #     # Determine batch order based on room ID (odd/even)
# # # # # # # # # # # # # # # # #     if room_to_arrange.id % 2 != 0:
# # # # # # # # # # # # # # # # #         batch_order = batch_names
# # # # # # # # # # # # # # # # #     else:
# # # # # # # # # # # # # # # # #         batch_order = list(reversed(batch_names))

# # # # # # # # # # # # # # # # #     seated_count = 0
# # # # # # # # # # # # # # # # #     is_finished = False

# # # # # # # # # # # # # # # # #     # Iterate through each "super-row"
# # # # # # # # # # # # # # # # #     for r in range(1, room_to_arrange.benches_per_column + 1):
# # # # # # # # # # # # # # # # #         # Iterate through each seat in the super-row
# # # # # # # # # # # # # # # # #         for seat_in_row in range(room_to_arrange.columns * room_to_arrange.students_per_bench):
# # # # # # # # # # # # # # # # #             # Determine which batch to pick for this seat based on the alternating pattern
# # # # # # # # # # # # # # # # #             batch_to_pick_name = batch_order[seat_in_row % len(batch_order)]

# # # # # # # # # # # # # # # # #             if students_by_batch[batch_to_pick_name]:
# # # # # # # # # # # # # # # # #                 student = students_by_batch[batch_to_pick_name].pop(0)
                
# # # # # # # # # # # # # # # # #                 # Calculate which column and bench this student belongs to
# # # # # # # # # # # # # # # # #                 col_num = (seat_in_row // room_to_arrange.students_per_bench) + 1
                
# # # # # # # # # # # # # # # # #                 bench, _ = Bench.objects.get_or_create(room=room_to_arrange, row_num=r, col_num=col_num)
# # # # # # # # # # # # # # # # #                 bench.students.add(student)
# # # # # # # # # # # # # # # # #                 seated_count += 1
# # # # # # # # # # # # # # # # #             else:
# # # # # # # # # # # # # # # # #                 # A required batch is empty, so we cannot continue the arrangement.
# # # # # # # # # # # # # # # # #                 is_finished = True
# # # # # # # # # # # # # # # # #                 break
        
# # # # # # # # # # # # # # # # #         if is_finished:
# # # # # # # # # # # # # # # # #             break
            
# # # # # # # # # # # # # # # # #     messages.success(request, f'Successfully arranged {seated_count} students in {room_to_arrange.name}.')
# # # # # # # # # # # # # # # # #     return redirect('room_list')

















# # # # # # # # # # # # # # # # # attendance/views.py

# # # # # # # # # # # # # # # # from django.shortcuts import render, get_object_or_404, redirect
# # # # # # # # # # # # # # # # from django.http import JsonResponse
# # # # # # # # # # # # # # # # from django.views.decorators.csrf import csrf_exempt
# # # # # # # # # # # # # # # # from django.contrib import messages
# # # # # # # # # # # # # # # # from collections import defaultdict
# # # # # # # # # # # # # # # # import json
# # # # # # # # # # # # # # # # import pandas as pd

# # # # # # # # # # # # # # # # from .models import Room, Student, Bench, Absentee

# # # # # # # # # # # # # # # # def room_list(request):
# # # # # # # # # # # # # # # #     rooms = Room.objects.all()
# # # # # # # # # # # # # # # #     return render(request, 'attendance/room_list.html', {'rooms': rooms})

# # # # # # # # # # # # # # # # def seating_plan_view(request, room_id):
# # # # # # # # # # # # # # # #     room = get_object_or_404(Room, pk=room_id)
# # # # # # # # # # # # # # # #     benches = Bench.objects.filter(room=room).order_by('col_num', 'row_num')
# # # # # # # # # # # # # # # #     plan = [[] for _ in range(room.columns)]
    
# # # # # # # # # # # # # # # #     for bench in benches:
# # # # # # # # # # # # # # # #         # The database now preserves the correct order automatically via the 'through' model
# # # # # # # # # # # # # # # #         students_on_bench = list(bench.students.all())
# # # # # # # # # # # # # # # #         seats = []
# # # # # # # # # # # # # # # #         for i in range(room.students_per_bench):
# # # # # # # # # # # # # # # #             if i < len(students_on_bench):
# # # # # # # # # # # # # # # #                 seats.append(students_on_bench[i])
# # # # # # # # # # # # # # # #             else:
# # # # # # # # # # # # # # # #                 seats.append(None) # Add a placeholder for an empty seat
# # # # # # # # # # # # # # # #         bench.seats = seats
# # # # # # # # # # # # # # # #         plan[bench.col_num - 1].append(bench)
        
# # # # # # # # # # # # # # # #     return render(request, 'attendance/seating_plan.html', {'room': room, 'plan': plan})

# # # # # # # # # # # # # # # # @csrf_exempt
# # # # # # # # # # # # # # # # def mark_absent(request):
# # # # # # # # # # # # # # # #     if request.method == 'POST':
# # # # # # # # # # # # # # # #         data = json.loads(request.body)
# # # # # # # # # # # # # # # #         student_id, room_id = data.get('student_id'), data.get('room_id')
# # # # # # # # # # # # # # # #         if not student_id or not room_id:
# # # # # # # # # # # # # # # #             return JsonResponse({'status': 'error', 'message': 'Missing data'}, status=400)
# # # # # # # # # # # # # # # #         try:
# # # # # # # # # # # # # # # #             student = Student.objects.get(student_id=student_id)
# # # # # # # # # # # # # # # #             room = Room.objects.get(id=room_id)
# # # # # # # # # # # # # # # #             Absentee.objects.get_or_create(room=room, student=student)
# # # # # # # # # # # # # # # #             return JsonResponse({'status': 'success', 'message': f'Student {student_id} marked absent.'})
# # # # # # # # # # # # # # # #         except (Student.DoesNotExist, Room.DoesNotExist):
# # # # # # # # # # # # # # # #             return JsonResponse({'status': 'error', 'message': 'Invalid ID'}, status=404)
# # # # # # # # # # # # # # # #     return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=405)

# # # # # # # # # # # # # # # # def upload_students(request):
# # # # # # # # # # # # # # # #     if request.method == 'POST':
# # # # # # # # # # # # # # # #         excel_file = request.FILES.get('excel_file')
# # # # # # # # # # # # # # # #         if not excel_file or not excel_file.name.endswith('.xlsx'):
# # # # # # # # # # # # # # # #             messages.error(request, 'Please upload a valid .xlsx file.')
# # # # # # # # # # # # # # # #             return redirect('upload_students')
        
# # # # # # # # # # # # # # # #         try:
# # # # # # # # # # # # # # # #             df = pd.read_excel(excel_file)
# # # # # # # # # # # # # # # #             required_cols = ['StudentID', 'Batch']
# # # # # # # # # # # # # # # #             if not all(col in df.columns for col in required_cols):
# # # # # # # # # # # # # # # #                 messages.error(request, "Excel file must have columns named 'StudentID' and 'Batch'.")
# # # # # # # # # # # # # # # #                 return redirect('upload_students')

# # # # # # # # # # # # # # # #             created_count = 0
# # # # # # # # # # # # # # # #             for index, row in df.iterrows():
# # # # # # # # # # # # # # # #                 sid = str(row['StudentID'])
# # # # # # # # # # # # # # # #                 batch_name = str(row['Batch'])
                
# # # # # # # # # # # # # # # #                 student, created = Student.objects.update_or_create(
# # # # # # # # # # # # # # # #                     student_id=sid,
# # # # # # # # # # # # # # # #                     defaults={'batch': batch_name}
# # # # # # # # # # # # # # # #                 )
# # # # # # # # # # # # # # # #                 if created:
# # # # # # # # # # # # # # # #                     created_count += 1
            
# # # # # # # # # # # # # # # #             messages.success(request, f'Successfully processed file. Added {created_count} new students.')
# # # # # # # # # # # # # # # #             return redirect('room_list')

# # # # # # # # # # # # # # # #         except Exception as e:
# # # # # # # # # # # # # # # #             messages.error(request, f'An error occurred: {e}')
# # # # # # # # # # # # # # # #             return redirect('upload_students')

# # # # # # # # # # # # # # # #     return render(request, 'attendance/upload_students.html')

# # # # # # # # # # # # # # # # def auto_arrange_seating(request, room_id):
# # # # # # # # # # # # # # # #     room_to_arrange = get_object_or_404(Room, pk=room_id)
    
# # # # # # # # # # # # # # # #     seated_students_ids = Bench.objects.values_list('students', flat=True)
# # # # # # # # # # # # # # # #     students_to_seat = Student.objects.exclude(id__in=seated_students_ids).order_by('id')

# # # # # # # # # # # # # # # #     if not students_to_seat:
# # # # # # # # # # # # # # # #         messages.warning(request, 'No unseated students available to arrange.')
# # # # # # # # # # # # # # # #         return redirect('room_list')

# # # # # # # # # # # # # # # #     Bench.objects.filter(room=room_to_arrange).delete()

# # # # # # # # # # # # # # # #     students_by_batch = defaultdict(list)
# # # # # # # # # # # # # # # #     for student in students_to_seat:
# # # # # # # # # # # # # # # #         students_by_batch[student.batch].append(student)

# # # # # # # # # # # # # # # #     batch_names = sorted(students_by_batch.keys())
    
# # # # # # # # # # # # # # # #     if len(batch_names) < 2:
# # # # # # # # # # # # # # # #         messages.warning(request, 'Seating arrangement requires at least two batches of students.')
# # # # # # # # # # # # # # # #         return redirect('room_list')
        
# # # # # # # # # # # # # # # #     if room_to_arrange.id % 2 != 0:
# # # # # # # # # # # # # # # #         batch_order = batch_names
# # # # # # # # # # # # # # # #     else:
# # # # # # # # # # # # # # # #         batch_order = list(reversed(batch_names))

# # # # # # # # # # # # # # # #     seated_count = 0
# # # # # # # # # # # # # # # #     is_finished = False

# # # # # # # # # # # # # # # #     for r in range(1, room_to_arrange.benches_per_column + 1):
# # # # # # # # # # # # # # # #         for seat_in_row in range(room_to_arrange.columns * room_to_arrange.students_per_bench):
# # # # # # # # # # # # # # # #             batch_to_pick_name = batch_order[seat_in_row % len(batch_order)]

# # # # # # # # # # # # # # # #             if students_by_batch[batch_to_pick_name]:
# # # # # # # # # # # # # # # #                 student = students_by_batch[batch_to_pick_name].pop(0)
                
# # # # # # # # # # # # # # # #                 col_num = (seat_in_row // room_to_arrange.students_per_bench) + 1
                
# # # # # # # # # # # # # # # #                 bench, _ = Bench.objects.get_or_create(room=room_to_arrange, row_num=r, col_num=col_num)
# # # # # # # # # # # # # # # #                 bench.students.add(student)
# # # # # # # # # # # # # # # #                 seated_count += 1
# # # # # # # # # # # # # # # #             else:
# # # # # # # # # # # # # # # #                 is_finished = True
# # # # # # # # # # # # # # # #                 break
        
# # # # # # # # # # # # # # # #         if is_finished:
# # # # # # # # # # # # # # # #             break
            
# # # # # # # # # # # # # # # #     messages.success(request, f'Successfully arranged {seated_count} students in {room_to_arrange.name}.')
# # # # # # # # # # # # # # # #     return redirect('room_list')























# # # # # # # # # # # # # # # # attendance/views.py

# # # # # # # # # # # # # # # from django.shortcuts import render, get_object_or_404, redirect
# # # # # # # # # # # # # # # from django.http import JsonResponse
# # # # # # # # # # # # # # # from django.views.decorators.csrf import csrf_exempt
# # # # # # # # # # # # # # # from django.contrib import messages
# # # # # # # # # # # # # # # from collections import defaultdict
# # # # # # # # # # # # # # # import json
# # # # # # # # # # # # # # # import pandas as pd

# # # # # # # # # # # # # # # from .models import Room, Student, Bench, Absentee

# # # # # # # # # # # # # # # def room_list(request):
# # # # # # # # # # # # # # #     rooms = Room.objects.all()
# # # # # # # # # # # # # # #     return render(request, 'attendance/room_list.html', {'rooms': rooms})


# # # # # # # # # # # # # # # def seating_plan_view(request, room_id):
# # # # # # # # # # # # # # #     room = get_object_or_404(Room, pk=room_id)
# # # # # # # # # # # # # # #     benches = Bench.objects.filter(room=room).order_by('col_num', 'row_num')
# # # # # # # # # # # # # # #     plan = [[] for _ in range(room.columns)]
    
# # # # # # # # # # # # # # #     for bench in benches:
# # # # # # # # # # # # # # #         # The database now preserves the correct order automatically via the 'through' model
# # # # # # # # # # # # # # #         students_on_bench = list(bench.students.all())
# # # # # # # # # # # # # # #         seats = []
# # # # # # # # # # # # # # #         for i in range(room.students_per_bench):
# # # # # # # # # # # # # # #             if i < len(students_on_bench):
# # # # # # # # # # # # # # #                 seats.append(students_on_bench[i])
# # # # # # # # # # # # # # #             else:
# # # # # # # # # # # # # # #                 seats.append(None) # Add a placeholder for an empty seat
# # # # # # # # # # # # # # #         bench.seats = seats
# # # # # # # # # # # # # # #         plan[bench.col_num - 1].append(bench)
        
# # # # # # # # # # # # # # #     return render(request, 'attendance/seating_plan.html', {'room': room, 'plan': plan})



# # # # # # # # # # # # # # # @csrf_exempt
# # # # # # # # # # # # # # # def mark_absent(request):
# # # # # # # # # # # # # # #     if request.method == 'POST':
# # # # # # # # # # # # # # #         data = json.loads(request.body)
# # # # # # # # # # # # # # #         student_id, room_id = data.get('student_id'), data.get('room_id')
# # # # # # # # # # # # # # #         if not student_id or not room_id:
# # # # # # # # # # # # # # #             return JsonResponse({'status': 'error', 'message': 'Missing data'}, status=400)
# # # # # # # # # # # # # # #         try:
# # # # # # # # # # # # # # #             student = Student.objects.get(student_id=student_id)
# # # # # # # # # # # # # # #             room = Room.objects.get(id=room_id)
# # # # # # # # # # # # # # #             Absentee.objects.get_or_create(room=room, student=student)
# # # # # # # # # # # # # # #             return JsonResponse({'status': 'success', 'message': f'Student {student_id} marked absent.'})
# # # # # # # # # # # # # # #         except (Student.DoesNotExist, Room.DoesNotExist):
# # # # # # # # # # # # # # #             return JsonResponse({'status': 'error', 'message': 'Invalid ID'}, status=404)
# # # # # # # # # # # # # # #     return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=405)

# # # # # # # # # # # # # # # def upload_students(request):
# # # # # # # # # # # # # # #     if request.method == 'POST':
# # # # # # # # # # # # # # #         excel_file = request.FILES.get('excel_file')
# # # # # # # # # # # # # # #         if not excel_file or not excel_file.name.endswith('.xlsx'):
# # # # # # # # # # # # # # #             messages.error(request, 'Please upload a valid .xlsx file.')
# # # # # # # # # # # # # # #             return redirect('upload_students')
        
# # # # # # # # # # # # # # #         try:
# # # # # # # # # # # # # # #             df = pd.read_excel(excel_file)
# # # # # # # # # # # # # # #             required_cols = ['StudentID', 'Batch']
# # # # # # # # # # # # # # #             if not all(col in df.columns for col in required_cols):
# # # # # # # # # # # # # # #                 messages.error(request, "Excel file must have columns named 'StudentID' and 'Batch'.")
# # # # # # # # # # # # # # #                 return redirect('upload_students')

# # # # # # # # # # # # # # #             created_count = 0
# # # # # # # # # # # # # # #             for index, row in df.iterrows():
# # # # # # # # # # # # # # #                 sid = str(row['StudentID'])
# # # # # # # # # # # # # # #                 batch_name = str(row['Batch'])
                
# # # # # # # # # # # # # # #                 student, created = Student.objects.update_or_create(
# # # # # # # # # # # # # # #                     student_id=sid,
# # # # # # # # # # # # # # #                     defaults={'batch': batch_name}
# # # # # # # # # # # # # # #                 )
# # # # # # # # # # # # # # #                 if created:
# # # # # # # # # # # # # # #                     created_count += 1
            
# # # # # # # # # # # # # # #             messages.success(request, f'Successfully processed file. Added {created_count} new students.')
# # # # # # # # # # # # # # #             return redirect('room_list')

# # # # # # # # # # # # # # #         except Exception as e:
# # # # # # # # # # # # # # #             messages.error(request, f'An error occurred: {e}')
# # # # # # # # # # # # # # #             return redirect('upload_students')

# # # # # # # # # # # # # # #     return render(request, 'attendance/upload_students.html')

# # # # # # # # # # # # # # # def auto_arrange_seating(request, room_id):
# # # # # # # # # # # # # # #     room_to_arrange = get_object_or_404(Room, pk=room_id)
    
# # # # # # # # # # # # # # #     seated_students_ids = Bench.objects.values_list('students', flat=True)
# # # # # # # # # # # # # # #     students_to_seat = Student.objects.exclude(id__in=seated_students_ids).order_by('id')

# # # # # # # # # # # # # # #     if not students_to_seat:
# # # # # # # # # # # # # # #         messages.warning(request, 'No unseated students available to arrange.')
# # # # # # # # # # # # # # #         return redirect('room_list')

# # # # # # # # # # # # # # #     Bench.objects.filter(room=room_to_arrange).delete()

# # # # # # # # # # # # # # #     students_by_batch = defaultdict(list)
# # # # # # # # # # # # # # #     for student in students_to_seat:
# # # # # # # # # # # # # # #         students_by_batch[student.batch].append(student)

# # # # # # # # # # # # # # #     batch_names = sorted(students_by_batch.keys())
    
# # # # # # # # # # # # # # #     if len(batch_names) < 2:
# # # # # # # # # # # # # # #         messages.warning(request, 'Seating arrangement requires at least two batches of students.')
# # # # # # # # # # # # # # #         return redirect('room_list')
        
# # # # # # # # # # # # # # #     if room_to_arrange.id % 2 != 0:
# # # # # # # # # # # # # # #         batch_order = batch_names
# # # # # # # # # # # # # # #     else:
# # # # # # # # # # # # # # #         batch_order = list(reversed(batch_names))

# # # # # # # # # # # # # # #     seated_count = 0
# # # # # # # # # # # # # # #     total_virtual_columns = room_to_arrange.columns * room_to_arrange.students_per_bench

# # # # # # # # # # # # # # #     # Iterate through each "virtual column" of individual seats
# # # # # # # # # # # # # # #     for virtual_col_idx in range(total_virtual_columns):
# # # # # # # # # # # # # # #         # Determine which batch to use for this entire virtual column
# # # # # # # # # # # # # # #         batch_to_pick_name = batch_order[virtual_col_idx % len(batch_order)]
        
# # # # # # # # # # # # # # #         # Determine the physical bench column and the seat index within that bench
# # # # # # # # # # # # # # #         real_bench_col = (virtual_col_idx // room_to_arrange.students_per_bench) + 1
        
# # # # # # # # # # # # # # #         # Fill this virtual column from top to bottom (row 1 to N)
# # # # # # # # # # # # # # #         for r in range(1, room_to_arrange.benches_per_column + 1):
# # # # # # # # # # # # # # #             if students_by_batch[batch_to_pick_name]:
# # # # # # # # # # # # # # #                 student = students_by_batch[batch_to_pick_name].pop(0)
                
# # # # # # # # # # # # # # #                 # Get or create the physical bench
# # # # # # # # # # # # # # #                 bench, _ = Bench.objects.get_or_create(room=room_to_arrange, row_num=r, col_num=real_bench_col)
# # # # # # # # # # # # # # #                 bench.students.add(student)
# # # # # # # # # # # # # # #                 seated_count += 1
# # # # # # # # # # # # # # #             else:
# # # # # # # # # # # # # # #                 # This batch is empty, so we cannot fill this virtual column anymore.
# # # # # # # # # # # # # # #                 # Move to the next virtual column.
# # # # # # # # # # # # # # #                 break
            
# # # # # # # # # # # # # # #     messages.success(request, f'Successfully arranged {seated_count} students in {room_to_arrange.name}.')
# # # # # # # # # # # # # # #     return redirect('room_list')







# # # # # # # # # # # # # # # # def auto_arrange_seating(request, room_id):
# # # # # # # # # # # # # # # #     room_to_arrange = get_object_or_404(Room, pk=room_id)
    
# # # # # # # # # # # # # # # #     seated_students_ids = Bench.objects.values_list('students', flat=True)
# # # # # # # # # # # # # # # #     students_to_seat = Student.objects.exclude(id__in=seated_students_ids).order_by('id')

# # # # # # # # # # # # # # # #     if not students_to_seat:
# # # # # # # # # # # # # # # #         messages.warning(request, 'No unseated students available to arrange.')
# # # # # # # # # # # # # # # #         return redirect('room_list')

# # # # # # # # # # # # # # # #     Bench.objects.filter(room=room_to_arrange).delete()

# # # # # # # # # # # # # # # #     students_by_batch = defaultdict(list)
# # # # # # # # # # # # # # # #     for student in students_to_seat:
# # # # # # # # # # # # # # # #         students_by_batch[student.batch].append(student)

# # # # # # # # # # # # # # # #     batch_names = sorted(students_by_batch.keys())
    
# # # # # # # # # # # # # # # #     if len(batch_names) < 2:
# # # # # # # # # # # # # # # #         messages.warning(request, 'Seating arrangement requires at least two batches of students.')
# # # # # # # # # # # # # # # #         return redirect('room_list')
        
# # # # # # # # # # # # # # # #     if room_to_arrange.id % 2 != 0:
# # # # # # # # # # # # # # # #         batch_order = batch_names
# # # # # # # # # # # # # # # #     else:
# # # # # # # # # # # # # # # #         batch_order = list(reversed(batch_names))

# # # # # # # # # # # # # # # #     seated_count = 0
# # # # # # # # # # # # # # # #     is_finished = False

# # # # # # # # # # # # # # # #     for r in range(1, room_to_arrange.benches_per_column + 1):
# # # # # # # # # # # # # # # #         for seat_in_row in range(room_to_arrange.columns * room_to_arrange.students_per_bench):
# # # # # # # # # # # # # # # #             batch_to_pick_name = batch_order[seat_in_row % len(batch_order)]

# # # # # # # # # # # # # # # #             if students_by_batch[batch_to_pick_name]:
# # # # # # # # # # # # # # # #                 student = students_by_batch[batch_to_pick_name].pop(0)
                
# # # # # # # # # # # # # # # #                 col_num = (seat_in_row // room_to_arrange.students_per_bench) + 1
                
# # # # # # # # # # # # # # # #                 bench, _ = Bench.objects.get_or_create(room=room_to_arrange, row_num=r, col_num=col_num)
# # # # # # # # # # # # # # # #                 bench.students.add(student)
# # # # # # # # # # # # # # # #                 seated_count += 1
# # # # # # # # # # # # # # # #             else:
# # # # # # # # # # # # # # # #                 is_finished = True
# # # # # # # # # # # # # # # #                 break
        
# # # # # # # # # # # # # # # #         if is_finished:
# # # # # # # # # # # # # # # #             break
            
# # # # # # # # # # # # # # # #     messages.success(request, f'Successfully arranged {seated_count} students in {room_to_arrange.name}.')
# # # # # # # # # # # # # # # #     return redirect('room_list')



















# # # # # # # # # # # # # # # attendance/views.py

# # # # # # # # # # # # # # from django.shortcuts import render, get_object_or_404, redirect
# # # # # # # # # # # # # # from django.http import JsonResponse
# # # # # # # # # # # # # # from django.views.decorators.csrf import csrf_exempt
# # # # # # # # # # # # # # from django.contrib import messages
# # # # # # # # # # # # # # from collections import defaultdict
# # # # # # # # # # # # # # import json
# # # # # # # # # # # # # # import pandas as pd

# # # # # # # # # # # # # # from .models import Room, Student, Bench, Absentee

# # # # # # # # # # # # # # def room_list(request):
# # # # # # # # # # # # # #     rooms = Room.objects.all()
# # # # # # # # # # # # # #     return render(request, 'attendance/room_list.html', {'rooms': rooms})

# # # # # # # # # # # # # # def seating_plan_view(request, room_id):
# # # # # # # # # # # # # #     room = get_object_or_404(Room, pk=room_id)
# # # # # # # # # # # # # #     benches = Bench.objects.filter(room=room).order_by('col_num', 'row_num')
# # # # # # # # # # # # # #     plan = [[] for _ in range(room.columns)]
    
# # # # # # # # # # # # # #     for bench in benches:
# # # # # # # # # # # # # #         students_on_bench = list(bench.students.all())
# # # # # # # # # # # # # #         seats = []
# # # # # # # # # # # # # #         for i in range(room.students_per_bench):
# # # # # # # # # # # # # #             if i < len(students_on_bench):
# # # # # # # # # # # # # #                 seats.append(students_on_bench[i])
# # # # # # # # # # # # # #             else:
# # # # # # # # # # # # # #                 seats.append(None)
# # # # # # # # # # # # # #         bench.seats = seats
# # # # # # # # # # # # # #         plan[bench.col_num - 1].append(bench)
        
# # # # # # # # # # # # # #     return render(request, 'attendance/seating_plan.html', {'room': room, 'plan': plan})

# # # # # # # # # # # # # # @csrf_exempt
# # # # # # # # # # # # # # def save_absentees(request): # RENAMED
# # # # # # # # # # # # # #     if request.method == 'POST':
# # # # # # # # # # # # # #         data = json.loads(request.body)
# # # # # # # # # # # # # #         room_id = data.get('room_id')
# # # # # # # # # # # # # #         absent_ids = data.get('absent_ids', []) # Expect a list of IDs

# # # # # # # # # # # # # #         if not room_id:
# # # # # # # # # # # # # #             return JsonResponse({'status': 'error', 'message': 'Missing room_id'}, status=400)
        
# # # # # # # # # # # # # #         try:
# # # # # # # # # # # # # #             room = Room.objects.get(id=room_id)
# # # # # # # # # # # # # #             # Optional: Clear previous absentee records for this room for a clean slate
# # # # # # # # # # # # # #             # Absentee.objects.filter(room=room).delete()

# # # # # # # # # # # # # #             for student_id in absent_ids:
# # # # # # # # # # # # # #                 student = Student.objects.get(student_id=student_id)
# # # # # # # # # # # # # #                 Absentee.objects.get_or_create(room=room, student=student)
            
# # # # # # # # # # # # # #             return JsonResponse({'status': 'success', 'message': f'{len(absent_ids)} absentees recorded for {room.name}.'})
# # # # # # # # # # # # # #         except (Student.DoesNotExist, Room.DoesNotExist):
# # # # # # # # # # # # # #             return JsonResponse({'status': 'error', 'message': 'Invalid student or room ID found.'}, status=404)
            
# # # # # # # # # # # # # #     return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# # # # # # # # # # # # # # def upload_students(request):
# # # # # # # # # # # # # #     if request.method == 'POST':
# # # # # # # # # # # # # #         excel_file = request.FILES.get('excel_file')
# # # # # # # # # # # # # #         if not excel_file or not excel_file.name.endswith('.xlsx'):
# # # # # # # # # # # # # #             messages.error(request, 'Please upload a valid .xlsx file.')
# # # # # # # # # # # # # #             return redirect('upload_students')
        
# # # # # # # # # # # # # #         try:
# # # # # # # # # # # # # #             df = pd.read_excel(excel_file)
# # # # # # # # # # # # # #             required_cols = ['StudentID', 'Batch']
# # # # # # # # # # # # # #             if not all(col in df.columns for col in required_cols):
# # # # # # # # # # # # # #                 messages.error(request, "Excel file must have columns named 'StudentID' and 'Batch'.")
# # # # # # # # # # # # # #                 return redirect('upload_students')

# # # # # # # # # # # # # #             created_count = 0
# # # # # # # # # # # # # #             for index, row in df.iterrows():
# # # # # # # # # # # # # #                 sid = str(row['StudentID'])
# # # # # # # # # # # # # #                 batch_name = str(row['Batch'])
                
# # # # # # # # # # # # # #                 student, created = Student.objects.update_or_create(
# # # # # # # # # # # # # #                     student_id=sid,
# # # # # # # # # # # # # #                     defaults={'batch': batch_name}
# # # # # # # # # # # # # #                 )
# # # # # # # # # # # # # #                 if created:
# # # # # # # # # # # # # #                     created_count += 1
            
# # # # # # # # # # # # # #             messages.success(request, f'Successfully processed file. Added {created_count} new students.')
# # # # # # # # # # # # # #             return redirect('room_list')

# # # # # # # # # # # # # #         except Exception as e:
# # # # # # # # # # # # # #             messages.error(request, f'An error occurred: {e}')
# # # # # # # # # # # # # #             return redirect('upload_students')

# # # # # # # # # # # # # #     return render(request, 'attendance/upload_students.html')

# # # # # # # # # # # # # # def auto_arrange_seating(request, room_id):
# # # # # # # # # # # # # #     room_to_arrange = get_object_or_404(Room, pk=room_id)
    
# # # # # # # # # # # # # #     seated_students_ids = Bench.objects.values_list('students', flat=True)
# # # # # # # # # # # # # #     students_to_seat = Student.objects.exclude(id__in=seated_students_ids).order_by('id')

# # # # # # # # # # # # # #     if not students_to_seat:
# # # # # # # # # # # # # #         messages.warning(request, 'No unseated students available to arrange.')
# # # # # # # # # # # # # #         return redirect('room_list')

# # # # # # # # # # # # # #     Bench.objects.filter(room=room_to_arrange).delete()

# # # # # # # # # # # # # #     students_by_batch = defaultdict(list)
# # # # # # # # # # # # # #     for student in students_to_seat:
# # # # # # # # # # # # # #         students_by_batch[student.batch].append(student)

# # # # # # # # # # # # # #     batch_names = sorted(students_by_batch.keys())
    
# # # # # # # # # # # # # #     if len(batch_names) < 2:
# # # # # # # # # # # # # #         messages.warning(request, 'Seating arrangement requires at least two batches of students.')
# # # # # # # # # # # # # #         return redirect('room_list')
        
# # # # # # # # # # # # # #     if room_to_arrange.id % 2 != 0:
# # # # # # # # # # # # # #         batch_order = batch_names
# # # # # # # # # # # # # #     else:
# # # # # # # # # # # # # #         batch_order = list(reversed(batch_names))

# # # # # # # # # # # # # #     seated_count = 0
# # # # # # # # # # # # # #     total_virtual_columns = room_to_arrange.columns * room_to_arrange.students_per_bench

# # # # # # # # # # # # # #     for virtual_col_idx in range(total_virtual_columns):
# # # # # # # # # # # # # #         batch_to_pick_name = batch_order[virtual_col_idx % len(batch_order)]
        
# # # # # # # # # # # # # #         real_bench_col = (virtual_col_idx // room_to_arrange.students_per_bench) + 1
        
# # # # # # # # # # # # # #         for r in range(1, room_to_arrange.benches_per_column + 1):
# # # # # # # # # # # # # #             if students_by_batch[batch_to_pick_name]:
# # # # # # # # # # # # # #                 student = students_by_batch[batch_to_pick_name].pop(0)
                
# # # # # # # # # # # # # #                 bench, _ = Bench.objects.get_or_create(room=room_to_arrange, row_num=r, col_num=real_bench_col)
# # # # # # # # # # # # # #                 bench.students.add(student)
# # # # # # # # # # # # # #                 seated_count += 1
# # # # # # # # # # # # # #             else:
# # # # # # # # # # # # # #                 break
            
# # # # # # # # # # # # # #     messages.success(request, f'Successfully arranged {seated_count} students in {room_to_arrange.name}.')
# # # # # # # # # # # # # #     return redirect('room_list')



















# # # # # # # # # # # # # # attendance/views.py

# # # # # # # # # # # # # from django.shortcuts import render, get_object_or_404, redirect
# # # # # # # # # # # # # from django.http import HttpResponse, JsonResponse
# # # # # # # # # # # # # from django.views.decorators.csrf import csrf_exempt
# # # # # # # # # # # # # from django.contrib import messages
# # # # # # # # # # # # # from collections import defaultdict
# # # # # # # # # # # # # import json
# # # # # # # # # # # # # import pandas as pd
# # # # # # # # # # # # # import io

# # # # # # # # # # # # # from .models import Room, Student, Bench, Absentee

# # # # # # # # # # # # # def room_list(request):
# # # # # # # # # # # # #     rooms = Room.objects.all()
# # # # # # # # # # # # #     return render(request, 'attendance/room_list.html', {'rooms': rooms})

# # # # # # # # # # # # # def seating_plan_view(request, room_id):
# # # # # # # # # # # # #     room = get_object_or_404(Room, pk=room_id)
# # # # # # # # # # # # #     benches = Bench.objects.filter(room=room).order_by('col_num', 'row_num')
# # # # # # # # # # # # #     plan = [[] for _ in range(room.columns)]
    
# # # # # # # # # # # # #     for bench in benches:
# # # # # # # # # # # # #         students_on_bench = list(bench.students.all())
# # # # # # # # # # # # #         seats = []
# # # # # # # # # # # # #         for i in range(room.students_per_bench):
# # # # # # # # # # # # #             if i < len(students_on_bench):
# # # # # # # # # # # # #                 seats.append(students_on_bench[i])
# # # # # # # # # # # # #             else:
# # # # # # # # # # # # #                 seats.append(None)
# # # # # # # # # # # # #         bench.seats = seats
# # # # # # # # # # # # #         plan[bench.col_num - 1].append(bench)
        
# # # # # # # # # # # # #     return render(request, 'attendance/seating_plan.html', {'room': room, 'plan': plan})

# # # # # # # # # # # # # @csrf_exempt
# # # # # # # # # # # # # def save_absentees(request):
# # # # # # # # # # # # #     if request.method == 'POST':
# # # # # # # # # # # # #         data = json.loads(request.body)
# # # # # # # # # # # # #         room_id = data.get('room_id')
# # # # # # # # # # # # #         absent_ids = data.get('absent_ids', [])

# # # # # # # # # # # # #         if not room_id:
# # # # # # # # # # # # #             return JsonResponse({'status': 'error', 'message': 'Missing room_id'}, status=400)
        
# # # # # # # # # # # # #         try:
# # # # # # # # # # # # #             room = Room.objects.get(id=room_id)
# # # # # # # # # # # # #             # First, clear previous absentee records for this room to handle re-saves
# # # # # # # # # # # # #             Absentee.objects.filter(room=room).delete()

# # # # # # # # # # # # #             for student_id in absent_ids:
# # # # # # # # # # # # #                 student = Student.objects.get(student_id=student_id)
# # # # # # # # # # # # #                 Absentee.objects.get_or_create(room=room, student=student)
            
# # # # # # # # # # # # #             return JsonResponse({'status': 'success', 'message': f'{len(absent_ids)} absentees recorded for {room.name}.'})
# # # # # # # # # # # # #         except (Student.DoesNotExist, Room.DoesNotExist):
# # # # # # # # # # # # #             return JsonResponse({'status': 'error', 'message': 'Invalid student or room ID found.'}, status=404)
            
# # # # # # # # # # # # #     return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# # # # # # # # # # # # # def upload_students(request):
# # # # # # # # # # # # #     if request.method == 'POST':
# # # # # # # # # # # # #         excel_file = request.FILES.get('excel_file')
# # # # # # # # # # # # #         if not excel_file or not excel_file.name.endswith('.xlsx'):
# # # # # # # # # # # # #             messages.error(request, 'Please upload a valid .xlsx file.')
# # # # # # # # # # # # #             return redirect('upload_students')
        
# # # # # # # # # # # # #         try:
# # # # # # # # # # # # #             df = pd.read_excel(excel_file)
# # # # # # # # # # # # #             required_cols = ['StudentID', 'Batch']
# # # # # # # # # # # # #             if not all(col in df.columns for col in required_cols):
# # # # # # # # # # # # #                 messages.error(request, "Excel file must have columns named 'StudentID' and 'Batch'.")
# # # # # # # # # # # # #                 return redirect('upload_students')

# # # # # # # # # # # # #             created_count = 0
# # # # # # # # # # # # #             for index, row in df.iterrows():
# # # # # # # # # # # # #                 sid = str(row['StudentID'])
# # # # # # # # # # # # #                 batch_name = str(row['Batch'])
                
# # # # # # # # # # # # #                 student, created = Student.objects.update_or_create(
# # # # # # # # # # # # #                     student_id=sid,
# # # # # # # # # # # # #                     defaults={'batch': batch_name}
# # # # # # # # # # # # #                 )
# # # # # # # # # # # # #                 if created:
# # # # # # # # # # # # #                     created_count += 1
            
# # # # # # # # # # # # #             messages.success(request, f'Successfully processed file. Added {created_count} new students.')
# # # # # # # # # # # # #             return redirect('room_list')

# # # # # # # # # # # # #         except Exception as e:
# # # # # # # # # # # # #             messages.error(request, f'An error occurred: {e}')
# # # # # # # # # # # # #             return redirect('upload_students')

# # # # # # # # # # # # #     return render(request, 'attendance/upload_students.html')

# # # # # # # # # # # # # def auto_arrange_seating(request, room_id):
# # # # # # # # # # # # #     room_to_arrange = get_object_or_404(Room, pk=room_id)
    
# # # # # # # # # # # # #     seated_students_ids = Bench.objects.values_list('students', flat=True)
# # # # # # # # # # # # #     students_to_seat = Student.objects.exclude(id__in=seated_students_ids).order_by('id')

# # # # # # # # # # # # #     if not students_to_seat:
# # # # # # # # # # # # #         messages.warning(request, 'No unseated students available to arrange.')
# # # # # # # # # # # # #         return redirect('room_list')

# # # # # # # # # # # # #     Bench.objects.filter(room=room_to_arrange).delete()

# # # # # # # # # # # # #     students_by_batch = defaultdict(list)
# # # # # # # # # # # # #     for student in students_to_seat:
# # # # # # # # # # # # #         students_by_batch[student.batch].append(student)

# # # # # # # # # # # # #     batch_names = sorted(students_by_batch.keys())
    
# # # # # # # # # # # # #     if len(batch_names) < 2:
# # # # # # # # # # # # #         messages.warning(request, 'Seating arrangement requires at least two batches of students.')
# # # # # # # # # # # # #         return redirect('room_list')
        
# # # # # # # # # # # # #     if room_to_arrange.id % 2 != 0:
# # # # # # # # # # # # #         batch_order = batch_names
# # # # # # # # # # # # #     else:
# # # # # # # # # # # # #         batch_order = list(reversed(batch_names))

# # # # # # # # # # # # #     seated_count = 0
# # # # # # # # # # # # #     total_virtual_columns = room_to_arrange.columns * room_to_arrange.students_per_bench

# # # # # # # # # # # # #     for virtual_col_idx in range(total_virtual_columns):
# # # # # # # # # # # # #         batch_to_pick_name = batch_order[virtual_col_idx % len(batch_order)]
        
# # # # # # # # # # # # #         real_bench_col = (virtual_col_idx // room_to_arrange.students_per_bench) + 1
        
# # # # # # # # # # # # #         for r in range(1, room_to_arrange.benches_per_column + 1):
# # # # # # # # # # # # #             if students_by_batch[batch_to_pick_name]:
# # # # # # # # # # # # #                 student = students_by_batch[batch_to_pick_name].pop(0)
                
# # # # # # # # # # # # #                 bench, _ = Bench.objects.get_or_create(room=room_to_arrange, row_num=r, col_num=real_bench_col)
# # # # # # # # # # # # #                 bench.students.add(student)
# # # # # # # # # # # # #                 seated_count += 1
# # # # # # # # # # # # #             else:
# # # # # # # # # # # # #                 break
            
# # # # # # # # # # # # #     messages.success(request, f'Successfully arranged {seated_count} students in {room_to_arrange.name}.')
# # # # # # # # # # # # #     return redirect('room_list')

# # # # # # # # # # # # # def download_report(request):
# # # # # # # # # # # # #     absentees = Absentee.objects.select_related('room', 'student').order_by('room__name', 'student__batch')

# # # # # # # # # # # # #     # --- Prepare data for Sheet 1: Detailed Report ---
# # # # # # # # # # # # #     detailed_data = defaultdict(lambda: defaultdict(list))
# # # # # # # # # # # # #     for ab in absentees:
# # # # # # # # # # # # #         detailed_data[ab.room.name][ab.student.batch].append(ab.student.student_id)

# # # # # # # # # # # # #     detailed_rows = []
# # # # # # # # # # # # #     for room_name, batches in detailed_data.items():
# # # # # # # # # # # # #         for batch_name, student_ids in batches.items():
# # # # # # # # # # # # #             detailed_rows.append({
# # # # # # # # # # # # #                 'Room Number': room_name,
# # # # # # # # # # # # #                 'Batch': batch_name,
# # # # # # # # # # # # #                 'Absentees': ', '.join(student_ids)
# # # # # # # # # # # # #             })
    
# # # # # # # # # # # # #     df1 = pd.DataFrame(detailed_rows)

# # # # # # # # # # # # #     # --- Prepare data for Sheet 2: Consolidated Report ---
# # # # # # # # # # # # #     summary_data = defaultdict(int)
# # # # # # # # # # # # #     for ab in absentees:
# # # # # # # # # # # # #         summary_data[ab.student.batch] += 1
    
# # # # # # # # # # # # #     summary_rows = [{'Batch': batch, 'Absentees Count': count} for batch, count in summary_data.items()]
# # # # # # # # # # # # #     df2 = pd.DataFrame(summary_rows)

# # # # # # # # # # # # #     # --- Create Excel file in memory ---
# # # # # # # # # # # # #     output = io.BytesIO()
# # # # # # # # # # # # #     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
# # # # # # # # # # # # #         df1.to_excel(writer, sheet_name='Detailed Report', index=False)
# # # # # # # # # # # # #         df2.to_excel(writer, sheet_name='Consolidated Report', index=False)

# # # # # # # # # # # # #         # --- Format the 'Detailed Report' sheet ---
# # # # # # # # # # # # #         workbook = writer.book
# # # # # # # # # # # # #         worksheet = writer.sheets['Detailed Report']
        
# # # # # # # # # # # # #         # Add formatting for headers
# # # # # # # # # # # # #         header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
# # # # # # # # # # # # #         for col_num, value in enumerate(df1.columns.values):
# # # # # # # # # # # # #             worksheet.write(0, col_num, value, header_format)

# # # # # # # # # # # # #         # Logic to merge cells for Room Number
# # # # # # # # # # # # #         if not df1.empty:
# # # # # # # # # # # # #             merge_start_row = 1
# # # # # # # # # # # # #             for i in range(1, len(df1)):
# # # # # # # # # # # # #                 if df1.iloc[i]['Room Number'] != df1.iloc[i-1]['Room Number']:
# # # # # # # # # # # # #                     if merge_start_row < i:
# # # # # # # # # # # # #                         worksheet.merge_range(merge_start_row, 0, i, 0, df1.iloc[i-1]['Room Number'])
# # # # # # # # # # # # #                     merge_start_row = i + 1
# # # # # # # # # # # # #             # Merge the last group
# # # # # # # # # # # # #             worksheet.merge_range(merge_start_row, 0, len(df1), 0, df1.iloc[-1]['Room Number'])

# # # # # # # # # # # # #     output.seek(0)
    
# # # # # # # # # # # # #     response = HttpResponse(
# # # # # # # # # # # # #         output,
# # # # # # # # # # # # #         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
# # # # # # # # # # # # #     )
# # # # # # # # # # # # #     response['Content-Disposition'] = 'attachment; filename="absentee_report.xlsx"'
    
# # # # # # # # # # # # #     return response















# # # # # # # # # # # # # attendance/views.py

# # # # # # # # # # # # from django.shortcuts import render, get_object_or_404, redirect
# # # # # # # # # # # # from django.http import HttpResponse, JsonResponse
# # # # # # # # # # # # from django.views.decorators.csrf import csrf_exempt
# # # # # # # # # # # # from django.contrib import messages
# # # # # # # # # # # # from collections import defaultdict
# # # # # # # # # # # # import json
# # # # # # # # # # # # import pandas as pd
# # # # # # # # # # # # import io

# # # # # # # # # # # # from .models import Room, Student, Bench, Absentee

# # # # # # # # # # # # def room_list(request):
# # # # # # # # # # # #     rooms = Room.objects.all()
# # # # # # # # # # # #     return render(request, 'attendance/room_list.html', {'rooms': rooms})

# # # # # # # # # # # # def seating_plan_view(request, room_id):
# # # # # # # # # # # #     room = get_object_or_404(Room, pk=room_id)
# # # # # # # # # # # #     benches = Bench.objects.filter(room=room).order_by('col_num', 'row_num')
# # # # # # # # # # # #     plan = [[] for _ in range(room.columns)]
    
# # # # # # # # # # # #     for bench in benches:
# # # # # # # # # # # #         students_on_bench = list(bench.students.all())
# # # # # # # # # # # #         seats = []
# # # # # # # # # # # #         for i in range(room.students_per_bench):
# # # # # # # # # # # #             if i < len(students_on_bench):
# # # # # # # # # # # #                 seats.append(students_on_bench[i])
# # # # # # # # # # # #             else:
# # # # # # # # # # # #                 seats.append(None)
# # # # # # # # # # # #         bench.seats = seats
# # # # # # # # # # # #         plan[bench.col_num - 1].append(bench)
        
# # # # # # # # # # # #     return render(request, 'attendance/seating_plan.html', {'room': room, 'plan': plan})

# # # # # # # # # # # # @csrf_exempt
# # # # # # # # # # # # def save_absentees(request):
# # # # # # # # # # # #     if request.method == 'POST':
# # # # # # # # # # # #         data = json.loads(request.body)
# # # # # # # # # # # #         room_id = data.get('room_id')
# # # # # # # # # # # #         absent_ids = data.get('absent_ids', [])

# # # # # # # # # # # #         if not room_id:
# # # # # # # # # # # #             return JsonResponse({'status': 'error', 'message': 'Missing room_id'}, status=400)
        
# # # # # # # # # # # #         try:
# # # # # # # # # # # #             room = Room.objects.get(id=room_id)
# # # # # # # # # # # #             Absentee.objects.filter(room=room).delete()

# # # # # # # # # # # #             for student_id in absent_ids:
# # # # # # # # # # # #                 student = Student.objects.get(student_id=student_id)
# # # # # # # # # # # #                 Absentee.objects.get_or_create(room=room, student=student)
            
# # # # # # # # # # # #             return JsonResponse({'status': 'success', 'message': f'{len(absent_ids)} absentees recorded for {room.name}.'})
# # # # # # # # # # # #         except (Student.DoesNotExist, Room.DoesNotExist):
# # # # # # # # # # # #             return JsonResponse({'status': 'error', 'message': 'Invalid student or room ID found.'}, status=404)
            
# # # # # # # # # # # #     return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# # # # # # # # # # # # def upload_students(request):
# # # # # # # # # # # #     if request.method == 'POST':
# # # # # # # # # # # #         excel_file = request.FILES.get('excel_file')
# # # # # # # # # # # #         if not excel_file or not excel_file.name.endswith('.xlsx'):
# # # # # # # # # # # #             messages.error(request, 'Please upload a valid .xlsx file.')
# # # # # # # # # # # #             return redirect('upload_students')
        
# # # # # # # # # # # #         try:
# # # # # # # # # # # #             df = pd.read_excel(excel_file)
# # # # # # # # # # # #             required_cols = ['StudentID', 'Batch']
# # # # # # # # # # # #             if not all(col in df.columns for col in required_cols):
# # # # # # # # # # # #                 messages.error(request, "Excel file must have columns named 'StudentID' and 'Batch'.")
# # # # # # # # # # # #                 return redirect('upload_students')

# # # # # # # # # # # #             created_count = 0
# # # # # # # # # # # #             for index, row in df.iterrows():
# # # # # # # # # # # #                 sid = str(row['StudentID'])
# # # # # # # # # # # #                 batch_name = str(row['Batch'])
                
# # # # # # # # # # # #                 student, created = Student.objects.update_or_create(
# # # # # # # # # # # #                     student_id=sid,
# # # # # # # # # # # #                     defaults={'batch': batch_name}
# # # # # # # # # # # #                 )
# # # # # # # # # # # #                 if created:
# # # # # # # # # # # #                     created_count += 1
            
# # # # # # # # # # # #             messages.success(request, f'Successfully processed file. Added {created_count} new students.')
# # # # # # # # # # # #             return redirect('room_list')

# # # # # # # # # # # #         except Exception as e:
# # # # # # # # # # # #             messages.error(request, f'An error occurred: {e}')
# # # # # # # # # # # #             return redirect('upload_students')

# # # # # # # # # # # #     return render(request, 'attendance/upload_students.html')

# # # # # # # # # # # # def auto_arrange_seating(request, room_id):
# # # # # # # # # # # #     room_to_arrange = get_object_or_404(Room, pk=room_id)
    
# # # # # # # # # # # #     seated_students_ids = Bench.objects.values_list('students', flat=True)
# # # # # # # # # # # #     students_to_seat = Student.objects.exclude(id__in=seated_students_ids).order_by('id')

# # # # # # # # # # # #     if not students_to_seat:
# # # # # # # # # # # #         messages.warning(request, 'No unseated students available to arrange.')
# # # # # # # # # # # #         return redirect('room_list')

# # # # # # # # # # # #     Bench.objects.filter(room=room_to_arrange).delete()

# # # # # # # # # # # #     students_by_batch = defaultdict(list)
# # # # # # # # # # # #     for student in students_to_seat:
# # # # # # # # # # # #         students_by_batch[student.batch].append(student)

# # # # # # # # # # # #     batch_names = sorted(students_by_batch.keys())
    
# # # # # # # # # # # #     if len(batch_names) < 2:
# # # # # # # # # # # #         messages.warning(request, 'Seating arrangement requires at least two batches of students.')
# # # # # # # # # # # #         return redirect('room_list')
        
# # # # # # # # # # # #     if room_to_arrange.id % 2 != 0:
# # # # # # # # # # # #         batch_order = batch_names
# # # # # # # # # # # #     else:
# # # # # # # # # # # #         batch_order = list(reversed(batch_names))

# # # # # # # # # # # #     seated_count = 0
# # # # # # # # # # # #     total_virtual_columns = room_to_arrange.columns * room_to_arrange.students_per_bench

# # # # # # # # # # # #     for virtual_col_idx in range(total_virtual_columns):
# # # # # # # # # # # #         batch_to_pick_name = batch_order[virtual_col_idx % len(batch_order)]
        
# # # # # # # # # # # #         real_bench_col = (virtual_col_idx // room_to_arrange.students_per_bench) + 1
        
# # # # # # # # # # # #         for r in range(1, room_to_arrange.benches_per_column + 1):
# # # # # # # # # # # #             if students_by_batch[batch_to_pick_name]:
# # # # # # # # # # # #                 student = students_by_batch[batch_to_pick_name].pop(0)
                
# # # # # # # # # # # #                 bench, _ = Bench.objects.get_or_create(room=room_to_arrange, row_num=r, col_num=real_bench_col)
# # # # # # # # # # # #                 bench.students.add(student)
# # # # # # # # # # # #                 seated_count += 1
# # # # # # # # # # # #             else:
# # # # # # # # # # # #                 break
            
# # # # # # # # # # # #     messages.success(request, f'Successfully arranged {seated_count} students in {room_to_arrange.name}.')
# # # # # # # # # # # #     return redirect('room_list')

# # # # # # # # # # # # def download_report(request):
# # # # # # # # # # # #     absentees = Absentee.objects.select_related('room', 'student').order_by('room__name', 'student__batch')

# # # # # # # # # # # #     detailed_data = defaultdict(lambda: defaultdict(list))
# # # # # # # # # # # #     for ab in absentees:
# # # # # # # # # # # #         detailed_data[ab.room.name][ab.student.batch].append(ab.student.student_id)

# # # # # # # # # # # #     detailed_rows = []
# # # # # # # # # # # #     for room_name, batches in detailed_data.items():
# # # # # # # # # # # #         for batch_name, student_ids in batches.items():
# # # # # # # # # # # #             detailed_rows.append({
# # # # # # # # # # # #                 'Room Number': room_name,
# # # # # # # # # # # #                 'Batch': batch_name,
# # # # # # # # # # # #                 'Absentees': ', '.join(student_ids)
# # # # # # # # # # # #             })
    
# # # # # # # # # # # #     df1 = pd.DataFrame(detailed_rows)

# # # # # # # # # # # #     summary_data = defaultdict(int)
# # # # # # # # # # # #     for ab in absentees:
# # # # # # # # # # # #         summary_data[ab.student.batch] += 1
    
# # # # # # # # # # # #     summary_rows = [{'Batch': batch, 'Absentees Count': count} for batch, count in summary_data.items()]
# # # # # # # # # # # #     df2 = pd.DataFrame(summary_rows)

# # # # # # # # # # # #     output = io.BytesIO()
# # # # # # # # # # # #     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
# # # # # # # # # # # #         df1.to_excel(writer, sheet_name='Detailed Report', index=False)
# # # # # # # # # # # #         df2.to_excel(writer, sheet_name='Consolidated Report', index=False)

# # # # # # # # # # # #         workbook = writer.book
# # # # # # # # # # # #         worksheet = writer.sheets['Detailed Report']
        
# # # # # # # # # # # #         header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
# # # # # # # # # # # #         for col_num, value in enumerate(df1.columns.values):
# # # # # # # # # # # #             worksheet.write(0, col_num, value, header_format)

# # # # # # # # # # # #         if not df1.empty:
# # # # # # # # # # # #             merge_start_row = 1
# # # # # # # # # # # #             for i in range(1, len(df1)):
# # # # # # # # # # # #                 if df1.iloc[i]['Room Number'] != df1.iloc[i-1]['Room Number']:
# # # # # # # # # # # #                     if merge_start_row < i:
# # # # # # # # # # # #                         worksheet.merge_range(merge_start_row, 0, i, 0, df1.iloc[i-1]['Room Number'])
# # # # # # # # # # # #                     merge_start_row = i + 1
# # # # # # # # # # # #             worksheet.merge_range(merge_start_row, 0, len(df1), 0, df1.iloc[-1]['Room Number'])

# # # # # # # # # # # #     output.seek(0)
    
# # # # # # # # # # # #     response = HttpResponse(
# # # # # # # # # # # #         output,
# # # # # # # # # # # #         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
# # # # # # # # # # # #     )
# # # # # # # # # # # #     response['Content-Disposition'] = 'attachment; filename="absentee_report.xlsx"'
    
# # # # # # # # # # # #     return response

# # # # # # # # # # # # def download_seating_plan(request, room_id):
# # # # # # # # # # # #     room = get_object_or_404(Room, pk=room_id)
# # # # # # # # # # # #     benches = Bench.objects.filter(room=room).prefetch_related('students').order_by('row_num', 'col_num')

# # # # # # # # # # # #     # Create an empty grid based on room dimensions
# # # # # # # # # # # #     num_rows = room.benches_per_column
# # # # # # # # # # # #     num_cols = room.columns * room.students_per_bench
# # # # # # # # # # # #     plan_data = [['' for _ in range(num_cols)] for _ in range(num_rows)]

# # # # # # # # # # # #     # Populate the grid with student IDs
# # # # # # # # # # # #     for bench in benches:
# # # # # # # # # # # #         students_on_bench = list(bench.students.all())
# # # # # # # # # # # #         start_col = (bench.col_num - 1) * room.students_per_bench
# # # # # # # # # # # #         for i, student in enumerate(students_on_bench):
# # # # # # # # # # # #             plan_data[bench.row_num - 1][start_col + i] = student.student_id

# # # # # # # # # # # #     df = pd.DataFrame(plan_data)

# # # # # # # # # # # #     # Create Excel file in memory
# # # # # # # # # # # #     output = io.BytesIO()
# # # # # # # # # # # #     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
# # # # # # # # # # # #         df.to_excel(writer, sheet_name=room.name, index=False, header=False)
        
# # # # # # # # # # # #         # Optional: Auto-fit column widths
# # # # # # # # # # # #         worksheet = writer.sheets[room.name]
# # # # # # # # # # # #         for idx, col in enumerate(df):
# # # # # # # # # # # #             series = df[col]
# # # # # # # # # # # #             max_len = max((series.astype(str).map(len).max(), len(str(series.name)))) + 1
# # # # # # # # # # # #             worksheet.set_column(idx, idx, max_len)

# # # # # # # # # # # #     output.seek(0)
    
# # # # # # # # # # # #     response = HttpResponse(
# # # # # # # # # # # #         output,
# # # # # # # # # # # #         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
# # # # # # # # # # # #     )
# # # # # # # # # # # #     response['Content-Disposition'] = f'attachment; filename="seating_plan_{room.name}.xlsx"'
    
# # # # # # # # # # # #     return response













# # # # # # # # # # # # attendance/views.py

# # # # # # # # # # # from django.shortcuts import render, get_object_or_404, redirect
# # # # # # # # # # # from django.http import HttpResponse, JsonResponse
# # # # # # # # # # # from django.views.decorators.csrf import csrf_exempt
# # # # # # # # # # # from django.contrib import messages
# # # # # # # # # # # from collections import defaultdict
# # # # # # # # # # # import json
# # # # # # # # # # # import pandas as pd
# # # # # # # # # # # import io

# # # # # # # # # # # from .models import Room, Student, Bench, Absentee

# # # # # # # # # # # def room_list(request):
# # # # # # # # # # #     rooms = Room.objects.all()
# # # # # # # # # # #     return render(request, 'attendance/room_list.html', {'rooms': rooms})

# # # # # # # # # # # def seating_plan_view(request, room_id):
# # # # # # # # # # #     room = get_object_or_404(Room, pk=room_id)
# # # # # # # # # # #     benches = Bench.objects.filter(room=room).order_by('col_num', 'row_num')
# # # # # # # # # # #     plan = [[] for _ in range(room.columns)]
    
# # # # # # # # # # #     for bench in benches:
# # # # # # # # # # #         students_on_bench = list(bench.students.all())
# # # # # # # # # # #         seats = []
# # # # # # # # # # #         for i in range(room.students_per_bench):
# # # # # # # # # # #             if i < len(students_on_bench):
# # # # # # # # # # #                 seats.append(students_on_bench[i])
# # # # # # # # # # #             else:
# # # # # # # # # # #                 seats.append(None)
# # # # # # # # # # #         bench.seats = seats
# # # # # # # # # # #         plan[bench.col_num - 1].append(bench)
        
# # # # # # # # # # #     return render(request, 'attendance/seating_plan.html', {'room': room, 'plan': plan})

# # # # # # # # # # # @csrf_exempt
# # # # # # # # # # # def save_absentees(request):
# # # # # # # # # # #     if request.method == 'POST':
# # # # # # # # # # #         data = json.loads(request.body)
# # # # # # # # # # #         room_id = data.get('room_id')
# # # # # # # # # # #         absent_ids = data.get('absent_ids', [])

# # # # # # # # # # #         if not room_id:
# # # # # # # # # # #             return JsonResponse({'status': 'error', 'message': 'Missing room_id'}, status=400)
        
# # # # # # # # # # #         try:
# # # # # # # # # # #             room = Room.objects.get(id=room_id)
# # # # # # # # # # #             Absentee.objects.filter(room=room).delete()

# # # # # # # # # # #             for student_id in absent_ids:
# # # # # # # # # # #                 student = Student.objects.get(student_id=student_id)
# # # # # # # # # # #                 Absentee.objects.get_or_create(room=room, student=student)
            
# # # # # # # # # # #             return JsonResponse({'status': 'success', 'message': f'{len(absent_ids)} absentees recorded for {room.name}.'})
# # # # # # # # # # #         except (Student.DoesNotExist, Room.DoesNotExist):
# # # # # # # # # # #             return JsonResponse({'status': 'error', 'message': 'Invalid student or room ID found.'}, status=404)
            
# # # # # # # # # # #     return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# # # # # # # # # # # def upload_students(request):
# # # # # # # # # # #     if request.method == 'POST':
# # # # # # # # # # #         excel_file = request.FILES.get('excel_file')
# # # # # # # # # # #         if not excel_file or not excel_file.name.endswith('.xlsx'):
# # # # # # # # # # #             messages.error(request, 'Please upload a valid .xlsx file.')
# # # # # # # # # # #             return redirect('upload_students')
        
# # # # # # # # # # #         try:
# # # # # # # # # # #             df = pd.read_excel(excel_file)
# # # # # # # # # # #             required_cols = ['StudentID', 'Batch']
# # # # # # # # # # #             if not all(col in df.columns for col in required_cols):
# # # # # # # # # # #                 messages.error(request, "Excel file must have columns named 'StudentID' and 'Batch'.")
# # # # # # # # # # #                 return redirect('upload_students')

# # # # # # # # # # #             created_count = 0
# # # # # # # # # # #             for index, row in df.iterrows():
# # # # # # # # # # #                 sid = str(row['StudentID'])
# # # # # # # # # # #                 batch_name = str(row['Batch'])
                
# # # # # # # # # # #                 student, created = Student.objects.update_or_create(
# # # # # # # # # # #                     student_id=sid,
# # # # # # # # # # #                     defaults={'batch': batch_name}
# # # # # # # # # # #                 )
# # # # # # # # # # #                 if created:
# # # # # # # # # # #                     created_count += 1
            
# # # # # # # # # # #             messages.success(request, f'Successfully processed file. Added {created_count} new students.')
# # # # # # # # # # #             return redirect('room_list')

# # # # # # # # # # #         except Exception as e:
# # # # # # # # # # #             messages.error(request, f'An error occurred: {e}')
# # # # # # # # # # #             return redirect('upload_students')

# # # # # # # # # # #     return render(request, 'attendance/upload_students.html')

# # # # # # # # # # # def auto_arrange_seating(request, room_id):
# # # # # # # # # # #     room_to_arrange = get_object_or_404(Room, pk=room_id)
    
# # # # # # # # # # #     seated_students_ids = Bench.objects.values_list('students', flat=True)
# # # # # # # # # # #     students_to_seat = Student.objects.exclude(id__in=seated_students_ids).order_by('id')

# # # # # # # # # # #     if not students_to_seat:
# # # # # # # # # # #         messages.warning(request, 'No unseated students available to arrange.')
# # # # # # # # # # #         return redirect('room_list')

# # # # # # # # # # #     Bench.objects.filter(room=room_to_arrange).delete()

# # # # # # # # # # #     students_by_batch = defaultdict(list)
# # # # # # # # # # #     for student in students_to_seat:
# # # # # # # # # # #         students_by_batch[student.batch].append(student)

# # # # # # # # # # #     batch_names = sorted(students_by_batch.keys())
    
# # # # # # # # # # #     if len(batch_names) < 2:
# # # # # # # # # # #         messages.warning(request, 'Seating arrangement requires at least two batches of students.')
# # # # # # # # # # #         return redirect('room_list')
        
# # # # # # # # # # #     if room_to_arrange.id % 2 != 0:
# # # # # # # # # # #         batch_order = batch_names
# # # # # # # # # # #     else:
# # # # # # # # # # #         batch_order = list(reversed(batch_names))

# # # # # # # # # # #     seated_count = 0
# # # # # # # # # # #     total_virtual_columns = room_to_arrange.columns * room_to_arrange.students_per_bench

# # # # # # # # # # #     for virtual_col_idx in range(total_virtual_columns):
# # # # # # # # # # #         batch_to_pick_name = batch_order[virtual_col_idx % len(batch_order)]
        
# # # # # # # # # # #         real_bench_col = (virtual_col_idx // room_to_arrange.students_per_bench) + 1
        
# # # # # # # # # # #         for r in range(1, room_to_arrange.benches_per_column + 1):
# # # # # # # # # # #             if students_by_batch[batch_to_pick_name]:
# # # # # # # # # # #                 student = students_by_batch[batch_to_pick_name].pop(0)
                
# # # # # # # # # # #                 bench, _ = Bench.objects.get_or_create(room=room_to_arrange, row_num=r, col_num=real_bench_col)
# # # # # # # # # # #                 bench.students.add(student)
# # # # # # # # # # #                 seated_count += 1
# # # # # # # # # # #             else:
# # # # # # # # # # #                 break
            
# # # # # # # # # # #     messages.success(request, f'Successfully arranged {seated_count} students in {room_to_arrange.name}.')
# # # # # # # # # # #     return redirect('room_list')

# # # # # # # # # # # def download_report(request):
# # # # # # # # # # #     absentees = Absentee.objects.select_related('room', 'student').order_by('room__name', 'student__batch')

# # # # # # # # # # #     detailed_data = defaultdict(lambda: defaultdict(list))
# # # # # # # # # # #     for ab in absentees:
# # # # # # # # # # #         detailed_data[ab.room.name][ab.student.batch].append(ab.student.student_id)

# # # # # # # # # # #     detailed_rows = []
# # # # # # # # # # #     for room_name, batches in detailed_data.items():
# # # # # # # # # # #         for batch_name, student_ids in batches.items():
# # # # # # # # # # #             detailed_rows.append({
# # # # # # # # # # #                 'Room Number': room_name,
# # # # # # # # # # #                 'Batch': batch_name,
# # # # # # # # # # #                 'Absentees': ', '.join(student_ids)
# # # # # # # # # # #             })
    
# # # # # # # # # # #     df1 = pd.DataFrame(detailed_rows)

# # # # # # # # # # #     summary_data = defaultdict(int)
# # # # # # # # # # #     for ab in absentees:
# # # # # # # # # # #         summary_data[ab.student.batch] += 1
    
# # # # # # # # # # #     summary_rows = [{'Batch': batch, 'Absentees Count': count} for batch, count in summary_data.items()]
# # # # # # # # # # #     df2 = pd.DataFrame(summary_rows)

# # # # # # # # # # #     output = io.BytesIO()
# # # # # # # # # # #     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
# # # # # # # # # # #         df1.to_excel(writer, sheet_name='Detailed Report', index=False)
# # # # # # # # # # #         df2.to_excel(writer, sheet_name='Consolidated Report', index=False)

# # # # # # # # # # #         workbook = writer.book
# # # # # # # # # # #         worksheet = writer.sheets['Detailed Report']
        
# # # # # # # # # # #         header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
# # # # # # # # # # #         for col_num, value in enumerate(df1.columns.values):
# # # # # # # # # # #             worksheet.write(0, col_num, value, header_format)

# # # # # # # # # # #         if not df1.empty:
# # # # # # # # # # #             merge_start_row = 1
# # # # # # # # # # #             for i in range(1, len(df1)):
# # # # # # # # # # #                 if df1.iloc[i]['Room Number'] != df1.iloc[i-1]['Room Number']:
# # # # # # # # # # #                     if merge_start_row < i:
# # # # # # # # # # #                         worksheet.merge_range(merge_start_row, 0, i, 0, df1.iloc[i-1]['Room Number'])
# # # # # # # # # # #                     merge_start_row = i + 1
# # # # # # # # # # #             worksheet.merge_range(merge_start_row, 0, len(df1), 0, df1.iloc[-1]['Room Number'])

# # # # # # # # # # #     output.seek(0)
    
# # # # # # # # # # #     response = HttpResponse(
# # # # # # # # # # #         output,
# # # # # # # # # # #         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
# # # # # # # # # # #     )
# # # # # # # # # # #     response['Content-Disposition'] = 'attachment; filename="absentee_report.xlsx"'
    
# # # # # # # # # # #     return response



# # # # # # # # # # # def download_seating_plan(request, room_id):
# # # # # # # # # # #     room = get_object_or_404(Room, pk=room_id)
# # # # # # # # # # #     benches = Bench.objects.filter(room=room).prefetch_related('students').order_by('row_num', 'col_num')

# # # # # # # # # # #     # --- Determine Headers ---
# # # # # # # # # # #     batch_names = sorted(list(Student.objects.values_list('batch', flat=True).distinct()))
    
# # # # # # # # # # #     if len(batch_names) < 2:
# # # # # # # # # # #         batch_order = batch_names
# # # # # # # # # # #     elif room.id % 2 != 0:
# # # # # # # # # # #         batch_order = batch_names
# # # # # # # # # # #     else:
# # # # # # # # # # #         batch_order = list(reversed(batch_names))

# # # # # # # # # # #     headers = []
# # # # # # # # # # #     total_virtual_columns = room.columns * room.students_per_bench
# # # # # # # # # # #     for virtual_col_idx in range(total_virtual_columns):
# # # # # # # # # # #         if batch_order:
# # # # # # # # # # #             batch_name = batch_order[virtual_col_idx % len(batch_order)]
# # # # # # # # # # #             headers.append(batch_name)
# # # # # # # # # # #         else:
# # # # # # # # # # #             headers.append(f'Seat {virtual_col_idx + 1}')

# # # # # # # # # # #     # --- Prepare Data Grid ---
# # # # # # # # # # #     num_rows = room.benches_per_column
# # # # # # # # # # #     plan_data = [['' for _ in range(total_virtual_columns)] for _ in range(num_rows)]

# # # # # # # # # # #     for bench in benches:
# # # # # # # # # # #         students_on_bench = list(bench.students.all())
# # # # # # # # # # #         start_col = (bench.col_num - 1) * room.students_per_bench
# # # # # # # # # # #         for i, student in enumerate(students_on_bench):
# # # # # # # # # # #             if start_col + i < len(plan_data[bench.row_num - 1]):
# # # # # # # # # # #                 plan_data[bench.row_num - 1][start_col + i] = student.student_id

# # # # # # # # # # #     df = pd.DataFrame(plan_data, columns=headers)

# # # # # # # # # # #     # --- Create Excel File ---
# # # # # # # # # # #     output = io.BytesIO()
# # # # # # # # # # #     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
# # # # # # # # # # #         df.to_excel(writer, sheet_name=room.name, index=False, header=True)
        
# # # # # # # # # # #         workbook = writer.book
# # # # # # # # # # #         worksheet = writer.sheets[room.name]
# # # # # # # # # # #         header_format = workbook.add_format({'bold': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
        
# # # # # # # # # # #         for col_num, value in enumerate(df.columns.values):
# # # # # # # # # # #             worksheet.write(0, col_num, value, header_format)

# # # # # # # # # # #         # --- CORRECTED COLUMN WIDTH LOGIC ---
# # # # # # # # # # #         for idx, col_name in enumerate(df.columns):
# # # # # # # # # # #             # Calculate max length of data in the column, handling empty columns safely
# # # # # # # # # # #             data_max_len = df[col_name].astype(str).map(len).max()
# # # # # # # # # # #             if pd.isna(data_max_len):
# # # # # # # # # # #                 data_max_len = 0

# # # # # # # # # # #             # Calculate length of the header
# # # # # # # # # # #             header_len = len(str(col_name))
            
# # # # # # # # # # #             # The final column width is the max of the two, plus a little padding
# # # # # # # # # # #             final_width = max(int(data_max_len), header_len) + 2
            
# # # # # # # # # # #             worksheet.set_column(idx, idx, final_width)

# # # # # # # # # # #     output.seek(0)
    
# # # # # # # # # # #     response = HttpResponse(
# # # # # # # # # # #         output,
# # # # # # # # # # #         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
# # # # # # # # # # #     )
# # # # # # # # # # #     response['Content-Disposition'] = f'attachment; filename="seating_plan_{room.name}.xlsx"'
    
# # # # # # # # # # #     return response






# # # # # # # # # # # # def download_seating_plan(request, room_id):
# # # # # # # # # # # #     room = get_object_or_404(Room, pk=room_id)
# # # # # # # # # # # #     benches = Bench.objects.filter(room=room).prefetch_related('students').order_by('row_num', 'col_num')

# # # # # # # # # # # #     # --- Determine Headers ---
# # # # # # # # # # # #     # This logic must match the arrangement logic to be correct
# # # # # # # # # # # #     batch_names = sorted(list(Student.objects.values_list('batch', flat=True).distinct()))
    
# # # # # # # # # # # #     if len(batch_names) < 2:
# # # # # # # # # # # #         batch_order = batch_names
# # # # # # # # # # # #     elif room.id % 2 != 0:
# # # # # # # # # # # #         batch_order = batch_names
# # # # # # # # # # # #     else:
# # # # # # # # # # # #         batch_order = list(reversed(batch_names))

# # # # # # # # # # # #     headers = []
# # # # # # # # # # # #     total_virtual_columns = room.columns * room.students_per_bench
# # # # # # # # # # # #     for virtual_col_idx in range(total_virtual_columns):
# # # # # # # # # # # #         if batch_order:
# # # # # # # # # # # #             batch_name = batch_order[virtual_col_idx % len(batch_order)]
# # # # # # # # # # # #             headers.append(batch_name)
# # # # # # # # # # # #         else:
# # # # # # # # # # # #             headers.append(f'Seat {virtual_col_idx + 1}') # Fallback header

# # # # # # # # # # # #     # --- Prepare Data Grid ---
# # # # # # # # # # # #     num_rows = room.benches_per_column
# # # # # # # # # # # #     plan_data = [['' for _ in range(total_virtual_columns)] for _ in range(num_rows)]

# # # # # # # # # # # #     for bench in benches:
# # # # # # # # # # # #         students_on_bench = list(bench.students.all())
# # # # # # # # # # # #         start_col = (bench.col_num - 1) * room.students_per_bench
# # # # # # # # # # # #         for i, student in enumerate(students_on_bench):
# # # # # # # # # # # #             if start_col + i < len(plan_data[bench.row_num - 1]):
# # # # # # # # # # # #                 plan_data[bench.row_num - 1][start_col + i] = student.student_id

# # # # # # # # # # # #     df = pd.DataFrame(plan_data, columns=headers)

# # # # # # # # # # # #     # --- Create Excel File ---
# # # # # # # # # # # #     output = io.BytesIO()
# # # # # # # # # # # #     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
# # # # # # # # # # # #         df.to_excel(writer, sheet_name=room.name, index=False, header=True)
        
# # # # # # # # # # # #         workbook = writer.book
# # # # # # # # # # # #         worksheet = writer.sheets[room.name]
# # # # # # # # # # # #         header_format = workbook.add_format({'bold': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
        
# # # # # # # # # # # #         for col_num, value in enumerate(df.columns.values):
# # # # # # # # # # # #             worksheet.write(0, col_num, value, header_format)

# # # # # # # # # # # #         for idx, col in enumerate(df):
# # # # # # # # # # # #             series = df[col]
# # # # # # # # # # # #             data_max_len = series.astype(str).map(len).max()
# # # # # # # # # # # #             if pd.isna(data_max_len):
# # # # # # # # # # # #                 data_max_len = 0
            
# # # # # # # # # # # #             max_len = max(data_max_len, len(str(df.columns[idx]))) + 2
# # # # # # # # # # # #             worksheet.set_column(idx, idx, max_len)

# # # # # # # # # # # #     output.seek(0)
    
# # # # # # # # # # # #     response = HttpResponse(
# # # # # # # # # # # #         output,
# # # # # # # # # # # #         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
# # # # # # # # # # # #     )
# # # # # # # # # # # #     response['Content-Disposition'] = f'attachment; filename="seating_plan_{room.name}.xlsx"'
    
# # # # # # # # # # # #     return response















# # # # # # # # # # # attendance/views.py

# # # # # # # # # # from django.shortcuts import render, get_object_or_404, redirect
# # # # # # # # # # from django.http import HttpResponse, JsonResponse
# # # # # # # # # # from django.views.decorators.csrf import csrf_exempt
# # # # # # # # # # from django.contrib import messages
# # # # # # # # # # from collections import defaultdict
# # # # # # # # # # import json
# # # # # # # # # # import pandas as pd
# # # # # # # # # # import io

# # # # # # # # # # from .models import Room, Student, Bench, Absentee

# # # # # # # # # # def room_list(request):
# # # # # # # # # #     rooms = Room.objects.all()
# # # # # # # # # #     return render(request, 'attendance/room_list.html', {'rooms': rooms})

# # # # # # # # # # def seating_plan_view(request, room_id):
# # # # # # # # # #     room = get_object_or_404(Room, pk=room_id)
# # # # # # # # # #     benches = Bench.objects.filter(room=room).order_by('col_num', 'row_num')
# # # # # # # # # #     plan = [[] for _ in range(room.columns)]
    
# # # # # # # # # #     for bench in benches:
# # # # # # # # # #         students_on_bench = list(bench.students.all())
# # # # # # # # # #         seats = []
# # # # # # # # # #         for i in range(room.students_per_bench):
# # # # # # # # # #             if i < len(students_on_bench):
# # # # # # # # # #                 seats.append(students_on_bench[i])
# # # # # # # # # #             else:
# # # # # # # # # #                 seats.append(None)
# # # # # # # # # #         bench.seats = seats
# # # # # # # # # #         plan[bench.col_num - 1].append(bench)
        
# # # # # # # # # #     return render(request, 'attendance/seating_plan.html', {'room': room, 'plan': plan})

# # # # # # # # # # @csrf_exempt
# # # # # # # # # # def save_absentees(request):
# # # # # # # # # #     if request.method == 'POST':
# # # # # # # # # #         data = json.loads(request.body)
# # # # # # # # # #         room_id = data.get('room_id')
# # # # # # # # # #         absent_ids = data.get('absent_ids', [])

# # # # # # # # # #         if not room_id:
# # # # # # # # # #             return JsonResponse({'status': 'error', 'message': 'Missing room_id'}, status=400)
        
# # # # # # # # # #         try:
# # # # # # # # # #             room = Room.objects.get(id=room_id)
# # # # # # # # # #             Absentee.objects.filter(room=room).delete()

# # # # # # # # # #             for student_id in absent_ids:
# # # # # # # # # #                 student = Student.objects.get(student_id=student_id)
# # # # # # # # # #                 Absentee.objects.get_or_create(room=room, student=student)
            
# # # # # # # # # #             return JsonResponse({'status': 'success', 'message': f'{len(absent_ids)} absentees recorded for {room.name}.'})
# # # # # # # # # #         except (Student.DoesNotExist, Room.DoesNotExist):
# # # # # # # # # #             return JsonResponse({'status': 'error', 'message': 'Invalid student or room ID found.'}, status=404)
            
# # # # # # # # # #     return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# # # # # # # # # # def upload_students(request):
# # # # # # # # # #     if request.method == 'POST':
# # # # # # # # # #         excel_file = request.FILES.get('excel_file')
# # # # # # # # # #         if not excel_file or not excel_file.name.endswith('.xlsx'):
# # # # # # # # # #             messages.error(request, 'Please upload a valid .xlsx file.')
# # # # # # # # # #             return redirect('upload_students')
        
# # # # # # # # # #         try:
# # # # # # # # # #             df = pd.read_excel(excel_file)
# # # # # # # # # #             required_cols = ['StudentID', 'Batch']
# # # # # # # # # #             if not all(col in df.columns for col in required_cols):
# # # # # # # # # #                 messages.error(request, "Excel file must have columns named 'StudentID' and 'Batch'.")
# # # # # # # # # #                 return redirect('upload_students')

# # # # # # # # # #             created_count = 0
# # # # # # # # # #             for index, row in df.iterrows():
# # # # # # # # # #                 sid = str(row['StudentID'])
# # # # # # # # # #                 batch_name = str(row['Batch'])
                
# # # # # # # # # #                 student, created = Student.objects.update_or_create(
# # # # # # # # # #                     student_id=sid,
# # # # # # # # # #                     defaults={'batch': batch_name}
# # # # # # # # # #                 )
# # # # # # # # # #                 if created:
# # # # # # # # # #                     created_count += 1
            
# # # # # # # # # #             messages.success(request, f'Successfully processed file. Added {created_count} new students.')
# # # # # # # # # #             return redirect('room_list')

# # # # # # # # # #         except Exception as e:
# # # # # # # # # #             messages.error(request, f'An error occurred: {e}')
# # # # # # # # # #             return redirect('upload_students')

# # # # # # # # # #     return render(request, 'attendance/upload_students.html')

# # # # # # # # # # def auto_arrange_seating(request, room_id):
# # # # # # # # # #     room_to_arrange = get_object_or_404(Room, pk=room_id)
    
# # # # # # # # # #     seated_students_ids = Bench.objects.values_list('students', flat=True)
# # # # # # # # # #     students_to_seat = Student.objects.exclude(id__in=seated_students_ids).order_by('id')

# # # # # # # # # #     if not students_to_seat:
# # # # # # # # # #         messages.warning(request, 'No unseated students available to arrange.')
# # # # # # # # # #         return redirect('room_list')

# # # # # # # # # #     Bench.objects.filter(room=room_to_arrange).delete()

# # # # # # # # # #     students_by_batch = defaultdict(list)
# # # # # # # # # #     for student in students_to_seat:
# # # # # # # # # #         students_by_batch[student.batch].append(student)

# # # # # # # # # #     batch_names = sorted(students_by_batch.keys())
    
# # # # # # # # # #     if len(batch_names) < 2:
# # # # # # # # # #         messages.warning(request, 'Seating arrangement requires at least two batches of students.')
# # # # # # # # # #         return redirect('room_list')
        
# # # # # # # # # #     if room_to_arrange.id % 2 != 0:
# # # # # # # # # #         batch_order = batch_names
# # # # # # # # # #     else:
# # # # # # # # # #         batch_order = list(reversed(batch_names))

# # # # # # # # # #     seated_count = 0
# # # # # # # # # #     total_virtual_columns = room_to_arrange.columns * room_to_arrange.students_per_bench

# # # # # # # # # #     for virtual_col_idx in range(total_virtual_columns):
# # # # # # # # # #         batch_to_pick_name = batch_order[virtual_col_idx % len(batch_order)]
        
# # # # # # # # # #         real_bench_col = (virtual_col_idx // room_to_arrange.students_per_bench) + 1
        
# # # # # # # # # #         for r in range(1, room_to_arrange.benches_per_column + 1):
# # # # # # # # # #             if students_by_batch[batch_to_pick_name]:
# # # # # # # # # #                 student = students_by_batch[batch_to_pick_name].pop(0)
                
# # # # # # # # # #                 bench, _ = Bench.objects.get_or_create(room=room_to_arrange, row_num=r, col_num=real_bench_col)
# # # # # # # # # #                 bench.students.add(student)
# # # # # # # # # #                 seated_count += 1
# # # # # # # # # #             else:
# # # # # # # # # #                 break
            
# # # # # # # # # #     messages.success(request, f'Successfully arranged {seated_count} students in {room_to_arrange.name}.')
# # # # # # # # # #     return redirect('room_list')

# # # # # # # # # # def download_report(request):
# # # # # # # # # #     absentees = Absentee.objects.select_related('room', 'student').order_by('room__name', 'student__batch')

# # # # # # # # # #     detailed_data = defaultdict(lambda: defaultdict(list))
# # # # # # # # # #     for ab in absentees:
# # # # # # # # # #         detailed_data[ab.room.name][ab.student.batch].append(ab.student.student_id)

# # # # # # # # # #     detailed_rows = []
# # # # # # # # # #     for room_name, batches in detailed_data.items():
# # # # # # # # # #         for batch_name, student_ids in batches.items():
# # # # # # # # # #             detailed_rows.append({
# # # # # # # # # #                 'Room Number': room_name,
# # # # # # # # # #                 'Batch': batch_name,
# # # # # # # # # #                 'Absentees': ', '.join(student_ids)
# # # # # # # # # #             })
    
# # # # # # # # # #     df1 = pd.DataFrame(detailed_rows)

# # # # # # # # # #     summary_data = defaultdict(int)
# # # # # # # # # #     for ab in absentees:
# # # # # # # # # #         summary_data[ab.student.batch] += 1
    
# # # # # # # # # #     summary_rows = [{'Batch': batch, 'Absentees Count': count} for batch, count in summary_data.items()]
# # # # # # # # # #     df2 = pd.DataFrame(summary_rows)

# # # # # # # # # #     output = io.BytesIO()
# # # # # # # # # #     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
# # # # # # # # # #         df1.to_excel(writer, sheet_name='Detailed Report', index=False)
# # # # # # # # # #         df2.to_excel(writer, sheet_name='Consolidated Report', index=False)

# # # # # # # # # #         workbook = writer.book
# # # # # # # # # #         worksheet = writer.sheets['Detailed Report']
        
# # # # # # # # # #         header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
# # # # # # # # # #         for col_num, value in enumerate(df1.columns.values):
# # # # # # # # # #             worksheet.write(0, col_num, value, header_format)

# # # # # # # # # #         if not df1.empty:
# # # # # # # # # #             merge_start_row = 1
# # # # # # # # # #             for i in range(1, len(df1)):
# # # # # # # # # #                 if df1.iloc[i]['Room Number'] != df1.iloc[i-1]['Room Number']:
# # # # # # # # # #                     if merge_start_row < i:
# # # # # # # # # #                         worksheet.merge_range(merge_start_row, 0, i, 0, df1.iloc[i-1]['Room Number'])
# # # # # # # # # #                     merge_start_row = i + 1
# # # # # # # # # #             worksheet.merge_range(merge_start_row, 0, len(df1), 0, df1.iloc[-1]['Room Number'])

# # # # # # # # # #     output.seek(0)
    
# # # # # # # # # #     response = HttpResponse(
# # # # # # # # # #         output,
# # # # # # # # # #         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
# # # # # # # # # #     )
# # # # # # # # # #     response['Content-Disposition'] = 'attachment; filename="absentee_report.xlsx"'
    
# # # # # # # # # #     return response

# # # # # # # # # # def download_seating_plan(request, room_id):
# # # # # # # # # #     room = get_object_or_404(Room, pk=room_id)
# # # # # # # # # #     benches = Bench.objects.filter(room=room).prefetch_related('students').order_by('row_num', 'col_num')

# # # # # # # # # #     # --- Determine Headers ---
# # # # # # # # # #     batch_names = sorted(list(Student.objects.values_list('batch', flat=True).distinct()))
    
# # # # # # # # # #     if len(batch_names) < 2:
# # # # # # # # # #         batch_order = batch_names
# # # # # # # # # #     elif room.id % 2 != 0:
# # # # # # # # # #         batch_order = batch_names
# # # # # # # # # #     else:
# # # # # # # # # #         batch_order = list(reversed(batch_names))

# # # # # # # # # #     headers = []
# # # # # # # # # #     total_virtual_columns = room.columns * room.students_per_bench
# # # # # # # # # #     for virtual_col_idx in range(total_virtual_columns):
# # # # # # # # # #         if batch_order:
# # # # # # # # # #             batch_name = batch_order[virtual_col_idx % len(batch_order)]
# # # # # # # # # #             headers.append(batch_name)
# # # # # # # # # #         else:
# # # # # # # # # #             headers.append(f'Seat {virtual_col_idx + 1}')

# # # # # # # # # #     # --- Prepare Data Grid ---
# # # # # # # # # #     num_rows = room.benches_per_column
# # # # # # # # # #     plan_data = [['' for _ in range(total_virtual_columns)] for _ in range(num_rows)]

# # # # # # # # # #     for bench in benches:
# # # # # # # # # #         students_on_bench = list(bench.students.all())
# # # # # # # # # #         start_col = (bench.col_num - 1) * room.students_per_bench
# # # # # # # # # #         for i, student in enumerate(students_on_bench):
# # # # # # # # # #             if start_col + i < len(plan_data[bench.row_num - 1]):
# # # # # # # # # #                 plan_data[bench.row_num - 1][start_col + i] = student.student_id

# # # # # # # # # #     df = pd.DataFrame(plan_data, columns=headers)

# # # # # # # # # #     # --- Create Excel File ---
# # # # # # # # # #     output = io.BytesIO()
# # # # # # # # # #     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
# # # # # # # # # #         df.to_excel(writer, sheet_name=room.name, index=False, header=True)
        
# # # # # # # # # #         workbook = writer.book
# # # # # # # # # #         worksheet = writer.sheets[room.name]
# # # # # # # # # #         header_format = workbook.add_format({'bold': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
        
# # # # # # # # # #         for col_num, value in enumerate(df.columns.values):
# # # # # # # # # #             worksheet.write(0, col_num, value, header_format)

# # # # # # # # # #         # --- CORRECTED COLUMN WIDTH LOGIC ---
# # # # # # # # # #         for idx, col_name in enumerate(df.columns):
# # # # # # # # # #             # Calculate max length of data in the column, handling empty columns safely
# # # # # # # # # #             data_max_len = df[col_name].astype(str).map(len).max()
# # # # # # # # # #             if pd.isna(data_max_len):
# # # # # # # # # #                 data_max_len = 0

# # # # # # # # # #             # Calculate length of the header
# # # # # # # # # #             header_len = len(str(col_name))
            
# # # # # # # # # #             # The final column width is the max of the two, plus a little padding
# # # # # # # # # #             final_width = max(int(data_max_len), header_len) + 2
            
# # # # # # # # # #             worksheet.set_column(idx, idx, final_width)

# # # # # # # # # #     output.seek(0)
    
# # # # # # # # # #     response = HttpResponse(
# # # # # # # # # #         output,
# # # # # # # # # #         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
# # # # # # # # # #     )
# # # # # # # # # #     response['Content-Disposition'] = f'attachment; filename="seating_plan_{room.name}.xlsx"'
    
# # # # # # # # # #     return response










# # # # # # # # # # attendance/views.py

# # # # # # # # # from django.shortcuts import render, get_object_or_404, redirect
# # # # # # # # # from django.http import HttpResponse, JsonResponse
# # # # # # # # # from django.views.decorators.csrf import csrf_exempt
# # # # # # # # # from django.contrib import messages
# # # # # # # # # from collections import defaultdict
# # # # # # # # # import json
# # # # # # # # # import pandas as pd
# # # # # # # # # import io

# # # # # # # # # from .models import Room, Student, Bench, Absentee

# # # # # # # # # def room_list(request):
# # # # # # # # #     rooms = Room.objects.all()
# # # # # # # # #     return render(request, 'attendance/room_list.html', {'rooms': rooms})

# # # # # # # # # def seating_plan_view(request, room_id):
# # # # # # # # #     room = get_object_or_404(Room, pk=room_id)
# # # # # # # # #     benches = Bench.objects.filter(room=room).order_by('col_num', 'row_num')
# # # # # # # # #     plan = [[] for _ in range(room.columns)]
    
# # # # # # # # #     for bench in benches:
# # # # # # # # #         students_on_bench = list(bench.students.all())
# # # # # # # # #         seats = []
# # # # # # # # #         for i in range(room.students_per_bench):
# # # # # # # # #             if i < len(students_on_bench):
# # # # # # # # #                 seats.append(students_on_bench[i])
# # # # # # # # #             else:
# # # # # # # # #                 seats.append(None)
# # # # # # # # #         bench.seats = seats
# # # # # # # # #         plan[bench.col_num - 1].append(bench)
        
# # # # # # # # #     return render(request, 'attendance/seating_plan.html', {'room': room, 'plan': plan})

# # # # # # # # # @csrf_exempt
# # # # # # # # # def save_absentees(request):
# # # # # # # # #     if request.method == 'POST':
# # # # # # # # #         data = json.loads(request.body)
# # # # # # # # #         room_id = data.get('room_id')
# # # # # # # # #         absent_ids = data.get('absent_ids', [])

# # # # # # # # #         if not room_id:
# # # # # # # # #             return JsonResponse({'status': 'error', 'message': 'Missing room_id'}, status=400)
        
# # # # # # # # #         try:
# # # # # # # # #             room = Room.objects.get(id=room_id)
# # # # # # # # #             Absentee.objects.filter(room=room).delete()

# # # # # # # # #             for student_id in absent_ids:
# # # # # # # # #                 student = Student.objects.get(student_id=student_id)
# # # # # # # # #                 Absentee.objects.get_or_create(room=room, student=student)
            
# # # # # # # # #             return JsonResponse({'status': 'success', 'message': f'{len(absent_ids)} absentees recorded for {room.name}.'})
# # # # # # # # #         except (Student.DoesNotExist, Room.DoesNotExist):
# # # # # # # # #             return JsonResponse({'status': 'error', 'message': 'Invalid student or room ID found.'}, status=404)
            
# # # # # # # # #     return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# # # # # # # # # def upload_students(request):
# # # # # # # # #     if request.method == 'POST':
# # # # # # # # #         excel_file = request.FILES.get('excel_file')
# # # # # # # # #         if not excel_file or not excel_file.name.endswith('.xlsx'):
# # # # # # # # #             messages.error(request, 'Please upload a valid .xlsx file.')
# # # # # # # # #             return redirect('upload_students')
        
# # # # # # # # #         try:
# # # # # # # # #             df = pd.read_excel(excel_file)
# # # # # # # # #             required_cols = ['StudentID', 'Batch']
# # # # # # # # #             if not all(col in df.columns for col in required_cols):
# # # # # # # # #                 messages.error(request, "Excel file must have columns named 'StudentID' and 'Batch'.")
# # # # # # # # #                 return redirect('upload_students')

# # # # # # # # #             created_count = 0
# # # # # # # # #             for index, row in df.iterrows():
# # # # # # # # #                 sid = str(row['StudentID'])
# # # # # # # # #                 batch_name = str(row['Batch'])
                
# # # # # # # # #                 student, created = Student.objects.update_or_create(
# # # # # # # # #                     student_id=sid,
# # # # # # # # #                     defaults={'batch': batch_name}
# # # # # # # # #                 )
# # # # # # # # #                 if created:
# # # # # # # # #                     created_count += 1
            
# # # # # # # # #             messages.success(request, f'Successfully processed file. Added {created_count} new students.')
# # # # # # # # #             return redirect('room_list')

# # # # # # # # #         except Exception as e:
# # # # # # # # #             messages.error(request, f'An error occurred: {e}')
# # # # # # # # #             return redirect('upload_students')

# # # # # # # # #     return render(request, 'attendance/upload_students.html')

# # # # # # # # # def auto_arrange_seating(request, room_id):
# # # # # # # # #     room_to_arrange = get_object_or_404(Room, pk=room_id)
    
# # # # # # # # #     seated_students_ids = Bench.objects.values_list('students', flat=True)
# # # # # # # # #     students_to_seat = Student.objects.exclude(id__in=seated_students_ids).order_by('id')

# # # # # # # # #     if not students_to_seat:
# # # # # # # # #         messages.warning(request, 'No unseated students available to arrange.')
# # # # # # # # #         return redirect('room_list')

# # # # # # # # #     Bench.objects.filter(room=room_to_arrange).delete()

# # # # # # # # #     students_by_batch = defaultdict(list)
# # # # # # # # #     for student in students_to_seat:
# # # # # # # # #         students_by_batch[student.batch].append(student)

# # # # # # # # #     batch_names = sorted(students_by_batch.keys())
    
# # # # # # # # #     if len(batch_names) < 2:
# # # # # # # # #         messages.warning(request, 'Seating arrangement requires at least two batches of students.')
# # # # # # # # #         return redirect('room_list')
        
# # # # # # # # #     if room_to_arrange.id % 2 != 0:
# # # # # # # # #         batch_order = batch_names
# # # # # # # # #     else:
# # # # # # # # #         batch_order = list(reversed(batch_names))

# # # # # # # # #     seated_count = 0
# # # # # # # # #     total_virtual_columns = room_to_arrange.columns * room_to_arrange.students_per_bench

# # # # # # # # #     for virtual_col_idx in range(total_virtual_columns):
# # # # # # # # #         batch_to_pick_name = batch_order[virtual_col_idx % len(batch_order)]
        
# # # # # # # # #         real_bench_col = (virtual_col_idx // room_to_arrange.students_per_bench) + 1
        
# # # # # # # # #         for r in range(1, room_to_arrange.benches_per_column + 1):
# # # # # # # # #             if students_by_batch[batch_to_pick_name]:
# # # # # # # # #                 student = students_by_batch[batch_to_pick_name].pop(0)
                
# # # # # # # # #                 bench, _ = Bench.objects.get_or_create(room=room_to_arrange, row_num=r, col_num=real_bench_col)
# # # # # # # # #                 bench.students.add(student)
# # # # # # # # #                 seated_count += 1
# # # # # # # # #             else:
# # # # # # # # #                 break
            
# # # # # # # # #     messages.success(request, f'Successfully arranged {seated_count} students in {room_to_arrange.name}.')
# # # # # # # # #     return redirect('room_list')

# # # # # # # # # def download_report(request):
# # # # # # # # #     absentees = Absentee.objects.select_related('room', 'student').order_by('room__name', 'student__batch')

# # # # # # # # #     detailed_data = defaultdict(lambda: defaultdict(list))
# # # # # # # # #     for ab in absentees:
# # # # # # # # #         detailed_data[ab.room.name][ab.student.batch].append(ab.student.student_id)

# # # # # # # # #     detailed_rows = []
# # # # # # # # #     for room_name, batches in detailed_data.items():
# # # # # # # # #         for batch_name, student_ids in batches.items():
# # # # # # # # #             detailed_rows.append({
# # # # # # # # #                 'Room Number': room_name,
# # # # # # # # #                 'Batch': batch_name,
# # # # # # # # #                 'Absentees': ', '.join(student_ids)
# # # # # # # # #             })
    
# # # # # # # # #     df1 = pd.DataFrame(detailed_rows)

# # # # # # # # #     summary_data = defaultdict(int)
# # # # # # # # #     for ab in absentees:
# # # # # # # # #         summary_data[ab.student.batch] += 1
    
# # # # # # # # #     summary_rows = [{'Batch': batch, 'Absentees Count': count} for batch, count in summary_data.items()]
# # # # # # # # #     df2 = pd.DataFrame(summary_rows)

# # # # # # # # #     output = io.BytesIO()
# # # # # # # # #     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
# # # # # # # # #         df1.to_excel(writer, sheet_name='Detailed Report', index=False)
# # # # # # # # #         df2.to_excel(writer, sheet_name='Consolidated Report', index=False)

# # # # # # # # #         workbook = writer.book
# # # # # # # # #         worksheet = writer.sheets['Detailed Report']
        
# # # # # # # # #         header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
# # # # # # # # #         for col_num, value in enumerate(df1.columns.values):
# # # # # # # # #             worksheet.write(0, col_num, value, header_format)

# # # # # # # # #         if not df1.empty:
# # # # # # # # #             merge_start_row = 1
# # # # # # # # #             for i in range(1, len(df1)):
# # # # # # # # #                 if df1.iloc[i]['Room Number'] != df1.iloc[i-1]['Room Number']:
# # # # # # # # #                     if merge_start_row < i:
# # # # # # # # #                         worksheet.merge_range(merge_start_row, 0, i, 0, df1.iloc[i-1]['Room Number'])
# # # # # # # # #                     merge_start_row = i + 1
# # # # # # # # #             worksheet.merge_range(merge_start_row, 0, len(df1), 0, df1.iloc[-1]['Room Number'])

# # # # # # # # #     output.seek(0)
    
# # # # # # # # #     response = HttpResponse(
# # # # # # # # #         output,
# # # # # # # # #         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
# # # # # # # # #     )
# # # # # # # # #     response['Content-Disposition'] = 'attachment; filename="absentee_report.xlsx"'
    
# # # # # # # # #     return response

# # # # # # # # # def download_seating_plan(request, room_id):
# # # # # # # # #     room = get_object_or_404(Room, pk=room_id)
# # # # # # # # #     benches = Bench.objects.filter(room=room).prefetch_related('students').order_by('row_num', 'col_num')

# # # # # # # # #     # --- Determine Headers ---
# # # # # # # # #     batch_names = sorted(list(Student.objects.values_list('batch', flat=True).distinct()))
    
# # # # # # # # #     if len(batch_names) < 2:
# # # # # # # # #         batch_order = batch_names
# # # # # # # # #     elif room.id % 2 != 0:
# # # # # # # # #         batch_order = batch_names
# # # # # # # # #     else:
# # # # # # # # #         batch_order = list(reversed(batch_names))

# # # # # # # # #     headers = []
# # # # # # # # #     total_virtual_columns = room.columns * room.students_per_bench
# # # # # # # # #     for virtual_col_idx in range(total_virtual_columns):
# # # # # # # # #         if batch_order:
# # # # # # # # #             batch_name = batch_order[virtual_col_idx % len(batch_order)]
# # # # # # # # #             headers.append(batch_name)
# # # # # # # # #         else:
# # # # # # # # #             headers.append(f'Seat {virtual_col_idx + 1}')

# # # # # # # # #     # --- Prepare Data Grid ---
# # # # # # # # #     num_rows = room.benches_per_column
# # # # # # # # #     plan_data = [['' for _ in range(total_virtual_columns)] for _ in range(num_rows)]

# # # # # # # # #     for bench in benches:
# # # # # # # # #         students_on_bench = list(bench.students.all())
# # # # # # # # #         start_col = (bench.col_num - 1) * room.students_per_bench
# # # # # # # # #         for i, student in enumerate(students_on_bench):
# # # # # # # # #             if start_col + i < len(plan_data[bench.row_num - 1]):
# # # # # # # # #                 plan_data[bench.row_num - 1][start_col + i] = student.student_id

# # # # # # # # #     df = pd.DataFrame(plan_data, columns=headers)

# # # # # # # # #     # --- Create Excel File ---
# # # # # # # # #     output = io.BytesIO()
# # # # # # # # #     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
# # # # # # # # #         df.to_excel(writer, sheet_name=room.name, index=False, header=True)
        
# # # # # # # # #         workbook = writer.book
# # # # # # # # #         worksheet = writer.sheets[room.name]
# # # # # # # # #         header_format = workbook.add_format({'bold': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
        
# # # # # # # # #         for col_num, value in enumerate(df.columns.values):
# # # # # # # # #             worksheet.write(0, col_num, value, header_format)

# # # # # # # # #         # --- CORRECTED COLUMN WIDTH LOGIC ---
# # # # # # # # #         for idx in range(len(df.columns)):
# # # # # # # # #             # Select column by its integer position (iloc) to avoid ambiguity
# # # # # # # # #             series = df.iloc[:, idx]
            
# # # # # # # # #             # Calculate max length of data in the column
# # # # # # # # #             data_max_len = series.astype(str).map(len).max()
# # # # # # # # #             if pd.isna(data_max_len):
# # # # # # # # #                 data_max_len = 0

# # # # # # # # #             # Calculate length of the header
# # # # # # # # #             header_len = len(str(df.columns[idx]))
            
# # # # # # # # #             # The final column width is the max of the two, plus a little padding
# # # # # # # # #             final_width = max(int(data_max_len), header_len) + 2
            
# # # # # # # # #             worksheet.set_column(idx, idx, final_width)

# # # # # # # # #     output.seek(0)
    
# # # # # # # # #     response = HttpResponse(
# # # # # # # # #         output,
# # # # # # # # #         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
# # # # # # # # #     )
# # # # # # # # #     response['Content-Disposition'] = f'attachment; filename="seating_plan_{room.name}.xlsx"'
    
# # # # # # # # #     return response

















# # # # # # # # # attendance/views.py

# # # # # # # # from django.shortcuts import render, get_object_or_404, redirect
# # # # # # # # from django.http import HttpResponse, JsonResponse
# # # # # # # # from django.views.decorators.csrf import csrf_exempt
# # # # # # # # from django.contrib import messages
# # # # # # # # from django.contrib.auth.decorators import login_required # Import login_required
# # # # # # # # from collections import defaultdict
# # # # # # # # import json
# # # # # # # # import pandas as pd
# # # # # # # # import io

# # # # # # # # from .models import Room, Student, Bench, Absentee

# # # # # # # # @login_required
# # # # # # # # def room_list(request):
# # # # # # # #     rooms = Room.objects.all()
# # # # # # # #     return render(request, 'attendance/room_list.html', {'rooms': rooms})

# # # # # # # # @login_required
# # # # # # # # def seating_plan_view(request, room_id):
# # # # # # # #     room = get_object_or_404(Room, pk=room_id)
# # # # # # # #     benches = Bench.objects.filter(room=room).order_by('col_num', 'row_num')
# # # # # # # #     plan = [[] for _ in range(room.columns)]
    
# # # # # # # #     for bench in benches:
# # # # # # # #         students_on_bench = list(bench.students.all())
# # # # # # # #         seats = []
# # # # # # # #         for i in range(room.students_per_bench):
# # # # # # # #             if i < len(students_on_bench):
# # # # # # # #                 seats.append(students_on_bench[i])
# # # # # # # #             else:
# # # # # # # #                 seats.append(None)
# # # # # # # #         bench.seats = seats
# # # # # # # #         plan[bench.col_num - 1].append(bench)
        
# # # # # # # #     return render(request, 'attendance/seating_plan.html', {'room': room, 'plan': plan})

# # # # # # # # @csrf_exempt
# # # # # # # # @login_required
# # # # # # # # def save_absentees(request):
# # # # # # # #     if request.method == 'POST':
# # # # # # # #         data = json.loads(request.body)
# # # # # # # #         room_id = data.get('room_id')
# # # # # # # #         absent_ids = data.get('absent_ids', [])

# # # # # # # #         if not room_id:
# # # # # # # #             return JsonResponse({'status': 'error', 'message': 'Missing room_id'}, status=400)
        
# # # # # # # #         try:
# # # # # # # #             room = Room.objects.get(id=room_id)
# # # # # # # #             Absentee.objects.filter(room=room).delete()

# # # # # # # #             for student_id in absent_ids:
# # # # # # # #                 student = Student.objects.get(student_id=student_id)
# # # # # # # #                 Absentee.objects.get_or_create(room=room, student=student)
            
# # # # # # # #             return JsonResponse({'status': 'success', 'message': f'{len(absent_ids)} absentees recorded for {room.name}.'})
# # # # # # # #         except (Student.DoesNotExist, Room.DoesNotExist):
# # # # # # # #             return JsonResponse({'status': 'error', 'message': 'Invalid student or room ID found.'}, status=404)
            
# # # # # # # #     return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# # # # # # # # @login_required
# # # # # # # # def upload_students(request):
# # # # # # # #     if not request.user.is_staff:
# # # # # # # #         return redirect('room_list')
# # # # # # # #     # ... (rest of the view is the same)
# # # # # # # #     if request.method == 'POST':
# # # # # # # #         excel_file = request.FILES.get('excel_file')
# # # # # # # #         if not excel_file or not excel_file.name.endswith('.xlsx'):
# # # # # # # #             messages.error(request, 'Please upload a valid .xlsx file.')
# # # # # # # #             return redirect('upload_students')
        
# # # # # # # #         try:
# # # # # # # #             df = pd.read_excel(excel_file)
# # # # # # # #             required_cols = ['StudentID', 'Batch']
# # # # # # # #             if not all(col in df.columns for col in required_cols):
# # # # # # # #                 messages.error(request, "Excel file must have columns named 'StudentID' and 'Batch'.")
# # # # # # # #                 return redirect('upload_students')

# # # # # # # #             created_count = 0
# # # # # # # #             for index, row in df.iterrows():
# # # # # # # #                 sid = str(row['StudentID'])
# # # # # # # #                 batch_name = str(row['Batch'])
                
# # # # # # # #                 student, created = Student.objects.update_or_create(
# # # # # # # #                     student_id=sid,
# # # # # # # #                     defaults={'batch': batch_name}
# # # # # # # #                 )
# # # # # # # #                 if created:
# # # # # # # #                     created_count += 1
            
# # # # # # # #             messages.success(request, f'Successfully processed file. Added {created_count} new students.')
# # # # # # # #             return redirect('room_list')

# # # # # # # #         except Exception as e:
# # # # # # # #             messages.error(request, f'An error occurred: {e}')
# # # # # # # #             return redirect('upload_students')

# # # # # # # #     return render(request, 'attendance/upload_students.html')

# # # # # # # # @login_required
# # # # # # # # def auto_arrange_seating(request, room_id):
# # # # # # # #     if not request.user.is_staff:
# # # # # # # #         return redirect('room_list')
# # # # # # # #     # ... (rest of the view is the same)
# # # # # # # #     room_to_arrange = get_object_or_404(Room, pk=room_id)
    
# # # # # # # #     seated_students_ids = Bench.objects.values_list('students', flat=True)
# # # # # # # #     students_to_seat = Student.objects.exclude(id__in=seated_students_ids).order_by('id')

# # # # # # # #     if not students_to_seat:
# # # # # # # #         messages.warning(request, 'No unseated students available to arrange.')
# # # # # # # #         return redirect('room_list')

# # # # # # # #     Bench.objects.filter(room=room_to_arrange).delete()

# # # # # # # #     students_by_batch = defaultdict(list)
# # # # # # # #     for student in students_to_seat:
# # # # # # # #         students_by_batch[student.batch].append(student)

# # # # # # # #     batch_names = sorted(students_by_batch.keys())
    
# # # # # # # #     if len(batch_names) < 2:
# # # # # # # #         messages.warning(request, 'Seating arrangement requires at least two batches of students.')
# # # # # # # #         return redirect('room_list')
        
# # # # # # # #     if room_to_arrange.id % 2 != 0:
# # # # # # # #         batch_order = batch_names
# # # # # # # #     else:
# # # # # # # #         batch_order = list(reversed(batch_names))

# # # # # # # #     seated_count = 0
# # # # # # # #     total_virtual_columns = room_to_arrange.columns * room_to_arrange.students_per_bench

# # # # # # # #     for virtual_col_idx in range(total_virtual_columns):
# # # # # # # #         batch_to_pick_name = batch_order[virtual_col_idx % len(batch_order)]
        
# # # # # # # #         real_bench_col = (virtual_col_idx // room_to_arrange.students_per_bench) + 1
        
# # # # # # # #         for r in range(1, room_to_arrange.benches_per_column + 1):
# # # # # # # #             if students_by_batch[batch_to_pick_name]:
# # # # # # # #                 student = students_by_batch[batch_to_pick_name].pop(0)
                
# # # # # # # #                 bench, _ = Bench.objects.get_or_create(room=room_to_arrange, row_num=r, col_num=real_bench_col)
# # # # # # # #                 bench.students.add(student)
# # # # # # # #                 seated_count += 1
# # # # # # # #             else:
# # # # # # # #                 break
            
# # # # # # # #     messages.success(request, f'Successfully arranged {seated_count} students in {room_to_arrange.name}.')
# # # # # # # #     return redirect('room_list')

# # # # # # # # @login_required
# # # # # # # # def download_report(request):
# # # # # # # #     if not request.user.is_staff:
# # # # # # # #         return redirect('room_list')
# # # # # # # #     # ... (rest of the view is the same)
# # # # # # # #     absentees = Absentee.objects.select_related('room', 'student').order_by('room__name', 'student__batch')

# # # # # # # #     detailed_data = defaultdict(lambda: defaultdict(list))
# # # # # # # #     for ab in absentees:
# # # # # # # #         detailed_data[ab.room.name][ab.student.batch].append(ab.student.student_id)

# # # # # # # #     detailed_rows = []
# # # # # # # #     for room_name, batches in detailed_data.items():
# # # # # # # #         for batch_name, student_ids in batches.items():
# # # # # # # #             detailed_rows.append({
# # # # # # # #                 'Room Number': room_name,
# # # # # # # #                 'Batch': batch_name,
# # # # # # # #                 'Absentees': ', '.join(student_ids)
# # # # # # # #             })
    
# # # # # # # #     df1 = pd.DataFrame(detailed_rows)

# # # # # # # #     summary_data = defaultdict(int)
# # # # # # # #     for ab in absentees:
# # # # # # # #         summary_data[ab.student.batch] += 1
    
# # # # # # # #     summary_rows = [{'Batch': batch, 'Absentees Count': count} for batch, count in summary_data.items()]
# # # # # # # #     df2 = pd.DataFrame(summary_rows)

# # # # # # # #     output = io.BytesIO()
# # # # # # # #     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
# # # # # # # #         df1.to_excel(writer, sheet_name='Detailed Report', index=False)
# # # # # # # #         df2.to_excel(writer, sheet_name='Consolidated Report', index=False)

# # # # # # # #         workbook = writer.book
# # # # # # # #         worksheet = writer.sheets['Detailed Report']
        
# # # # # # # #         header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
# # # # # # # #         for col_num, value in enumerate(df1.columns.values):
# # # # # # # #             worksheet.write(0, col_num, value, header_format)

# # # # # # # #         if not df1.empty:
# # # # # # # #             merge_start_row = 1
# # # # # # # #             for i in range(1, len(df1)):
# # # # # # # #                 if df1.iloc[i]['Room Number'] != df1.iloc[i-1]['Room Number']:
# # # # # # # #                     if merge_start_row < i:
# # # # # # # #                         worksheet.merge_range(merge_start_row, 0, i, 0, df1.iloc[i-1]['Room Number'])
# # # # # # # #                     merge_start_row = i + 1
# # # # # # # #             worksheet.merge_range(merge_start_row, 0, len(df1), 0, df1.iloc[-1]['Room Number'])

# # # # # # # #     output.seek(0)
    
# # # # # # # #     response = HttpResponse(
# # # # # # # #         output,
# # # # # # # #         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
# # # # # # # #     )
# # # # # # # #     response['Content-Disposition'] = 'attachment; filename="absentee_report.xlsx"'
    
# # # # # # # #     return response

# # # # # # # # @login_required
# # # # # # # # def download_seating_plan(request, room_id):
# # # # # # # #     if not request.user.is_staff:
# # # # # # # #         return redirect('room_list')
# # # # # # # #     # ... (rest of the view is the same)
# # # # # # # #     room = get_object_or_404(Room, pk=room_id)
# # # # # # # #     benches = Bench.objects.filter(room=room).prefetch_related('students').order_by('row_num', 'col_num')

# # # # # # # #     batch_names = sorted(list(Student.objects.values_list('batch', flat=True).distinct()))
    
# # # # # # # #     if len(batch_names) < 2:
# # # # # # # #         batch_order = batch_names
# # # # # # # #     elif room.id % 2 != 0:
# # # # # # # #         batch_order = batch_names
# # # # # # # #     else:
# # # # # # # #         batch_order = list(reversed(batch_names))

# # # # # # # #     headers = []
# # # # # # # #     total_virtual_columns = room.columns * room.students_per_bench
# # # # # # # #     for virtual_col_idx in range(total_virtual_columns):
# # # # # # # #         if batch_order:
# # # # # # # #             batch_name = batch_order[virtual_col_idx % len(batch_order)]
# # # # # # # #             headers.append(batch_name)
# # # # # # # #         else:
# # # # # # # #             headers.append(f'Seat {virtual_col_idx + 1}')

# # # # # # # #     num_rows = room.benches_per_column
# # # # # # # #     plan_data = [['' for _ in range(total_virtual_columns)] for _ in range(num_rows)]

# # # # # # # #     for bench in benches:
# # # # # # # #         students_on_bench = list(bench.students.all())
# # # # # # # #         start_col = (bench.col_num - 1) * room.students_per_bench
# # # # # # # #         for i, student in enumerate(students_on_bench):
# # # # # # # #             if start_col + i < len(plan_data[bench.row_num - 1]):
# # # # # # # #                 plan_data[bench.row_num - 1][start_col + i] = student.student_id

# # # # # # # #     df = pd.DataFrame(plan_data, columns=headers)

# # # # # # # #     output = io.BytesIO()
# # # # # # # #     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
# # # # # # # #         df.to_excel(writer, sheet_name=room.name, index=False, header=True)
        
# # # # # # # #         workbook = writer.book
# # # # # # # #         worksheet = writer.sheets[room.name]
# # # # # # # #         header_format = workbook.add_format({'bold': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
        
# # # # # # # #         for col_num, value in enumerate(df.columns.values):
# # # # # # # #             worksheet.write(0, col_num, value, header_format)

# # # # # # # #         for idx in range(len(df.columns)):
# # # # # # # #             series = df.iloc[:, idx]
            
# # # # # # # #             data_max_len = series.astype(str).map(len).max()
# # # # # # # #             if pd.isna(data_max_len):
# # # # # # # #                 data_max_len = 0

# # # # # # # #             header_len = len(str(df.columns[idx]))
            
# # # # # # # #             final_width = max(int(data_max_len), header_len) + 2
            
# # # # # # # #             worksheet.set_column(idx, idx, final_width)

# # # # # # # #     output.seek(0)
    
# # # # # # # #     response = HttpResponse(
# # # # # # # #         output,
# # # # # # # #         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
# # # # # # # #     )
# # # # # # # #     response['Content-Disposition'] = f'attachment; filename="seating_plan_{room.name}.xlsx"'
    
# # # # # # # #     return response















# # # # # # # # attendance/views.py

# # # # # # # from django.shortcuts import render, get_object_or_404, redirect
# # # # # # # from django.http import HttpResponse, JsonResponse, Http404
# # # # # # # from django.views.decorators.csrf import csrf_exempt
# # # # # # # from django.contrib import messages
# # # # # # # from django.contrib.auth.decorators import login_required
# # # # # # # from collections import defaultdict
# # # # # # # import json
# # # # # # # import pandas as pd
# # # # # # # import io

# # # # # # # from .models import Room, Student, Bench, Absentee, InvigilatorAssignment

# # # # # # # @login_required
# # # # # # # def room_list(request):
# # # # # # #     if request.user.is_staff:
# # # # # # #         # Admins see all rooms
# # # # # # #         rooms = Room.objects.all()
# # # # # # #     else:
# # # # # # #         # Invigilators only see rooms they are assigned to
# # # # # # #         assigned_room_ids = InvigilatorAssignment.objects.filter(invigilator=request.user).values_list('room_id', flat=True)
# # # # # # #         rooms = Room.objects.filter(id__in=assigned_room_ids)
        
# # # # # # #     return render(request, 'attendance/room_list.html', {'rooms': rooms})

# # # # # # # @login_required
# # # # # # # def seating_plan_view(request, room_id):
# # # # # # #     room = get_object_or_404(Room, pk=room_id)
    
# # # # # # #     start_col, end_col = 1, room.columns
    
# # # # # # #     if not request.user.is_staff:
# # # # # # #         try:
# # # # # # #             assignment = InvigilatorAssignment.objects.get(invigilator=request.user, room=room)
# # # # # # #             start_col = assignment.start_column
# # # # # # #             end_col = assignment.end_column
# # # # # # #         except InvigilatorAssignment.DoesNotExist:
# # # # # # #             # If a non-staff user tries to access a room they aren't assigned to
# # # # # # #             raise Http404("You are not assigned to this room.")

# # # # # # #     benches = Bench.objects.filter(
# # # # # # #         room=room, 
# # # # # # #         col_num__gte=start_col, 
# # # # # # #         col_num__lte=end_col
# # # # # # #     ).order_by('col_num', 'row_num')
    
# # # # # # #     # Adjust the plan grid to only include the assigned number of columns
# # # # # # #     num_display_columns = (end_col - start_col) + 1
# # # # # # #     plan = [[] for _ in range(num_display_columns)]
    
# # # # # # #     for bench in benches:
# # # # # # #         students_on_bench = list(bench.students.all())
# # # # # # #         seats = []
# # # # # # #         for i in range(room.students_per_bench):
# # # # # # #             if i < len(students_on_bench):
# # # # # # #                 seats.append(students_on_bench[i])
# # # # # # #             else:
# # # # # # #                 seats.append(None)
# # # # # # #         bench.seats = seats
# # # # # # #         # Adjust the index for the plan grid
# # # # # # #         plan_col_index = bench.col_num - start_col
# # # # # # #         plan[plan_col_index].append(bench)
        
# # # # # # #     context = {
# # # # # # #         'room': room,
# # # # # # #         'plan': plan,
# # # # # # #         'start_col': start_col,
# # # # # # #     }
# # # # # # #     return render(request, 'attendance/seating_plan.html', context)

# # # # # # # @csrf_exempt
# # # # # # # @login_required
# # # # # # # def save_absentees(request):
# # # # # # #     # This view is now also protected by the logic in seating_plan_view,
# # # # # # #     # as an invigilator cannot even see students outside their assigned columns.
# # # # # # #     # ... (rest of the view is the same)
# # # # # # #     if request.method == 'POST':
# # # # # # #         data = json.loads(request.body)
# # # # # # #         room_id = data.get('room_id')
# # # # # # #         absent_ids = data.get('absent_ids', [])

# # # # # # #         if not room_id:
# # # # # # #             return JsonResponse({'status': 'error', 'message': 'Missing room_id'}, status=400)
        
# # # # # # #         try:
# # # # # # #             room = Room.objects.get(id=room_id)
# # # # # # #             Absentee.objects.filter(room=room).delete()

# # # # # # #             for student_id in absent_ids:
# # # # # # #                 student = Student.objects.get(student_id=student_id)
# # # # # # #                 Absentee.objects.get_or_create(room=room, student=student)
            
# # # # # # #             return JsonResponse({'status': 'success', 'message': f'{len(absent_ids)} absentees recorded for {room.name}.'})
# # # # # # #         except (Student.DoesNotExist, Room.DoesNotExist):
# # # # # # #             return JsonResponse({'status': 'error', 'message': 'Invalid student or room ID found.'}, status=404)
            
# # # # # # #     return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# # # # # # # # ... (The rest of the views: upload_students, auto_arrange_seating, download_report, download_seating_plan remain the same,
# # # # # # # # but are now protected by the login_required decorator and the is_staff check at the beginning of each function)
# # # # # # # @login_required
# # # # # # # def upload_students(request):
# # # # # # #     if not request.user.is_staff: return redirect('room_list')
# # # # # # #     # ... (rest of the view is the same)
# # # # # # #     if request.method == 'POST':
# # # # # # #         excel_file = request.FILES.get('excel_file')
# # # # # # #         if not excel_file or not excel_file.name.endswith('.xlsx'):
# # # # # # #             messages.error(request, 'Please upload a valid .xlsx file.')
# # # # # # #             return redirect('upload_students')
        
# # # # # # #         try:
# # # # # # #             df = pd.read_excel(excel_file)
# # # # # # #             required_cols = ['StudentID', 'Batch']
# # # # # # #             if not all(col in df.columns for col in required_cols):
# # # # # # #                 messages.error(request, "Excel file must have columns named 'StudentID' and 'Batch'.")
# # # # # # #                 return redirect('upload_students')

# # # # # # #             created_count = 0
# # # # # # #             for index, row in df.iterrows():
# # # # # # #                 sid = str(row['StudentID'])
# # # # # # #                 batch_name = str(row['Batch'])
                
# # # # # # #                 student, created = Student.objects.update_or_create(
# # # # # # #                     student_id=sid,
# # # # # # #                     defaults={'batch': batch_name}
# # # # # # #                 )
# # # # # # #                 if created:
# # # # # # #                     created_count += 1
            
# # # # # # #             messages.success(request, f'Successfully processed file. Added {created_count} new students.')
# # # # # # #             return redirect('room_list')

# # # # # # #         except Exception as e:
# # # # # # #             messages.error(request, f'An error occurred: {e}')
# # # # # # #             return redirect('upload_students')

# # # # # # #     return render(request, 'attendance/upload_students.html')

# # # # # # # @login_required
# # # # # # # def auto_arrange_seating(request, room_id):
# # # # # # #     if not request.user.is_staff: return redirect('room_list')
# # # # # # #     # ... (rest of the view is the same)
# # # # # # #     room_to_arrange = get_object_or_404(Room, pk=room_id)
    
# # # # # # #     seated_students_ids = Bench.objects.values_list('students', flat=True)
# # # # # # #     students_to_seat = Student.objects.exclude(id__in=seated_students_ids).order_by('id')

# # # # # # #     if not students_to_seat:
# # # # # # #         messages.warning(request, 'No unseated students available to arrange.')
# # # # # # #         return redirect('room_list')

# # # # # # #     Bench.objects.filter(room=room_to_arrange).delete()

# # # # # # #     students_by_batch = defaultdict(list)
# # # # # # #     for student in students_to_seat:
# # # # # # #         students_by_batch[student.batch].append(student)

# # # # # # #     batch_names = sorted(students_by_batch.keys())
    
# # # # # # #     if len(batch_names) < 2:
# # # # # # #         messages.warning(request, 'Seating arrangement requires at least two batches of students.')
# # # # # # #         return redirect('room_list')
        
# # # # # # #     if room_to_arrange.id % 2 != 0:
# # # # # # #         batch_order = batch_names
# # # # # # #     else:
# # # # # # #         batch_order = list(reversed(batch_names))

# # # # # # #     seated_count = 0
# # # # # # #     total_virtual_columns = room_to_arrange.columns * room_to_arrange.students_per_bench

# # # # # # #     for virtual_col_idx in range(total_virtual_columns):
# # # # # # #         batch_to_pick_name = batch_order[virtual_col_idx % len(batch_order)]
        
# # # # # # #         real_bench_col = (virtual_col_idx // room_to_arrange.students_per_bench) + 1
        
# # # # # # #         for r in range(1, room_to_arrange.benches_per_column + 1):
# # # # # # #             if students_by_batch[batch_to_pick_name]:
# # # # # # #                 student = students_by_batch[batch_to_pick_name].pop(0)
                
# # # # # # #                 bench, _ = Bench.objects.get_or_create(room=room_to_arrange, row_num=r, col_num=real_bench_col)
# # # # # # #                 bench.students.add(student)
# # # # # # #                 seated_count += 1
# # # # # # #             else:
# # # # # # #                 break
            
# # # # # # #     messages.success(request, f'Successfully arranged {seated_count} students in {room_to_arrange.name}.')
# # # # # # #     return redirect('room_list')

# # # # # # # @login_required
# # # # # # # def download_report(request):
# # # # # # #     if not request.user.is_staff: return redirect('room_list')
# # # # # # #     # ... (rest of the view is the same)
# # # # # # #     absentees = Absentee.objects.select_related('room', 'student').order_by('room__name', 'student__batch')

# # # # # # #     detailed_data = defaultdict(lambda: defaultdict(list))
# # # # # # #     for ab in absentees:
# # # # # # #         detailed_data[ab.room.name][ab.student.batch].append(ab.student.student_id)

# # # # # # #     detailed_rows = []
# # # # # # #     for room_name, batches in detailed_data.items():
# # # # # # #         for batch_name, student_ids in batches.items():
# # # # # # #             detailed_rows.append({
# # # # # # #                 'Room Number': room_name,
# # # # # # #                 'Batch': batch_name,
# # # # # # #                 'Absentees': ', '.join(student_ids)
# # # # # # #             })
    
# # # # # # #     df1 = pd.DataFrame(detailed_rows)

# # # # # # #     summary_data = defaultdict(int)
# # # # # # #     for ab in absentees:
# # # # # # #         summary_data[ab.student.batch] += 1
    
# # # # # # #     summary_rows = [{'Batch': batch, 'Absentees Count': count} for batch, count in summary_data.items()]
# # # # # # #     df2 = pd.DataFrame(summary_rows)

# # # # # # #     output = io.BytesIO()
# # # # # # #     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
# # # # # # #         df1.to_excel(writer, sheet_name='Detailed Report', index=False)
# # # # # # #         df2.to_excel(writer, sheet_name='Consolidated Report', index=False)

# # # # # # #         workbook = writer.book
# # # # # # #         worksheet = writer.sheets['Detailed Report']
        
# # # # # # #         header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
# # # # # # #         for col_num, value in enumerate(df1.columns.values):
# # # # # # #             worksheet.write(0, col_num, value, header_format)

# # # # # # #         if not df1.empty:
# # # # # # #             merge_start_row = 1
# # # # # # #             for i in range(1, len(df1)):
# # # # # # #                 if df1.iloc[i]['Room Number'] != df1.iloc[i-1]['Room Number']:
# # # # # # #                     if merge_start_row < i:
# # # # # # #                         worksheet.merge_range(merge_start_row, 0, i, 0, df1.iloc[i-1]['Room Number'])
# # # # # # #                     merge_start_row = i + 1
# # # # # # #             worksheet.merge_range(merge_start_row, 0, len(df1), 0, df1.iloc[-1]['Room Number'])

# # # # # # #     output.seek(0)
    
# # # # # # #     response = HttpResponse(
# # # # # # #         output,
# # # # # # #         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
# # # # # # #     )
# # # # # # #     response['Content-Disposition'] = 'attachment; filename="absentee_report.xlsx"'
    
# # # # # # #     return response

# # # # # # # @login_required
# # # # # # # def download_seating_plan(request, room_id):
# # # # # # #     if not request.user.is_staff: return redirect('room_list')
# # # # # # #     # ... (rest of the view is the same)
# # # # # # #     room = get_object_or_404(Room, pk=room_id)
# # # # # # #     benches = Bench.objects.filter(room=room).prefetch_related('students').order_by('row_num', 'col_num')

# # # # # # #     batch_names = sorted(list(Student.objects.values_list('batch', flat=True).distinct()))
    
# # # # # # #     if len(batch_names) < 2:
# # # # # # #         batch_order = batch_names
# # # # # # #     elif room.id % 2 != 0:
# # # # # # #         batch_order = batch_names
# # # # # # #     else:
# # # # # # #         batch_order = list(reversed(batch_names))

# # # # # # #     headers = []
# # # # # # #     total_virtual_columns = room.columns * room.students_per_bench
# # # # # # #     for virtual_col_idx in range(total_virtual_columns):
# # # # # # #         if batch_order:
# # # # # # #             batch_name = batch_order[virtual_col_idx % len(batch_order)]
# # # # # # #             headers.append(batch_name)
# # # # # # #         else:
# # # # # # #             headers.append(f'Seat {virtual_col_idx + 1}')

# # # # # # #     num_rows = room.benches_per_column
# # # # # # #     plan_data = [['' for _ in range(total_virtual_columns)] for _ in range(num_rows)]

# # # # # # #     for bench in benches:
# # # # # # #         students_on_bench = list(bench.students.all())
# # # # # # #         start_col = (bench.col_num - 1) * room.students_per_bench
# # # # # # #         for i, student in enumerate(students_on_bench):
# # # # # # #             if start_col + i < len(plan_data[bench.row_num - 1]):
# # # # # # #                 plan_data[bench.row_num - 1][start_col + i] = student.student_id

# # # # # # #     df = pd.DataFrame(plan_data, columns=headers)

# # # # # # #     output = io.BytesIO()
# # # # # # #     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
# # # # # # #         df.to_excel(writer, sheet_name=room.name, index=False, header=True)
        
# # # # # # #         workbook = writer.book
# # # # # # #         worksheet = writer.sheets[room.name]
# # # # # # #         header_format = workbook.add_format({'bold': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
        
# # # # # # #         for col_num, value in enumerate(df.columns.values):
# # # # # # #             worksheet.write(0, col_num, value, header_format)

# # # # # # #         for idx in range(len(df.columns)):
# # # # # # #             series = df.iloc[:, idx]
            
# # # # # # #             data_max_len = series.astype(str).map(len).max()
# # # # # # #             if pd.isna(data_max_len):
# # # # # # #                 data_max_len = 0

# # # # # # #             header_len = len(str(df.columns[idx]))
            
# # # # # # #             final_width = max(int(data_max_len), header_len) + 2
            
# # # # # # #             worksheet.set_column(idx, idx, final_width)

# # # # # # #     output.seek(0)
    
# # # # # # #     response = HttpResponse(
# # # # # # #         output,
# # # # # # #         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
# # # # # # #     )
# # # # # # #     response['Content-Disposition'] = f'attachment; filename="seating_plan_{room.name}.xlsx"'
    
# # # # # # #     return response











# # # # # # # attendance/views.py

# # # # # # from django.shortcuts import render, get_object_or_404, redirect
# # # # # # from django.http import HttpResponse, JsonResponse, Http404
# # # # # # from django.views.decorators.csrf import csrf_exempt
# # # # # # from django.contrib import messages
# # # # # # from django.contrib.auth.decorators import login_required
# # # # # # from collections import defaultdict
# # # # # # import json
# # # # # # import pandas as pd
# # # # # # import io

# # # # # # from .models import Room, Student, Bench, Absentee, InvigilatorAssignment

# # # # # # @login_required
# # # # # # def room_list(request):
# # # # # #     if request.user.is_staff:
# # # # # #         # Admins see all rooms
# # # # # #         rooms = Room.objects.all()
# # # # # #     else:
# # # # # #         # Invigilators only see rooms they are assigned to.
# # # # # #         # Using invigilator_id=request.user.id is more explicit and robust.
# # # # # #         assigned_room_ids = InvigilatorAssignment.objects.filter(
# # # # # #             invigilator_id=request.user.id
# # # # # #         ).values_list('room_id', flat=True)
# # # # # #         rooms = Room.objects.filter(id__in=assigned_room_ids)
        
# # # # # #     return render(request, 'attendance/room_list.html', {'rooms': rooms})

# # # # # # @login_required
# # # # # # def seating_plan_view(request, room_id):
# # # # # #     room = get_object_or_404(Room, pk=room_id)
    
# # # # # #     start_col, end_col = 1, room.columns
    
# # # # # #     if not request.user.is_staff:
# # # # # #         try:
# # # # # #             assignment = InvigilatorAssignment.objects.get(invigilator=request.user, room=room)
# # # # # #             start_col = assignment.start_column
# # # # # #             end_col = assignment.end_column
# # # # # #         except InvigilatorAssignment.DoesNotExist:
# # # # # #             # If a non-staff user tries to access a room they aren't assigned to
# # # # # #             raise Http404("You are not assigned to this room.")

# # # # # #     benches = Bench.objects.filter(
# # # # # #         room=room, 
# # # # # #         col_num__gte=start_col, 
# # # # # #         col_num__lte=end_col
# # # # # #     ).order_by('col_num', 'row_num')
    
# # # # # #     num_display_columns = (end_col - start_col) + 1
# # # # # #     plan = [[] for _ in range(num_display_columns)]
    
# # # # # #     for bench in benches:
# # # # # #         students_on_bench = list(bench.students.all())
# # # # # #         seats = []
# # # # # #         for i in range(room.students_per_bench):
# # # # # #             if i < len(students_on_bench):
# # # # # #                 seats.append(students_on_bench[i])
# # # # # #             else:
# # # # # #                 seats.append(None)
# # # # # #         bench.seats = seats
# # # # # #         plan_col_index = bench.col_num - start_col
# # # # # #         plan[plan_col_index].append(bench)
        
# # # # # #     context = {
# # # # # #         'room': room,
# # # # # #         'plan': plan,
# # # # # #         'start_col': start_col,
# # # # # #     }
# # # # # #     return render(request, 'attendance/seating_plan.html', context)

# # # # # # @csrf_exempt
# # # # # # @login_required
# # # # # # def save_absentees(request):
# # # # # #     if request.method == 'POST':
# # # # # #         data = json.loads(request.body)
# # # # # #         room_id = data.get('room_id')
# # # # # #         absent_ids = data.get('absent_ids', [])

# # # # # #         if not room_id:
# # # # # #             return JsonResponse({'status': 'error', 'message': 'Missing room_id'}, status=400)
        
# # # # # #         try:
# # # # # #             room = Room.objects.get(id=room_id)
# # # # # #             Absentee.objects.filter(room=room).delete()

# # # # # #             for student_id in absent_ids:
# # # # # #                 student = Student.objects.get(student_id=student_id)
# # # # # #                 Absentee.objects.get_or_create(room=room, student=student)
            
# # # # # #             return JsonResponse({'status': 'success', 'message': f'{len(absent_ids)} absentees recorded for {room.name}.'})
# # # # # #         except (Student.DoesNotExist, Room.DoesNotExist):
# # # # # #             return JsonResponse({'status': 'error', 'message': 'Invalid student or room ID found.'}, status=404)
            
# # # # # #     return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# # # # # # @login_required
# # # # # # def upload_students(request):
# # # # # #     if not request.user.is_staff: return redirect('room_list')
# # # # # #     if request.method == 'POST':
# # # # # #         excel_file = request.FILES.get('excel_file')
# # # # # #         if not excel_file or not excel_file.name.endswith('.xlsx'):
# # # # # #             messages.error(request, 'Please upload a valid .xlsx file.')
# # # # # #             return redirect('upload_students')
        
# # # # # #         try:
# # # # # #             df = pd.read_excel(excel_file)
# # # # # #             required_cols = ['StudentID', 'Batch']
# # # # # #             if not all(col in df.columns for col in required_cols):
# # # # # #                 messages.error(request, "Excel file must have columns named 'StudentID' and 'Batch'.")
# # # # # #                 return redirect('upload_students')

# # # # # #             created_count = 0
# # # # # #             for index, row in df.iterrows():
# # # # # #                 sid = str(row['StudentID'])
# # # # # #                 batch_name = str(row['Batch'])
                
# # # # # #                 student, created = Student.objects.update_or_create(
# # # # # #                     student_id=sid,
# # # # # #                     defaults={'batch': batch_name}
# # # # # #                 )
# # # # # #                 if created:
# # # # # #                     created_count += 1
            
# # # # # #             messages.success(request, f'Successfully processed file. Added {created_count} new students.')
# # # # # #             return redirect('room_list')

# # # # # #         except Exception as e:
# # # # # #             messages.error(request, f'An error occurred: {e}')
# # # # # #             return redirect('upload_students')

# # # # # #     return render(request, 'attendance/upload_students.html')

# # # # # # @login_required
# # # # # # def auto_arrange_seating(request, room_id):
# # # # # #     if not request.user.is_staff: return redirect('room_list')
# # # # # #     room_to_arrange = get_object_or_404(Room, pk=room_id)
    
# # # # # #     seated_students_ids = Bench.objects.values_list('students', flat=True)
# # # # # #     students_to_seat = Student.objects.exclude(id__in=seated_students_ids).order_by('id')

# # # # # #     if not students_to_seat:
# # # # # #         messages.warning(request, 'No unseated students available to arrange.')
# # # # # #         return redirect('room_list')

# # # # # #     Bench.objects.filter(room=room_to_arrange).delete()

# # # # # #     students_by_batch = defaultdict(list)
# # # # # #     for student in students_to_seat:
# # # # # #         students_by_batch[student.batch].append(student)

# # # # # #     batch_names = sorted(students_by_batch.keys())
    
# # # # # #     if len(batch_names) < 2:
# # # # # #         messages.warning(request, 'Seating arrangement requires at least two batches of students.')
# # # # # #         return redirect('room_list')
        
# # # # # #     if room_to_arrange.id % 2 != 0:
# # # # # #         batch_order = batch_names
# # # # # #     else:
# # # # # #         batch_order = list(reversed(batch_names))

# # # # # #     seated_count = 0
# # # # # #     total_virtual_columns = room_to_arrange.columns * room_to_arrange.students_per_bench

# # # # # #     for virtual_col_idx in range(total_virtual_columns):
# # # # # #         batch_to_pick_name = batch_order[virtual_col_idx % len(batch_order)]
        
# # # # # #         real_bench_col = (virtual_col_idx // room_to_arrange.students_per_bench) + 1
        
# # # # # #         for r in range(1, room_to_arrange.benches_per_column + 1):
# # # # # #             if students_by_batch[batch_to_pick_name]:
# # # # # #                 student = students_by_batch[batch_to_pick_name].pop(0)
                
# # # # # #                 bench, _ = Bench.objects.get_or_create(room=room_to_arrange, row_num=r, col_num=real_bench_col)
# # # # # #                 bench.students.add(student)
# # # # # #                 seated_count += 1
# # # # # #             else:
# # # # # #                 break
            
# # # # # #     messages.success(request, f'Successfully arranged {seated_count} students in {room_to_arrange.name}.')
# # # # # #     return redirect('room_list')

# # # # # # @login_required
# # # # # # def download_report(request):
# # # # # #     if not request.user.is_staff: return redirect('room_list')
# # # # # #     absentees = Absentee.objects.select_related('room', 'student').order_by('room__name', 'student__batch')

# # # # # #     detailed_data = defaultdict(lambda: defaultdict(list))
# # # # # #     for ab in absentees:
# # # # # #         detailed_data[ab.room.name][ab.student.batch].append(ab.student.student_id)

# # # # # #     detailed_rows = []
# # # # # #     for room_name, batches in detailed_data.items():
# # # # # #         for batch_name, student_ids in batches.items():
# # # # # #             detailed_rows.append({
# # # # # #                 'Room Number': room_name,
# # # # # #                 'Batch': batch_name,
# # # # # #                 'Absentees': ', '.join(student_ids)
# # # # # #             })
    
# # # # # #     df1 = pd.DataFrame(detailed_rows)

# # # # # #     summary_data = defaultdict(int)
# # # # # #     for ab in absentees:
# # # # # #         summary_data[ab.student.batch] += 1
    
# # # # # #     summary_rows = [{'Batch': batch, 'Absentees Count': count} for batch, count in summary_data.items()]
# # # # # #     df2 = pd.DataFrame(summary_rows)

# # # # # #     output = io.BytesIO()
# # # # # #     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
# # # # # #         df1.to_excel(writer, sheet_name='Detailed Report', index=False)
# # # # # #         df2.to_excel(writer, sheet_name='Consolidated Report', index=False)

# # # # # #         workbook = writer.book
# # # # # #         worksheet = writer.sheets['Detailed Report']
        
# # # # # #         header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
# # # # # #         for col_num, value in enumerate(df1.columns.values):
# # # # # #             worksheet.write(0, col_num, value, header_format)

# # # # # #         if not df1.empty:
# # # # # #             merge_start_row = 1
# # # # # #             for i in range(1, len(df1)):
# # # # # #                 if df1.iloc[i]['Room Number'] != df1.iloc[i-1]['Room Number']:
# # # # # #                     if merge_start_row < i:
# # # # # #                         worksheet.merge_range(merge_start_row, 0, i, 0, df1.iloc[i-1]['Room Number'])
# # # # # #                     merge_start_row = i + 1
# # # # # #             worksheet.merge_range(merge_start_row, 0, len(df1), 0, df1.iloc[-1]['Room Number'])

# # # # # #     output.seek(0)
    
# # # # # #     response = HttpResponse(
# # # # # #         output,
# # # # # #         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
# # # # # #     )
# # # # # #     response['Content-Disposition'] = 'attachment; filename="absentee_report.xlsx"'
    
# # # # # #     return response

# # # # # # @login_required
# # # # # # def download_seating_plan(request, room_id):
# # # # # #     if not request.user.is_staff: return redirect('room_list')
# # # # # #     room = get_object_or_404(Room, pk=room_id)
# # # # # #     benches = Bench.objects.filter(room=room).prefetch_related('students').order_by('row_num', 'col_num')

# # # # # #     batch_names = sorted(list(Student.objects.values_list('batch', flat=True).distinct()))
    
# # # # # #     if len(batch_names) < 2:
# # # # # #         batch_order = batch_names
# # # # # #     elif room.id % 2 != 0:
# # # # # #         batch_order = batch_names
# # # # # #     else:
# # # # # #         batch_order = list(reversed(batch_names))

# # # # # #     headers = []
# # # # # #     total_virtual_columns = room.columns * room.students_per_bench
# # # # # #     for virtual_col_idx in range(total_virtual_columns):
# # # # # #         if batch_order:
# # # # # #             batch_name = batch_order[virtual_col_idx % len(batch_order)]
# # # # # #             headers.append(batch_name)
# # # # # #         else:
# # # # # #             headers.append(f'Seat {virtual_col_idx + 1}')

# # # # # #     num_rows = room.benches_per_column
# # # # # #     plan_data = [['' for _ in range(total_virtual_columns)] for _ in range(num_rows)]

# # # # # #     for bench in benches:
# # # # # #         students_on_bench = list(bench.students.all())
# # # # # #         start_col = (bench.col_num - 1) * room.students_per_bench
# # # # # #         for i, student in enumerate(students_on_bench):
# # # # # #             if start_col + i < len(plan_data[bench.row_num - 1]):
# # # # # #                 plan_data[bench.row_num - 1][start_col + i] = student.student_id

# # # # # #     df = pd.DataFrame(plan_data, columns=headers)

# # # # # #     output = io.BytesIO()
# # # # # #     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
# # # # # #         df.to_excel(writer, sheet_name=room.name, index=False, header=True)
        
# # # # # #         workbook = writer.book
# # # # # #         worksheet = writer.sheets[room.name]
# # # # # #         header_format = workbook.add_format({'bold': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
        
# # # # # #         for col_num, value in enumerate(df.columns.values):
# # # # # #             worksheet.write(0, col_num, value, header_format)

# # # # # #         for idx in range(len(df.columns)):
# # # # # #             series = df.iloc[:, idx]
            
# # # # # #             data_max_len = series.astype(str).map(len).max()
# # # # # #             if pd.isna(data_max_len):
# # # # # #                 data_max_len = 0

# # # # # #             header_len = len(str(df.columns[idx]))
            
# # # # # #             final_width = max(int(data_max_len), header_len) + 2
            
# # # # # #             worksheet.set_column(idx, idx, final_width)

# # # # # #     output.seek(0)
    
# # # # # #     response = HttpResponse(
# # # # # #         output,
# # # # # #         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
# # # # # #     )
# # # # # #     response['Content-Disposition'] = f'attachment; filename="seating_plan_{room.name}.xlsx"'
    
# # # # # #     return response









# # # # # # attendance/views.py

# # # # # from django.shortcuts import render, get_object_or_404, redirect
# # # # # from django.http import HttpResponse, JsonResponse, Http404
# # # # # from django.views.decorators.csrf import csrf_exempt
# # # # # from django.contrib import messages
# # # # # from django.contrib.auth.decorators import login_required
# # # # # from collections import defaultdict
# # # # # import json
# # # # # import pandas as pd
# # # # # import io

# # # # # from .models import Room, Student, Bench, Absentee, InvigilatorAssignment

# # # # # @login_required
# # # # # def room_list(request):
# # # # #     if request.user.is_staff:
# # # # #         # Admins see all rooms
# # # # #         rooms = Room.objects.all()
# # # # #     else:
# # # # #         # Invigilators only see rooms they are assigned to.
# # # # #         # This query is more robust and prevents potential errors.
# # # # #         assigned_room_ids = InvigilatorAssignment.objects.filter(
# # # # #             invigilator_id=request.user.id
# # # # #         ).values_list('room_id', flat=True).distinct()
# # # # #         rooms = Room.objects.filter(id__in=assigned_room_ids)
        
# # # # #     return render(request, 'attendance/room_list.html', {'rooms': rooms})

# # # # # @login_required
# # # # # def seating_plan_view(request, room_id):
# # # # #     room = get_object_or_404(Room, pk=room_id)
    
# # # # #     start_col, end_col = 1, room.columns
    
# # # # #     if not request.user.is_staff:
# # # # #         try:
# # # # #             assignment = InvigilatorAssignment.objects.get(invigilator=request.user, room=room)
# # # # #             start_col = assignment.start_column
# # # # #             end_col = assignment.end_column
# # # # #         except InvigilatorAssignment.DoesNotExist:
# # # # #             raise Http404("You are not assigned to this room.")

# # # # #     benches = Bench.objects.filter(
# # # # #         room=room, 
# # # # #         col_num__gte=start_col, 
# # # # #         col_num__lte=end_col
# # # # #     ).order_by('col_num', 'row_num')
    
# # # # #     num_display_columns = (end_col - start_col) + 1
# # # # #     plan = [[] for _ in range(num_display_columns)]
    
# # # # #     for bench in benches:
# # # # #         students_on_bench = list(bench.students.all())
# # # # #         seats = []
# # # # #         for i in range(room.students_per_bench):
# # # # #             if i < len(students_on_bench):
# # # # #                 seats.append(students_on_bench[i])
# # # # #             else:
# # # # #                 seats.append(None)
# # # # #         bench.seats = seats
# # # # #         plan_col_index = bench.col_num - start_col
# # # # #         plan[plan_col_index].append(bench)
        
# # # # #     context = {
# # # # #         'room': room,
# # # # #         'plan': plan,
# # # # #         'start_col': start_col,
# # # # #     }
# # # # #     return render(request, 'attendance/seating_plan.html', context)

# # # # # @csrf_exempt
# # # # # @login_required
# # # # # def save_absentees(request):
# # # # #     if request.method == 'POST':
# # # # #         data = json.loads(request.body)
# # # # #         room_id = data.get('room_id')
# # # # #         absent_ids = data.get('absent_ids', [])

# # # # #         if not room_id:
# # # # #             return JsonResponse({'status': 'error', 'message': 'Missing room_id'}, status=400)
        
# # # # #         try:
# # # # #             room = Room.objects.get(id=room_id)
# # # # #             Absentee.objects.filter(room=room).delete()

# # # # #             for student_id in absent_ids:
# # # # #                 student = Student.objects.get(student_id=student_id)
# # # # #                 Absentee.objects.get_or_create(room=room, student=student)
            
# # # # #             return JsonResponse({'status': 'success', 'message': f'{len(absent_ids)} absentees recorded for {room.name}.'})
# # # # #         except (Student.DoesNotExist, Room.DoesNotExist):
# # # # #             return JsonResponse({'status': 'error', 'message': 'Invalid student or room ID found.'}, status=404)
            
# # # # #     return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# # # # # @login_required
# # # # # def upload_students(request):
# # # # #     if not request.user.is_staff: return redirect('room_list')
# # # # #     if request.method == 'POST':
# # # # #         excel_file = request.FILES.get('excel_file')
# # # # #         if not excel_file or not excel_file.name.endswith('.xlsx'):
# # # # #             messages.error(request, 'Please upload a valid .xlsx file.')
# # # # #             return redirect('upload_students')
        
# # # # #         try:
# # # # #             df = pd.read_excel(excel_file)
# # # # #             required_cols = ['StudentID', 'Batch']
# # # # #             if not all(col in df.columns for col in required_cols):
# # # # #                 messages.error(request, "Excel file must have columns named 'StudentID' and 'Batch'.")
# # # # #                 return redirect('upload_students')

# # # # #             created_count = 0
# # # # #             for index, row in df.iterrows():
# # # # #                 sid = str(row['StudentID'])
# # # # #                 batch_name = str(row['Batch'])
                
# # # # #                 student, created = Student.objects.update_or_create(
# # # # #                     student_id=sid,
# # # # #                     defaults={'batch': batch_name}
# # # # #                 )
# # # # #                 if created:
# # # # #                     created_count += 1
            
# # # # #             messages.success(request, f'Successfully processed file. Added {created_count} new students.')
# # # # #             return redirect('room_list')

# # # # #         except Exception as e:
# # # # #             messages.error(request, f'An error occurred: {e}')
# # # # #             return redirect('upload_students')

# # # # #     return render(request, 'attendance/upload_students.html')

# # # # # @login_required
# # # # # def auto_arrange_seating(request, room_id):
# # # # #     if not request.user.is_staff: return redirect('room_list')
# # # # #     room_to_arrange = get_object_or_404(Room, pk=room_id)
    
# # # # #     seated_students_ids = Bench.objects.values_list('students', flat=True)
# # # # #     students_to_seat = Student.objects.exclude(id__in=seated_students_ids).order_by('id')

# # # # #     if not students_to_seat:
# # # # #         messages.warning(request, 'No unseated students available to arrange.')
# # # # #         return redirect('room_list')

# # # # #     Bench.objects.filter(room=room_to_arrange).delete()

# # # # #     students_by_batch = defaultdict(list)
# # # # #     for student in students_to_seat:
# # # # #         students_by_batch[student.batch].append(student)

# # # # #     batch_names = sorted(students_by_batch.keys())
    
# # # # #     if len(batch_names) < 2:
# # # # #         messages.warning(request, 'Seating arrangement requires at least two batches of students.')
# # # # #         return redirect('room_list')
        
# # # # #     if room_to_arrange.id % 2 != 0:
# # # # #         batch_order = batch_names
# # # # #     else:
# # # # #         batch_order = list(reversed(batch_names))

# # # # #     seated_count = 0
# # # # #     total_virtual_columns = room_to_arrange.columns * room_to_arrange.students_per_bench

# # # # #     for virtual_col_idx in range(total_virtual_columns):
# # # # #         batch_to_pick_name = batch_order[virtual_col_idx % len(batch_order)]
        
# # # # #         real_bench_col = (virtual_col_idx // room_to_arrange.students_per_bench) + 1
        
# # # # #         for r in range(1, room_to_arrange.benches_per_column + 1):
# # # # #             if students_by_batch[batch_to_pick_name]:
# # # # #                 student = students_by_batch[batch_to_pick_name].pop(0)
                
# # # # #                 bench, _ = Bench.objects.get_or_create(room=room_to_arrange, row_num=r, col_num=real_bench_col)
# # # # #                 bench.students.add(student)
# # # # #                 seated_count += 1
# # # # #             else:
# # # # #                 break
            
# # # # #     messages.success(request, f'Successfully arranged {seated_count} students in {room_to_arrange.name}.')
# # # # #     return redirect('room_list')

# # # # # @login_required
# # # # # def download_report(request):
# # # # #     if not request.user.is_staff: return redirect('room_list')
# # # # #     absentees = Absentee.objects.select_related('room', 'student').order_by('room__name', 'student__batch')

# # # # #     detailed_data = defaultdict(lambda: defaultdict(list))
# # # # #     for ab in absentees:
# # # # #         detailed_data[ab.room.name][ab.student.batch].append(ab.student.student_id)

# # # # #     detailed_rows = []
# # # # #     for room_name, batches in detailed_data.items():
# # # # #         for batch_name, student_ids in batches.items():
# # # # #             detailed_rows.append({
# # # # #                 'Room Number': room_name,
# # # # #                 'Batch': batch_name,
# # # # #                 'Absentees': ', '.join(student_ids)
# # # # #             })
    
# # # # #     df1 = pd.DataFrame(detailed_rows)

# # # # #     summary_data = defaultdict(int)
# # # # #     for ab in absentees:
# # # # #         summary_data[ab.student.batch] += 1
    
# # # # #     summary_rows = [{'Batch': batch, 'Absentees Count': count} for batch, count in summary_data.items()]
# # # # #     df2 = pd.DataFrame(summary_rows)

# # # # #     output = io.BytesIO()
# # # # #     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
# # # # #         df1.to_excel(writer, sheet_name='Detailed Report', index=False)
# # # # #         df2.to_excel(writer, sheet_name='Consolidated Report', index=False)

# # # # #         workbook = writer.book
# # # # #         worksheet = writer.sheets['Detailed Report']
        
# # # # #         header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
# # # # #         for col_num, value in enumerate(df1.columns.values):
# # # # #             worksheet.write(0, col_num, value, header_format)

# # # # #         if not df1.empty:
# # # # #             merge_start_row = 1
# # # # #             for i in range(1, len(df1)):
# # # # #                 if df1.iloc[i]['Room Number'] != df1.iloc[i-1]['Room Number']:
# # # # #                     if merge_start_row < i:
# # # # #                         worksheet.merge_range(merge_start_row, 0, i, 0, df1.iloc[i-1]['Room Number'])
# # # # #                     merge_start_row = i + 1
# # # # #             worksheet.merge_range(merge_start_row, 0, len(df1), 0, df1.iloc[-1]['Room Number'])

# # # # #     output.seek(0)
    
# # # # #     response = HttpResponse(
# # # # #         output,
# # # # #         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
# # # # #     )
# # # # #     response['Content-Disposition'] = 'attachment; filename="absentee_report.xlsx"'
    
# # # # #     return response

# # # # # @login_required
# # # # # def download_seating_plan(request, room_id):
# # # # #     if not request.user.is_staff: return redirect('room_list')
# # # # #     room = get_object_or_404(Room, pk=room_id)
# # # # #     benches = Bench.objects.filter(room=room).prefetch_related('students').order_by('row_num', 'col_num')

# # # # #     batch_names = sorted(list(Student.objects.values_list('batch', flat=True).distinct()))
    
# # # # #     if len(batch_names) < 2:
# # # # #         batch_order = batch_names
# # # # #     elif room.id % 2 != 0:
# # # # #         batch_order = batch_names
# # # # #     else:
# # # # #         batch_order = list(reversed(batch_names))

# # # # #     headers = []
# # # # #     total_virtual_columns = room.columns * room.students_per_bench
# # # # #     for virtual_col_idx in range(total_virtual_columns):
# # # # #         if batch_order:
# # # # #             batch_name = batch_order[virtual_col_idx % len(batch_order)]
# # # # #             headers.append(batch_name)
# # # # #         else:
# # # # #             headers.append(f'Seat {virtual_col_idx + 1}')

# # # # #     num_rows = room.benches_per_column
# # # # #     plan_data = [['' for _ in range(total_virtual_columns)] for _ in range(num_rows)]

# # # # #     for bench in benches:
# # # # #         students_on_bench = list(bench.students.all())
# # # # #         start_col = (bench.col_num - 1) * room.students_per_bench
# # # # #         for i, student in enumerate(students_on_bench):
# # # # #             if start_col + i < len(plan_data[bench.row_num - 1]):
# # # # #                 plan_data[bench.row_num - 1][start_col + i] = student.student_id

# # # # #     df = pd.DataFrame(plan_data, columns=headers)

# # # # #     output = io.BytesIO()
# # # # #     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
# # # # #         df.to_excel(writer, sheet_name=room.name, index=False, header=True)
        
# # # # #         workbook = writer.book
# # # # #         worksheet = writer.sheets[room.name]
# # # # #         header_format = workbook.add_format({'bold': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
        
# # # # #         for col_num, value in enumerate(df.columns.values):
# # # # #             worksheet.write(0, col_num, value, header_format)

# # # # #         for idx in range(len(df.columns)):
# # # # #             series = df.iloc[:, idx]
            
# # # # #             data_max_len = series.astype(str).map(len).max()
# # # # #             if pd.isna(data_max_len):
# # # # #                 data_max_len = 0

# # # # #             header_len = len(str(df.columns[idx]))
            
# # # # #             final_width = max(int(data_max_len), header_len) + 2
            
# # # # #             worksheet.set_column(idx, idx, final_width)

# # # # #     output.seek(0)
    
# # # # #     response = HttpResponse(
# # # # #         output,
# # # # #         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
# # # # #     )
# # # # #     response['Content-Disposition'] = f'attachment; filename="seating_plan_{room.name}.xlsx"'
    
# # # # #     return response




















# # # # # attendance/views.py

# # # # from django.shortcuts import render, get_object_or_404, redirect
# # # # from django.http import HttpResponse, JsonResponse, Http404
# # # # from django.views.decorators.csrf import csrf_exempt
# # # # from django.contrib import messages
# # # # from django.contrib.auth.decorators import login_required
# # # # from collections import defaultdict
# # # # import json
# # # # import pandas as pd
# # # # import io

# # # # from .models import Room, Student, Bench, Absentee, InvigilatorAssignment

# # # # @login_required
# # # # def room_list(request):
# # # #     if request.user.is_staff:
# # # #         # Admins see all rooms
# # # #         rooms = Room.objects.all()
# # # #     else:
# # # #         # Invigilators only see rooms they are assigned to.
# # # #         # This query is more robust and prevents potential errors.
# # # #         assigned_room_ids = InvigilatorAssignment.objects.filter(
# # # #             invigilator_id=request.user.id
# # # #         ).values_list('room_id', flat=True).distinct()
# # # #         rooms = Room.objects.filter(id__in=assigned_room_ids)
        
# # # #     return render(request, 'attendance/room_list.html', {'rooms': rooms})

# # # # @login_required
# # # # def seating_plan_view(request, room_id):
# # # #     room = get_object_or_404(Room, pk=room_id)
    
# # # #     start_col, end_col = 1, room.columns
    
# # # #     if not request.user.is_staff:
# # # #         try:
# # # #             assignment = InvigilatorAssignment.objects.get(invigilator=request.user, room=room)
# # # #             start_col = assignment.start_column
# # # #             end_col = assignment.end_column
# # # #         except InvigilatorAssignment.DoesNotExist:
# # # #             raise Http404("You are not assigned to this room.")

# # # #     benches = Bench.objects.filter(
# # # #         room=room, 
# # # #         col_num__gte=start_col, 
# # # #         col_num__lte=end_col
# # # #     ).order_by('col_num', 'row_num')
    
# # # #     num_display_columns = (end_col - start_col) + 1
# # # #     plan = [[] for _ in range(num_display_columns)]
    
# # # #     for bench in benches:
# # # #         students_on_bench = list(bench.students.all())
# # # #         seats = []
# # # #         for i in range(room.students_per_bench):
# # # #             if i < len(students_on_bench):
# # # #                 seats.append(students_on_bench[i])
# # # #             else:
# # # #                 seats.append(None)
# # # #         bench.seats = seats
# # # #         plan_col_index = bench.col_num - start_col
# # # #         plan[plan_col_index].append(bench)
        
# # # #     context = {
# # # #         'room': room,
# # # #         'plan': plan,
# # # #         'start_col': start_col,
# # # #     }
# # # #     return render(request, 'attendance/seating_plan.html', context)

# # # # @csrf_exempt
# # # # @login_required
# # # # def save_absentees(request):
# # # #     if request.method == 'POST':
# # # #         data = json.loads(request.body)
# # # #         room_id = data.get('room_id')
# # # #         absent_ids = data.get('absent_ids', [])

# # # #         if not room_id:
# # # #             return JsonResponse({'status': 'error', 'message': 'Missing room_id'}, status=400)
        
# # # #         try:
# # # #             room = Room.objects.get(id=room_id)
# # # #             Absentee.objects.filter(room=room).delete()

# # # #             for student_id in absent_ids:
# # # #                 student = Student.objects.get(student_id=student_id)
# # # #                 Absentee.objects.get_or_create(room=room, student=student)
            
# # # #             return JsonResponse({'status': 'success', 'message': f'{len(absent_ids)} absentees recorded for {room.name}.'})
# # # #         except (Student.DoesNotExist, Room.DoesNotExist):
# # # #             return JsonResponse({'status': 'error', 'message': 'Invalid student or room ID found.'}, status=404)
            
# # # #     return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# # # # @login_required
# # # # def upload_students(request):
# # # #     if not request.user.is_staff: return redirect('room_list')
# # # #     if request.method == 'POST':
# # # #         excel_file = request.FILES.get('excel_file')
# # # #         if not excel_file or not excel_file.name.endswith('.xlsx'):
# # # #             messages.error(request, 'Please upload a valid .xlsx file.')
# # # #             return redirect('upload_students')
        
# # # #         try:
# # # #             df = pd.read_excel(excel_file)
# # # #             required_cols = ['StudentID', 'Batch']
# # # #             if not all(col in df.columns for col in required_cols):
# # # #                 messages.error(request, "Excel file must have columns named 'StudentID' and 'Batch'.")
# # # #                 return redirect('upload_students')

# # # #             created_count = 0
# # # #             for index, row in df.iterrows():
# # # #                 sid = str(row['StudentID'])
# # # #                 batch_name = str(row['Batch'])
                
# # # #                 student, created = Student.objects.update_or_create(
# # # #                     student_id=sid,
# # # #                     defaults={'batch': batch_name}
# # # #                 )
# # # #                 if created:
# # # #                     created_count += 1
            
# # # #             messages.success(request, f'Successfully processed file. Added {created_count} new students.')
# # # #             return redirect('room_list')

# # # #         except Exception as e:
# # # #             messages.error(request, f'An error occurred: {e}')
# # # #             return redirect('upload_students')

# # # #     return render(request, 'attendance/upload_students.html')

# # # # @login_required
# # # # def auto_arrange_seating(request, room_id):
# # # #     if not request.user.is_staff: return redirect('room_list')
# # # #     room_to_arrange = get_object_or_404(Room, pk=room_id)
    
# # # #     seated_students_ids = Bench.objects.values_list('students', flat=True)
# # # #     students_to_seat = Student.objects.exclude(id__in=seated_students_ids).order_by('id')

# # # #     if not students_to_seat:
# # # #         messages.warning(request, 'No unseated students available to arrange.')
# # # #         return redirect('room_list')

# # # #     Bench.objects.filter(room=room_to_arrange).delete()

# # # #     students_by_batch = defaultdict(list)
# # # #     for student in students_to_seat:
# # # #         students_by_batch[student.batch].append(student)

# # # #     batch_names = sorted(students_by_batch.keys())
    
# # # #     if len(batch_names) < 2:
# # # #         messages.warning(request, 'Seating arrangement requires at least two batches of students.')
# # # #         return redirect('room_list')
        
# # # #     if room_to_arrange.id % 2 != 0:
# # # #         batch_order = batch_names
# # # #     else:
# # # #         batch_order = list(reversed(batch_names))

# # # #     seated_count = 0
# # # #     total_virtual_columns = room_to_arrange.columns * room_to_arrange.students_per_bench

# # # #     for virtual_col_idx in range(total_virtual_columns):
# # # #         batch_to_pick_name = batch_order[virtual_col_idx % len(batch_order)]
        
# # # #         real_bench_col = (virtual_col_idx // room_to_arrange.students_per_bench) + 1
        
# # # #         for r in range(1, room_to_arrange.benches_per_column + 1):
# # # #             if students_by_batch[batch_to_pick_name]:
# # # #                 student = students_by_batch[batch_to_pick_name].pop(0)
                
# # # #                 bench, _ = Bench.objects.get_or_create(room=room_to_arrange, row_num=r, col_num=real_bench_col)
# # # #                 bench.students.add(student)
# # # #                 seated_count += 1
# # # #             else:
# # # #                 break
            
# # # #     messages.success(request, f'Successfully arranged {seated_count} students in {room_to_arrange.name}.')
# # # #     return redirect('room_list')

# # # # @login_required
# # # # def download_report(request):
# # # #     if not request.user.is_staff: return redirect('room_list')
# # # #     absentees = Absentee.objects.select_related('room', 'student').order_by('room__name', 'student__batch')

# # # #     detailed_data = defaultdict(lambda: defaultdict(list))
# # # #     for ab in absentees:
# # # #         detailed_data[ab.room.name][ab.student.batch].append(ab.student.student_id)

# # # #     detailed_rows = []
# # # #     for room_name, batches in detailed_data.items():
# # # #         for batch_name, student_ids in batches.items():
# # # #             detailed_rows.append({
# # # #                 'Room Number': room_name,
# # # #                 'Batch': batch_name,
# # # #                 'Absentees': ', '.join(student_ids)
# # # #             })
    
# # # #     df1 = pd.DataFrame(detailed_rows)

# # # #     summary_data = defaultdict(int)
# # # #     for ab in absentees:
# # # #         summary_data[ab.student.batch] += 1
    
# # # #     summary_rows = [{'Batch': batch, 'Absentees Count': count} for batch, count in summary_data.items()]
# # # #     df2 = pd.DataFrame(summary_rows)

# # # #     output = io.BytesIO()
# # # #     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
# # # #         df1.to_excel(writer, sheet_name='Detailed Report', index=False)
# # # #         df2.to_excel(writer, sheet_name='Consolidated Report', index=False)

# # # #         workbook = writer.book
# # # #         worksheet = writer.sheets['Detailed Report']
        
# # # #         header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
# # # #         for col_num, value in enumerate(df1.columns.values):
# # # #             worksheet.write(0, col_num, value, header_format)

# # # #         if not df1.empty:
# # # #             merge_start_row = 1
# # # #             for i in range(1, len(df1)):
# # # #                 if df1.iloc[i]['Room Number'] != df1.iloc[i-1]['Room Number']:
# # # #                     if merge_start_row < i:
# # # #                         worksheet.merge_range(merge_start_row, 0, i, 0, df1.iloc[i-1]['Room Number'])
# # # #                     merge_start_row = i + 1
# # # #             worksheet.merge_range(merge_start_row, 0, len(df1), 0, df1.iloc[-1]['Room Number'])

# # # #     output.seek(0)
    
# # # #     response = HttpResponse(
# # # #         output,
# # # #         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
# # # #     )
# # # #     response['Content-Disposition'] = 'attachment; filename="absentee_report.xlsx"'
    
# # # #     return response

# # # # @login_required
# # # # def download_seating_plan(request, room_id):
# # # #     if not request.user.is_staff: return redirect('room_list')
# # # #     room = get_object_or_404(Room, pk=room_id)
# # # #     benches = Bench.objects.filter(room=room).prefetch_related('students').order_by('row_num', 'col_num')

# # # #     batch_names = sorted(list(Student.objects.values_list('batch', flat=True).distinct()))
    
# # # #     if len(batch_names) < 2:
# # # #         batch_order = batch_names
# # # #     elif room.id % 2 != 0:
# # # #         batch_order = batch_names
# # # #     else:
# # # #         batch_order = list(reversed(batch_names))

# # # #     headers = []
# # # #     total_virtual_columns = room.columns * room.students_per_bench
# # # #     for virtual_col_idx in range(total_virtual_columns):
# # # #         if batch_order:
# # # #             batch_name = batch_order[virtual_col_idx % len(batch_order)]
# # # #             headers.append(batch_name)
# # # #         else:
# # # #             headers.append(f'Seat {virtual_col_idx + 1}')

# # # #     num_rows = room.benches_per_column
# # # #     plan_data = [['' for _ in range(total_virtual_columns)] for _ in range(num_rows)]

# # # #     for bench in benches:
# # # #         students_on_bench = list(bench.students.all())
# # # #         start_col = (bench.col_num - 1) * room.students_per_bench
# # # #         for i, student in enumerate(students_on_bench):
# # # #             if start_col + i < len(plan_data[bench.row_num - 1]):
# # # #                 plan_data[bench.row_num - 1][start_col + i] = student.student_id

# # # #     df = pd.DataFrame(plan_data, columns=headers)

# # # #     output = io.BytesIO()
# # # #     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
# # # #         df.to_excel(writer, sheet_name=room.name, index=False, header=True)
        
# # # #         workbook = writer.book
# # # #         worksheet = writer.sheets[room.name]
# # # #         header_format = workbook.add_format({'bold': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
        
# # # #         for col_num, value in enumerate(df.columns.values):
# # # #             worksheet.write(0, col_num, value, header_format)

# # # #         for idx in range(len(df.columns)):
# # # #             series = df.iloc[:, idx]
            
# # # #             data_max_len = series.astype(str).map(len).max()
# # # #             if pd.isna(data_max_len):
# # # #                 data_max_len = 0

# # # #             header_len = len(str(df.columns[idx]))
            
# # # #             final_width = max(int(data_max_len), header_len) + 2
            
# # # #             worksheet.set_column(idx, idx, final_width)

# # # #     output.seek(0)
    
# # # #     response = HttpResponse(
# # # #         output,
# # # #         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
# # # #     )
# # # #     response['Content-Disposition'] = f'attachment; filename="seating_plan_{room.name}.xlsx"'
    
# # # #     return response










# # # # attendance/views.py

# # # from django.shortcuts import render, get_object_or_404, redirect
# # # from django.http import HttpResponse, JsonResponse, Http404
# # # from django.views.decorators.csrf import csrf_exempt
# # # from django.contrib import messages
# # # from django.contrib.auth.decorators import login_required
# # # from django.contrib.auth import login
# # # from django.contrib.auth.forms import AuthenticationForm
# # # from collections import defaultdict
# # # import json
# # # import pandas as pd
# # # import io

# # # from .models import Room, Student, Bench, Absentee, InvigilatorAssignment

# # # def landing_page(request):
# # #     if request.user.is_authenticated:
# # #         return redirect('dashboard') # Redirect to dashboard if already logged in

# # #     if request.method == 'POST':
# # #         form = AuthenticationForm(request, data=request.POST)
# # #         if form.is_valid():
# # #             user = form.get_user()
# # #             login(request, user)
# # #             return redirect('dashboard')
# # #     else:
# # #         form = AuthenticationForm()
# # #     return render(request, 'attendance/landing_page.html', {'form': form})

# # # @login_required
# # # def dashboard(request): # Renamed from room_list
# # #     if request.user.is_staff:
# # #         rooms = Room.objects.all()
# # #     else:
# # #         assigned_room_ids = InvigilatorAssignment.objects.filter(
# # #             invigilator_id=request.user.id
# # #         ).values_list('room_id', flat=True).distinct()
# # #         rooms = Room.objects.filter(id__in=assigned_room_ids)
        
# # #     return render(request, 'attendance/dashboard.html', {'rooms': rooms})

# # # @login_required
# # # def seating_plan_view(request, room_id):
# # #     room = get_object_or_404(Room, pk=room_id)
    
# # #     start_col, end_col = 1, room.columns
    
# # #     if not request.user.is_staff:
# # #         try:
# # #             assignment = InvigilatorAssignment.objects.get(invigilator=request.user, room=room)
# # #             start_col = assignment.start_column
# # #             end_col = assignment.end_column
# # #         except InvigilatorAssignment.DoesNotExist:
# # #             raise Http404("You are not assigned to this room.")

# # #     benches = Bench.objects.filter(
# # #         room=room, 
# # #         col_num__gte=start_col, 
# # #         col_num__lte=end_col
# # #     ).order_by('col_num', 'row_num')
    
# # #     num_display_columns = (end_col - start_col) + 1
# # #     plan = [[] for _ in range(num_display_columns)]
    
# # #     for bench in benches:
# # #         students_on_bench = list(bench.students.all())
# # #         seats = []
# # #         for i in range(room.students_per_bench):
# # #             if i < len(students_on_bench):
# # #                 seats.append(students_on_bench[i])
# # #             else:
# # #                 seats.append(None)
# # #         bench.seats = seats
# # #         plan_col_index = bench.col_num - start_col
# # #         plan[plan_col_index].append(bench)
        
# # #     context = {
# # #         'room': room,
# # #         'plan': plan,
# # #         'start_col': start_col,
# # #     }
# # #     return render(request, 'attendance/seating_plan.html', context)

# # # @csrf_exempt
# # # @login_required
# # # def save_absentees(request):
# # #     if request.method == 'POST':
# # #         data = json.loads(request.body)
# # #         room_id = data.get('room_id')
# # #         absent_ids = data.get('absent_ids', [])

# # #         if not room_id:
# # #             return JsonResponse({'status': 'error', 'message': 'Missing room_id'}, status=400)
        
# # #         try:
# # #             room = Room.objects.get(id=room_id)
# # #             Absentee.objects.filter(room=room).delete()

# # #             for student_id in absent_ids:
# # #                 student = Student.objects.get(student_id=student_id)
# # #                 Absentee.objects.get_or_create(room=room, student=student)
            
# # #             return JsonResponse({'status': 'success', 'message': f'{len(absent_ids)} absentees recorded for {room.name}.'})
# # #         except (Student.DoesNotExist, Room.DoesNotExist):
# # #             return JsonResponse({'status': 'error', 'message': 'Invalid student or room ID found.'}, status=404)
            
# # #     return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# # # @login_required
# # # def upload_students(request):
# # #     if not request.user.is_staff: return redirect('dashboard')
# # #     if request.method == 'POST':
# # #         excel_file = request.FILES.get('excel_file')
# # #         if not excel_file or not excel_file.name.endswith('.xlsx'):
# # #             messages.error(request, 'Please upload a valid .xlsx file.')
# # #             return redirect('upload_students')
        
# # #         try:
# # #             df = pd.read_excel(excel_file)
# # #             required_cols = ['StudentID', 'Batch']
# # #             if not all(col in df.columns for col in required_cols):
# # #                 messages.error(request, "Excel file must have columns named 'StudentID' and 'Batch'.")
# # #                 return redirect('upload_students')

# # #             created_count = 0
# # #             for index, row in df.iterrows():
# # #                 sid = str(row['StudentID'])
# # #                 batch_name = str(row['Batch'])
                
# # #                 student, created = Student.objects.update_or_create(
# # #                     student_id=sid,
# # #                     defaults={'batch': batch_name}
# # #                 )
# # #                 if created:
# # #                     created_count += 1
            
# # #             messages.success(request, f'Successfully processed file. Added {created_count} new students.')
# # #             return redirect('dashboard')

# # #         except Exception as e:
# # #             messages.error(request, f'An error occurred: {e}')
# # #             return redirect('upload_students')

# # #     return render(request, 'attendance/upload_students.html')

# # # @login_required
# # # def auto_arrange_seating(request, room_id):
# # #     if not request.user.is_staff: return redirect('dashboard')
# # #     room_to_arrange = get_object_or_404(Room, pk=room_id)
    
# # #     seated_students_ids = Bench.objects.values_list('students', flat=True)
# # #     students_to_seat = Student.objects.exclude(id__in=seated_students_ids).order_by('id')

# # #     if not students_to_seat:
# # #         messages.warning(request, 'No unseated students available to arrange.')
# # #         return redirect('dashboard')

# # #     Bench.objects.filter(room=room_to_arrange).delete()

# # #     students_by_batch = defaultdict(list)
# # #     for student in students_to_seat:
# # #         students_by_batch[student.batch].append(student)

# # #     batch_names = sorted(students_by_batch.keys())
    
# # #     if len(batch_names) < 2:
# # #         messages.warning(request, 'Seating arrangement requires at least two batches of students.')
# # #         return redirect('dashboard')
        
# # #     if room_to_arrange.id % 2 != 0:
# # #         batch_order = batch_names
# # #     else:
# # #         batch_order = list(reversed(batch_names))

# # #     seated_count = 0
# # #     total_virtual_columns = room_to_arrange.columns * room_to_arrange.students_per_bench

# # #     for virtual_col_idx in range(total_virtual_columns):
# # #         batch_to_pick_name = batch_order[virtual_col_idx % len(batch_order)]
        
# # #         real_bench_col = (virtual_col_idx // room_to_arrange.students_per_bench) + 1
        
# # #         for r in range(1, room_to_arrange.benches_per_column + 1):
# # #             if students_by_batch[batch_to_pick_name]:
# # #                 student = students_by_batch[batch_to_pick_name].pop(0)
                
# # #                 bench, _ = Bench.objects.get_or_create(room=room_to_arrange, row_num=r, col_num=real_bench_col)
# # #                 bench.students.add(student)
# # #                 seated_count += 1
# # #             else:
# # #                 break
            
# # #     messages.success(request, f'Successfully arranged {seated_count} students in {room_to_arrange.name}.')
# # #     return redirect('dashboard')

# # # @login_required
# # # def download_report(request):
# # #     if not request.user.is_staff: return redirect('dashboard')
# # #     # ... (rest of view is the same)
# # #     absentees = Absentee.objects.select_related('room', 'student').order_by('room__name', 'student__batch')
# # #     detailed_data = defaultdict(lambda: defaultdict(list))
# # #     for ab in absentees:
# # #         detailed_data[ab.room.name][ab.student.batch].append(ab.student.student_id)
# # #     detailed_rows = []
# # #     for room_name, batches in detailed_data.items():
# # #         for batch_name, student_ids in batches.items():
# # #             detailed_rows.append({'Room Number': room_name, 'Batch': batch_name, 'Absentees': ', '.join(student_ids)})
# # #     df1 = pd.DataFrame(detailed_rows)
# # #     summary_data = defaultdict(int)
# # #     for ab in absentees:
# # #         summary_data[ab.student.batch] += 1
# # #     summary_rows = [{'Batch': batch, 'Absentees Count': count} for batch, count in summary_data.items()]
# # #     df2 = pd.DataFrame(summary_rows)
# # #     output = io.BytesIO()
# # #     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
# # #         df1.to_excel(writer, sheet_name='Detailed Report', index=False)
# # #         df2.to_excel(writer, sheet_name='Consolidated Report', index=False)
# # #         workbook = writer.book
# # #         worksheet = writer.sheets['Detailed Report']
# # #         header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
# # #         for col_num, value in enumerate(df1.columns.values):
# # #             worksheet.write(0, col_num, value, header_format)
# # #         if not df1.empty:
# # #             merge_start_row = 1
# # #             for i in range(1, len(df1)):
# # #                 if df1.iloc[i]['Room Number'] != df1.iloc[i-1]['Room Number']:
# # #                     if merge_start_row < i:
# # #                         worksheet.merge_range(merge_start_row, 0, i, 0, df1.iloc[i-1]['Room Number'])
# # #                     merge_start_row = i + 1
# # #             worksheet.merge_range(merge_start_row, 0, len(df1), 0, df1.iloc[-1]['Room Number'])
# # #     output.seek(0)
# # #     response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
# # #     response['Content-Disposition'] = 'attachment; filename="absentee_report.xlsx"'
# # #     return response

# # # @login_required
# # # def download_seating_plan(request, room_id):
# # #     if not request.user.is_staff: return redirect('dashboard')
# # #     # ... (rest of view is the same)
# # #     room = get_object_or_404(Room, pk=room_id)
# # #     benches = Bench.objects.filter(room=room).prefetch_related('students').order_by('row_num', 'col_num')
# # #     batch_names = sorted(list(Student.objects.values_list('batch', flat=True).distinct()))
# # #     if len(batch_names) < 2:
# # #         batch_order = batch_names
# # #     elif room.id % 2 != 0:
# # #         batch_order = batch_names
# # #     else:
# # #         batch_order = list(reversed(batch_names))
# # #     headers = []
# # #     total_virtual_columns = room.columns * room.students_per_bench
# # #     for virtual_col_idx in range(total_virtual_columns):
# # #         if batch_order:
# # #             batch_name = batch_order[virtual_col_idx % len(batch_order)]
# # #             headers.append(batch_name)
# # #         else:
# # #             headers.append(f'Seat {virtual_col_idx + 1}')
# # #     num_rows = room.benches_per_column
# # #     plan_data = [['' for _ in range(total_virtual_columns)] for _ in range(num_rows)]
# # #     for bench in benches:
# # #         students_on_bench = list(bench.students.all())
# # #         start_col = (bench.col_num - 1) * room.students_per_bench
# # #         for i, student in enumerate(students_on_bench):
# # #             if start_col + i < len(plan_data[bench.row_num - 1]):
# # #                 plan_data[bench.row_num - 1][start_col + i] = student.student_id
# # #     df = pd.DataFrame(plan_data, columns=headers)
# # #     output = io.BytesIO()
# # #     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
# # #         df.to_excel(writer, sheet_name=room.name, index=False, header=True)
# # #         workbook = writer.book
# # #         worksheet = writer.sheets[room.name]
# # #         header_format = workbook.add_format({'bold': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
# # #         for col_num, value in enumerate(df.columns.values):
# # #             worksheet.write(0, col_num, value, header_format)
# # #         for idx in range(len(df.columns)):
# # #             series = df.iloc[:, idx]
# # #             data_max_len = series.astype(str).map(len).max()
# # #             if pd.isna(data_max_len):
# # #                 data_max_len = 0
# # #             header_len = len(str(df.columns[idx]))
# # #             final_width = max(int(data_max_len), header_len) + 2
# # #             worksheet.set_column(idx, idx, final_width)
# # #     output.seek(0)
# # #     response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
# # #     response['Content-Disposition'] = f'attachment; filename="seating_plan_{room.name}.xlsx"'
# # #     return response














# # # attendance/views.py

# # from django.shortcuts import render, get_object_or_404, redirect
# # from django.http import HttpResponse, JsonResponse, Http404
# # from django.views.decorators.csrf import csrf_exempt
# # from django.contrib import messages
# # from django.contrib.auth.decorators import login_required
# # from django.contrib.auth import login
# # from django.contrib.auth.forms import AuthenticationForm
# # from collections import defaultdict
# # import json
# # import pandas as pd
# # import io

# # from .models import Room, Student, Bench, Absentee, InvigilatorAssignment

# # def landing_page(request):
# #     if request.user.is_authenticated:
# #         return redirect('dashboard') # Redirect to dashboard if already logged in

# #     if request.method == 'POST':
# #         form = AuthenticationForm(request, data=request.POST)
# #         if form.is_valid():
# #             user = form.get_user()
# #             login(request, user)
# #             return redirect('dashboard')
# #     else:
# #         form = AuthenticationForm()
# #     return render(request, 'attendance/landing_page.html', {'form': form})

# # @login_required
# # def dashboard(request): # Renamed from room_list
# #     if request.user.is_staff:
# #         rooms = Room.objects.all()
# #     else:
# #         # CORRECTED QUERY: Use the user object directly for a more robust filter.
# #         assigned_room_ids = InvigilatorAssignment.objects.filter(
# #             invigilator=request.user
# #         ).values_list('room_id', flat=True).distinct()
# #         rooms = Room.objects.filter(id__in=assigned_room_ids)
        
# #     return render(request, 'attendance/dashboard.html', {'rooms': rooms})

# # @login_required
# # def seating_plan_view(request, room_id):
# #     room = get_object_or_404(Room, pk=room_id)
    
# #     start_col, end_col = 1, room.columns
    
# #     if not request.user.is_staff:
# #         try:
# #             assignment = InvigilatorAssignment.objects.get(invigilator=request.user, room=room)
# #             start_col = assignment.start_column
# #             end_col = assignment.end_column
# #         except InvigilatorAssignment.DoesNotExist:
# #             raise Http404("You are not assigned to this room.")

# #     benches = Bench.objects.filter(
# #         room=room, 
# #         col_num__gte=start_col, 
# #         col_num__lte=end_col
# #     ).order_by('col_num', 'row_num')
    
# #     num_display_columns = (end_col - start_col) + 1
# #     plan = [[] for _ in range(num_display_columns)]
    
# #     for bench in benches:
# #         students_on_bench = list(bench.students.all())
# #         seats = []
# #         for i in range(room.students_per_bench):
# #             if i < len(students_on_bench):
# #                 seats.append(students_on_bench[i])
# #             else:
# #                 seats.append(None)
# #         bench.seats = seats
# #         plan_col_index = bench.col_num - start_col
# #         plan[plan_col_index].append(bench)
        
# #     context = {
# #         'room': room,
# #         'plan': plan,
# #         'start_col': start_col,
# #     }
# #     return render(request, 'attendance/seating_plan.html', context)

# # @csrf_exempt
# # @login_required
# # def save_absentees(request):
# #     if request.method == 'POST':
# #         data = json.loads(request.body)
# #         room_id = data.get('room_id')
# #         absent_ids = data.get('absent_ids', [])

# #         if not room_id:
# #             return JsonResponse({'status': 'error', 'message': 'Missing room_id'}, status=400)
        
# #         try:
# #             room = Room.objects.get(id=room_id)
# #             Absentee.objects.filter(room=room).delete()

# #             for student_id in absent_ids:
# #                 student = Student.objects.get(student_id=student_id)
# #                 Absentee.objects.get_or_create(room=room, student=student)
            
# #             return JsonResponse({'status': 'success', 'message': f'{len(absent_ids)} absentees recorded for {room.name}.'})
# #         except (Student.DoesNotExist, Room.DoesNotExist):
# #             return JsonResponse({'status': 'error', 'message': 'Invalid student or room ID found.'}, status=404)
            
# #     return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# # @login_required
# # def upload_students(request):
# #     if not request.user.is_staff: return redirect('dashboard')
# #     if request.method == 'POST':
# #         excel_file = request.FILES.get('excel_file')
# #         if not excel_file or not excel_file.name.endswith('.xlsx'):
# #             messages.error(request, 'Please upload a valid .xlsx file.')
# #             return redirect('upload_students')
        
# #         try:
# #             df = pd.read_excel(excel_file)
# #             required_cols = ['StudentID', 'Batch']
# #             if not all(col in df.columns for col in required_cols):
# #                 messages.error(request, "Excel file must have columns named 'StudentID' and 'Batch'.")
# #                 return redirect('upload_students')

# #             created_count = 0
# #             for index, row in df.iterrows():
# #                 sid = str(row['StudentID'])
# #                 batch_name = str(row['Batch'])
                
# #                 student, created = Student.objects.update_or_create(
# #                     student_id=sid,
# #                     defaults={'batch': batch_name}
# #                 )
# #                 if created:
# #                     created_count += 1
            
# #             messages.success(request, f'Successfully processed file. Added {created_count} new students.')
# #             return redirect('dashboard')

# #         except Exception as e:
# #             messages.error(request, f'An error occurred: {e}')
# #             return redirect('upload_students')

# #     return render(request, 'attendance/upload_students.html')

# # @login_required
# # def auto_arrange_seating(request, room_id):
# #     if not request.user.is_staff: return redirect('dashboard')
# #     room_to_arrange = get_object_or_404(Room, pk=room_id)
    
# #     seated_students_ids = Bench.objects.values_list('students', flat=True)
# #     students_to_seat = Student.objects.exclude(id__in=seated_students_ids).order_by('id')

# #     if not students_to_seat:
# #         messages.warning(request, 'No unseated students available to arrange.')
# #         return redirect('dashboard')

# #     Bench.objects.filter(room=room_to_arrange).delete()

# #     students_by_batch = defaultdict(list)
# #     for student in students_to_seat:
# #         students_by_batch[student.batch].append(student)

# #     batch_names = sorted(students_by_batch.keys())
    
# #     if len(batch_names) < 2:
# #         messages.warning(request, 'Seating arrangement requires at least two batches of students.')
# #         return redirect('dashboard')
        
# #     if room_to_arrange.id % 2 != 0:
# #         batch_order = batch_names
# #     else:
# #         batch_order = list(reversed(batch_names))

# #     seated_count = 0
# #     total_virtual_columns = room_to_arrange.columns * room_to_arrange.students_per_bench

# #     for virtual_col_idx in range(total_virtual_columns):
# #         batch_to_pick_name = batch_order[virtual_col_idx % len(batch_order)]
        
# #         real_bench_col = (virtual_col_idx // room_to_arrange.students_per_bench) + 1
        
# #         for r in range(1, room_to_arrange.benches_per_column + 1):
# #             if students_by_batch[batch_to_pick_name]:
# #                 student = students_by_batch[batch_to_pick_name].pop(0)
                
# #                 bench, _ = Bench.objects.get_or_create(room=room_to_arrange, row_num=r, col_num=real_bench_col)
# #                 bench.students.add(student)
# #                 seated_count += 1
# #             else:
# #                 break
            
# #     messages.success(request, f'Successfully arranged {seated_count} students in {room_to_arrange.name}.')
# #     return redirect('dashboard')

# # @login_required
# # def download_report(request):
# #     if not request.user.is_staff: return redirect('dashboard')
# #     absentees = Absentee.objects.select_related('room', 'student').order_by('room__name', 'student__batch')
# #     detailed_data = defaultdict(lambda: defaultdict(list))
# #     for ab in absentees:
# #         detailed_data[ab.room.name][ab.student.batch].append(ab.student.student_id)
# #     detailed_rows = []
# #     for room_name, batches in detailed_data.items():
# #         for batch_name, student_ids in batches.items():
# #             detailed_rows.append({'Room Number': room_name, 'Batch': batch_name, 'Absentees': ', '.join(student_ids)})
# #     df1 = pd.DataFrame(detailed_rows)
# #     summary_data = defaultdict(int)
# #     for ab in absentees:
# #         summary_data[ab.student.batch] += 1
# #     summary_rows = [{'Batch': batch, 'Absentees Count': count} for batch, count in summary_data.items()]
# #     df2 = pd.DataFrame(summary_rows)
# #     output = io.BytesIO()
# #     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
# #         df1.to_excel(writer, sheet_name='Detailed Report', index=False)
# #         df2.to_excel(writer, sheet_name='Consolidated Report', index=False)
# #         workbook = writer.book
# #         worksheet = writer.sheets['Detailed Report']
# #         header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
# #         for col_num, value in enumerate(df1.columns.values):
# #             worksheet.write(0, col_num, value, header_format)
# #         if not df1.empty:
# #             merge_start_row = 1
# #             for i in range(1, len(df1)):
# #                 if df1.iloc[i]['Room Number'] != df1.iloc[i-1]['Room Number']:
# #                     if merge_start_row < i:
# #                         worksheet.merge_range(merge_start_row, 0, i, 0, df1.iloc[i-1]['Room Number'])
# #                     merge_start_row = i + 1
# #             worksheet.merge_range(merge_start_row, 0, len(df1), 0, df1.iloc[-1]['Room Number'])
# #     output.seek(0)
# #     response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
# #     response['Content-Disposition'] = 'attachment; filename="absentee_report.xlsx"'
# #     return response

# # @login_required
# # def download_seating_plan(request, room_id):
# #     if not request.user.is_staff: return redirect('dashboard')
# #     room = get_object_or_404(Room, pk=room_id)
# #     benches = Bench.objects.filter(room=room).prefetch_related('students').order_by('row_num', 'col_num')
# #     batch_names = sorted(list(Student.objects.values_list('batch', flat=True).distinct()))
# #     if len(batch_names) < 2:
# #         batch_order = batch_names
# #     elif room.id % 2 != 0:
# #         batch_order = batch_names
# #     else:
# #         batch_order = list(reversed(batch_names))
# #     headers = []
# #     total_virtual_columns = room.columns * room.students_per_bench
# #     for virtual_col_idx in range(total_virtual_columns):
# #         if batch_order:
# #             batch_name = batch_order[virtual_col_idx % len(batch_order)]
# #             headers.append(batch_name)
# #         else:
# #             headers.append(f'Seat {virtual_col_idx + 1}')
# #     num_rows = room.benches_per_column
# #     plan_data = [['' for _ in range(total_virtual_columns)] for _ in range(num_rows)]
# #     for bench in benches:
# #         students_on_bench = list(bench.students.all())
# #         start_col = (bench.col_num - 1) * room.students_per_bench
# #         for i, student in enumerate(students_on_bench):
# #             if start_col + i < len(plan_data[bench.row_num - 1]):
# #                 plan_data[bench.row_num - 1][start_col + i] = student.student_id
# #     df = pd.DataFrame(plan_data, columns=headers)
# #     output = io.BytesIO()
# #     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
# #         df.to_excel(writer, sheet_name=room.name, index=False, header=True)
# #         workbook = writer.book
# #         worksheet = writer.sheets[room.name]
# #         header_format = workbook.add_format({'bold': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
# #         for col_num, value in enumerate(df.columns.values):
# #             worksheet.write(0, col_num, value, header_format)
# #         for idx in range(len(df.columns)):
# #             series = df.iloc[:, idx]
# #             data_max_len = series.astype(str).map(len).max()
# #             if pd.isna(data_max_len):
# #                 data_max_len = 0
# #             header_len = len(str(df.columns[idx]))
# #             final_width = max(int(data_max_len), header_len) + 2
# #             worksheet.set_column(idx, idx, final_width)
# #     output.seek(0)
# #     response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
# #     response['Content-Disposition'] = f'attachment; filename="seating_plan_{room.name}.xlsx"'
# #     return response





# # attendance/views.py

# from django.shortcuts import render, get_object_or_404, redirect
# from django.http import HttpResponse, JsonResponse, Http404
# from django.views.decorators.csrf import csrf_exempt
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth import login
# from django.contrib.auth.forms import AuthenticationForm
# from collections import defaultdict
# import json
# import pandas as pd
# import io

# from .models import Room, Student, Bench, Absentee, InvigilatorAssignment

# def landing_page(request):
#     if request.user.is_authenticated:
#         return redirect('dashboard') # Redirect to dashboard if already logged in

#     if request.method == 'POST':
#         form = AuthenticationForm(request, data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)
#             return redirect('dashboard')
#     else:
#         form = AuthenticationForm()
#     return render(request, 'attendance/landing_page.html', {'form': form})

# @login_required
# def dashboard(request): # Renamed from room_list
#     if request.user.is_staff:
#         rooms = Room.objects.all()
#     else:
#         # CORRECTED QUERY: Use the user object directly for a more robust filter.
#         assigned_room_ids = InvigilatorAssignment.objects.filter(
#             invigilator=request.user
#         ).values_list('room_id', flat=True).distinct()
#         rooms = Room.objects.filter(id__in=assigned_room_ids)
        
#     return render(request, 'attendance/dashboard.html', {'rooms': rooms})

# @login_required
# def seating_plan_view(request, room_id):
#     room = get_object_or_404(Room, pk=room_id)
    
#     start_col, end_col = 1, room.columns
    
#     if not request.user.is_staff:
#         try:
#             assignment = InvigilatorAssignment.objects.get(invigilator=request.user, room=room)
#             start_col = assignment.start_column
#             end_col = assignment.end_column
#         except InvigilatorAssignment.DoesNotExist:
#             raise Http404("You are not assigned to this room.")

#     benches = Bench.objects.filter(
#         room=room, 
#         col_num__gte=start_col, 
#         col_num__lte=end_col
#     ).order_by('col_num', 'row_num')
    
#     num_display_columns = (end_col - start_col) + 1
#     plan = [[] for _ in range(num_display_columns)]
    
#     for bench in benches:
#         students_on_bench = list(bench.students.all())
#         seats = []
#         for i in range(room.students_per_bench):
#             if i < len(students_on_bench):
#                 seats.append(students_on_bench[i])
#             else:
#                 seats.append(None)
#         bench.seats = seats
#         plan_col_index = bench.col_num - start_col
#         plan[plan_col_index].append(bench)
        
#     context = {
#         'room': room,
#         'plan': plan,
#         'start_col': start_col,
#     }
#     return render(request, 'attendance/seating_plan.html', context)

# @csrf_exempt
# @login_required
# def save_absentees(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         room_id = data.get('room_id')
#         absent_ids = data.get('absent_ids', [])

#         if not room_id:
#             return JsonResponse({'status': 'error', 'message': 'Missing room_id'}, status=400)
        
#         try:
#             room = Room.objects.get(id=room_id)
#             Absentee.objects.filter(room=room).delete()

#             for student_id in absent_ids:
#                 student = Student.objects.get(student_id=student_id)
#                 Absentee.objects.get_or_create(room=room, student=student)
            
#             return JsonResponse({'status': 'success', 'message': f'{len(absent_ids)} absentees recorded for {room.name}.'})
#         except (Student.DoesNotExist, Room.DoesNotExist):
#             return JsonResponse({'status': 'error', 'message': 'Invalid student or room ID found.'}, status=404)
            
#     return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# @login_required
# def upload_students(request):
#     if not request.user.is_staff: return redirect('dashboard')
#     if request.method == 'POST':
#         excel_file = request.FILES.get('excel_file')
#         if not excel_file or not excel_file.name.endswith('.xlsx'):
#             messages.error(request, 'Please upload a valid .xlsx file.')
#             return redirect('upload_students')
        
#         try:
#             df = pd.read_excel(excel_file)
#             required_cols = ['StudentID', 'Batch']
#             if not all(col in df.columns for col in required_cols):
#                 messages.error(request, "Excel file must have columns named 'StudentID' and 'Batch'.")
#                 return redirect('upload_students')

#             created_count = 0
#             for index, row in df.iterrows():
#                 sid = str(row['StudentID'])
#                 batch_name = str(row['Batch'])
                
#                 student, created = Student.objects.update_or_create(
#                     student_id=sid,
#                     defaults={'batch': batch_name}
#                 )
#                 if created:
#                     created_count += 1
            
#             messages.success(request, f'Successfully processed file. Added {created_count} new students.')
#             return redirect('dashboard')

#         except Exception as e:
#             messages.error(request, f'An error occurred: {e}')
#             return redirect('upload_students')

#     return render(request, 'attendance/upload_students.html')

# @login_required
# def auto_arrange_seating(request, room_id):
#     if not request.user.is_staff: return redirect('dashboard')
#     room_to_arrange = get_object_or_404(Room, pk=room_id)
    
#     seated_students_ids = Bench.objects.values_list('students', flat=True)
#     students_to_seat = Student.objects.exclude(id__in=seated_students_ids).order_by('id')

#     if not students_to_seat:
#         messages.warning(request, 'No unseated students available to arrange.')
#         return redirect('dashboard')

#     Bench.objects.filter(room=room_to_arrange).delete()

#     students_by_batch = defaultdict(list)
#     for student in students_to_seat:
#         students_by_batch[student.batch].append(student)

#     batch_names = sorted(students_by_batch.keys())
    
#     if len(batch_names) < 2:
#         messages.warning(request, 'Seating arrangement requires at least two batches of students.')
#         return redirect('dashboard')
        
#     if room_to_arrange.id % 2 != 0:
#         batch_order = batch_names
#     else:
#         batch_order = list(reversed(batch_names))

#     seated_count = 0
#     total_virtual_columns = room_to_arrange.columns * room_to_arrange.students_per_bench

#     for virtual_col_idx in range(total_virtual_columns):
#         batch_to_pick_name = batch_order[virtual_col_idx % len(batch_order)]
        
#         real_bench_col = (virtual_col_idx // room_to_arrange.students_per_bench) + 1
        
#         for r in range(1, room_to_arrange.benches_per_column + 1):
#             if students_by_batch[batch_to_pick_name]:
#                 student = students_by_batch[batch_to_pick_name].pop(0)
                
#                 bench, _ = Bench.objects.get_or_create(room=room_to_arrange, row_num=r, col_num=real_bench_col)
#                 bench.students.add(student)
#                 seated_count += 1
#             else:
#                 break
            
#     messages.success(request, f'Successfully arranged {seated_count} students in {room_to_arrange.name}.')
#     return redirect('dashboard')

# @login_required
# def download_report(request):
#     if not request.user.is_staff: return redirect('dashboard')
#     absentees = Absentee.objects.select_related('room', 'student').order_by('room__name', 'student__batch')
#     detailed_data = defaultdict(lambda: defaultdict(list))
#     for ab in absentees:
#         detailed_data[ab.room.name][ab.student.batch].append(ab.student.student_id)
#     detailed_rows = []
#     for room_name, batches in detailed_data.items():
#         for batch_name, student_ids in batches.items():
#             detailed_rows.append({'Room Number': room_name, 'Batch': batch_name, 'Absentees': ', '.join(student_ids)})
#     df1 = pd.DataFrame(detailed_rows)
#     summary_data = defaultdict(int)
#     for ab in absentees:
#         summary_data[ab.student.batch] += 1
#     summary_rows = [{'Batch': batch, 'Absentees Count': count} for batch, count in summary_data.items()]
#     df2 = pd.DataFrame(summary_rows)
#     output = io.BytesIO()
#     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
#         df1.to_excel(writer, sheet_name='Detailed Report', index=False)
#         df2.to_excel(writer, sheet_name='Consolidated Report', index=False)
#         workbook = writer.book
#         worksheet = writer.sheets['Detailed Report']
#         header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
#         for col_num, value in enumerate(df1.columns.values):
#             worksheet.write(0, col_num, value, header_format)
#         if not df1.empty:
#             merge_start_row = 1
#             for i in range(1, len(df1)):
#                 if df1.iloc[i]['Room Number'] != df1.iloc[i-1]['Room Number']:
#                     if merge_start_row < i:
#                         worksheet.merge_range(merge_start_row, 0, i, 0, df1.iloc[i-1]['Room Number'])
#                     merge_start_row = i + 1
#             worksheet.merge_range(merge_start_row, 0, len(df1), 0, df1.iloc[-1]['Room Number'])
#     output.seek(0)
#     response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#     response['Content-Disposition'] = 'attachment; filename="absentee_report.xlsx"'
#     return response

# @login_required
# def download_seating_plan(request, room_id):
#     if not request.user.is_staff: return redirect('dashboard')
#     room = get_object_or_404(Room, pk=room_id)
#     benches = Bench.objects.filter(room=room).prefetch_related('students').order_by('row_num', 'col_num')
#     batch_names = sorted(list(Student.objects.values_list('batch', flat=True).distinct()))
#     if len(batch_names) < 2:
#         batch_order = batch_names
#     elif room.id % 2 != 0:
#         batch_order = batch_names
#     else:
#         batch_order = list(reversed(batch_names))
#     headers = []
#     total_virtual_columns = room.columns * room.students_per_bench
#     for virtual_col_idx in range(total_virtual_columns):
#         if batch_order:
#             batch_name = batch_order[virtual_col_idx % len(batch_order)]
#             headers.append(batch_name)
#         else:
#             headers.append(f'Seat {virtual_col_idx + 1}')
#     num_rows = room.benches_per_column
#     plan_data = [['' for _ in range(total_virtual_columns)] for _ in range(num_rows)]
#     for bench in benches:
#         students_on_bench = list(bench.students.all())
#         start_col = (bench.col_num - 1) * room.students_per_bench
#         for i, student in enumerate(students_on_bench):
#             if start_col + i < len(plan_data[bench.row_num - 1]):
#                 plan_data[bench.row_num - 1][start_col + i] = student.student_id
#     df = pd.DataFrame(plan_data, columns=headers)
#     output = io.BytesIO()
#     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
#         df.to_excel(writer, sheet_name=room.name, index=False, header=True)
#         workbook = writer.book
#         worksheet = writer.sheets[room.name]
#         header_format = workbook.add_format({'bold': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
#         for col_num, value in enumerate(df.columns.values):
#             worksheet.write(0, col_num, value, header_format)
#         for idx in range(len(df.columns)):
#             series = df.iloc[:, idx]
#             data_max_len = series.astype(str).map(len).max()
#             if pd.isna(data_max_len):
#                 data_max_len = 0
#             header_len = len(str(df.columns[idx]))
#             final_width = max(int(data_max_len), header_len) + 2
#             worksheet.set_column(idx, idx, final_width)
#     output.seek(0)
#     response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#     response['Content-Disposition'] = f'attachment; filename="seating_plan_{room.name}.xlsx"'
#     return response





# attendance/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from collections import defaultdict
import json
import pandas as pd
import io

from .models import Room, Student, Bench, Absentee, InvigilatorAssignment

@login_required
def dashboard(request):
    if request.user.is_staff:
        rooms = Room.objects.all()
    else:
        # CORRECTED QUERY: Use the user object directly for a more robust filter.
        assigned_room_ids = InvigilatorAssignment.objects.filter(
            invigilator=request.user
        ).values_list('room_id', flat=True).distinct()
        rooms = Room.objects.filter(id__in=assigned_room_ids)
        
    return render(request, 'attendance/dashboard.html', {'rooms': rooms})

@login_required
def seating_plan_view(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    
    start_col, end_col = 1, room.columns
    
    if not request.user.is_staff:
        try:
            assignment = InvigilatorAssignment.objects.get(invigilator=request.user, room=room)
            start_col = assignment.start_column
            end_col = assignment.end_column
        except InvigilatorAssignment.DoesNotExist:
            raise Http404("You are not assigned to this room.")

    benches = Bench.objects.filter(
        room=room, 
        col_num__gte=start_col, 
        col_num__lte=end_col
    ).order_by('col_num', 'row_num')
    
    num_display_columns = (end_col - start_col) + 1
    plan = [[] for _ in range(num_display_columns)]
    
    for bench in benches:
        students_on_bench = list(bench.students.all())
        seats = []
        for i in range(room.students_per_bench):
            if i < len(students_on_bench):
                seats.append(students_on_bench[i])
            else:
                seats.append(None)
        bench.seats = seats
        plan_col_index = bench.col_num - start_col
        plan[plan_col_index].append(bench)
        
    context = {
        'room': room,
        'plan': plan,
        'start_col': start_col,
    }
    return render(request, 'attendance/seating_plan.html', context)

@csrf_exempt
@login_required
def save_absentees(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        room_id = data.get('room_id')
        absent_ids = data.get('absent_ids', [])

        if not room_id:
            return JsonResponse({'status': 'error', 'message': 'Missing room_id'}, status=400)
        
        try:
            room = Room.objects.get(id=room_id)
            Absentee.objects.filter(room=room).delete()

            for student_id in absent_ids:
                student = Student.objects.get(student_id=student_id)
                Absentee.objects.get_or_create(room=room, student=student)
            
            return JsonResponse({'status': 'success', 'message': f'{len(absent_ids)} absentees recorded for {room.name}.'})
        except (Student.DoesNotExist, Room.DoesNotExist):
            return JsonResponse({'status': 'error', 'message': 'Invalid student or room ID found.'}, status=404)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def upload_students(request):
    if not request.user.is_staff: return redirect('dashboard')
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')
        if not excel_file or not excel_file.name.endswith('.xlsx'):
            messages.error(request, 'Please upload a valid .xlsx file.')
            return redirect('upload_students')
        
        try:
            df = pd.read_excel(excel_file)
            required_cols = ['StudentID', 'Batch']
            if not all(col in df.columns for col in required_cols):
                messages.error(request, "Excel file must have columns named 'StudentID' and 'Batch'.")
                return redirect('upload_students')

            created_count = 0
            for index, row in df.iterrows():
                sid = str(row['StudentID'])
                batch_name = str(row['Batch'])
                
                student, created = Student.objects.update_or_create(
                    student_id=sid,
                    defaults={'batch': batch_name}
                )
                if created:
                    created_count += 1
            
            messages.success(request, f'Successfully processed file. Added {created_count} new students.')
            return redirect('dashboard')

        except Exception as e:
            messages.error(request, f'An error occurred: {e}')
            return redirect('upload_students')

    return render(request, 'attendance/upload_students.html')

@login_required
def auto_arrange_seating(request, room_id):
    if not request.user.is_staff: return redirect('dashboard')
    room_to_arrange = get_object_or_404(Room, pk=room_id)
    
    seated_students_ids = Bench.objects.values_list('students', flat=True)
    students_to_seat = Student.objects.exclude(id__in=seated_students_ids).order_by('id')

    if not students_to_seat:
        messages.warning(request, 'No unseated students available to arrange.')
        return redirect('dashboard')

    Bench.objects.filter(room=room_to_arrange).delete()

    students_by_batch = defaultdict(list)
    for student in students_to_seat:
        students_by_batch[student.batch].append(student)

    batch_names = sorted(students_by_batch.keys())
    
    if len(batch_names) < 2:
        messages.warning(request, 'Seating arrangement requires at least two batches of students.')
        return redirect('dashboard')
        
    if room_to_arrange.id % 2 != 0:
        batch_order = batch_names
    else:
        batch_order = list(reversed(batch_names))

    seated_count = 0
    total_virtual_columns = room_to_arrange.columns * room_to_arrange.students_per_bench

    for virtual_col_idx in range(total_virtual_columns):
        batch_to_pick_name = batch_order[virtual_col_idx % len(batch_order)]
        
        real_bench_col = (virtual_col_idx // room_to_arrange.students_per_bench) + 1
        
        for r in range(1, room_to_arrange.benches_per_column + 1):
            if students_by_batch[batch_to_pick_name]:
                student = students_by_batch[batch_to_pick_name].pop(0)
                
                bench, _ = Bench.objects.get_or_create(room=room_to_arrange, row_num=r, col_num=real_bench_col)
                bench.students.add(student)
                seated_count += 1
            else:
                break
            
    messages.success(request, f'Successfully arranged {seated_count} students in {room_to_arrange.name}.')
    return redirect('dashboard')

@login_required
def download_report(request):
    if not request.user.is_staff: return redirect('dashboard')
    # ... (rest of view is the same)
    absentees = Absentee.objects.select_related('room', 'student').order_by('room__name', 'student__batch')
    detailed_data = defaultdict(lambda: defaultdict(list))
    for ab in absentees:
        detailed_data[ab.room.name][ab.student.batch].append(ab.student.student_id)
    detailed_rows = []
    for room_name, batches in detailed_data.items():
        for batch_name, student_ids in batches.items():
            detailed_rows.append({'Room Number': room_name, 'Batch': batch_name, 'Absentees': ', '.join(student_ids)})
    df1 = pd.DataFrame(detailed_rows)
    summary_data = defaultdict(int)
    for ab in absentees:
        summary_data[ab.student.batch] += 1
    summary_rows = [{'Batch': batch, 'Absentees Count': count} for batch, count in summary_data.items()]
    df2 = pd.DataFrame(summary_rows)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df1.to_excel(writer, sheet_name='Detailed Report', index=False)
        df2.to_excel(writer, sheet_name='Consolidated Report', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Detailed Report']
        header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
        for col_num, value in enumerate(df1.columns.values):
            worksheet.write(0, col_num, value, header_format)
        if not df1.empty:
            merge_start_row = 1
            for i in range(1, len(df1)):
                if df1.iloc[i]['Room Number'] != df1.iloc[i-1]['Room Number']:
                    if merge_start_row < i:
                        worksheet.merge_range(merge_start_row, 0, i, 0, df1.iloc[i-1]['Room Number'])
                    merge_start_row = i + 1
            worksheet.merge_range(merge_start_row, 0, len(df1), 0, df1.iloc[-1]['Room Number'])
    output.seek(0)
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="absentee_report.xlsx"'
    return response

@login_required
def download_seating_plan(request, room_id):
    if not request.user.is_staff: return redirect('dashboard')
    # ... (rest of view is the same)
    room = get_object_or_404(Room, pk=room_id)
    benches = Bench.objects.filter(room=room).prefetch_related('students').order_by('row_num', 'col_num')
    batch_names = sorted(list(Student.objects.values_list('batch', flat=True).distinct()))
    if len(batch_names) < 2:
        batch_order = batch_names
    elif room.id % 2 != 0:
        batch_order = batch_names
    else:
        batch_order = list(reversed(batch_names))
    headers = []
    total_virtual_columns = room.columns * room.students_per_bench
    for virtual_col_idx in range(total_virtual_columns):
        if batch_order:
            batch_name = batch_order[virtual_col_idx % len(batch_order)]
            headers.append(batch_name)
        else:
            headers.append(f'Seat {virtual_col_idx + 1}')
    num_rows = room.benches_per_column
    plan_data = [['' for _ in range(total_virtual_columns)] for _ in range(num_rows)]
    for bench in benches:
        students_on_bench = list(bench.students.all())
        start_col = (bench.col_num - 1) * room.students_per_bench
        for i, student in enumerate(students_on_bench):
            if start_col + i < len(plan_data[bench.row_num - 1]):
                plan_data[bench.row_num - 1][start_col + i] = student.student_id
    df = pd.DataFrame(plan_data, columns=headers)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name=room.name, index=False, header=True)
        workbook = writer.book
        worksheet = writer.sheets[room.name]
        header_format = workbook.add_format({'bold': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        for idx in range(len(df.columns)):
            series = df.iloc[:, idx]
            data_max_len = series.astype(str).map(len).max()
            if pd.isna(data_max_len):
                data_max_len = 0
            header_len = len(str(df.columns[idx]))
            final_width = max(int(data_max_len), header_len) + 2
            worksheet.set_column(idx, idx, final_width)
    output.seek(0)
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="seating_plan_{room.name}.xlsx"'
    return response
