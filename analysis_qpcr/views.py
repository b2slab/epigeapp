from django.shortcuts import render
from .forms import SampleForm


def main_view(request):
    data_form = None
    if request.method == 'POST':
        register_form = SampleForm(request.POST, request.FILES)
        if register_form.is_valid():
            new_register = register_form
            new_register.save()
            data_form = new_register.cleaned_data
    else:
        register_form = SampleForm()
    return render(request, 'analysis_qpcr/analysis.html', {'register_form': register_form, 'data_register': data_form})
