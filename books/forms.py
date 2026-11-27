from django import forms
from .models import Book, Tag, Reading

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'year', 'tags']
        widgets = {
            'tags': forms.CheckboxSelectMultiple(),
        }

class TagForm(forms.ModelForm):

    class Meta:
        model = Tag
        fields = ['name']

class ReadingForm(forms.ModelForm):
    reread_eligible = forms.BooleanField(
        required = False,
        initial = False,
        label = "Eligble for reread?"
    )
    class Meta:
        model = Reading
        fields = ['book', 'start_date', 'end_date', 'asynchronous', 'status']