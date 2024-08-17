from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from .models import CustomUser, Table, Column, Data, Relation, Row
from django.db import IntegrityError
from .forms import CustomUserCreationForm, CustomAuthenticationForm, TableForm, ColumnForm, DataForm
from django.db.models import Prefetch, Count
from django.urls import reverse
from django.contrib import messages
from .forms import CustomUserChangeForm
import csv
import openpyxl
from openpyxl.utils import get_column_letter
import openpyxl
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import TextIOWrapper
import json
from django.core.paginator import Paginator

def index(request):
    return redirect('dashboard')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
        else:
            # Tambahkan pesan kesalahan ke dalam konteks
            return render(request, 'register.html', {'form': form, 'errors': form.errors, 'success': 'Akun berhasil dibuat. Silakan masuk.'})
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    tables = Table.objects.filter(user=request.user).annotate(row_count=Count('rows'))
    return render(request, 'dashboard.html', {'tables': tables})

@login_required
def create_table_view(request):
    if request.method == 'POST':
        form = TableForm(request.POST)
        if form.is_valid():
            table = form.save(commit=False)
            table.user = request.user
            table.save()
            return redirect('table_detail', table_id=table.id)
    else:
        form = TableForm()
    return render(request, 'dashboard.html', {'form': form})

@login_required
def table_detail_view(request, table_id):
    table = get_object_or_404(Table, id=table_id, user=request.user)
    columns = table.columns.all()
    rows = table.rows.all()

    # Tambahkan logika pencarian
    search_query = request.GET.get('search', '')
    if search_query:
        filtered_rows = []
        for row in rows:
            if any(search_query.lower() in str(value).lower() for value in row.data_json.values()):
                filtered_rows.append(row)
        rows = filtered_rows

    data = []
    for row in rows:
        row_data = {'id': row.id, 'values': []}
        for column in columns:
            value = row.data_json.get(str(column.id), '')
            if column.related_table and value:
                try:
                    related_row = Row.objects.filter(id=int(value), table=column.related_table).first()
                    if related_row:
                        value = related_row.data_json.get(str(related_row.table.columns.first().id), '')
                except ValueError:
                    value = ''
            row_data['values'].append(value)
        data.append(row_data)
    
    # Tambahkan data untuk kolom dengan relasi
    for column in columns:
        if column.related_table:
            related_rows = Row.objects.filter(table=column.related_table)
            column.related_table_rows = [
                {
                    'id': row.id,
                    'display_value': row.data_json.get(str(row.table.columns.first().id), '')
                }
                for row in related_rows
            ]
    
    user_tables = Table.objects.filter(user=request.user).exclude(id=table_id)
    
    api_url = request.build_absolute_uri(reverse('api_table-detail', args=[table_id]))

    # Paginasi
    paginator = Paginator(data, 15)  # Menampilkan 15 item per halaman
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Ganti 'data' dengan 'page_obj' dalam konteks

    # Tambahkan ini untuk menangani permintaan AJAX untuk edit dan hapus
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == 'POST':
            action = request.POST.get('action')
            row_id = request.POST.get('row_id')
            if action == 'edit':
                row = get_object_or_404(Row, id=row_id, table__user=request.user)
                data_json = {}
                for key, value in request.POST.items():
                    if key.startswith('column_'):
                        column_id = key.split('_')[1]
                        column = get_object_or_404(Column, id=column_id, table=table)
                        if column.related_table:
                            data_json[column_id] = value
                        else:
                            data_json[column_id] = value
                row.data_json = data_json
                row.save()
                return JsonResponse({'success': True, 'message': 'Data berhasil diubah'})
            elif action == 'delete':
                row = get_object_or_404(Row, id=row_id, table__user=request.user)
                row.delete()
                return JsonResponse({'success': True, 'message': 'Data berhasil dihapus'})
            elif action == 'bulk_delete':
                row_ids = json.loads(request.POST.get('row_ids', '[]'))
                try:
                    # Lakukan penghapusan data berdasarkan row_ids
                    Row.objects.filter(id__in=row_ids).delete()
                    return JsonResponse({'success': True, 'message': 'Data berhasil dihapus.'})
                except Exception as e:
                    return JsonResponse({'success': False, 'message': str(e)})
        return JsonResponse({'success': False, 'message': 'Permintaan tidak valid'})

    return render(request, 'table_detail.html', {
        'table': table,
        'columns': columns,
        'page_obj': page_obj,
        'user_tables': user_tables,
        'api_url': api_url,
        'total_rows': table.rows.count()  # Tambahkan ini
    })

@login_required
def add_column_view(request, table_id):
    table = get_object_or_404(Table, id=table_id, user=request.user)
    if request.method == 'POST':
        form = ColumnForm(request.POST, user=request.user, current_table=table)
        if form.is_valid():
            column = form.save(commit=False)
            column.table = table
            column.save()
            return redirect('table_detail', table_id=table.id)
    else:
        form = ColumnForm(user=request.user, current_table=table)
    
    # Tambahkan ini untuk menyertakan daftar tabel pengguna
    user_tables = Table.objects.filter(user=request.user).exclude(id=table_id)
    
    return render(request, 'table_detail.html', {
        'form': form, 
        'table': table,
        'user_tables': user_tables  # Tambahkan ini ke konteks
    })

@login_required
def add_data_view(request, table_id):
    table = get_object_or_404(Table, id=table_id, user=request.user)
    if request.method == 'POST':
        form = DataForm(request.POST, request.FILES, table=table)
        if form.is_valid():
            row = Row.objects.create(table=table)
            data_json = {}
            for field_name, value in form.cleaned_data.items():
                if field_name.startswith('column_'):
                    column_id = field_name.split('_')[1]
                    column = Column.objects.get(id=column_id)
                    if column.related_table:
                        data_json[column_id] = str(value.id) if value else ''
                    else:
                        data_json[column_id] = str(value) if value is not None else ''
            row.data_json = data_json
            row.save()
            return redirect('table_detail', table_id=table.id)
    else:
        form = DataForm(table=table)
    return render(request, 'table_detail.html', {'form': form, 'table': table})

@login_required
def edit_data_view(request, row_id):
    row = get_object_or_404(Row, id=row_id, table__user=request.user)
    table = row.table
    columns = table.columns.all()

    if request.method == 'POST':
        data_json = {}
        for column in columns:
            value = request.POST.get(f'column_{column.id}')
            if column.related_table:
                data_json[column.name] = value if value else None
            else:
                data_json[column.name] = value
        row.data_json = data_json
        row.save()
        return redirect('table_detail', table_id=table.id)

    return render(request, 'table_detail.html', {'row': row, 'columns': columns})

@login_required
def delete_data_view(request, row_id):
    row = get_object_or_404(Row, id=row_id, table__user=request.user)
    table_id = row.table.id
    row.delete()
    return redirect('table_detail', table_id=table_id)

@login_required
def edit_table_view(request, table_id):
    table = get_object_or_404(Table, id=table_id, user=request.user)
    if request.method == 'POST':
        form = TableForm(request.POST, instance=table)
        if form.is_valid():
            form.save()
            return redirect('table_detail', table_id=table.id)
        else:
            return render(request, 'table_detail.html', {'form': form, 'table': table})
    return render(request, 'table_detail.html', {'form': form, 'table': table})

@login_required
def delete_table_view(request, table_id):
    table = get_object_or_404(Table, id=table_id, user=request.user)
    table.delete()
    return redirect('dashboard')

@login_required
def get_columns(request, table_id):
    table = get_object_or_404(Table, id=table_id, user=request.user)
    columns = Column.objects.filter(table=table)
    data = [{'id': column.id, 'name': column.name} for column in columns]
    return JsonResponse({'columns': data})
    
@login_required
def profile_view(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil berhasil diperbarui.')
            return redirect('profile')
        else:
            messages.error(request, 'Terjadi kesalahan. Silakan periksa form Anda.')
    else:
        form = CustomUserChangeForm(instance=request.user)
    
    return render(request, 'profile.html', {'form': form})

@login_required
def export_table_data(request, table_id, format):
    table = get_object_or_404(Table, id=table_id, user=request.user)
    columns = table.columns.all()
    rows = table.rows.all()

    if format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{table.name}.csv"'
        writer = csv.writer(response)

        # Tulis header
        header = [column.name for column in columns]
        writer.writerow(header)

        # Tulis data
        for row in rows:
            row_data = []
            for column in columns:
                value = row.data_json.get(str(column.id), '')
                if column.related_table and value:
                    related_row = Row.objects.filter(id=int(value), table=column.related_table).first()
                    if related_row:
                        value = related_row.data_json.get(str(related_row.table.columns.first().id), '')
                row_data.append(value)
            writer.writerow(row_data)

        return response

    elif format == 'excel':
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = table.name

        # Tulis header
        for col_num, column in enumerate(columns, 1):
            cell = worksheet.cell(row=1, column=col_num)
            cell.value = column.name

        # Tulis data
        for row_num, row in enumerate(rows, 2):
            for col_num, column in enumerate(columns, 1):
                cell = worksheet.cell(row=row_num, column=col_num)
                value = row.data_json.get(str(column.id), '')
                if column.related_table and value:
                    related_row = Row.objects.filter(id=int(value), table=column.related_table).first()
                    if related_row:
                        value = related_row.data_json.get(str(related_row.table.columns.first().id), '')
                cell.value = value

        # Atur lebar kolom
        for column in worksheet.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)
            worksheet.column_dimensions[column_letter].width = adjusted_width

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{table.name}.xlsx"'
        workbook.save(response)
        return response

    return HttpResponse("Format tidak didukung", status=400)

@login_required
def import_data(request, table_id):
    table = get_object_or_404(Table, id=table_id, user=request.user)
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        file_extension = file.name.split('.')[-1].lower()
        
        if file_extension == 'csv':
            csv_file = TextIOWrapper(file, encoding='utf-8')
            reader = csv.DictReader(csv_file)
        elif file_extension in ['xlsx', 'xls']:
            workbook = openpyxl.load_workbook(file)
            sheet = workbook.active
            headers = [cell.value for cell in sheet[1]]
            reader = [
                {headers[i]: cell.value for i, cell in enumerate(row)}
                for row in sheet.iter_rows(min_row=2)
            ]
        else:
            messages.error(request, 'Format file tidak didukung. Gunakan CSV atau Excel.')
            return redirect('table_detail', table_id=table.id)

        columns = {column.name: column for column in table.columns.all()}
        for row in reader:
            new_row = Row(table=table)
            data_json = {}
            for column_name, value in row.items():
                if column_name in columns:
                    column = columns[column_name]
                    if column.related_table:
                        # Cari data yang cocok di tabel terkait
                        related_rows = Row.objects.filter(table=column.related_table)
                        related_column = column.related_table.columns.first()
                        if related_column:
                            for related_row in related_rows:
                                if related_row.data_json.get(str(related_column.id)) == str(value):
                                    data_json[str(column.id)] = str(related_row.id)
                                    break
                    else:
                        data_json[str(column.id)] = str(value) if value is not None else ''
            new_row.data_json = data_json
            new_row.save()

        messages.success(request, 'Data berhasil diimpor.')
        return redirect('table_detail', table_id=table.id)

    return render(request, 'import_data.html', {'table': table})

@login_required
def import_table(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        file_extension = file.name.split('.')[-1].lower()
        
        if file_extension == 'csv':
            csv_file = TextIOWrapper(file, encoding='utf-8')
            reader = csv.DictReader(csv_file)
            headers = reader.fieldnames
        elif file_extension in ['xlsx', 'xls']:
            workbook = openpyxl.load_workbook(file)
            sheet = workbook.active
            headers = [cell.value for cell in sheet[1]]
            reader = [
                {headers[i]: cell.value for i, cell in enumerate(row)}
                for row in sheet.iter_rows(min_row=2)
            ]
        else:
            messages.error(request, 'Format file tidak didukung. Gunakan CSV atau Excel.')
            return redirect('dashboard')

        table_name = request.POST.get('table_name', 'Tabel Impor')
        new_table = Table.objects.create(name=table_name, user=request.user)

        for header in headers:
            Column.objects.create(name=header, table=new_table)

        for row in reader:
            new_row = Row(table=new_table)
            data_json = {
                str(new_table.columns.get(name=column_name).id): str(value) if value is not None else ''
                for column_name, value in row.items()
            }
            new_row.data_json = data_json
            new_row.save()

        messages.success(request, 'Tabel baru berhasil diimpor.')
        return redirect('table_detail', table_id=new_table.id)

    return render(request, 'import_table.html')

@login_required
def edit_column_view(request, table_id, column_id):
    table = get_object_or_404(Table, id=table_id, user=request.user)
    column = get_object_or_404(Column, id=column_id, table=table)
    
    if request.method == 'POST':
        form = ColumnForm(request.POST, instance=column, user=request.user, current_table=table)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kolom berhasil diubah.')
            return redirect('table_detail', table_id=table.id)
    else:
        form = ColumnForm(instance=column, user=request.user, current_table=table)
    
    return render(request, 'table_detail.html', {'form': form, 'table': table, 'column': column})

@login_required
def delete_column_view(request, table_id, column_id):
    table = get_object_or_404(Table, id=table_id, user=request.user)
    column = get_object_or_404(Column, id=column_id, table=table)
    
    if request.method == 'POST':
        column.delete()
        messages.success(request, 'Kolom berhasil dihapus.')
        return redirect('table_detail', table_id=table.id)
    
    return render(request, 'table_detail.html', {'table': table, 'column': column})