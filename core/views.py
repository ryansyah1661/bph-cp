from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django import forms
from django.db.models import Min, Max, Q
from django.contrib.auth import logout
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.core.serializers import serialize
from django.http import HttpResponse
from .models import Article, Project, Client, Story, Service, Location, Category, Modul, ContactMessage, Gallery, Profile, Folder, TeamMember

# ==========================================
# JALUR FRONTEND WEBSITE (NAVBAR & MENU)
# ==========================================
def homepage(request):
    articles = Article.objects.order_by('-tanggal')[:3]
    stories = Story.objects.order_by('-tanggal')[:1]
    return render(request, 'core/homepage.html', {
        'articles': articles,
        'stories': stories,
    })

def about_view(request):
    advisors = TeamMember.objects.filter(kategori='advisors').order_by('urutan', 'id')
    executives = TeamMember.objects.filter(kategori='executives').order_by('urutan', 'id')
    staff = TeamMember.objects.filter(kategori='staff').order_by('urutan', 'id')
    associates = TeamMember.objects.filter(kategori='associates').order_by('urutan', 'id')

    return render(request, 'core/about.html', {
        'advisors': advisors,
        'executives': executives,
        'staff': staff,
        'associates': associates,
    })

def services_view(request):
    services_nrm = Service.objects.filter(portfolio='NRM').prefetch_related('categories')
    services_nru = Service.objects.filter(portfolio='NRU').prefetch_related('categories')
    return render(request, 'core/services.html', {
        'services_nrm': services_nrm,
        'services_nru': services_nru,
    })

def experience_view(request):
    projects = Project.objects.select_related('client').prefetch_related('locations', 'categories').order_by('-tahun', '-id')
    categories = Category.objects.filter(projects__isnull=False).distinct().order_by('name')
    years = Project.objects.order_by('-tahun').values_list('tahun', flat=True).distinct()
    
    clients_swasta = Client.objects.filter(sektor='swasta')
    clients_publik = Client.objects.filter(sektor='publik')

    total_proyek = Project.objects.count()
    total_provinsi = Location.objects.filter(projects__isnull=False).distinct().count()
    total_klien = Client.objects.filter(projects__isnull=False).distinct().count()
    
    tahun_bounds = Project.objects.all().aggregate(Min('tahun'), Max('tahun'))
    if tahun_bounds['tahun__min'] and tahun_bounds['tahun__max']:
        total_tahun_bekerja = (tahun_bounds['tahun__max'] - tahun_bounds['tahun__min']) + 1
    else:
        total_tahun_bekerja = 5

    locations_with_projects = Location.objects.filter(projects__isnull=False).prefetch_related('projects').distinct()
    all_stories = Story.objects.select_related('lokasi', 'project').order_by('-tanggal')
    selected_year = request.GET.get('year', 'all')

    return render(request, 'core/experience.html', {
        'projects': projects,
        'categories': categories,
        'years': years,
        'clients_swasta': clients_swasta,
        'clients_publik': clients_publik,
        'selected_year': selected_year,
        'total_tahun_bekerja': total_tahun_bekerja,
        'total_proyek': total_proyek,
        'total_provinsi': total_provinsi,
        'total_klien': total_klien,
        'locations_with_projects': locations_with_projects,
        'all_stories': all_stories,
    })

def provinces_geojson_api(request):
    geojson_path = settings.BASE_DIR / 'static' / 'data' / 'indonesia_provinces.json'
    with open(geojson_path, 'r', encoding='utf-8') as f:
        geojson_data = f.read()
    return HttpResponse(geojson_data, content_type='application/json')

def gallery_view(request):
    articles = Article.objects.order_by('-tanggal')
    stories = Story.objects.order_by('-tanggal')
    documents = Modul.objects.order_by('-tanggal_rilis')
    categories = Category.objects.filter(folders__isnull=False).distinct().order_by('name')
    gallery_items = Gallery.objects.all().order_by('-tanggal_upload', '-id')
    folders = Folder.objects.select_related('kategori').prefetch_related('images').order_by('-tahun', '-id')

    return render(request, 'core/gallery.html', {
        'articles': articles,
        'stories': stories,
        'gallery_items': gallery_items,
        'folders': folders,
        'documents': documents,
        'categories': categories,
    })

def contact_view(request):
    if request.method == 'POST':
        nama = request.POST.get('nama_lengkap')
        email = request.POST.get('email')
        subjek = request.POST.get('subjek')
        pesan = request.POST.get('pesan')
        
        if nama and email and subjek and pesan:
            contact_msg = ContactMessage.objects.create(
                nama_lengkap=nama,
                email=email,
                subjek=subjek,
                pesan=pesan
            )
            
            try:
                recipient_email = getattr(settings, 'BPH_NOTIFICATION_EMAIL', 'muhammadrian1602@gmail.com')
                sender_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@bhumipasahijau.com')
                
                email_subject = f"[Pesan Baru Web BPH] {subjek}"
                email_body = f"""
Halo Tim PT Bhumi Pasa Hijau,

Ada pesan baru masuk melalui Kontak Website:

--------------------------------------------------
Nama Pengirim : {nama}
Email Pengirim: {email}
Subjek/Topik  : {subjek}

Isi Pesan:
{pesan}
--------------------------------------------------

Pesan ini telah tersimpan di Dashboard Admin Bhumi Pasa Hijau.
                """
                
                send_mail(
                    subject=email_subject,
                    message=email_body,
                    from_email=sender_email,
                    recipient_list=[recipient_email],
                    fail_silently=False
                )
            except Exception as e:
                print(f"Gagal mengirim notifikasi email: {e}")

            messages.success(request, 'Pesan Anda berhasil dikirim! Tim kami akan segera menghubungi Anda.')
            return redirect('contact')
        else:
            messages.error(request, 'Gagal mengirim pesan. Harap isi semua kolom formulir dengan benar.')

    return render(request, 'core/contact.html')

def story_view(request):
    stories_data = Story.objects.select_related('lokasi', 'project').order_by('-tanggal')
    return render(request, 'core/story.html', {'stories': stories_data})

# ==========================================
# JALUR FRONTEND HALAMAN DETAIL
# ==========================================
def detail_articles_view(request, slug):
    article_data = get_object_or_404(Article, Q(slug_ind=slug) | Q(slug_en=slug) if hasattr(Article, 'slug_en') else Q(slug=slug))
    
    related_articles = Article.objects.filter(
        Q(author=article_data.author)
    ).exclude(pk=article_data.pk).order_by('-tanggal')[:3]
    
    if related_articles.count() < 3:
        extra_articles = Article.objects.exclude(pk=article_data.pk).exclude(pk__in=related_articles.values_list('pk', flat=True)).order_by('-tanggal')[:3 - related_articles.count()]
        related_articles = list(related_articles) + list(extra_articles)

    return render(request, 'core/detail-articles.html', {
        'article': article_data,
        'related_articles': related_articles
    })

def detail_experience_view(request, slug):
    project_data = get_object_or_404(
        Project.objects.select_related('client', 'service_portfolio').prefetch_related('locations', 'categories', 'metrics'),
        Q(slug_ind=slug) | Q(slug_en=slug) if hasattr(Project, 'slug_en') else Q(slug=slug)
    )
    related_projects = Project.objects.filter(
        categories__in=project_data.categories.all()
    ).exclude(pk=project_data.pk).distinct().order_by('-tahun', '-id')[:3]
    
    return render(request, 'core/detail-experience.html', {
        'project': project_data,
        'related_projects': related_projects,
    })

def detail_services_view(request, slug):
    # Menggunakan Q(slug_ind=slug) | Q(slug_en=slug) agar aman mendeteksi slug ID maupun EN
    query_condition = Q(slug_ind=slug) | Q(slug_en=slug) if hasattr(Service, 'slug_en') else Q(slug=slug)
    service_data = get_object_or_404(Service, query_condition)
    
    nrm_services = Service.objects.filter(portfolio='NRM')
    nru_services = Service.objects.filter(portfolio='NRU')
    
    return render(request, 'core/detail-services.html', {
        'service': service_data,
        'nrm_services': nrm_services,
        'nru_services': nru_services,
    })

def detail_story_view(request, slug):
    story_data = get_object_or_404(
        Story.objects.select_related('lokasi', 'project'), 
        Q(slug_ind=slug) | Q(slug_en=slug) if hasattr(Story, 'slug_en') else Q(slug=slug)
    )
    
    related_stories = Story.objects.filter(
        Q(author=story_data.author) | Q(lokasi=story_data.lokasi)
    ).exclude(pk=story_data.pk).distinct().order_by('-tanggal')[:3]
    
    if related_stories.count() < 3:
        extra_stories = Story.objects.exclude(pk=story_data.pk).exclude(pk__in=related_stories.values_list('pk', flat=True)).order_by('-tanggal')[:3 - related_stories.count()]
        related_stories = list(related_stories) + list(extra_stories)

    return render(request, 'core/detail-story.html', {
        'story': story_data,
        'related_stories': related_stories
    })


# ==========================================
# PROTEKSI & SECURITY
# ==========================================
@login_required(login_url='/be/login/')
def custom_dashboard(request):
    if not request.user.is_staff:
        logout(request)  # Logout otomatis akun non-staff dari sesi
        messages.error(request, 'Akses ditolak! Hanya pengguna dengan hak staff yang dapat mengakses dashboard.')
        return redirect('homepage')
    context = {
        'total_articles': Article.objects.count(),
        'total_projects': Project.objects.count(),
        'total_clients': Client.objects.count(),
        'total_stories': Story.objects.count(),
        'total_documents': Modul.objects.count(),  
        'total_messages': ContactMessage.objects.count(),
        'total_gallery': Gallery.objects.count(),
        'total_team': TeamMember.objects.count(),
        'recent_articles': Article.objects.order_by('-tanggal', '-id')[:5],
        'recent_projects': Project.objects.order_by('-tahun', '-id')[:5],
    }
    return render(request, 'core/custom_admin/dashboard.html', context)

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/be/login/'
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        if self.request.user.is_authenticated and not self.request.user.is_staff:
            logout(self.request)  # Logout otomatis akun non-staff dari sesi
            messages.error(self.request, 'Akses ditolak! Hanya pengguna dengan hak staff yang dapat mengakses panel admin.')
            return redirect('homepage')
        return super().handle_no_permission()


# ==========================================
# 1. MANAGEMENT ARTIKEL & WAWASAN TEKNIS
# ==========================================
class ArticleListView(AdminRequiredMixin, ListView):
    model = Article
    template_name = 'core/custom_admin/articles/articles_list.html'
    context_object_name = 'articles'

    def get_queryset(self):
        return Article.objects.all().order_by('-tanggal', '-id')

class ArticleCreateView(AdminRequiredMixin, CreateView):
    model = Article
    template_name = 'core/custom_admin/articles/articles_form.html'
    fields = ['judul_ind', 'judul_en', 'slug_ind', 'slug_en', 'short_ind', 'short_en', 'deskripsi_ind', 'deskripsi_en', 'tanggal', 'gambar']
    success_url = reverse_lazy('article_list')

    def form_valid(self, form):
        from django.utils.text import slugify
        
        user = self.request.user
        form.instance.author = user.profile.nama_lengkap if hasattr(user, 'profile') and user.profile.nama_lengkap else user.username

        base_slug = form.cleaned_data.get('slug') or slugify(form.cleaned_data.get('judul_ind') or form.cleaned_data.get('judul'))
        slug = base_slug[:200]
        
        queryset = Article.objects.filter(slug=slug)
        if queryset.exists():
            original_slug = slug
            counter = 1
            while Article.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1
                
        form.instance.slug = slug
        messages.success(self.request, 'Artikel baru berhasil ditambahkan!')
        return super().form_valid(form)

class ArticleUpdateView(AdminRequiredMixin, UpdateView):
    model = Article
    template_name = 'core/custom_admin/articles/articles_form.html'
    fields = ['judul_ind', 'judul_en', 'slug_ind', 'slug_en', 'short_ind', 'short_en', 'deskripsi_ind', 'deskripsi_en', 'tanggal', 'gambar']
    success_url = reverse_lazy('article_list')

    def form_valid(self, form):
        from django.utils.text import slugify
        
        user = self.request.user
        form.instance.author = user.profile.nama_lengkap if hasattr(user, 'profile') and user.profile.nama_lengkap else user.username

        base_slug = form.cleaned_data.get('slug') or slugify(form.cleaned_data.get('judul_ind') or form.cleaned_data.get('judul'))
        slug = base_slug[:200]
        
        queryset = Article.objects.filter(slug=slug).exclude(pk=self.object.pk)
        if queryset.exists():
            original_slug = slug
            counter = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.object.pk).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1
                
        form.instance.slug = slug
        messages.success(self.request, 'Perubahan artikel berhasil disimpan!')
        return super().form_valid(form)

@login_required(login_url='/be/login/')
@user_passes_test(lambda u: u.is_staff, login_url='/be/login/')
def article_delete_view(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Artikel berhasil dihapus!')
    return redirect('article_list')


# ==========================================
# 2. MANAGEMENT PROYEK (EXPERIENCE)
# ==========================================
class ProjectListView(AdminRequiredMixin, ListView):
    model = Project
    template_name = 'core/custom_admin/experience/experience_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        return Project.objects.all().order_by('-tahun', '-id')

class ProjectCreateView(AdminRequiredMixin, CreateView):
    model = Project
    template_name = 'core/custom_admin/experience/experience_form.html'
    fields = ['name_ind', 'name_en', 'slug_ind', 'slug_en', 'description_ind', 'description_en', 'tahun', 'image', 'client', 'service_portfolio', 'locations', 'categories']
    success_url = reverse_lazy('project_list')

    def form_valid(self, form):
        messages.success(self.request, 'Proyek baru berhasil ditambahkan!')
        return super().form_valid(form)

class ProjectUpdateView(AdminRequiredMixin, UpdateView):
    model = Project
    template_name = 'core/custom_admin/experience/experience_form.html'
    fields = ['name_ind', 'name_en', 'slug_ind', 'slug_en', 'description_ind', 'description_en', 'tahun', 'image', 'client', 'service_portfolio', 'locations', 'categories']
    success_url = reverse_lazy('project_list')

    def form_valid(self, form):
        messages.success(self.request, 'Perubahan data proyek berhasil disimpan!')
        return super().form_valid(form)

@login_required(login_url='/be/login/')
@user_passes_test(lambda u: u.is_staff, login_url='/be/login/')
def project_delete_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Data proyek berhasil dihapus!')
    return redirect('project_list')

# ==========================================
# 3. MANAGEMENT CERITA LAPANGAN
# ==========================================
class StoryListView(AdminRequiredMixin, ListView):
    model = Story
    template_name = 'core/custom_admin/story/story_list.html'
    context_object_name = 'stories'

    def get_queryset(self):
        return Story.objects.all().order_by('-tanggal', '-id')

class StoryCreateView(AdminRequiredMixin, CreateView):
    model = Story
    template_name = 'core/custom_admin/story/story_form.html'
    fields = ['judul_ind', 'judul_en', 'slug_ind', 'slug_en', 'tanggal', 'lokasi', 'short_ind', 'short_en', 'deskripsi_ind', 'deskripsi_en', 'gambar', 'project']
    success_url = reverse_lazy('story_list')

    def form_valid(self, form):
        from django.utils.text import slugify

        user = self.request.user
        form.instance.author = user.profile.nama_lengkap if hasattr(user, 'profile') and user.profile.nama_lengkap else user.username

        base_slug = form.cleaned_data.get('slug') or slugify(form.cleaned_data.get('judul_ind'))
        slug = base_slug[:200]

        queryset = Story.objects.filter(slug=slug)
        if queryset.exists():
            original_slug = slug
            counter = 1
            while Story.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1

        form.instance.slug = slug
        messages.success(self.request, 'Cerita lapangan baru berhasil ditambahkan!')
        return super().form_valid(form)

class StoryUpdateView(AdminRequiredMixin, UpdateView):
    model = Story
    template_name = 'core/custom_admin/story/story_form.html'
    fields = ['judul_ind', 'judul_en', 'slug_ind', 'slug_en', 'tanggal', 'lokasi', 'short_ind', 'short_en', 'deskripsi_ind', 'deskripsi_en', 'gambar', 'project']
    success_url = reverse_lazy('story_list')

    def form_valid(self, form):
        from django.utils.text import slugify

        user = self.request.user
        form.instance.author = user.profile.nama_lengkap if hasattr(user, 'profile') and user.profile.nama_lengkap else user.username

        base_slug = form.cleaned_data.get('slug') or slugify(form.cleaned_data.get('judul_ind'))
        slug = base_slug[:200]

        queryset = Story.objects.filter(slug=slug).exclude(pk=self.object.pk)
        if queryset.exists():
            original_slug = slug
            counter = 1
            while Story.objects.filter(slug=slug).exclude(pk=self.object.pk).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1

        form.instance.slug = slug
        messages.success(self.request, 'Perubahan cerita lapangan berhasil disimpan!')
        return super().form_valid(form)

@login_required(login_url='/be/login/')
@user_passes_test(lambda u: u.is_staff, login_url='/be/login/')
def story_delete_view(request, pk):
    story = get_object_or_404(Story, pk=pk)
    if request.method == 'POST':
        story.delete()
        messages.success(request, 'Cerita lapangan berhasil dihapus!')
    return redirect('story_list')


# ==========================================
# 4. MANAGEMENT MITRA / KLIEN
# ==========================================
class ClientListView(AdminRequiredMixin, ListView):
    model = Client
    template_name = 'core/custom_admin/client/client_list.html'
    context_object_name = 'clients'

    def get_queryset(self):
        return Client.objects.all().order_by('-id')

class ClientCreateView(AdminRequiredMixin, CreateView):
    model = Client
    template_name = 'core/custom_admin/client/client_form.html'
    fields = ['nama_ind', 'nama_en', 'sektor', 'logo']
    success_url = reverse_lazy('client_list')

    def form_valid(self, form):
        messages.success(self.request, 'Klien baru berhasil ditambahkan!')
        return super().form_valid(form)

class ClientUpdateView(AdminRequiredMixin, UpdateView):
    model = Client
    template_name = 'core/custom_admin/client/client_form.html'
    fields = ['nama_ind', 'nama_en', 'sektor', 'logo']
    success_url = reverse_lazy('client_list')

    def form_valid(self, form):
        messages.success(self.request, 'Data klien berhasil diperbarui!')
        return super().form_valid(form)

@login_required(login_url='/be/login/')
@user_passes_test(lambda u: u.is_staff, login_url='/be/login/')
def client_delete_view(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        client.delete()
        messages.success(request, 'Data klien berhasil dihapus!')
    return redirect('client_list')


# ==========================================
# 5. MANAGEMENT LAYANAN (SERVICES)
# ==========================================
class ServiceListView(AdminRequiredMixin, ListView):
    model = Service
    template_name = 'core/custom_admin/services/services_list.html'
    context_object_name = 'services'

    def get_queryset(self):
        return Service.objects.all().order_by('-id')

class ServiceCreateView(AdminRequiredMixin, CreateView):
    model = Service
    template_name = 'core/custom_admin/services/services_form.html'
    fields = ['title_ind', 'title_en', 'slug_ind', 'slug_en', 'approach_ind', 'approach_en', 'portfolio', 'icon', 'thumbnail', 'bg_image', 'categories']
    success_url = reverse_lazy('service_list')

    def form_valid(self, form):
        messages.success(self.request, 'Layanan baru berhasil ditambahkan!')
        return super().form_valid(form)

class ServiceUpdateView(AdminRequiredMixin, UpdateView):
    model = Service
    template_name = 'core/custom_admin/services/services_form.html'
    fields = ['title_ind', 'title_en', 'slug_ind', 'slug_en', 'approach_ind', 'approach_en', 'portfolio', 'icon', 'thumbnail', 'bg_image', 'categories']
    success_url = reverse_lazy('service_list')

    def form_valid(self, form):
        messages.success(self.request, 'Data layanan berhasil diperbarui!')
        return super().form_valid(form)

@login_required(login_url='/be/login/')
@user_passes_test(lambda u: u.is_staff, login_url='/be/login/')
def service_delete_view(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Data Layanan berhasil dihapus!')
    return redirect('service_list')


# ==========================================
# 6. MANAGEMENT LOKASI WILAYAH
# ==========================================
class LocationListView(AdminRequiredMixin, ListView):
    model = Location
    template_name = 'core/custom_admin/location/location_list.html'
    context_object_name = 'locations'

    def get_queryset(self):
        return Location.objects.all().order_by('-id')

class LocationCreateView(AdminRequiredMixin, CreateView):
    model = Location
    template_name = 'core/custom_admin/location/location_form.html'
    fields = ['nama_provinsi_ind', 'nama_provinsi_en', 'slug_ind', 'slug_en', 'kode_wilayah', 'geom']
    success_url = reverse_lazy('location_list')

    def form_valid(self, form):
        messages.success(self.request, 'Lokasi baru berhasil ditambahkan!')
        return super().form_valid(form)

class LocationUpdateView(AdminRequiredMixin, UpdateView):
    model = Location
    template_name = 'core/custom_admin/location/location_form.html'
    fields = ['nama_provinsi_ind', 'nama_provinsi_en', 'slug_ind', 'slug_en', 'kode_wilayah', 'geom']
    success_url = reverse_lazy('location_list')

    def form_valid(self, form):
        messages.success(self.request, 'Data lokasi berhasil diperbarui!')
        return super().form_valid(form)

@login_required(login_url='/be/login/')
@user_passes_test(lambda u: u.is_staff, login_url='/be/login/')
def location_delete_view(request, pk):
    location = get_object_or_404(Location, pk=pk)
    if request.method == 'POST':
        location.delete()
        messages.success(request, 'Data lokasi berhasil dihapus!')
    return redirect('location_list')


# ==========================================
# 7. MANAGEMENT KATEGORI
# ==========================================
class CategoryListView(AdminRequiredMixin, ListView):
    model = Category
    template_name = 'core/custom_admin/category/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.all().order_by('-id')

class CategoryCreateView(AdminRequiredMixin, CreateView):
    model = Category
    template_name = 'core/custom_admin/category/category_form.html'
    fields = ['name_ind', 'name_en', 'slug_ind', 'slug_en']
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Kategori baru berhasil ditambahkan!')
        return super().form_valid(form)

class CategoryUpdateView(AdminRequiredMixin, UpdateView):
    model = Category
    template_name = 'core/custom_admin/category/category_form.html'
    fields = ['name_ind', 'name_en', 'slug_ind', 'slug_en']
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Data kategori berhasil diperbarui!')
        return super().form_valid(form)

@login_required(login_url='/be/login/')
@user_passes_test(lambda u: u.is_staff, login_url='/be/login/')
def category_delete_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Data kategori berhasil dihapus!')
    return redirect('category_list')


# ==========================================
# 8. MANAGEMENT MODUL DOKUMEN
# ==========================================
class DocumentListView(AdminRequiredMixin, ListView):
    model = Modul  
    template_name = 'core/custom_admin/modul/modul_list.html'
    context_object_name = 'documents'

    def get_queryset(self):
        return Modul.objects.all().order_by('-tanggal_rilis', '-id')

class DocumentCreateView(AdminRequiredMixin, CreateView):
    model = Modul
    template_name = 'core/custom_admin/modul/modul_form.html'
    fields = '__all__'
    success_url = reverse_lazy('document_list')

    def form_valid(self, form):
        messages.success(self.request, 'Modul baru berhasil ditambahkan!')
        return super().form_valid(form)

class DocumentUpdateView(AdminRequiredMixin, UpdateView):
    model = Modul
    template_name = 'core/custom_admin/modul/modul_form.html'
    fields = '__all__'
    success_url = reverse_lazy('document_list')

    def form_valid(self, form):
        messages.success(self.request, 'Data modul berhasil diperbarui!')
        return super().form_valid(form)

@login_required(login_url='/be/login/')
@user_passes_test(lambda u: u.is_staff, login_url='/be/login/')
def document_delete_view(request, pk):
    doc = get_object_or_404(Modul, pk=pk)
    if request.method == 'POST':
        doc.delete()
        messages.success(request, 'Data modul berhasil dihapus!')
    return redirect('document_list')


# ==========================================
# 9. MANAGEMENT KONTAK / PESAN MASUK
# ==========================================
class ContactListView(AdminRequiredMixin, ListView):
    model = ContactMessage
    template_name = 'core/custom_admin/contact/contact_list.html'
    context_object_name = 'contacts'

    def get_queryset(self):
        return ContactMessage.objects.all().order_by('-tanggal_kirim')

@login_required(login_url='/be/login/')
@user_passes_test(lambda u: u.is_staff, login_url='/be/login/')
def contact_delete_view(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    if request.method == 'POST':
        msg.delete()
        messages.success(request, 'Pesan berhasil dihapus!')
    return redirect('contact_list')

@login_required(login_url='/be/login/')
def mark_message_as_read(request, pk):
    if request.method == 'POST':
        msg = get_object_or_404(ContactMessage, pk=pk)
        if not msg.is_read:
            msg.is_read = True
            msg.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)


# ==========================================
# 10. MANAGEMENT GALERI DOKUMENTASI
# ==========================================
class GalleryListView(AdminRequiredMixin, ListView):
    model = Gallery
    template_name = 'core/custom_admin/gallery/gallery_list.html'
    context_object_name = 'items'

    def get_queryset(self):
        return Gallery.objects.all().order_by('-tanggal_upload', '-id')

class GalleryCreateView(AdminRequiredMixin, CreateView):
    model = Gallery
    template_name = 'core/custom_admin/gallery/gallery_form.html'
    fields = ['caption_ind', 'caption_en', 'gambar', 'folder', 'kategori', 'tanggal_upload']
    success_url = reverse_lazy('gallery_admin_list')

    def form_valid(self, form):
        messages.success(self.request, 'Gambar baru berhasil ditambahkan ke galeri!')
        return super().form_valid(form)

class GalleryUpdateView(AdminRequiredMixin, UpdateView):
    model = Gallery
    template_name = 'core/custom_admin/gallery/gallery_form.html'
    fields = ['caption_ind', 'caption_en', 'gambar', 'folder', 'kategori', 'tanggal_upload']
    success_url = reverse_lazy('gallery_admin_list')

    def form_valid(self, form):
        messages.success(self.request, 'Data gambar berhasil diperbarui!')
        return super().form_valid(form)

@login_required(login_url='/be/login/')
@user_passes_test(lambda u: u.is_staff, login_url='/be/login/')
def gallery_delete_view(request, pk):
    item = get_object_or_404(Gallery, pk=pk)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Gambar berhasil dihapus!')
    return redirect('gallery_admin_list')


# ==========================================
# 10b. MANAGEMENT FOLDER / ALBUM GALERI
# ==========================================
class FolderListView(AdminRequiredMixin, ListView):
    model = Folder
    template_name = 'core/custom_admin/gallery/folder_list.html'
    context_object_name = 'folders'

    def get_queryset(self):
        return Folder.objects.all().order_by('-tahun', '-id')

class FolderCreateView(AdminRequiredMixin, CreateView):
    model = Folder
    template_name = 'core/custom_admin/gallery/folder_form.html'
    fields = ['nama_ind', 'nama_en', 'tahun']
    success_url = reverse_lazy('folder_list')

    def form_valid(self, form):
        messages.success(self.request, 'Folder baru berhasil ditambahkan!')
        return super().form_valid(form)

class FolderUpdateView(AdminRequiredMixin, UpdateView):
    model = Folder
    template_name = 'core/custom_admin/gallery/folder_form.html'
    fields = ['nama_ind', 'nama_en', 'tahun']
    success_url = reverse_lazy('folder_list')

    def form_valid(self, form):
        messages.success(self.request, 'Data folder berhasil diperbarui!')
        return super().form_valid(form)

@login_required(login_url='/be/login/')
@user_passes_test(lambda u: u.is_staff, login_url='/be/login/')
def folder_delete_view(request, pk):
    folder = get_object_or_404(Folder, pk=pk)
    if request.method == 'POST':
        folder.delete()
        messages.success(request, 'Data folder berhasil dihapus!')
    return redirect('folder_list')


# ==========================================
# 10c. MANAGEMENT TIM AHLI KAMI (TEAM)
# ==========================================
class TeamListView(AdminRequiredMixin, ListView):
    model = TeamMember
    template_name = 'core/custom_admin/team/team_list.html'
    context_object_name = 'members'

    def get_queryset(self):
        return TeamMember.objects.all().order_by('urutan', '-id')

class TeamCreateView(AdminRequiredMixin, CreateView):
    model = TeamMember
    template_name = 'core/custom_admin/team/team_form.html'
    fields = ['nama', 'jabatan_ind', 'jabatan_en', 'bio_ind', 'bio_en', 'kategori_ind', 'kategori_en', 'urutan', 'foto']
    success_url = reverse_lazy('team_list')

    def form_valid(self, form):
        messages.success(self.request, 'Anggota tim baru berhasil ditambahkan!')
        return super().form_valid(form)

class TeamUpdateView(AdminRequiredMixin, UpdateView):
    model = TeamMember
    template_name = 'core/custom_admin/team/team_form.html'
    fields = ['nama', 'jabatan_ind', 'jabatan_en', 'bio_ind', 'bio_en', 'kategori_ind', 'kategori_en', 'urutan', 'foto']
    success_url = reverse_lazy('team_list')

    def form_valid(self, form):
        messages.success(self.request, 'Data anggota tim berhasil diperbarui!')
        return super().form_valid(form)

@login_required(login_url='/be/login/')
@user_passes_test(lambda u: u.is_staff, login_url='/be/login/')
def team_delete_view(request, pk):
    member = get_object_or_404(TeamMember, pk=pk)
    if request.method == 'POST':
        member.delete()
        messages.success(request, 'Anggota tim berhasil dihapus!')
    return redirect('team_list')


## ==========================================
# PROTEKSI KHUSUS SUPERUSER
# ==========================================
class SuperuserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/be/login/'

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_superuser

    def handle_no_permission(self):
        if self.request.user.is_authenticated and not self.request.user.is_superuser:
            messages.error(self.request, 'Akses ditolak! Menu Manajemen Pengguna hanya dapat diakses oleh Superuser.')
            return redirect('custom_dashboard')
        return super().handle_no_permission()


# ==========================================
# 11. MANAGEMENT USER / PENGGUNA
# ==========================================
class UserCreateForm(forms.ModelForm):
    nama_lengkap = forms.CharField(max_length=150, required=True, label="Nama Lengkap")

    class Meta:
        model = User
        fields = ['username', 'nama_lengkap', 'email', 'password', 'is_staff', 'is_active', 'is_superuser']

    def clean_nama_lengkap(self):
        nama = self.cleaned_data.get('nama_lengkap')
        if Profile.objects.filter(nama_lengkap=nama).exists():
            raise forms.ValidationError("Nama ini sudah digunakan. Silakan gunakan nama lain.")
        return nama

class UserUpdateForm(forms.ModelForm):
    nama_lengkap = forms.CharField(max_length=150, required=True, label="Nama Lengkap")

    class Meta:
        model = User
        fields = ['username', 'nama_lengkap', 'email', 'is_staff', 'is_active', 'is_superuser']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'profile'):
            self.fields['nama_lengkap'].initial = self.instance.profile.nama_lengkap

    def clean_nama_lengkap(self):
        nama = self.cleaned_data.get('nama_lengkap')
        qs = Profile.objects.filter(nama_lengkap=nama)
        if self.instance and self.instance.pk:
            qs = qs.exclude(user=self.instance)
        if qs.exists():
            raise forms.ValidationError("Nama ini sudah digunakan. Silakan gunakan nama lain.")
        return nama

class UserListView(SuperuserRequiredMixin, ListView):
    model = User
    template_name = 'core/custom_admin/user/user_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        return User.objects.all().order_by('-date_joined')

class UserCreateView(SuperuserRequiredMixin, CreateView):
    model = User
    template_name = 'core/custom_admin/user/user_form.html'
    form_class = UserCreateForm
    success_url = reverse_lazy('user_list')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()  
        
        profile = Profile.objects.get(user=user)
        profile.nama_lengkap = form.cleaned_data['nama_lengkap']
        profile.save()
        
        user.profile = profile 
        
        messages.success(self.request, 'Pengguna baru berhasil ditambahkan!')
        return super(CreateView, self).form_valid(form)

class UserUpdateView(SuperuserRequiredMixin, UpdateView):
    model = User
    template_name = 'core/custom_admin/user/user_form.html'
    form_class = UserUpdateForm
    success_url = reverse_lazy('user_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        
        profile, _ = Profile.objects.get_or_create(user=self.object)
        profile.nama_lengkap = form.cleaned_data['nama_lengkap']
        profile.save()
        
        messages.success(self.request, 'Data pengguna berhasil diperbarui!')
        return response

@login_required(login_url='/be/login/')
def user_delete_view(request, pk):
    if not request.user.is_superuser:
        messages.error(request, 'Akses ditolak! Penghapusan pengguna hanya dapat dilakukan oleh Superuser.')
        return redirect('custom_dashboard')
        
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Pengguna berhasil dihapus!')
    return redirect('user_list')


# ==========================================
# 12. FITUR EDIT PROFIL MANDIRI USER
# ==========================================
class ProfileProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['nama_lengkap', 'foto_profil']

    def clean_nama_lengkap(self):
        nama = self.cleaned_data.get('nama_lengkap')
        qs = Profile.objects.filter(nama_lengkap=nama)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Nama ini sudah digunakan. Silakan gunakan nama lain.")
        return nama

@login_required(login_url='/be/login/')
def user_edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil Anda berhasil diperbarui!')
            return redirect('custom_dashboard')
    else:
        form = ProfileProfileForm(instance=profile)
        
    return render(request, 'core/custom_admin/user/user_edit_profile.html', {'form': form})


# ==========================================
# 13. UPLOAD GAMBAR QUILL EDITOR
# ==========================================
@login_required(login_url='/be/login/')
@user_passes_test(lambda u: u.is_staff, login_url='/be/login/')
def quill_image_upload(request):
    """Endpoint untuk upload gambar dari Quill Editor via AJAX."""
    if request.method == 'POST' and request.FILES.get('image'):
        import uuid, os
        image = request.FILES['image']

        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if image.content_type not in allowed_types:
            return JsonResponse({'error': 'Tipe file tidak didukung. Gunakan JPG, PNG, GIF, atau WebP.'}, status=400)

        if image.size > 5 * 1024 * 1024:
            return JsonResponse({'error': 'Ukuran file terlalu besar. Maksimal 5MB.'}, status=400)

        ext = os.path.splitext(image.name)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'editor_uploads')
        os.makedirs(upload_dir, exist_ok=True)

        filepath = os.path.join(upload_dir, filename)
        with open(filepath, 'wb+') as f:
            for chunk in image.chunks():
                f.write(chunk)

        image_url = f"{settings.MEDIA_URL}editor_uploads/{filename}"
        return JsonResponse({'url': image_url})

    return JsonResponse({'error': 'Tidak ada file yang dikirim.'}, status=400)