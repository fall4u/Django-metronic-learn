from django import forms


class UploadFileForm(forms.Form):
    skufile = forms.FileField()
    store = forms.CharField()


class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file'
    )


class bookQueryForm(forms.Form):
    author = forms.CharField(required=False)

    # press  = forms.CharField()
    # ISBN   = forms.CharField()
    # status = forms.CharField()
    # bookname   = forms.CharField()

    def error_detail(self):
        error_response = {}
        error_response['data'] = self.errors
        return error_response
