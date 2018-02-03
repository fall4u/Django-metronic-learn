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


class bookAddForm(forms.Form):
    name = forms.CharField(required=True)
    author = forms.CharField(required=True)
    press = forms.CharField(required=True)
    isbn = forms.IntegerField(required=True)
    price = forms.IntegerField(required=True)
    imageurl = forms.CharField(required=False)

class libBookAddForm(forms.Form):
    isbn = forms.IntegerField(required=True)
    uuid = forms.UUIDField(required=True)