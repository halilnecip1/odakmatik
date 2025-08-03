# instructor/management/commands/fix_student_end_dates.py
from django.core.management.base import BaseCommand
from instructor.models import InstructorStudent
from datetime import date
from dateutil.relativedelta import relativedelta

class Command(BaseCommand):
    help = 'Fixes missing end_date for existing InstructorStudent records where duration_months is set.'

    def handle(self, *args, **options):
        # duration_months'ı olan ama end_date'i olmayan kayıtları bul
        students_to_fix = InstructorStudent.objects.filter(duration_months__isnull=False, end_date__isnull=True)
        
        fixed_count = 0
        for student_relation in students_to_fix:
            # duration_months'ı int'e çevir
            duration = int(student_relation.duration_months)
            
            # end_date'i hesapla ve kaydet
            student_relation.end_date = student_relation.added_at.date() + relativedelta(months=+duration)
            student_relation.save(update_fields=['end_date']) # Sadece end_date alanını güncelle
            fixed_count += 1
            self.stdout.write(self.style.SUCCESS(f'Fixed end_date for student: {student_relation.student.username}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully fixed {fixed_count} InstructorStudent records.'))