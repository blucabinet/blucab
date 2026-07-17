from dal import autocomplete
from .models import Language, Actor, Director, Studio

class LanguageAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Language.objects.none()
        
        qs = Language.objects.all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs

class ActorAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Actor.objects.none()
            
        qs = Actor.objects.all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs

class DirectorAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Director.objects.none()
            
        qs = Director.objects.all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs

class StudioAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Studio.objects.none()
            
        qs = Studio.objects.all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs
        