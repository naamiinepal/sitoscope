from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib import messages

from . import models
from . import forms

# Create your views here.
def index(request: HttpRequest):
    return render(request, "sample/index.html")


class SymptomsView(View):
    def get(self, request: HttpRequest):
        symptoms = models.DiarrheaSymptom.objects.all().order_by("name")
        context = {"symptoms": symptoms}
        return render(request, "sample/diarrhea_symptoms/list.html", context=context)


class SymptomFormView(View):
    form_class = forms.DiarrheaSymptomsForm
    template_name = 'sample/diarrhea_symptoms/form.html'
    
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        user = request.user
        form = self.form_class(request.POST)
        if form.is_valid():
            symptom = form.save(commit=False)
            symptom.user = user
            symptom.save()
            messages.success(request, "Successfully added symptom.")
            return redirect('sample:get_diarrhea_symptoms')

        return render(request, self.template_name, {'form': form})


