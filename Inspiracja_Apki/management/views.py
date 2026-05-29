import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Incydent, Zasob
from .forms import IncydentForm, ZasobForm





def lista_incydentow(request):
    filter_priority = request.GET.get('priority')
    filter_status = request.GET.get('status')
    filter_type = request.GET.get('type')

    incydenty = Incydent.objects.all().order_by('-id')

    if filter_priority:
        incydenty = incydenty.filter(priority=filter_priority)
    if filter_status:
        incydenty = incydenty.filter(status=filter_status)
    if filter_type:
        incydenty = incydenty.filter(type=filter_type)

    return render(request, 'management/incydenty.html', {
        'incydenty': incydenty,
        'selected_priority': filter_priority,
        'selected_status': filter_status,
        'selected_type': filter_type,
    })


def czy_dyspozytor(user):
    return user.role == 'dispatcher' or user.is_superuser

@login_required
@user_passes_test(czy_dyspozytor)
def nowy_incydent(request):
    if request.method == "POST":
        form = IncydentForm(request.POST)
        if form.is_valid():
            incydent = form.save(commit=False)
            incydent.reporter = request.user
            incydent.status = 'reported'
            incydent.save()
            return redirect('lista_incydentow')
    else:
        form = IncydentForm()

    return render(request, 'management/nowy_incydent.html', {'form': form})

@login_required
def lista_zasobow(request):
    filter_type = request.GET.get('type')
    filter_status = request.GET.get('status')
    filter_specjalizacja = request.GET.get('specialization')

    zasoby = Zasob.objects.all().order_by('type', 'name')

    if filter_type:
        zasoby = zasoby.filter(type=filter_type)
    if filter_status:
        zasoby = zasoby.filter(status=filter_status)
    if filter_specjalizacja:
        zasoby = zasoby.filter(specialization=filter_specjalizacja)

    # Get unique values for filter dropdowns
    all_types = Zasob.objects.values_list('type', flat=True).distinct()
    all_statuses = Zasob.STATUS_CHOICES  # Use model choices directly
    all_specjaliz = Zasob.objects.filter(specialization__gt='').values_list('specialization', flat=True).distinct()
    # Always include "General" for empty/default specialization
    all_specjaliz = set(all_specjaliz)
    all_specjaliz.add('General')

    return render(request, 'management/zasoby.html', {
        'zasoby': zasoby,
        'selected_type': filter_type,
        'selected_status': filter_status,
        'selected_specialization': filter_specjalizacja,
        'all_types': all_types,
        'all_statuses': all_statuses,
        'all_specjaliz': all_specjaliz,
    })

@login_required
def przypisz_zasob(request, zasob_id):
    zasob = get_object_or_404(Zasob, id=zasob_id)
    inc_id = request.GET.get('incydent_id')

    if inc_id:
        incydent = get_object_or_404(Incydent, id=inc_id)

        if incydent.status == 'closed':
            return redirect('szczegoly_incydentu', pk=inc_id)

        # Assign resource to incident using new FK
        zasob.assigned_to = incydent
        zasob.status = 'assigned'
        zasob.save()

        # Update incident status to in_progress
        incydent.status = 'in_progress'
        incydent.save()

        return redirect('szczegoly_incydentu', pk=inc_id)

    return redirect('lista_incydentow')



@login_required
def usun_przypisanie_zasobu(request, pk, zasob_id):
    incydent = get_object_or_404(Incydent, pk=pk)
    zasob = get_object_or_404(Zasob, pk=zasob_id)

    # Make sure resource is assigned to this incident before releasing
    if zasob.assigned_to_id == incydent.id:
        zasob.assigned_to = None
        zasob.status = 'available'
        zasob.save()

    # Optional: if no resources remain assigned and incident isn't closed, set back to "reported"
    assigned_left = Zasob.objects.filter(assigned_to=incydent).exists()
    if not assigned_left and incydent.status != 'closed':
        incydent.status = 'reported'
        incydent.save()

    return redirect('szczegoly_incydentu', pk=pk)


@login_required
def zakoncz_incydent(request, pk):
    incydent = get_object_or_404(Incydent, pk=pk)
    incydent.status = 'closed'
    incydent.save()

    # Release all resources assigned to this incident
    Zasob.objects.filter(assigned_to=incydent).update(
        assigned_to=None,
        status='available'
    )

    return redirect('szczegoly_incydentu', pk=pk)

@login_required
def szczegoly_incydentu(request, pk):
    incydent = get_object_or_404(Incydent, pk=pk)
    # Get resources assigned to this incident via FK
    przypisane_zasoby = Zasob.objects.filter(assigned_to=incydent)
    # Get available resources (not assigned to any incident)
    wolne_zasoby = Zasob.objects.filter(status='available')

    return render(request, 'management/incydent_detale.html', {
        'incydent': incydent,
        'zasoby': przypisane_zasoby,
        'wolne_zasoby': wolne_zasoby
    })


@login_required
def dashboard(request):
    total_incidents = Incydent.objects.count()
    active_incidents = Incydent.objects.exclude(status='closed').count()
    available_resources = Zasob.objects.filter(status='available').count()
    recent_incidents = Incydent.objects.all().order_by('-id')[:5]

    return render(request, 'management/dashboard.html', {
        'total': total_incidents,
        'active': active_incidents,
        'resources': available_resources,
        'recent_incidents': recent_incidents,
    })


@login_required
def archiwum_incydentow(request):
    total = Incydent.objects.count()
    active = Incydent.objects.exclude(status='closed').count()
    resolved = Incydent.objects.filter(status='closed').count()

    type_data = Incydent.objects.values('type').annotate(count=Count('id'))
    type_labels = [item['type'] for item in type_data]
    type_counts = [item['count'] for item in type_data]

    in_use = Zasob.objects.exclude(status='available').count()
    available = Zasob.objects.filter(status='available').count()

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

@login_required
def eksportuj_raport(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="raport_rescuenet.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Type', 'Priority', 'Status', 'Latitude', 'Longitude', 'Date Reported'])

    incydenty = Incydent.objects.all()
    for inc in incydenty:
        writer.writerow([inc.id, inc.type, inc.priority, inc.status, inc.latitude, inc.longitude, inc.reported_at])

    return response

@login_required
def usun_zasob(request, zasob_id):
    if request.user.role != 'admin' and not request.user.is_superuser:
        return redirect('lista_zasobow')

    zasob = get_object_or_404(Zasob, id=zasob_id)

    if request.method == 'POST':
        zasob.delete()

    return redirect('lista_zasobow')


@login_required
def dodaj_zasob(request):
    
    if request.user.role != 'admin' and not request.user.is_superuser:
        return redirect('dashboard')

    if request.method == 'POST':
        form = ZasobForm(request.POST)
        if form.is_valid():
            if Zasob.objects.filter(name=form.cleaned_data['name']).exists():
                form.add_error('name', 'A resource with this name already exists.')
            else:
                form.save()
                return redirect('lista_zasobow')
    else:
        form = ZasobForm() 

    return render(request, 'management/dodaj_zasob.html', {'form': form})
