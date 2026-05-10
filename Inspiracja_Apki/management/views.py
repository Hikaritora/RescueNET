from django.shortcuts import render
from django.db.models import Count
# Create your views here.
from django.shortcuts import render
from .models import Incydent

def lista_incydentow(request):
    # Pobieramy parametry z adresu URL (np. ?priority=wysoki)
    filter_priority = request.GET.get('priority')
    filter_status = request.GET.get('status')

    # Zaczynamy od wszystkich incydentów
    incydenty = Incydent.objects.all().order_by('-id')

    # Nakładamy filtry, jeśli zostały wybrane 
    if filter_priority:
        incydenty = incydenty.filter(priorytet=filter_priority)
    if filter_status:
        incydenty = incydenty.filter(status=filter_status)
    stats_data = Incydent.objects.values('typ').annotate(total=Count('id'))
    
    # Przygotowujemy listy dla JavaScript (etykiety i wartości)
    chart_labels = [item['typ'] for item in stats_data]
    chart_values = [item['total'] for item in stats_data]
    return render(request, 'management/incydenty.html', {
        'incydenty': incydenty,
        'selected_priority': filter_priority,
        'selected_status': filter_status
    })

from django.shortcuts import render, redirect
from .forms import IncydentForm
from django.contrib.auth.decorators import login_required, user_passes_test

def czy_dyspozytor(user):
    return user.rola == 'dyspozytor' or user.is_superuser

@login_required
@user_passes_test(czy_dyspozytor)

def nowy_incydent(request):
    if request.method == "POST":
        form = IncydentForm(request.POST)
        if form.is_valid():
            incydent = form.save(commit=False)
            incydent.zglaszajacy = request.user  # Przypisujemy zalogowanego dyspozytora
            incydent.status = 'zgłoszony'
            incydent.save()
            return redirect('lista_incydentow')
    else:
        form = IncydentForm()
    
    return render(request, 'management/nowy_incydent.html', {'form': form})

from .models import Zasob
@login_required
def lista_zasobow(request):
    # Pobieramy wszystkie zasoby
    zasoby = Zasob.objects.all().order_by('typ', 'nazwa')
    return render(request, 'management/zasoby.html', {'zasoby': zasoby})

from django.shortcuts import get_object_or_404, redirect, render
from .models import Zasob, Incydent # Pamiętaj o dodaniu Operacja, jeśli ją masz w modelach
@login_required
def przypisz_zasob(request, zasob_id):
    zasob = get_object_or_404(Zasob, id=zasob_id)
    inc_id = request.GET.get('incydent_id')
    
    if inc_id:
        incydent = get_object_or_404(Incydent, id=inc_id)
        
        # ZABEZPIECZENIE: Nie przypisuj do zakończonych spraw
        if incydent.status == 'zakończony':
            return redirect('szczegoly_incydentu', pk=inc_id)
            
        zasob.dostepnosc = False
        zasob.status = f"Assigned to INC-{incydent.id}"
        zasob.save()
        
        return redirect('szczegoly_incydentu', pk=inc_id)
    
    return redirect('lista_incydentow')


from django.shortcuts import get_object_or_404, redirect
from .models import Incydent, Zasob
@login_required
def zakoncz_incydent(request, pk):
    incydent = get_object_or_404(Incydent, pk=pk)
    incydent.status = 'zakończony'
    incydent.save()

    # AUTOMATYCZNE ZWALNIANIE: Znajdź wszystkie jednostki przypisane do tego INC
    Zasob.objects.filter(status__icontains=f"INC-{incydent.id}").update(
        dostepnosc=True,
        status='Available'
    )

    return redirect('szczegoly_incydentu', pk=pk)

from django.shortcuts import render, get_object_or_404
from .models import Incydent, Zasob
@login_required
@login_required
def szczegoly_incydentu(request, pk):
    incydent = get_object_or_404(Incydent, pk=pk)
    
    # Używamy icontains (case-insensitive), żeby było bezpieczniej
    # Szukamy po prostu numeru ID w statusie
    przypisane_zasoby = Zasob.objects.filter(status__icontains=f"INC-{incydent.id}")
    
    wolne_zasoby = Zasob.objects.filter(dostepnosc=True)
    
    return render(request, 'management/incydent_detale.html', {
        'incydent': incydent,
        'zasoby': przypisane_zasoby, # Ta zmienna musi trafić do szablonu
        'wolne_zasoby': wolne_zasoby
    })


# management/views.py
from .models import Incydent, Zasob
@login_required
def dashboard(request):
    total_incidents = Incydent.objects.count()
    active_incidents = Incydent.objects.exclude(status='zakończony').count()
    available_resources = Zasob.objects.filter(dostepnosc=True).count()
    
    # Pobieramy 5 najnowszych incydentów
    recent_incidents = Incydent.objects.all().order_by('-id')[:5]
    
    return render(request, 'management/dashboard.html', {
        'total': total_incidents,
        'active': active_incidents,
        'resources': available_resources,
        'recent_incidents': recent_incidents,
    })


import csv
from django.http import HttpResponse
from .models import Incydent

# 1. Widok listy archiwalnej
from django.db.models import Count
@login_required
def archiwum_incydentow(request):
    # 1. Statystyki ogólne
    total = Incydent.objects.count()
    active = Incydent.objects.exclude(status='zakończony').count()
    resolved = Incydent.objects.filter(status='zakończony').count()

    # 2. Dane do wykresu kołowego (Incidents by Type)
    type_data = Incydent.objects.values('typ').annotate(count=Count('id'))
    type_labels = [item['typ'] for item in type_data]
    type_counts = [item['count'] for item in type_data]

    # 3. Dane do wykresu słupkowego (Resource Status)
    in_use = Zasob.objects.filter(dostepnosc=False).count()
    available = Zasob.objects.filter(dostepnosc=True).count()

    # 4. Lista do tabeli
    archiwalne = Incydent.objects.all().order_by('-id')

    return render(request, 'management/archiwum.html', {
        'total': total,
        'active': active,
        'resolved': resolved,
        'type_labels': type_labels,
        'type_counts': type_counts,
        'resource_stats': [in_use, available],
        'incydenty': archiwalne
    })
# 2. Funkcja generowania raportu CSV
@login_required
def eksportuj_raport(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="raport_rescuenet.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Typ', 'Priorytet', 'Status', 'Szerokosc', 'Dlugosc'])

    incydenty = Incydent.objects.all()
    for inc in incydenty:
        writer.writerow([inc.id, inc.typ, inc.priorytet, inc.status, inc.lat, inc.lng])

    return response