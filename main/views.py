from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg
from .models import Category, Company, Job, Application

def home(request):
    jobs = Job.object.all()
    return render(request, 'main/home.html', {'jobs':jobs})


def job_list(request):
    jobs = Job.objects.all()
    jobs = jobs.select_related('company', 'category')
    jobs = jobs.exclude(is_active=False)

    q = request.GET.get('q')
    category = request.GET.get('category')
    company = request.GET.get('company')
    min_salary = request.GET.get('min_salary')
    max_salary = request.GET.get('max_salary')

    if q:
        jobs = jobs.filter(title__icontains=q)
    if category:
        jobs = jobs.filter(category_id=category)
    if company:
        jobs = jobs.filter(company_id=company)
    if min_salary:
        jobs = jobs.filter(salary__gte=min_salary)
    if max_salary:
        jobs = jobs.filter(salary__lte=max_salary)

    categories = Category.objects.all()
    companies = Company.objects.all()
    return render(request, 'main/job_list.html', {'jobs': jobs, 'categories': categories, 'companies': companies})


def job_detail(request, pk):
    jobs = Job.objects.prefetch_related('application_set')
    job = get_object_or_404(jobs, pk=pk)
    applications = job.application_set.all()
    return render(request, 'main/job_detail.html', {'job': job, 'applications': applications})



@login_required
def job_create(request):
    if request.method == 'POST':
        job = Job.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            salary=request.POST.get('salary'),
            location=request.POST.get('location'),
            employment_type=request.POST.get('employment_type'),
            company_id=request.POST.get('company'),
            category_id=request.POST.get('category'),
            created_by=request.user,
        )
        return redirect('job_detail', pk=job.pk)

    categories = Category.objects.all()
    companies = Company.objects.all()
    return render(request, 'main/job_create.html', {'categories': categories, 'companies': companies})




@login_required
def job_update(request, pk):
    job = get_object_or_404(Job, pk=pk)

    if job.created_by != request.user and not request.user.is_staff:
        return redirect('job_detail', pk=pk)

    if request.method == 'POST':
        job.title = request.POST.get('title')
        job.description = request.POST.get('description')
        job.salary = request.POST.get('salary')
        job.location = request.POST.get('location')
        job.employment_type = request.POST.get('employment_type')
        job.company_id = request.POST.get('company')
        job.category_id = request.POST.get('category')
        job.save()
        return redirect('job_detail', pk=pk)

    categories = Category.objects.all()
    companies = Company.objects.all()
    return render(request, 'main/job_update.html', {'job': job, 'categories': categories, 'companies': companies})





@login_required
def job_delete(request, pk):
    job = get_object_or_404(Job, pk=pk)

    if job.created_by != request.user and not request.user.is_staff:
        return redirect('job_detail', pk=pk)

    if request.method == 'POST':
        job.delete()
        return redirect('job_list')

    return render(request, 'main/job_delete.html', {'job': job})




@login_required
def job_apply(request, pk):
    job = get_object_or_404(Job, pk=pk)

    if request.method == 'POST':
        Application.objects.create(
            job=job,
            user=request.user,
            cover_letter=request.POST.get('cover_letter'),
        )
    return redirect('job_detail', pk=pk)


def stats(request):
    total = Job.objects.aggregate(count=Count('id'), avg_salary=Avg('salary'))
    applications_count = Application.objects.count()
    companies = Company.objects.annotate(jobs_count=Count('job'))
    return render(request, 'main/stats.html', {'total': total, 'applications_count': applications_count, 'companies': companies})