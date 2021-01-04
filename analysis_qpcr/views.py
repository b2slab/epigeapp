from django.shortcuts import render
from .forms import SampleForm


def main_view(request):
    if request.method == 'POST':
        form = SampleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return render(request, 'analysis_qpcr/success.html')
    else:
        form = SampleForm()
    return render(request, 'analysis_qpcr/upload_file.html', {'form': form})
