from django.forms import ModelForm, TextInput, Textarea, ValidationError
from MainApp.models import Snippet

# Описание возможностей по настройке форм
# https://docs.djangoproject.com/en/dev/ref/forms/widgets/#django.forms.Widget.attrs

class SnippetForm(ModelForm):
    class Meta:
        model = Snippet
        # Описываем поля, которые будем заполнять в форме
        fields = ['name', 'lang', 'code']
        labels = {"name": "", "lang": "", "code":""}
        widgets = {
            "name": TextInput(attrs={
                "class": "form-control",
                "placeholder": "Название сниппета",
                "style": "max-width:300px",
            }),
            "code": Textarea(attrs={
               "placeholder": "Код сниппета",
                "rows": 5,
                "class": "input-large",
                "style": "width: 50% !important; resize: vertical !important;",     
            })
        }



    def clean_name(self):
        """Метод для проверки длины поля <name>"""
        snippet_name = self.cleaned_data.get("name")
        if snippet_name is not None and len(snippet_name) > 3:
            return snippet_name
        raise ValidationError("Snippet's name is too short.")