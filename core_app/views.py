from django.shortcuts import render, redirect
from .forms import UploadFileForm, InstructionsForm
from .pipeline import handle_uploaded_file, read_txt_pcr, standard_names, processing_data, run_max


def instructions_view(request):
    if request.method == 'POST':
        form = InstructionsForm(request.POST)
        if form.is_valid():
            return redirect('core_app:analysis')
    else:
        form = InstructionsForm()
    return render(request, 'core_app/instructions.html', {'form': form})


def analysis_view(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            read_txt_pcr()
            standard_names()
            processing_data()
            run_max()
            return render(request, 'core_app/success.html')
    else:
        form = UploadFileForm()
    return render(request, 'core_app/upload_file.html', {'form': form})
