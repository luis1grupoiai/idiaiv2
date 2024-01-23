from django import forms
from .models import TRegistroDeModulo
from cryptography.fernet import Fernet


ENCRYPTION_KEY_DESCRIPCION = b'VVsQPaM9IhXYrWNwLyKkAnmJdzdFR8R0MwdvZpHGsA8='
ENCRYPTION_KEY_NOMBRE = b'VVsQPaM9IhXYrWNwLyKkAnmJdzdFR8R0MwdvZpHGsA8='



class ModuloForm(forms.ModelForm):
    nombre = forms.CharField(max_length=128, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    descripcion = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), required=False)

    class Meta:
        model = TRegistroDeModulo
        fields = ['nombre', 'descripcion']  # Usa los campos reales del modelo, pero serán manejados en save()
   
    
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        f_nombre = Fernet(ENCRYPTION_KEY_NOMBRE)
        f_descripcion = Fernet(ENCRYPTION_KEY_DESCRIPCION)
        instance._nombre = f_nombre.encrypt(self.cleaned_data['nombre'].encode()).decode()
        instance._descripcion = f_descripcion.encrypt(self.cleaned_data['descripcion'].encode()).decode()
        if commit:
            instance.save()
        return instance