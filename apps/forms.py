from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import CustomUser, Table, Column, Data, Row
from django.contrib.auth.forms import UserChangeForm

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email',)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Password tidak cocok")
        return cleaned_data

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password']

class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['name', 'description']

class ColumnForm(forms.ModelForm):
    class Meta:
        model = Column
        fields = ['name', 'related_table']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        current_table = kwargs.pop('current_table', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['related_table'].queryset = Table.objects.filter(user=user)
        if current_table:
            self.fields['related_table'].queryset = self.fields['related_table'].queryset.exclude(id=current_table.id)
        self.fields['related_table'].required = False
        self.fields['related_table'].label = 'Tabel Terkait (opsional)'
        self.fields['related_table'].empty_label = 'Tidak ada'

class DataForm(forms.ModelForm):
    class Meta:
        model = Data
        fields = []

    def __init__(self, *args, **kwargs):
        table = kwargs.pop('table', None)
        super().__init__(*args, **kwargs)
        if table:
            columns = Column.objects.filter(table=table)
            for column in columns:
                if column.related_table:
                    self.fields[f'column_{column.id}'] = forms.ModelChoiceField(
                        queryset=Row.objects.filter(table=column.related_table),
                        label=column.name,
                        required=False,
                        to_field_name='id',
                        widget=forms.Select(attrs={'class': 'form-control'}),
                    )
                    # Mengubah tampilan opsi menjadi nama kolom pertama dari tabel terkait
                    self.fields[f'column_{column.id}'].label_from_instance = lambda obj: obj.data_json.get(str(obj.table.columns.first().id), '')
                else:
                    self.fields[f'column_{column.id}'] = forms.CharField(label=column.name, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'address', 'avatar', 'date_of_birth')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('password')