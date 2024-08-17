from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Table, Row, Column
from .serializers import TableSerializer
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

class TableViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TableSerializer

    def get_queryset(self):
        return Table.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        table = self.get_object()
        rows_data = request.data.get('rows', [])
        
        if not rows_data:
            return Response({"error": "Data baris tidak disediakan"}, status=status.HTTP_400_BAD_REQUEST)

        updated_rows = []
        for row_data in rows_data:
            row_id = row_data.get('id')
            if not row_id:
                return Response({"error": "ID baris tidak disediakan"}, status=status.HTTP_400_BAD_REQUEST)

            row = get_object_or_404(Row, id=row_id, table=table)
            data_json = {}

            for key, value in row_data.items():
                if key != 'id':
                    column = table.columns.filter(name=key).first()
                    if column:
                        if column.related_table:
                            related_row = self.get_related_row(column.related_table, value)
                            if related_row:
                                data_json[str(column.id)] = str(related_row.id)
                            else:
                                return Response({"error": f"Nilai tidak valid untuk kolom relasi {key}"}, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            data_json[str(column.id)] = value
                    else:
                        return Response({"error": f"Kolom {key} tidak ditemukan"}, status=status.HTTP_400_BAD_REQUEST)

            row.data_json = data_json
            row.save()
            updated_rows.append(self.get_row_data(row))

        return Response(updated_rows)

    def get_related_row(self, related_table, value):
        first_column = related_table.columns.first()
        if first_column:
            return Row.objects.filter(table=related_table, data_json__icontains=value).first()
        return None

    def get_row_data(self, row):
        data = {"id": row.id}
        for column in row.table.columns.all():
            if column.related_table:
                related_row_id = row.data_json.get(str(column.id))
                if related_row_id:
                    related_row = Row.objects.filter(id=related_row_id, table=column.related_table).first()
                    if related_row:
                        first_column = column.related_table.columns.first()
                        data[column.name] = related_row.data_json.get(str(first_column.id), '')
                    else:
                        data[column.name] = ''
                else:
                    data[column.name] = ''
            else:
                data[column.name] = row.data_json.get(str(column.id), '')
        return data

    @swagger_auto_schema(
        operation_description="Menghapus baris dari tabel",
        manual_parameters=[
            openapi.Parameter(
                'row_id',
                openapi.IN_QUERY,
                description="ID baris yang akan dihapus",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            204: "Baris berhasil dihapus",
            400: "ID baris tidak disediakan",
            404: "Baris tidak ditemukan"
        }
    )
    def destroy(self, request, *args, **kwargs):
        table = self.get_object()
        row_id = request.query_params.get('row_id')
        if row_id:
            try:
                row = Row.objects.get(id=row_id, table=table)
                row.delete()
                return Response({"message": "Baris berhasil dihapus"}, status=status.HTTP_204_NO_CONTENT)
            except Row.DoesNotExist:
                return Response({"error": "Baris tidak ditemukan"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "ID baris tidak disediakan"}, status=status.HTTP_400_BAD_REQUEST)