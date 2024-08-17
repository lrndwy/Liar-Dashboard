from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Field tambahan pada CustomUser, misalnya:
    
    # Nomor telepon
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    # Alamat
    address = models.TextField(blank=True, null=True)
    
    # Avatar atau foto profil
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    # Tanggal lahir
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Menyimpan informasi tentang apakah user adalah admin atau bukan
    is_admin = models.BooleanField(default=False)
    
    # Email
    email = models.EmailField(unique=True)
    
    # Nama depan
    first_name = models.CharField(max_length=30, blank=True)
    
    # Nama belakang
    last_name = models.CharField(max_length=150, blank=True)
    
    # Anda bisa menambahkan field lain sesuai kebutuhan
    def __str__(self):
        return self.username
    
class Table(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name
    
class Column(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='columns')
    name = models.CharField(max_length=255)
    related_table = models.ForeignKey(Table, null=True, blank=True, on_delete=models.SET_NULL)
    
    def __str__(self):
        return self.name
    
class Row(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='rows')
    data_json = models.JSONField(default=dict)

class Data(models.Model):
    row = models.ForeignKey(Row, on_delete=models.CASCADE, related_name='data')
    column = models.ForeignKey(Column, on_delete=models.CASCADE)

class Relation(models.Model):
    source_table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='source_relations')
    target_table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='target_relations')
    source_column = models.ForeignKey(Column, on_delete=models.CASCADE, related_name='source_relations')
    target_column = models.ForeignKey(Column, on_delete=models.CASCADE, related_name='target_relations')

    class Meta:
        unique_together = ('source_table', 'target_table', 'source_column', 'target_column')

    def __str__(self):
        return f"{self.source_table.name}.{self.source_column.name} -> {self.target_table.name}.{self.target_column.name}"