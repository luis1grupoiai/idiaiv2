from django import forms
from .models import TRegistroDeModulo
from cryptography.fernet import Fernet
from django.core.exceptions import ValidationError


ENCRYPTION_KEY_DESCRIPCION = b'VVsQPaM9IhXYrWNwLyKkAnmJdzdFR8R0MwdvZpHGsA8='
ENCRYPTION_KEY_NOMBRE = b'o2GwoZ4O2UyRvsWTK7owoZKHOBQU2TbmYHUkHI1OWMs='



class ModuloForm(forms.ModelForm):
    nombre = forms.CharField(max_length=128, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    descripcion = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    nombre_completo = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))  # Nuevo campo agregado

    class Meta:
        model = TRegistroDeModulo
        fields = ['nombre', 'descripcion', 'nombre_completo']   # Usa los campos reales del modelo, pero serán manejados en save()
   
    def clean_nombre_completo(self):
        nombre_completo = self.cleaned_data.get('nombre_completo')
        
        # Verifica si el nombre_completo ya existe en la base de datos
        if TRegistroDeModulo.objects.filter(nombre_completo=nombre_completo).exists():
            raise ValidationError('El nombre completo ya existe. Por favor, elige uno diferente.')

        return nombre_completo
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        f_nombre = Fernet(ENCRYPTION_KEY_NOMBRE)
        f_descripcion = Fernet(ENCRYPTION_KEY_DESCRIPCION)
        instance._nombre = f_nombre.encrypt(self.cleaned_data['nombre'].encode()).decode()
        instance._descripcion = f_descripcion.encrypt(self.cleaned_data['descripcion'].encode()).decode()
        
        # Como 'nombre_completo' no necesita encriptación, simplemente lo asignamos
        instance.nombre_completo = self.cleaned_data.get('nombre_completo', '')
        
        if commit:
            instance.save()
        return instance