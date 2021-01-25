from django.shortcuts import render, redirect
from .forms import InstructionsForm, SampleModelForm
from .pipeline import read_txt_pcr, standard_names, processing_data, run_r_script
from .tasks import add


def home_view(request):
    add.delay(3, 5)
    return render(request, 'core_app/home.html')


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
        form = SampleModelForm(request.POST, request.FILES)
        if form.is_valid():
            sample_obj = form.save(commit=False)
            sample_obj.save()

            path_results = read_txt_pcr(path_txt=sample_obj.file.url)
            standard_names(path_results)
            processing_data(path_results)
            run_r_script(path_results)

            return redirect('core_app:success')
    else:
        form = SampleModelForm()
    return render(request, 'core_app/upload_file.html', {'form': form})


def terms_view(request):
    return render(request, 'core_app/terms.html')


def privacy_view(request):
    return render(request, 'core_app/privacy.html')


def legal_view(request):
    return render(request, 'core_app/legal.html')


def success_view(request):
    return render(request, 'core_app/success.html')
