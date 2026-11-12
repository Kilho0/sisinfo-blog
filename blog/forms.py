from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']
        labels = {
            'title': 'Título',
            'content': 'Conteúdo (HTML)',
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Título do post'}),
            'content': forms.Textarea(attrs={
                'rows': 14,
                'placeholder': '<p>Escreva o post em HTML...</p>',
            }),
        }
