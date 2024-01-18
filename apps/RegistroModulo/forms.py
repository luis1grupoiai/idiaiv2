from django import forms
from .models import TRegistroDeModulo

class ModuloForm(forms.ModelForm):
    descripcion = forms.CharField(max_length=128, required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}))  # Usar PasswordInput para ocultar la entrada

    class Meta:
        model = TRegistroDeModulo
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Establece la descripcion encriptada en el modelo
        instance.descripcion = self.cleaned_data['descripcion']
        if commit:
            instance.save()
        return instance