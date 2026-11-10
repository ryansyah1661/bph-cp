import json
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django import forms
from django.db.models import Min, Max, Q, Prefetch
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
from .models import Article, Project, ClientGroup, Client, Story, Service, Location, Category, Modul, ContactMessage, Gallery, Profile, Folder, TeamMember, Infografis, Video, Regency

# ==========================================
# JALUR FRONTEND WEBSITE (NAVBAR & MENU)
# ==========================================
def homepage(request):
    programs = Program.objects.order_by('-tanggal')
    articles = Article.objects.order_by('-tanggal')[:3]
    stories = Story.objects.order_by('-tanggal')[:1]
    return render(request, 'core/homepage.html', {
        'programs': programs,
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
    services = Service.objects.all().prefetch_related('categories').order_by('id')
    return render(request, 'core/services.html', {
        'services': services,
    })

def experience_view(request):
    projects = Project.objects.select_related('client', 'service_portfolio').prefetch_related('locations', 'regencies', 'categories').order_by('-tahun', '-id')
    categories = Category.objects.filter(projects__isnull=False).distinct().order_by('name')
    years = Project.objects.order_by('-tahun').values_list('tahun', flat=True).distinct()
    
    clients_swasta = ClientGroup.objects.filter(sektor='swasta').order_by('nama')
    clients_publik = ClientGroup.objects.filter(sektor='publik').order_by('nama')

    total_proyek = Project.objects.count()
    total_provinsi = Location.objects.filter(projects__isnull=False).distinct().count()
    total_kabkot = Regency.objects.filter(projects__isnull=False).distinct().count()
    
    # Hitung: jumlah anak perusahaan + jumlah grup yang tidak ada anak perusahaan
    anak_count = Client.objects.count()
    grup_tanpa_anak = ClientGroup.objects.filter(clients__isnull=True).distinct().count()
    total_klien = anak_count + grup_tanpa_anak
    
    tahun_bounds = Project.objects.all().aggregate(Min('tahun'), Max('tahun'))
    if tahun_bounds['tahun__min'] and tahun_bounds['tahun__max']:
        total_tahun_bekerja = (tahun_bounds['tahun__max'] - tahun_bounds['tahun__min']) + 1
    else:
        total_tahun_bekerja = 5

    locations_with_projects = Location.objects.filter(projects__isnull=False).prefetch_related(
        Prefetch(
            'projects',
            queryset=Project.objects.select_related('client', 'service_portfolio').prefetch_related('regencies', 'locations').order_by('-tahun', '-id')
        ),
        Prefetch(
            'regencies',
            queryset=Regency.objects.filter(projects__isnull=False).distinct().order_by('nama'),
            to_attr='active_regencies'
        )
    ).distinct()

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
        'total_kabkot': total_kabkot,
        'total_klien': total_klien,
        'locations_with_projects': locations_with_projects,
        'all_stories': all_stories,
    })

def provinces_geojson_api(request):
    geojson_path = settings.BASE_DIR / 'static' / 'data' / 'indonesia_provinces.json'
    with open(geojson_path, 'r', encoding='utf-8') as f:
        geojson_data = f.read()
    return HttpResponse(geojson_data, content_type='application/json')

def kabkot_geojson_api(request):
    geojson_path = settings.BASE_DIR / 'static' / 'data' / 'indonesia_kabkot.json'
    with open(geojson_path, 'r', encoding='utf-8') as f:
        geojson_data = f.read()
    return HttpResponse(geojson_data, content_type='application/json')

def gallery_view(request):
    programs = Program.objects.order_by('-tanggal')
    articles = Article.objects.order_by('-tanggal')
    stories = Story.objects.order_by('-tanggal')
    documents = Modul.objects.order_by('-tanggal_rilis')
    categories = Category.objects.filter(folders__isnull=False).distinct().order_by('name')
    gallery_items = Gallery.objects.all().order_by('-tanggal_upload', '-id')
    folders = Folder.objects.select_related('kategori').prefetch_related('images').order_by('-tahun', '-id')
    infografis = Infografis.objects.all().order_by('-tanggal_unggah', '-id')
    videos = Video.objects.all().order_by('-tanggal_unggah', '-id')

    return render(request, 'core/gallery.html', {
        'programs': programs,
        'articles': articles,
        'stories': stories,
        'gallery_items': gallery_items,
        'folders': folders,
        'documents': documents,
        'categories': categories,
        'infografis_list': infografis,
        'videos_list': videos,
    })

def contact_view(request):
    services = Service.objects.all().order_by('id')
    selected_service = request.GET.get('service', '').strip()

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
Layanan/Topik : {subjek}

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

    return render(request, 'core/contact.html', {
        'services': services,
        'selected_service': selected_service,
    })

def story_view(request):
    stories_data = Story.objects.select_related('lokasi', 'project').order_by('-tanggal')
    return render(request, 'core/story.html', {'stories': stories_data})

# ==========================================
# JALUR FRONTEND HALAMAN DETAIL
# ==========================================
def detail_articles_view(request, slug):
    article_data = get_object_or_404(Article, Q(slug_ind=slug) | Q(slug_en=slug) if hasattr(Article, 'slug_en') else Q(slug=slug))
    
    article_data.views_count += 1
    article_data.save(update_fields=['views_count'])
    
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
        Project.objects.select_related('client', 'service_portfolio').prefetch_related('locations', 'regencies__provinsi', 'categories', 'metrics'),
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
    
    all_services = Service.objects.all().order_by('id')
    
    return render(request, 'core/detail-services.html', {
        'service': service_data,
        'all_services': all_services,
    })

def detail_story_view(request, slug):
    story_data = get_object_or_404(
        Story.objects.select_related('lokasi', 'project'), 
        Q(slug_ind=slug) | Q(slug_en=slug) if hasattr(Story, 'slug_en') else Q(slug=slug)
    )
    
    story_data.views_count += 1
    story_data.save(update_fields=['views_count'])
    
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
        'total_clients': Client.objects.count() + ClientGroup.objects.filter(clients__isnull=True).distinct().count(),
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

class DateInputMixin:
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        date_fields = ['tanggal', 'tanggal_rilis', 'tanggal_upload', 'tanggal_unggah']
        for field in date_fields:
            if field in form.fields:
                form.fields[field].widget = forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'})
        return form


# ==========================================
# 1. MANAGEMENT ARTIKEL & WAWASAN TEKNIS
# ==========================================
class ArticleListView(AdminRequiredMixin, ListView):
    model = Article
    template_name = 'core/custom_admin/articles/articles_list.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        return Article.objects.all().order_by('-tanggal', '-id')


logger = logging.getLogger(__name__)

def auto_sync_file_to_gallery(instance, file_field_name='gambar', folder_name=None, caption=None):
    """
    Otomatis mendaftarkan file gambar yang diunggah dari laptop ke Asset Media (Gallery)
    di bawah Folder yang sesuai dengan konteks modulnya.
    """
    if not instance:
        return
    file_field = getattr(instance, file_field_name, None)
    if not file_field or not getattr(file_field, 'name', None):
        return

    try:
        from datetime import datetime
        from django.utils import timezone

        # Pemetaan folder otomatis berdasarkan nama model jika folder_name tidak ditentukan
        if not folder_name:
            model_name = instance._meta.model_name.lower()
            folder_map = {
                'article': ('Dokumentasi Artikel & Wawasan', 'Article & Insights Documentation'),
                'story': ('Dokumentasi Cerita Lapangan', 'Field Stories Documentation'),
                'project': ('Dokumentasi Proyek', 'Project Documentation'),
                'clientgroup': ('Logo Klien & Mitra', 'Client & Partner Logos'),
                'teammember': ('Foto Tim & Pengurus', 'Team & Management Photos'),
                'program': ('Dokumentasi Program', 'Program Documentation'),
                'infografis': ('Infografis & Visual Data', 'Infographics & Visual Data'),
                'service': ('Dokumentasi Layanan', 'Services Documentation'),
            }
            nama_id, nama_en = folder_map.get(model_name, ('Unggahan Sistem', 'System Uploads'))
        else:
            nama_id = folder_name
            nama_en = folder_name

        folder, _ = Folder.objects.get_or_create(
            nama=nama_id,
            defaults={
                'nama_ind': nama_id,
                'nama_en': nama_en,
                'tahun': datetime.now().year,
            }
        )

        # Penentuan caption otomatis yang informatif
        if not caption:
            if hasattr(instance, 'judul') and instance.judul:
                caption = str(instance.judul)
            elif hasattr(instance, 'judul_ind') and instance.judul_ind:
                caption = str(instance.judul_ind)
            elif hasattr(instance, 'name') and instance.name:
                caption = str(instance.name)
            elif hasattr(instance, 'name_ind') and instance.name_ind:
                caption = str(instance.name_ind)
            elif hasattr(instance, 'title') and instance.title:
                caption = str(instance.title)
            elif hasattr(instance, 'title_ind') and instance.title_ind:
                caption = str(instance.title_ind)
            elif hasattr(instance, 'nama') and instance.nama:
                if instance._meta.model_name == 'clientgroup':
                    caption = f"Logo {instance.nama}"
                else:
                    caption = str(instance.nama)
            elif hasattr(instance, 'deskripsi') and instance.deskripsi:
                caption = str(instance.deskripsi)[:60]
            else:
                caption = f"Foto {nama_id}"

        # Cegah duplikasi di Galeri jika gambar dengan path yang sama sudah ada
        if not Gallery.objects.filter(gambar=file_field.name).exists():
            Gallery.objects.create(
                caption=caption,
                caption_ind=caption,
                caption_en=caption,
                gambar=file_field.name,
                folder=folder,
                tanggal_upload=timezone.now().date(),
            )
    except Exception as e:
        logger.warning(f"Gagal auto-sync gambar ke galeri: {e}")

def auto_save_logo_to_gallery(client_group):
    return auto_sync_file_to_gallery(client_group, file_field_name='logo')


class MediaAssetPickerMixin:
    """
    Mixin untuk mendukung pemilihan gambar langsung dari Asset Media
    selain dari upload berkas lokal di laptop.
    Juga otomatis mendaftarkan file yang baru diunggah dari laptop ke Asset Media (Gallery)
    ke dalam folder yang sesuai dengan modulnya.
    """
    image_field_name = 'gambar'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        selected_asset = self.request.POST.get('selected_asset_media')
        has_existing = bool(getattr(getattr(self, 'object', None), self.image_field_name, None))
        if selected_asset or has_existing:
            if self.image_field_name in form.fields:
                form.fields[self.image_field_name].required = False
        return form

    def form_valid(self, form):
        selected_asset_id = self.request.POST.get('selected_asset_media')
        has_uploaded_file = bool(self.request.FILES.get(self.image_field_name))
        if selected_asset_id and not has_uploaded_file:
            asset = Gallery.objects.filter(id=selected_asset_id).first()
            if asset and asset.gambar:
                setattr(form.instance, self.image_field_name, asset.gambar.name)

        response = super().form_valid(form)

        # Jika diunggah langsung dari file manager laptop (bukan memilih dari asset media),
        # otomatis daftarkan ke Gallery di folder modul terkait!
        if has_uploaded_file and getattr(self, 'object', None):
            auto_sync_file_to_gallery(self.object, file_field_name=self.image_field_name)

        return response

class ArticleCreateView(AdminRequiredMixin, DateInputMixin, MediaAssetPickerMixin, CreateView):
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

class ArticleUpdateView(AdminRequiredMixin, DateInputMixin, MediaAssetPickerMixin, UpdateView):
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
    paginate_by = 10

    def get_queryset(self):
        return Project.objects.all().order_by('-tahun', '-id')

class ProjectCreateView(AdminRequiredMixin, MediaAssetPickerMixin, CreateView):
    model = Project
    image_field_name = 'image' 
    template_name = 'core/custom_admin/experience/experience_form.html'
    fields = ['name_ind', 'name_en', 'slug_ind', 'slug_en', 'description_ind', 'description_en', 'tahun', 'image', 'client_group', 'client', 'service_portfolio', 'locations', 'regencies', 'categories']
    success_url = reverse_lazy('project_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if 'client_group' in form.fields:
            form.fields['client_group'].required = True
            form.fields['client_group'].label = "Perusahaan Utama (Group)"
        if 'client' in form.fields:
            form.fields['client'].required = False
            form.fields['client'].label = "Klien (Anak Perusahaan)"
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_regencies = Regency.objects.select_related('provinsi').all()
        context['regencies_json'] = json.dumps([
            {
                'id': str(r.id),
                'text': str(r),
                'provinsi_id': str(r.provinsi_id)
            }
            for r in all_regencies
        ])
        context['client_groups'] = ClientGroup.objects.all().order_by('nama')
        all_clients = Client.objects.select_related('group').all().order_by('nama')
        context['clients_json'] = json.dumps([
            {
                'id': str(c.id),
                'text': str(c.nama),
                'group_id': str(c.group_id) if c.group_id else ''
            }
            for c in all_clients
        ])
        context['selected_group_id'] = ''
        return context

    def form_valid(self, form):
        if not form.instance.slug_en and form.instance.slug_ind:
            form.instance.slug_en = form.instance.slug_ind
        if form.instance.client and not form.instance.client_group:
            form.instance.client_group = form.instance.client.group
        messages.success(self.request, 'Proyek baru berhasil ditambahkan!')
        return super().form_valid(form)

class ProjectUpdateView(AdminRequiredMixin, MediaAssetPickerMixin, UpdateView):
    model = Project
    image_field_name = 'image' 
    template_name = 'core/custom_admin/experience/experience_form.html'
    fields = ['name_ind', 'name_en', 'slug_ind', 'slug_en', 'description_ind', 'description_en', 'tahun', 'image', 'client_group', 'client', 'service_portfolio', 'locations', 'regencies', 'categories']
    success_url = reverse_lazy('project_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if 'client_group' in form.fields:
            form.fields['client_group'].required = True
            form.fields['client_group'].label = "Perusahaan Utama (Group)"
        if 'client' in form.fields:
            form.fields['client'].required = False
            form.fields['client'].label = "Klien (Anak Perusahaan)"
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_regencies = Regency.objects.select_related('provinsi').all()
        context['regencies_json'] = json.dumps([
            {
                'id': str(r.id),
                'text': str(r),
                'provinsi_id': str(r.provinsi_id)
            }
            for r in all_regencies
        ])
        context['client_groups'] = ClientGroup.objects.all().order_by('nama')
        all_clients = Client.objects.select_related('group').all().order_by('nama')
        context['clients_json'] = json.dumps([
            {
                'id': str(c.id),
                'text': str(c.nama),
                'group_id': str(c.group_id) if c.group_id else ''
            }
            for c in all_clients
        ])
        selected_gid = ''
        if self.object:
            if self.object.client_group_id:
                selected_gid = str(self.object.client_group_id)
            elif self.object.client and self.object.client.group_id:
                selected_gid = str(self.object.client.group_id)
        context['selected_group_id'] = selected_gid
        return context

    def form_valid(self, form):
        if not form.instance.slug_en and form.instance.slug_ind:
            form.instance.slug_en = form.instance.slug_ind
        if form.instance.client and not form.instance.client_group:
            form.instance.client_group = form.instance.client.group
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
    paginate_by = 10

    def get_queryset(self):
        return Story.objects.all().order_by('-tanggal', '-id')

class StoryCreateView(AdminRequiredMixin, DateInputMixin, MediaAssetPickerMixin, CreateView):
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

class StoryUpdateView(AdminRequiredMixin, DateInputMixin, MediaAssetPickerMixin, UpdateView):
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
# 4. MANAGEMENT MITRA / KLIEN (GROUP + CLIENT)
# ==========================================

# --- CLIENT GROUP (Perusahaan Utama) ---
class ClientGroupListView(AdminRequiredMixin, ListView):
    model = ClientGroup
    template_name = 'core/custom_admin/client/group_list.html'
    context_object_name = 'groups'
    paginate_by = 10

    def get_queryset(self):
        return ClientGroup.objects.prefetch_related('clients').all().order_by('-id')

class ClientGroupCreateView(AdminRequiredMixin, MediaAssetPickerMixin, CreateView):
    model = ClientGroup
    image_field_name = 'logo'
    template_name = 'core/custom_admin/client/group_form.html'
    fields = ['nama', 'sektor', 'logo']
    success_url = reverse_lazy('client_group_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.FILES.get('logo'):
            auto_save_logo_to_gallery(self.object)
        messages.success(self.request, 'Group klien baru berhasil ditambahkan!')
        return response

class ClientGroupUpdateView(AdminRequiredMixin, MediaAssetPickerMixin, UpdateView):
    model = ClientGroup
    image_field_name = 'logo'
    template_name = 'core/custom_admin/client/group_form.html'
    fields = ['nama', 'sektor', 'logo']
    success_url = reverse_lazy('client_group_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.FILES.get('logo'):
            auto_save_logo_to_gallery(self.object)
        messages.success(self.request, 'Data group klien berhasil diperbarui!')
        return response

@login_required(login_url='/be/login/')
@user_passes_test(lambda u: u.is_staff, login_url='/be/login/')
def client_group_delete_view(request, pk):
    group = get_object_or_404(ClientGroup, pk=pk)
    if request.method == 'POST':
        group.delete()
        messages.success(request, 'Group klien berhasil dihapus!')
    return redirect('client_group_list')

@login_required(login_url='/be/login/')
@user_passes_test(lambda u: u.is_staff, login_url='/be/login/')
def quick_add_client_group_view(request):
    """
    Modal quick add group perusahaan utama langsung dari form tambah klien.
    """
    if request.method == 'POST':
        nama = request.POST.get('nama', '').strip()
        sektor = request.POST.get('sektor', 'swasta')
        logo = request.FILES.get('logo', None)

        if not nama:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('is_ajax'):
                return JsonResponse({'success': False, 'message': 'Nama group wajib diisi.'}, status=400)
            messages.error(request, 'Nama group wajib diisi.')
            return redirect(request.META.get('HTTP_REFERER', 'client_list'))

        group = ClientGroup.objects.create(
            nama=nama,
            nama_ind=nama,
            nama_en=nama,
            sektor=sektor,
            logo=logo
        )

        if logo:
            auto_save_logo_to_gallery(group)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('is_ajax'):
            return JsonResponse({
                'success': True,
                'id': group.id,
                'name': group.nama,
                'sektor': group.get_sektor_display(),
                'message': f'Group "{group.nama}" berhasil dibuat!'
            })

        messages.success(request, f'Group "{group.nama}" berhasil dibuat!')
        return redirect(request.META.get('HTTP_REFERER', 'client_list'))

    return JsonResponse({'success': False, 'message': 'Metode tidak diizinkan.'}, status=405)

# --- CLIENT (Manajemen Klien & Group Hierarkis - Tampilan Accordion) ---
class ClientListView(AdminRequiredMixin, ListView):
    model = ClientGroup
    template_name = 'core/custom_admin/client/client_list.html'
    context_object_name = 'groups'
    paginate_by = 25

    def get_queryset(self):
        qs = ClientGroup.objects.prefetch_related(
            Prefetch('clients', queryset=Client.objects.prefetch_related('projects').order_by('nama'))
        ).all().order_by('nama')

        search = self.request.GET.get('q', '').strip()
        if search:
            qs = qs.filter(
                Q(nama__icontains=search) | 
                Q(nama_ind__icontains=search) | 
                Q(clients__nama__icontains=search) |
                Q(clients__nama_ind__icontains=search)
            ).distinct()

        sektor = self.request.GET.get('sektor', '').strip()
        if sektor:
            qs = qs.filter(sektor=sektor)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_query'] = self.request.GET.get('q', '')
        ctx['current_sektor'] = self.request.GET.get('sektor', '')
        ctx['total_groups'] = ClientGroup.objects.count()
        ctx['total_anak'] = Client.objects.count()
        ctx['total_klien_efektif'] = ctx['total_anak'] + ClientGroup.objects.filter(clients__isnull=True).distinct().count()
        ctx['all_groups'] = ClientGroup.objects.all().order_by('nama')
        ctx['open_group_id'] = self.request.GET.get('open', '')
        return ctx

@login_required(login_url='/be/login/')
@user_passes_test(lambda u: u.is_staff, login_url='/be/login/')
def quick_add_client_view(request):
    """
    Tambah anak perusahaan (klien) instan dari popup modal atau tombol dalam accordion.
    """
    if request.method == 'POST':
        group_id = request.POST.get('group')
        nama = request.POST.get('nama', '').strip()

        if not group_id or not nama:
            messages.error(request, 'Group perusahaan utama dan nama anak perusahaan wajib diisi.')
            return redirect('client_list')

        group = get_object_or_404(ClientGroup, pk=group_id)
        client = Client.objects.create(
            group=group,
            nama=nama,
            nama_ind=nama,
            nama_en=nama
        )
        messages.success(request, f'Anak perusahaan "{client.nama}" berhasil ditambahkan ke group "{group.nama}"!')
        return redirect(f"/be/clients/?open={group.id}")

    return redirect('client_list')

class ClientCreateView(AdminRequiredMixin, CreateView):
    model = Client
    template_name = 'core/custom_admin/client/client_form.html'
    fields = ['group', 'nama_ind', 'nama_en']

    def get_initial(self):
        initial = super().get_initial()
        group_id = self.request.GET.get('group')
        if group_id:
            initial['group'] = group_id
        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['groups'] = ClientGroup.objects.all().order_by('nama')
        return ctx

    def form_valid(self, form):
        if not form.instance.nama_en and form.instance.nama_ind:
            form.instance.nama_en = form.instance.nama_ind
        form.instance.nama = form.instance.nama_ind or form.instance.nama
        messages.success(self.request, 'Anak perusahaan baru berhasil ditambahkan!')
        self.object = form.save()
        return redirect(f"/be/clients/?open={self.object.group_id}")

class ClientUpdateView(AdminRequiredMixin, UpdateView):
    model = Client
    template_name = 'core/custom_admin/client/client_form.html'
    fields = ['group', 'nama_ind', 'nama_en']

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['groups'] = ClientGroup.objects.all().order_by('nama')
        return ctx

    def form_valid(self, form):
        if not form.instance.nama_en and form.instance.nama_ind:
            form.instance.nama_en = form.instance.nama_ind
        form.instance.nama = form.instance.nama_ind or form.instance.nama
        messages.success(self.request, 'Data anak perusahaan berhasil diperbarui!')
        self.object = form.save()
        return redirect(f"/be/clients/?open={self.object.group_id}")

@login_required(login_url='/be/login/')
@user_passes_test(lambda u: u.is_staff, login_url='/be/login/')
def client_delete_view(request, pk):
    client = get_object_or_404(Client, pk=pk)
    group_id = client.group_id
    if request.method == 'POST':
        client.delete()
        messages.success(request, 'Data anak perusahaan berhasil dihapus!')
    return redirect(f"/be/clients/?open={group_id}" if group_id else 'client_list')


# ==========================================
# 5. MANAGEMENT LAYANAN (SERVICES)
# ==========================================
class ServiceListView(AdminRequiredMixin, ListView):
    model = Service
    template_name = 'core/custom_admin/services/services_list.html'
    context_object_name = 'services'
    paginate_by = 10

    def get_queryset(self):
        return Service.objects.all().order_by('-id')

class ServiceCreateView(AdminRequiredMixin, CreateView):
    model = Service
    template_name = 'core/custom_admin/services/services_form.html'
    fields = ['title_ind', 'title_en', 'slug_ind', 'slug_en', 'approach_ind', 'approach_en', 'portfolio', 'icon', 'thumbnail', 'bg_image', 'categories']
    success_url = reverse_lazy('service_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.FILES.get('thumbnail') and getattr(self, 'object', None):
            auto_sync_file_to_gallery(self.object, file_field_name='thumbnail', caption=f"Thumbnail Layanan {self.object.title}")
        if self.request.FILES.get('bg_image') and getattr(self, 'object', None):
            auto_sync_file_to_gallery(self.object, file_field_name='bg_image', caption=f"Banner Layanan {self.object.title}")
        messages.success(self.request, 'Layanan baru berhasil ditambahkan!')
        return response

class ServiceUpdateView(AdminRequiredMixin, UpdateView):
    model = Service
    template_name = 'core/custom_admin/services/services_form.html'
    fields = ['title_ind', 'title_en', 'slug_ind', 'slug_en', 'approach_ind', 'approach_en', 'portfolio', 'icon', 'thumbnail', 'bg_image', 'categories']
    success_url = reverse_lazy('service_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.FILES.get('thumbnail') and getattr(self, 'object', None):
            auto_sync_file_to_gallery(self.object, file_field_name='thumbnail', caption=f"Thumbnail Layanan {self.object.title}")
        if self.request.FILES.get('bg_image') and getattr(self, 'object', None):
            auto_sync_file_to_gallery(self.object, file_field_name='bg_image', caption=f"Banner Layanan {self.object.title}")
        messages.success(self.request, 'Data layanan berhasil diperbarui!')
        return response

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
    paginate_by = 10

    def get_queryset(self):
        return Location.objects.all().order_by('-id')

class LocationCreateView(AdminRequiredMixin, CreateView):
    model = Location
    template_name = 'core/custom_admin/location/location_form.html'
    fields = ['nama_provinsi_ind', 'nama_provinsi_en', 'slug_ind', 'slug_en', 'kode_wilayah']
    success_url = reverse_lazy('location_list')

    def form_valid(self, form):
        if not form.instance.slug_en and form.instance.slug_ind:
            form.instance.slug_en = form.instance.slug_ind
        messages.success(self.request, 'Lokasi baru berhasil ditambahkan!')
        return super().form_valid(form)

class LocationUpdateView(AdminRequiredMixin, UpdateView):
    model = Location
    template_name = 'core/custom_admin/location/location_form.html'
    fields = ['nama_provinsi_ind', 'nama_provinsi_en', 'slug_ind', 'slug_en', 'kode_wilayah']
    success_url = reverse_lazy('location_list')

    def form_valid(self, form):
        if not form.instance.slug_en and form.instance.slug_ind:
            form.instance.slug_en = form.instance.slug_ind
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
    paginate_by = 10

    def get_queryset(self):
        return Category.objects.all().order_by('-id')

class CategoryCreateView(AdminRequiredMixin, CreateView):
    model = Category
    template_name = 'core/custom_admin/category/category_form.html'
    fields = ['name_ind', 'name_en', 'slug_ind', 'slug_en']
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        if not form.instance.slug_en and form.instance.slug_ind:
            form.instance.slug_en = form.instance.slug_ind
        messages.success(self.request, 'Kategori baru berhasil ditambahkan!')
        return super().form_valid(form)

class CategoryUpdateView(AdminRequiredMixin, UpdateView):
    model = Category
    template_name = 'core/custom_admin/category/category_form.html'
    fields = ['name_ind', 'name_en', 'slug_ind', 'slug_en']
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        if not form.instance.slug_en and form.instance.slug_ind:
            form.instance.slug_en = form.instance.slug_ind
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
    fields = ['judul_ind', 'judul_en', 'deskripsi_ind', 'deskripsi_en', 'file_dokumen', 'url_dokumen']
    success_url = reverse_lazy('document_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['deskripsi_ind'].required = False
        form.fields['deskripsi_en'].required = False
        form.fields['file_dokumen'].required = False
        form.fields['url_dokumen'].required = False
        return form

    def form_valid(self, form):
        from django.utils import timezone
        if not form.instance.tanggal_rilis:
            form.instance.tanggal_rilis = timezone.now().date()
        messages.success(self.request, 'Modul baru berhasil ditambahkan!')
        return super().form_valid(form)

class DocumentUpdateView(AdminRequiredMixin, UpdateView):
    model = Modul
    template_name = 'core/custom_admin/modul/modul_form.html'
    fields = ['judul_ind', 'judul_en', 'deskripsi_ind', 'deskripsi_en', 'file_dokumen', 'url_dokumen']
    success_url = reverse_lazy('document_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['deskripsi_ind'].required = False
        form.fields['deskripsi_en'].required = False
        form.fields['file_dokumen'].required = False
        form.fields['url_dokumen'].required = False
        return form

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
    paginate_by = 10

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
# 10. MANAGEMENT ASSET MEDIA & GALERI
# ==========================================
@login_required(login_url='/be/login/')
@user_passes_test(lambda u: u.is_staff, login_url='/be/login/')
def quick_add_folder_view(request):
    """
    Membuat Folder / Album baru langsung dari halaman Asset Media
    atau modal picker tanpa perlu berpindah menu.
    """
    if request.method == 'POST':
        from datetime import datetime

        nama_ind = request.POST.get('nama_ind', '').strip()
        nama_en = request.POST.get('nama_en', '').strip() or nama_ind
        tahun = request.POST.get('tahun') or datetime.now().year
        kategori_id = request.POST.get('kategori') or None

        if not nama_ind:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('is_ajax'):
                return JsonResponse({'success': False, 'message': 'Nama album/folder wajib diisi.'}, status=400)
            messages.error(request, 'Nama album/folder wajib diisi.')
            return redirect(request.META.get('HTTP_REFERER', 'gallery_admin_list'))

        kategori = None
        if kategori_id:
            kategori = Category.objects.filter(id=kategori_id).first()

        folder = Folder.objects.create(
            nama=nama_ind,
            nama_ind=nama_ind,
            nama_en=nama_en,
            tahun=tahun,
            kategori=kategori
        )

        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('is_ajax'):
            return JsonResponse({
                'success': True,
                'id': folder.id,
                'name': folder.nama_ind,
                'tahun': folder.tahun,
                'message': f'Album "{folder.nama_ind}" berhasil dibuat!'
            })

        messages.success(request, f'Album "{folder.nama_ind}" berhasil dibuat!')
        return redirect(request.META.get('HTTP_REFERER', 'gallery_admin_list'))

    return JsonResponse({'success': False, 'message': 'Metode tidak diizinkan.'}, status=405)


@login_required(login_url='/be/login/')
@user_passes_test(lambda u: u.is_staff, login_url='/be/login/')
def media_assets_api(request):
    """
    API endpoint untuk Media Library Picker
    Mengembalikan daftar aset foto dan album/folder.
    """
    folder_id = request.GET.get('folder')
    search = request.GET.get('q', '').strip()

    qs = Gallery.objects.select_related('folder').all().order_by('-tanggal_upload', '-id')
    if folder_id:
        qs = qs.filter(folder_id=folder_id)
    if search:
        qs = qs.filter(Q(caption_ind__icontains=search) | Q(caption_en__icontains=search) | Q(caption__icontains=search))

    assets = []
    for g in qs[:80]:
        if g.gambar:
            assets.append({
                'id': g.id,
                'caption': g.caption_ind or g.caption or 'Tanpa Keterangan',
                'url': g.gambar.url,
                'folder_id': g.folder.id if g.folder else None,
                'folder_name': g.folder.nama_ind if g.folder else 'Tanpa Album',
                'date': g.tanggal_upload.strftime('%d/%m/%Y') if g.tanggal_upload else ''
            })

    folders = []
    for f in Folder.objects.all().order_by('-tahun', 'nama_ind'):
        folders.append({
            'id': f.id,
            'name': f.nama_ind or f.nama,
            'tahun': f.tahun
        })

    return JsonResponse({'assets': assets, 'folders': folders})


class GalleryListView(AdminRequiredMixin, ListView):
    model = Gallery
    template_name = 'core/custom_admin/gallery/gallery_list.html'
    context_object_name = 'items'
    paginate_by = 24

    def get_queryset(self):
        qs = Gallery.objects.select_related('folder').all().order_by('-tanggal_upload', '-id')
        folder_id = self.request.GET.get('folder')
        if folder_id:
            qs = qs.filter(folder_id=folder_id)
        search = self.request.GET.get('q')
        if search:
            qs = qs.filter(Q(caption_ind__icontains=search) | Q(caption_en__icontains=search) | Q(caption__icontains=search))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['folders'] = Folder.objects.all().order_by('-tahun', 'nama_ind')
        ctx['categories'] = Category.objects.all().order_by('name')
        ctx['current_folder'] = self.request.GET.get('folder', '')
        ctx['search_query'] = self.request.GET.get('q', '')
        return ctx

class GalleryCreateView(AdminRequiredMixin, DateInputMixin, CreateView):
    model = Gallery
    template_name = 'core/custom_admin/gallery/gallery_form.html'
    fields = ['caption_ind', 'folder', 'gambar']
    success_url = reverse_lazy('gallery_admin_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if 'caption_ind' in form.fields:
            form.fields['caption_ind'].required = False
            form.fields['caption_ind'].label = "Nama / Keterangan Asset (Opsional)"
        if 'folder' in form.fields:
            form.fields['folder'].required = False
            form.fields['folder'].label = "Pilih Album / Folder (Opsional)"
        return form

    def form_valid(self, form):
        import os
        # Jika caption_ind tidak diisi, otomatis gunakan nama file asli (tanpa ekstensi)
        if not form.cleaned_data.get('caption_ind') and self.request.FILES.get('gambar'):
            orig_name = self.request.FILES['gambar'].name
            base_name = os.path.splitext(orig_name)[0].replace('-', ' ').replace('_', ' ').strip().title()
            form.instance.caption_ind = base_name or "Asset Media"

        if hasattr(form.instance, 'caption_en'):
            form.instance.caption_en = form.instance.caption_ind
        form.instance.caption = form.instance.caption_ind or "Asset Media"
        if not form.instance.tanggal_upload:
            form.instance.tanggal_upload = timezone.now().date()

        messages.success(self.request, 'Asset media baru berhasil diunggah!')
        return super().form_valid(form)

class GalleryUpdateView(AdminRequiredMixin, DateInputMixin, UpdateView):
    model = Gallery
    template_name = 'core/custom_admin/gallery/gallery_form.html'
    fields = ['caption_ind', 'folder', 'gambar']
    success_url = reverse_lazy('gallery_admin_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if 'caption_ind' in form.fields:
            form.fields['caption_ind'].required = False
            form.fields['caption_ind'].label = "Nama / Keterangan Asset (Opsional)"
        if 'folder' in form.fields:
            form.fields['folder'].required = False
            form.fields['folder'].label = "Pilih Album / Folder (Opsional)"
        if 'gambar' in form.fields:
            form.fields['gambar'].required = False
        return form

    def form_valid(self, form):
        import os
        if not form.cleaned_data.get('caption_ind') and self.request.FILES.get('gambar'):
            orig_name = self.request.FILES['gambar'].name
            base_name = os.path.splitext(orig_name)[0].replace('-', ' ').replace('_', ' ').strip().title()
            form.instance.caption_ind = base_name or "Asset Media"

        if hasattr(form.instance, 'caption_en'):
            form.instance.caption_en = form.instance.caption_ind
        form.instance.caption = form.instance.caption_ind or "Asset Media"
        messages.success(self.request, 'Data asset media berhasil diperbarui!')
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
    paginate_by = 10

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
    paginate_by = 10

    def get_queryset(self):
        return TeamMember.objects.all().order_by('urutan', '-id')

class TeamCreateView(AdminRequiredMixin, MediaAssetPickerMixin, CreateView):
    model = TeamMember
    image_field_name = 'foto'
    template_name = 'core/custom_admin/team/team_form.html'
    fields = ['nama', 'jabatan_ind', 'jabatan_en', 'bio_ind', 'bio_en', 'kategori_ind', 'kategori_en', 'urutan', 'foto']
    success_url = reverse_lazy('team_list')

    def form_valid(self, form):
        messages.success(self.request, 'Anggota tim baru berhasil ditambahkan!')
        return super().form_valid(form)

class TeamUpdateView(AdminRequiredMixin, MediaAssetPickerMixin, UpdateView):
    model = TeamMember
    image_field_name = 'foto'
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

# ==========================================
# 10d. MANAGEMENT INFOGRAFIS
# ==========================================
class InfografisListView(AdminRequiredMixin, ListView):
    model = Infografis
    template_name = 'core/custom_admin/infografis/infografis_list.html'
    context_object_name = 'items'
    paginate_by = 10

    def get_queryset(self):
        return Infografis.objects.all().order_by('-tanggal_unggah', '-id')

class InfografisCreateView(AdminRequiredMixin, DateInputMixin, MediaAssetPickerMixin, CreateView):
    model = Infografis
    image_field_name = 'gambar'
    template_name = 'core/custom_admin/infografis/infografis_form.html'
    fields = ['deskripsi', 'gambar']
    success_url = reverse_lazy('infografis_list')

    def form_valid(self, form):
        messages.success(self.request, 'Infografis baru berhasil ditambahkan!')
        return super().form_valid(form)

class InfografisUpdateView(AdminRequiredMixin, DateInputMixin, MediaAssetPickerMixin, UpdateView):
    model = Infografis
    image_field_name = 'gambar'
    template_name = 'core/custom_admin/infografis/infografis_form.html'
    fields = ['deskripsi', 'gambar']
    success_url = reverse_lazy('infografis_list')

    def form_valid(self, form):
        messages.success(self.request, 'Data infografis berhasil diperbarui!')
        return super().form_valid(form)

@login_required(login_url='/be/login/')
@user_passes_test(lambda u: u.is_staff, login_url='/be/login/')
def infografis_delete_view(request, pk):
    item = get_object_or_404(Infografis, pk=pk)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Infografis berhasil dihapus!')
    return redirect('infografis_list')


# ==========================================
# 10e. MANAGEMENT VIDEO KEGIATAN
# ==========================================
class VideoListView(AdminRequiredMixin, ListView):
    model = Video
    template_name = 'core/custom_admin/video/video_list.html'
    context_object_name = 'items'
    paginate_by = 10

    def get_queryset(self):
        return Video.objects.all().order_by('-tanggal_unggah', '-id')

class VideoCreateView(AdminRequiredMixin, DateInputMixin, CreateView):
    model = Video
    template_name = 'core/custom_admin/video/video_form.html'
    fields = ['judul', 'url_video', 'thumbnail']
    success_url = reverse_lazy('video_list')

    def form_valid(self, form):
        messages.success(self.request, 'Video baru berhasil ditambahkan!')
        return super().form_valid(form)

class VideoUpdateView(AdminRequiredMixin, DateInputMixin, UpdateView):
    model = Video
    template_name = 'core/custom_admin/video/video_form.html'
    fields = ['judul', 'url_video', 'thumbnail']
    success_url = reverse_lazy('video_list')

    def form_valid(self, form):
        messages.success(self.request, 'Data video berhasil diperbarui!')
        return super().form_valid(form)

@login_required(login_url='/be/login/')
@user_passes_test(lambda u: u.is_staff, login_url='/be/login/')
def video_delete_view(request, pk):
    item = get_object_or_404(Video, pk=pk)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Video berhasil dihapus!')
    return redirect('video_list')


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
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, required=True, label="Role Pengguna")

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
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, required=True, label="Role Pengguna")

    class Meta:
        model = User
        fields = ['username', 'nama_lengkap', 'email', 'is_staff', 'is_active', 'is_superuser']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'profile'):
            self.fields['nama_lengkap'].initial = self.instance.profile.nama_lengkap
            self.fields['role'].initial = self.instance.profile.role

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
    paginate_by = 10

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
        profile.role = form.cleaned_data['role']
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
        profile.role = form.cleaned_data['role']
        profile.save()
        
        messages.success(self.request, 'Data pengguna berhasil diperbarui!')
        return response

@login_required(login_url='/be/login/')
def user_delete_view(request, pk):
    if not request.user.is_superuser:
        messages.error(request, 'Akses ditolak! Penghapusan pengguna hanya dapat dilakukan oleh Superuser.')
        return redirect('custom_dashboard')
        
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, 'Anda tidak dapat menghapus akun Anda sendiri yang sedang aktif!')
        return redirect('user_list')

    if request.method == 'POST':
        user.delete()
        messages.success(request, f'Pengguna "{user.username}" berhasil dihapus!')
        return redirect('user_list')
    return render(request, 'core/custom_admin/user/user_confim_delete.html', {'object': user})


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
        old_name = profile.nama_lengkap or request.user.username
        form = ProfileProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()

            # Sync author name across all articles & stories
            new_name = profile.nama_lengkap or request.user.username
            if old_name != new_name:
                Article.objects.filter(author=old_name).update(author=new_name)
                Story.objects.filter(author=old_name).update(author=new_name)

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
from .models import Program

class ProgramListView(AdminRequiredMixin, ListView):
    model = Program
    template_name = 'core/custom_admin/programs/programs_list.html'
    context_object_name = 'programs'
    paginate_by = 10

    def get_queryset(self):
        return Program.objects.all().order_by('-tanggal', '-id')

class ProgramCreateView(AdminRequiredMixin, DateInputMixin, MediaAssetPickerMixin, CreateView):
    model = Program
    template_name = 'core/custom_admin/programs/programs_form.html'
    fields = ['judul_ind', 'judul_en', 'slug_ind', 'slug_en', 'short_ind', 'short_en', 'deskripsi_ind', 'deskripsi_en', 'tanggal', 'gambar']
    success_url = reverse_lazy('program_list')

    def form_valid(self, form):
        from django.utils.text import slugify
        
        user = self.request.user
        form.instance.author = user.profile.nama_lengkap if hasattr(user, 'profile') and user.profile.nama_lengkap else user.username

        base_slug = form.cleaned_data.get('slug_ind') or slugify(form.cleaned_data.get('judul_ind') or form.cleaned_data.get('judul'))
        slug = base_slug[:200]
        
        queryset = Program.objects.filter(slug_ind=slug)
        if queryset.exists():
            original_slug = slug
            counter = 1
            while Program.objects.filter(slug_ind=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1
                
        form.instance.slug_ind = slug
        if not form.instance.slug_en:
            form.instance.slug_en = slug
        
        messages.success(self.request, 'Program baru berhasil ditambahkan!')
        return super().form_valid(form)

class ProgramUpdateView(AdminRequiredMixin, DateInputMixin, MediaAssetPickerMixin, UpdateView):
    model = Program
    template_name = 'core/custom_admin/programs/programs_form.html'
    fields = ['judul_ind', 'judul_en', 'slug_ind', 'slug_en', 'short_ind', 'short_en', 'deskripsi_ind', 'deskripsi_en', 'tanggal', 'gambar']
    success_url = reverse_lazy('program_list')

    def form_valid(self, form):
        from django.utils.text import slugify
        
        user = self.request.user
        form.instance.author = user.profile.nama_lengkap if hasattr(user, 'profile') and user.profile.nama_lengkap else user.username

        base_slug = form.cleaned_data.get('slug_ind') or slugify(form.cleaned_data.get('judul_ind') or form.cleaned_data.get('judul'))
        slug = base_slug[:200]
        
        queryset = Program.objects.filter(slug_ind=slug).exclude(pk=self.object.pk)
        if queryset.exists():
            original_slug = slug
            counter = 1
            while Program.objects.filter(slug_ind=slug).exclude(pk=self.object.pk).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1
                
        form.instance.slug_ind = slug
        if not form.instance.slug_en:
            form.instance.slug_en = slug
            
        messages.success(self.request, 'Data program berhasil diperbarui!')
        return super().form_valid(form)

def program_delete_view(request, pk):
    program = get_object_or_404(Program, pk=pk)
    if request.method == 'POST':
        program.delete()
        messages.success(request, 'Program berhasil dihapus!')
    return redirect('program_list')

def detail_program_view(request, slug):
    program_data = get_object_or_404(Program, Q(slug_ind=slug) | Q(slug_en=slug) if hasattr(Program, 'slug_en') else Q(slug=slug))
    
    program_data.views_count += 1
    program_data.save(update_fields=['views_count'])
    
    related_programs = Program.objects.filter(
        Q(author=program_data.author)
    ).exclude(pk=program_data.pk).order_by('-tanggal')[:3]
    
    if related_programs.count() < 3:
        extra_programs = Program.objects.exclude(pk=program_data.pk).exclude(pk__in=related_programs.values_list('pk', flat=True)).order_by('-tanggal')[:3 - related_programs.count()]
        related_programs = list(related_programs) + list(extra_programs)

    return render(request, 'core/detail-programs.html', {
        'program': program_data,
        'related_programs': related_programs
    })
