from rest_framework import serializers
from .models import Table, Column, Row

class RowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Row
        fields = ['id']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        columns = instance.table.columns.all()
        for column in columns:
            if column.related_table:
                related_row_id = instance.data_json.get(str(column.id))
                if related_row_id:
                    related_row = Row.objects.filter(id=related_row_id, table=column.related_table).first()
                    if related_row:
                        first_column = column.related_table.columns.first()
                        representation[column.name] = related_row.data_json.get(str(first_column.id), '')
                    else:
                        representation[column.name] = ''
                else:
                    representation[column.name] = ''
            else:
                representation[column.name] = instance.data_json.get(str(column.id), '')
        return representation

class TableSerializer(serializers.ModelSerializer):
    rows = RowSerializer(many=True)

    class Meta:
        model = Table
        fields = ['rows']

    def update(self, instance, validated_data):
        rows_data = validated_data.pop('rows', [])

        for row_data in rows_data:
            row_id = row_data.pop('id', None)
            if row_id:
                row = Row.objects.filter(id=row_id, table=instance).first()
                if row:
                    for key, value in row_data.items():
                        column = Column.objects.filter(name=key, table=instance).first()
                        if column:
                            row.data_json[str(column.id)] = value
                    row.save()
                else:
                    # Jika baris tidak ditemukan, buat baris baru
                    new_row = Row(table=instance)
                    new_row.data_json = {}
                    for key, value in row_data.items():
                        column = Column.objects.filter(name=key, table=instance).first()
                        if column:
                            new_row.data_json[str(column.id)] = value
                    new_row.save()

        return instance

    def to_representation(self, instance):
        try:
            representation = super().to_representation(instance)
            rows_data = representation.get('rows', [])
            return {'rows': rows_data}
        except Exception as e:
            return {'error': str(e)}