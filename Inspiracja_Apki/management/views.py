import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Incydent, Zasob
from .forms import IncydentForm, ZasobForm


def is_dispatcher(user):
    return user.role == 'dispatcher' or user.is_superuser



def list_incidents(request):
    filter_priority = request.GET.get('priority')
    filter_status = request.GET.get('status')
    filter_type = request.GET.get('type')

    incidents = Incydent.objects.all().order_by('-id')

    if filter_priority:
        incidents = incidents.filter(priority=filter_priority)
    if filter_status:
        incidents = incidents.filter(status=filter_status)
    if filter_type:
        incidents = incidents.filter(type=filter_type)

    return render(request, 'management/incidents.html', {
        'incidents': incidents,
        'selected_priority': filter_priority,
        'selected_status': filter_status,
        'selected_type': filter_type,
    })


@login_required
@user_passes_test(is_dispatcher)
def create_incident(request):
    if request.method == "POST":
        form = IncydentForm(request.POST)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.reporter = request.user
            incident.status = 'reported'
            incident.save()
            return redirect('incident_list')
    else:
        form = IncydentForm()

    return render(request, 'management/create_incident.html', {'form': form})

@login_required
def list_resources(request):
    filter_type = request.GET.get('type')
    filter_status = request.GET.get('status')
    filter_specialization = request.GET.get('specialization')

    resources = Zasob.objects.all().order_by('type', 'name')

    if filter_type:
        resources = resources.filter(type=filter_type)
    if filter_status:
        resources = resources.filter(status=filter_status)
    if filter_specialization:
        resources = resources.filter(specialization=filter_specialization)

    # Get unique values for filter dropdowns
    all_types = Zasob.objects.values_list('type', flat=True).distinct()
    all_statuses = Zasob.STATUS_CHOICES  # Use model choices directly
    all_specializations = Zasob.objects.filter(specialization__gt='').values_list('specialization', flat=True).distinct()
    # Always include "General" for empty/default specialization
    all_specializations = set(all_specializations)
    all_specializations.add('General')

    return render(request, 'management/resources.html', {
        'resources': resources,
        'selected_type': filter_type,
        'selected_status': filter_status,
        'selected_specialization': filter_specialization,
        'all_types': all_types,
        'all_statuses': all_statuses,
        'all_specializations': all_specializations,
    })

@login_required
def assign_resource(request, zasob_id):
    resource = get_object_or_404(Zasob, id=zasob_id)
    incident_id = request.GET.get('incident_id')

    if incident_id:
        incident = get_object_or_404(Incydent, id=incident_id)

        if incident.status == 'closed':
            return redirect('incident_detail', pk=incident_id)

        # Assign resource to incident using new FK
        resource.assigned_to = incident
        resource.status = 'assigned'
        resource.save()

        # Update incident status to in_progress
        incident.status = 'in_progress'
        incident.save()

        return redirect('incident_detail', pk=incident_id)

    return redirect('incident_list')



@login_required
def unassign_resource(request, pk, zasob_id):
    incident = get_object_or_404(Incydent, pk=pk)
    resource = get_object_or_404(Zasob, pk=zasob_id)

    # Make sure resource is assigned to this incident before releasing
    if resource.assigned_to_id == incident.id:
        resource.assigned_to = None
        resource.status = 'available'
        resource.save()

    # Optional: if no resources remain assigned and incident isn't closed, set back to "reported"
    assigned_left = Zasob.objects.filter(assigned_to=incident).exists()
    if not assigned_left and incident.status != 'closed':
        incident.status = 'reported'
        incident.save()

    return redirect('incident_detail', pk=pk)


@login_required
def close_incident(request, pk):
    incident = get_object_or_404(Incydent, pk=pk)
    incident.status = 'closed'
    incident.save()

    # Release all resources assigned to this incident
    Zasob.objects.filter(assigned_to=incident).update(
        assigned_to=None,
        status='available'
    )

    return redirect('incident_detail', pk=pk)

@login_required
def incident_detail(request, pk):
    incident = get_object_or_404(Incydent, pk=pk)
    # Get resources assigned to this incident via FK
    assigned_resources = Zasob.objects.filter(assigned_to=incident)
    # Get available resources (not assigned to any incident)
    available_resources = Zasob.objects.filter(status='available')

    return render(request, 'management/incident_detail.html', {
        'incident': incident,
        'resources': assigned_resources,
        'available_resources': available_resources
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
def archive(request):
    total = Incydent.objects.count()
    active = Incydent.objects.exclude(status='closed').count()
    resolved = Incydent.objects.filter(status='closed').count()

    type_data = Incydent.objects.values('type').annotate(count=Count('id'))
    type_labels = [item['type'] for item in type_data]
    type_counts = [item['count'] for item in type_data]

    in_use = Zasob.objects.exclude(status='available').count()
    available = Zasob.objects.filter(status='available').count()

    archived_incidents = Incydent.objects.all().order_by('-id')

    return render(request, 'management/archive.html', {
        'total': total,
        'active': active,
        'resolved': resolved,
        'type_labels': type_labels,
        'type_counts': type_counts,
        'resource_stats': [in_use, available],
        'incidents': archived_incidents
    })

@login_required
def export_report(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="rescuenet_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Type', 'Priority', 'Status', 'Latitude', 'Longitude', 'Date Reported'])

    incidents = Incydent.objects.all()
    for incident in incidents:
        writer.writerow([incident.id, incident.type, incident.priority, incident.status, incident.latitude, incident.longitude, incident.reported_at])

    return response

@login_required
def delete_resource(request, zasob_id):
    if request.user.role != 'admin' and not request.user.is_superuser:
        return redirect('resource_list')

    resource = get_object_or_404(Zasob, id=zasob_id)

    if request.method == 'POST':
        resource.delete()

    return redirect('resource_list')


@login_required
def add_resource(request):

    if request.user.role != 'admin' and not request.user.is_superuser:
        return redirect('dashboard')

    if request.method == 'POST':
        form = ZasobForm(request.POST)
        if form.is_valid():
            if Zasob.objects.filter(name=form.cleaned_data['name']).exists():
                form.add_error('name', 'A resource with this name already exists.')
            else:
                form.save()
                return redirect('resource_list')
    else:
        form = ZasobForm() 

    return render(request, 'management/add_resource.html', {'form': form})
