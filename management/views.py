import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Case, When, IntegerField
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import resolve_url
from django.core.exceptions import ValidationError

from .models import Incident, Resource
from .forms import IncidentForm, ResourceForm


def is_dispatcher(user):
    return user.role == 'dispatcher' or user.role == 'admin' or user.is_superuser



@login_required
def list_incidents(request):
    filter_priority = request.GET.get('priority')
    filter_status = request.GET.get('status')
    filter_type = request.GET.get('type')

    # Apply filters first
    incidents = Incident.objects.all()
    if filter_priority:
        incidents = incidents.filter(priority=filter_priority)
    if filter_status:
        incidents = incidents.filter(status=filter_status)
    if filter_type:
        incidents = incidents.filter(type=filter_type)

    # Sorting: allow only a safe whitelist of sortable fields
    allowed_sorts = {
        'id': 'id',
        'type': 'type',
        'reported_at': 'reported_at',
        'priority': 'priority',
        'status': 'status',
        'latitude': 'latitude',
        'longitude': 'longitude',
    }
    current_sort = request.GET.get('sort', 'reported_at')
    current_dir = request.GET.get('dir', 'desc')
    if current_sort not in allowed_sorts:
        current_sort = 'reported_at'
    if current_dir not in ('asc', 'desc'):
        current_dir = 'desc'

    order_prefix = '' if current_dir == 'asc' else '-'
    # Special-case priority ordering with a custom fixed order
    if current_sort == 'priority':
        priority_order = Case(
            When(priority='low', then=1),
            When(priority='medium', then=2),
            When(priority='high', then=3),
            When(priority='critical', then=4),
            default=0,
            output_field=IntegerField()
        )
        incidents = incidents.annotate(priority_order=priority_order)
        # Use annotated field for ordering
        if current_dir == 'asc':
            incidents = incidents.order_by('priority_order')
        else:
            incidents = incidents.order_by('-priority_order')
    # Support multi-column ordering for location (latitude then longitude)
    elif current_sort == 'latitude':
        incidents = incidents.order_by(f"{order_prefix}latitude", f"{order_prefix}longitude")
    else:
        order_field = order_prefix + allowed_sorts[current_sort]
        incidents = incidents.order_by(order_field)
    # Build a small base querystring for preserving filters in header links
    base_qs_parts = []
    if filter_type:
        base_qs_parts.append(f"type={filter_type}")
    if filter_status:
        base_qs_parts.append(f"status={filter_status}")
    if filter_priority:
        base_qs_parts.append(f"priority={filter_priority}")
    base_qs = "&".join(base_qs_parts)
    if base_qs:
        base_qs += '&'

    return render(request, 'management/incidents.html', {
        'incidents': incidents,
        'selected_priority': filter_priority,
        'selected_status': filter_status,
        'selected_type': filter_type,
        'current_sort': current_sort,
        'current_dir': current_dir,
        'base_qs': base_qs,
    })


@login_required
def create_incident(request):
    if not is_dispatcher(request.user):
        messages.error(request, "You are not authorized to create incidents.")
        return redirect('dashboard')

    if request.method == "POST":
        form = IncidentForm(request.POST)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.reporter = request.user
            incident.status = 'reported'
            incident.full_clean()
            incident.save()
            return redirect('incident_list')
    else:
        form = IncidentForm()

    return render(request, 'management/create_incident.html', {'form': form})

@login_required
def list_resources(request):
    filter_type = request.GET.get('type')
    filter_status = request.GET.get('status')
    filter_specialization = request.GET.get('specialization')

    resources = Resource.objects.all().order_by('type', 'id')

    if filter_type:
        resources = resources.filter(type=filter_type)
    if filter_status:
        resources = resources.filter(status=filter_status)
    if filter_specialization:
        resources = resources.filter(specialization=filter_specialization)

    # Get unique values for filter dropdowns
    all_types = Resource.objects.values_list('type', flat=True).distinct()
    all_statuses = Resource.STATUS_CHOICES  # Use model choices directly
    all_specializations = Resource.objects.filter(specialization__gt='').values_list('specialization', flat=True).distinct()
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
    resource = get_object_or_404(Resource, id=zasob_id)
    incident_id = request.GET.get('incident_id')

    # Role check
    if not is_dispatcher(request.user):
        messages.error(request, "You are not authorized to assign resources to incidents.")
        if incident_id:
            return redirect('incident_detail', pk=incident_id)
        return redirect('incident_list')

    if incident_id:
        incident = get_object_or_404(Incident, id=incident_id)

        if incident.status == 'closed':
            return redirect('incident_detail', pk=incident_id)

        # Assign resource to incident using new FK
        resource.assigned_to = incident
        resource.status = 'assigned'
        resource.save()

        # Update incident status to in_progress
        incident.status = 'in_progress'
        try:
            incident.full_clean()
            incident.save()
        except ValidationError as e:
            messages.error(request, f"Cannot update incident status: {e.message}")
            resource.assigned_to = None
            resource.status = 'available'
            resource.save()

        return redirect('incident_detail', pk=incident_id)

    return redirect('incident_list')



@login_required
def unassign_resource(request, pk, zasob_id):
    # Role check
    if not is_dispatcher(request.user):
        messages.error(request, "You are not authorized to unassign resources from incidents.")
        return redirect('incident_detail', pk=pk)

    incident = get_object_or_404(Incident, pk=pk)
    resource = get_object_or_404(Resource, pk=zasob_id)

    # Make sure resource is assigned to this incident before releasing
    if resource.assigned_to_id == incident.id:
        resource.assigned_to = None
        resource.status = 'available'
        resource.save()

    # Optional: if no resources remain assigned and incident isn't closed, set back to "reported"
    assigned_left = Resource.objects.filter(assigned_to=incident).exists()
    if not assigned_left and incident.status != 'closed':
        incident.status = 'reported'
        try:
            incident.full_clean()
            incident.save()
        except ValidationError as e:
            messages.error(request, f"Error updating incident status: {e.message}")

    return redirect('incident_detail', pk=pk)


@login_required
def close_incident(request, pk):
    if not is_dispatcher(request.user):
        messages.error(request, "You are not authorized to close incidents.")
        return redirect('incident_detail', pk=pk)

    incident = get_object_or_404(Incident, pk=pk)
    incident.status = 'closed'
    incident.full_clean()
    incident.save()

    # Release all resources assigned to this incident
    Resource.objects.filter(assigned_to=incident).update(
        assigned_to=None,
        status='available'
    )

    return redirect('incident_detail', pk=pk)

@login_required
def incident_detail(request, pk):
    incident = get_object_or_404(Incident, pk=pk)
    # Get resources assigned to this incident via FK
    assigned_resources = Resource.objects.filter(assigned_to=incident)
    # Get available resources (not assigned to any incident)
    available_resources = Resource.objects.filter(status='available')

    return render(request, 'management/incident_detail.html', {
        'incident': incident,
        'resources': assigned_resources,
        'available_resources': available_resources
    })


@login_required
def dashboard(request):
    total_incidents = Incident.objects.count()
    active_incidents = Incident.objects.exclude(status='closed').count()
    available_resources = Resource.objects.filter(status='available').count()
    recent_incidents = Incident.objects.exclude(status='closed').order_by('-reported_at')[:10]

    return render(request, 'management/dashboard.html', {
        'total': total_incidents,
        'active': active_incidents,
        'resources': available_resources,
        'recent_incidents': recent_incidents,
    })


@login_required
def archive(request):
    total = Incident.objects.count()
    active = Incident.objects.exclude(status='closed').count()
    resolved = Incident.objects.filter(status='closed').count()

    type_data = Incident.objects.values('type').annotate(count=Count('id'))
    type_labels = [item['type'] for item in type_data]
    type_counts = [item['count'] for item in type_data]

    in_use = Resource.objects.exclude(status='available').count()
    available = Resource.objects.filter(status='available').count()

    archived_incidents = Incident.objects.filter(status='closed').order_by('-reported_at')

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

    incidents = Incident.objects.all()
    for incident in incidents:
        writer.writerow([incident.id, incident.type, incident.priority, incident.status, incident.latitude, incident.longitude, incident.reported_at])

    return response

@login_required
def delete_resource(request, zasob_id):
    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, "You are not authorized to delete resources.")
        return redirect('resource_list')

    resource = get_object_or_404(Resource, id=zasob_id)

    if request.method == 'POST':
        resource.delete()

    return redirect('resource_list')


@login_required
def mark_unavailable(request, zasob_id):
    """Mark a resource as unavailable (admin only). Only allowed when resource is currently available.

    This is idempotent and safe: if the resource is not available we simply redirect back.
    """
    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, "You are not authorized to change resource availability.")
        return redirect('resource_list')

    resource = get_object_or_404(Resource, id=zasob_id)

    if request.method == 'POST':
        # Only allow toggling when resource is currently available
        if resource.status == 'available':
            resource.status = 'unavailable'
            # ensure it's not assigned
            resource.assigned_to = None
            resource.save()

    return redirect('resource_list')


@login_required
def mark_available(request, zasob_id):
    """Mark a resource as available (admin only). Only allowed when resource is currently unavailable.

    This reverses the unavailable state and is idempotent: if resource isn't unavailable we simply redirect back.
    """
    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, "You are not authorized to change resource availability.")
        return redirect('resource_list')

    resource = get_object_or_404(Resource, id=zasob_id)

    if request.method == 'POST':
        # Only allow toggling when resource is currently unavailable
        if resource.status == 'unavailable':
            resource.status = 'available'
            # cleared assigned_to should already be None, but ensure consistency
            resource.assigned_to = None
            resource.save()

    return redirect('resource_list')


@login_required
def add_resource(request):

    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, "You are not authorized to add resources.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = ResourceForm(request.POST)
        if form.is_valid():
            if Resource.objects.filter(name=form.cleaned_data['name']).exists():
                form.add_error('name', 'A resource with this name already exists.')
            else:
                form.save()
                return redirect('resource_list')
    else:
        form = ResourceForm()

    return render(request, 'management/add_resource.html', {'form': form})
