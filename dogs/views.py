from typing import Any, Dict
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from dogs.models import Breed, Dog



class ShowDogsView(TemplateView):
    template_name = "dogs/show_dogs.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['dogs'] = Dog.objects.all()
        return context

