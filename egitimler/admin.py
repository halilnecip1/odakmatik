from django.contrib import admin
from .models import Egitim
from satinalim.models import SatinAlim
from .models import Ders

admin.site.register(Egitim)
admin.site.register(SatinAlim)
admin.site.register(Ders)