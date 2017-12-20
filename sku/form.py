from django import forms


class UploadFileForm(forms.Form):
    skufile = forms.FileField()
    store = forms.CharField()


class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file'
    )
