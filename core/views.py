from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django import forms
from django.db.models import Min, Max
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Article, Project, Client, Story, Service, Location, Category, Modul, ContactMessage, Gallery, Profile, Folder, TeamMember

# ==========================================
# JALUR FRONTEND WEBSITE (NAVBAR & MENUS)
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
    projects = Project.objects.select_related('client').prefetch_related('locations', 'categories').order_by('-tahun')
    categories = Category.objects.filter(projects__isnull=False).distinct().order_by('name')
    years = Project.objects.order_by('-tahun').values_list('tahun', flat=True).distinct()
    
    # Kategori Mitra/Klien Swasta & Publik
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

def gallery_view(request):
    articles = Article.objects.order_by('-tanggal')
    stories = Story.objects.order_by('-tanggal')
    documents = Modul.objects.order_by('-tanggal_rilis')
    categories = Category.objects.filter(folders__isnull=False).distinct().order_by('name')
    gallery_items = Gallery.objects.all()
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
            ContactMessage.objects.create(
                nama_lengkap=nama,
                email=email,
                subjek=subjek,
                pesan=pesan
            )
            messages.success(request, 'Pesan Anda berhasil dikirim! Tim kami akan segera menghubungi Anda.')
            return redirect('contact')
        else:
            messages.error(request, 'Gagal mengirim pesan. Harap isi semua kolom formulir dengan benar.')

    return render(request, 'core/contact.html')

def story_view(request):
    stories_data = Story.objects.select_related('lokasi', 'project').order_by('-tanggal')
    return render(request, 'core/story.html', {'stories': stories_data})

# ==========================================
# JALUR FRONTEND HALAMAN DETAIL (DINAMIS)
# ==========================================
def detail_articles_view(request, slug):
    article_data = get_object_or_404(Article, slug=slug)
    return render(request, 'core/detail-articles.html', {'article': article_data})

def detail_experience_view(request, slug):
    project_data = get_object_or_404(
        Project.objects.select_related('client', 'service_portfolio').prefetch_related('locations', 'categories', 'metrics'),
        slug=slug
    )
    related_projects = Project.objects.filter(
        categories__in=project_data.categories.all()
    ).exclude(pk=project_data.pk).distinct().order_by('-tahun')[:3]
    return render(request, 'core/detail-experience.html', {
        'project': project_data,
        'related_projects': related_projects,
    })

def detail_services_view(request, slug):
    service_data = get_object_or_404(Service, slug=slug)
    nrm_services = Service.objects.filter(portfolio='NRM')
    nru_services = Service.objects.filter(portfolio='NRU')
    return render(request, 'core/detail-services.html', {
        'service': service_data,
        'nrm_services': nrm_services,
        'nru_services': nru_services,
    })

def detail_story_view(request, slug):
    story_data = get_object_or_404(Story.objects.select_related('lokasi', 'project'), slug=slug)
    return render(request, 'core/detail-story.html', {'story': story_data})


# ==========================================
# PROTEKSI & SECURITY MIXIN
# ==========================================
@user_passes_test(lambda u: u.is_staff, login_url='/be/login/')
def custom_dashboard(request):
    context = {
        'total_articles': Article.objects.count(),
        'total_projects': Project.objects.count(),
        'total_clients': Client.objects.count(),
        'total_stories': Story.objects.count(),
        'total_documents': Modul.objects.count(),  
        'total_messages': ContactMessage.objects.count(),
        'total_gallery': Gallery.objects.count(),
        'total_team': TeamMember.objects.count(),
        'recent_articles': Article.objects.order_by('-id')[:5],
        'recent_projects': Project.objects.order_by('-id')[:5],
    }
    return render(request, 'core/custom_admin/dashboard.html', context)

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/be/login/'
    def test_func(self):
        return self.request.user.is_staff


# ==========================================
# 1. MANAGEMENT ARTIKEL & WAWASAN TEKNIS
# ==========================================
class ArticleListView(AdminRequiredMixin, ListView):
    model = Article
    template_name = 'core/custom_admin/articles/articles_list.html'
    context_object_name = 'articles'

class ArticleCreateView(AdminRequiredMixin, CreateView):
    model = Article
    template_name = 'core/custom_admin/articles/articles_form.html'
    fields = ['judul', 'slug', 'author', 'short', 'deskripsi', 'tanggal', 'gambar']
    success_url = reverse_lazy('article_list')

    def form_valid(self, form):
        from django.utils.text import slugify
        base_slug = form.cleaned_data.get('slug') or slugify(form.cleaned_data.get('judul'))
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
    fields = ['judul', 'slug', 'author', 'short', 'deskripsi', 'tanggal', 'gambar']
    success_url = reverse_lazy('article_list')

    def form_valid(self, form):
        from django.utils.text import slugify
        base_slug = form.cleaned_data.get('slug') or slugify(form.cleaned_data.get('judul'))
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

class ArticleDeleteView(AdminRequiredMixin, DeleteView):
    model = Article
    template_name = 'core/custom_admin/articles/article_confirm_delete.html'
    success_url = reverse_lazy('article_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Artikel berhasil dihapus permanen!')
        return super().delete(request, *args, **kwargs)


# ==========================================
# 2. MANAGEMENT PROYEK (EXPERIENCE)
# ==========================================
class ProjectListView(AdminRequiredMixin, ListView):
    model = Project
    template_name = 'core/custom_admin/experience/experience_list.html'
    context_object_name = 'projects'

class ProjectCreateView(AdminRequiredMixin, CreateView):
    model = Project
    template_name = 'core/custom_admin/experience/experience_form.html'
    fields = ['name', 'slug', 'description', 'tahun', 'image', 'client', 'service_portfolio', 'locations', 'categories']
    success_url = reverse_lazy('project_list')

class ProjectUpdateView(AdminRequiredMixin, UpdateView):
    model = Project
    template_name = 'core/custom_admin/experience/experience_form.html'
    fields = ['name', 'slug', 'description', 'tahun', 'image', 'client', 'service_portfolio', 'locations', 'categories']
    success_url = reverse_lazy('project_list')

class ProjectDeleteView(AdminRequiredMixin, DeleteView):
    model = Project
    template_name = 'core/custom_admin/experience/experience_confirm_delete.html'
    success_url = reverse_lazy('project_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Data proyek berhasil dihapus!')
        return super().delete(request, *args, **kwargs)

# ==========================================
# 3. MANAGEMENT CERITA LAPANGAN
# ==========================================
class StoryListView(AdminRequiredMixin, ListView):
    model = Story
    template_name = 'core/custom_admin/story/story_list.html'
    context_object_name = 'stories'

class StoryCreateView(AdminRequiredMixin, CreateView):
    model = Story
    template_name = 'core/custom_admin/story/story_form.html'
    fields = '__all__'
    success_url = reverse_lazy('story_list')

class StoryUpdateView(AdminRequiredMixin, UpdateView):
    model = Story
    template_name = 'core/custom_admin/story/story_form.html'
    fields = '__all__'
    success_url = reverse_lazy('story_list')

class StoryDeleteView(AdminRequiredMixin, DeleteView):
    model = Story
    template_name = 'core/custom_admin/story/story_confirm_delete.html'
    success_url = reverse_lazy('story_list')


# ==========================================
# 4. MANAGEMENT MITRA / KLIEN
# ==========================================
class ClientListView(AdminRequiredMixin, ListView):
    model = Client
    template_name = 'core/custom_admin/client/client_list.html'
    context_object_name = 'clients'

class ClientCreateView(AdminRequiredMixin, CreateView):
    model = Client
    template_name = 'core/custom_admin/client/client_form.html'
    fields = ['nama', 'sektor', 'logo']
    success_url = reverse_lazy('client_list')

    def form_valid(self, form):
        messages.success(self.request, 'Klien baru berhasil ditambahkan!')
        return super().form_valid(form)

class ClientUpdateView(AdminRequiredMixin, UpdateView):
    model = Client
    template_name = 'core/custom_admin/client/client_form.html'
    fields = ['nama', 'sektor', 'logo']
    success_url = reverse_lazy('client_list')

    def form_valid(self, form):
        messages.success(self.request, 'Data klien berhasil diperbarui!')
        return super().form_valid(form)

class ClientDeleteView(AdminRequiredMixin, DeleteView):
    model = Client
    template_name = 'core/custom_admin/client/client_confirm_delete.html'
    success_url = reverse_lazy('client_list')


# ==========================================
# 5. MANAGEMENT LAYANAN (SERVICES)
# ==========================================
class ServiceListView(AdminRequiredMixin, ListView):
    model = Service
    template_name = 'core/custom_admin/services/services_list.html'
    context_object_name = 'services'

class ServiceCreateView(AdminRequiredMixin, CreateView):
    model = Service
    template_name = 'core/custom_admin/services/services_form.html'
    fields = ['title', 'slug', 'approach', 'portfolio', 'icon', 'thumbnail', 'bg_image', 'intro', 'categories']
    success_url = reverse_lazy('service_list')

class ServiceUpdateView(AdminRequiredMixin, UpdateView):
    model = Service
    template_name = 'core/custom_admin/services/services_form.html'
    fields = ['title', 'slug', 'approach', 'portfolio', 'icon', 'thumbnail', 'bg_image', 'intro', 'categories']
    success_url = reverse_lazy('service_list')

class ServiceDeleteView(AdminRequiredMixin, DeleteView):
    model = Service
    template_name = 'core/custom_admin/services/services_confirm_delete.html'
    success_url = reverse_lazy('service_list')


# ==========================================
# 6. MANAGEMENT LOKASI WILAYAH
# ==========================================
class LocationListView(AdminRequiredMixin, ListView):
    model = Location
    template_name = 'core/custom_admin/location/location_list.html'
    context_object_name = 'locations'

class LocationCreateView(AdminRequiredMixin, CreateView):
    model = Location
    template_name = 'core/custom_admin/location/location_form.html'
    fields = '__all__'
    success_url = reverse_lazy('location_list')

class LocationUpdateView(AdminRequiredMixin, UpdateView):
    model = Location
    template_name = 'core/custom_admin/location/location_form.html'
    fields = '__all__'
    success_url = reverse_lazy('location_list')

class LocationDeleteView(AdminRequiredMixin, DeleteView):
    model = Location
    template_name = 'core/custom_admin/location/location_confirm_delete.html'
    success_url = reverse_lazy('location_list')


# ==========================================
# 7. MANAGEMENT KATEGORI
# ==========================================
class CategoryListView(AdminRequiredMixin, ListView):
    model = Category
    template_name = 'core/custom_admin/category/category_list.html'
    context_object_name = 'categories'

class CategoryCreateView(AdminRequiredMixin, CreateView):
    model = Category
    template_name = 'core/custom_admin/category/category_form.html'
    fields = '__all__'
    success_url = reverse_lazy('category_list')

class CategoryUpdateView(AdminRequiredMixin, UpdateView):
    model = Category
    template_name = 'core/custom_admin/category/category_form.html'
    fields = '__all__'
    success_url = reverse_lazy('category_list')

class CategoryDeleteView(AdminRequiredMixin, DeleteView):
    model = Category
    template_name = 'core/custom_admin/category/category_confirm_delete.html'
    success_url = reverse_lazy('category_list')


# ==========================================
# 8. MANAGEMENT MODUL DOKUMEN
# ==========================================
class DocumentListView(AdminRequiredMixin, ListView):
    model = Modul  
    template_name = 'core/custom_admin/modul/modul_list.html'
    context_object_name = 'documents'

class DocumentCreateView(AdminRequiredMixin, CreateView):
    model = Modul
    template_name = 'core/custom_admin/modul/modul_form.html'
    fields = '__all__'
    success_url = reverse_lazy('document_list')

class DocumentUpdateView(AdminRequiredMixin, UpdateView):
    model = Modul
    template_name = 'core/custom_admin/modul/modul_form.html'
    fields = '__all__'
    success_url = reverse_lazy('document_list')

class DocumentDeleteView(AdminRequiredMixin, DeleteView):
    model = Modul
    template_name = 'core/custom_admin/modul/modul_confirm_delete.html'
    success_url = reverse_lazy('document_list')


# ==========================================
# 9. MANAGEMENT KONTAK / PESAN MASUK
# ==========================================
class ContactListView(AdminRequiredMixin, ListView):
    model = ContactMessage
    template_name = 'core/custom_admin/contact/contact_list.html'
    context_object_name = 'contacts'

    def get_queryset(self):
        return ContactMessage.objects.all().order_by('-tanggal_kirim')

class ContactDeleteView(AdminRequiredMixin, DeleteView):
    model = ContactMessage
    template_name = 'core/custom_admin/contact/contact_confirm_delete.html'
    success_url = reverse_lazy('contact_list')

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

class GalleryCreateView(AdminRequiredMixin, CreateView):
    model = Gallery
    template_name = 'core/custom_admin/gallery/gallery_form.html'
    fields = ['caption', 'gambar', 'folder', 'kategori', 'tanggal_upload']
    success_url = reverse_lazy('gallery_admin_list')

class GalleryUpdateView(AdminRequiredMixin, UpdateView):
    model = Gallery
    template_name = 'core/custom_admin/gallery/gallery_form.html'
    fields = ['caption', 'gambar', 'folder', 'kategori', 'tanggal_upload']
    success_url = reverse_lazy('gallery_admin_list')

class GalleryDeleteView(AdminRequiredMixin, DeleteView):
    model = Gallery
    template_name = 'core/custom_admin/gallery/gallery_confirm_delete.html'
    success_url = reverse_lazy('gallery_admin_list')


# ==========================================
# 10b. MANAGEMENT FOLDER / ALBUM GALERI
# ==========================================
class FolderListView(AdminRequiredMixin, ListView):
    model = Folder
    template_name = 'core/custom_admin/gallery/folder_list.html'
    context_object_name = 'folders'

class FolderCreateView(AdminRequiredMixin, CreateView):
    model = Folder
    template_name = 'core/custom_admin/gallery/folder_form.html'
    fields = '__all__'
    success_url = reverse_lazy('folder_list')

class FolderUpdateView(AdminRequiredMixin, UpdateView):
    model = Folder
    template_name = 'core/custom_admin/gallery/folder_form.html'
    fields = '__all__'
    success_url = reverse_lazy('folder_list')

class FolderDeleteView(AdminRequiredMixin, DeleteView):
    model = Folder
    template_name = 'core/custom_admin/gallery/folder_confirm_delete.html'
    success_url = reverse_lazy('folder_list')


# ==========================================
# 10c. MANAGEMENT TIM AHLI KAMI (TEAM)
# ==========================================
class TeamListView(AdminRequiredMixin, ListView):
    model = TeamMember
    template_name = 'core/custom_admin/team/team_list.html'
    context_object_name = 'members'

class TeamCreateView(AdminRequiredMixin, CreateView):
    model = TeamMember
    template_name = 'core/custom_admin/team/team_form.html'
    fields = ['nama', 'jabatan', 'bio', 'kategori', 'urutan', 'foto']
    success_url = reverse_lazy('team_list')

    def form_valid(self, form):
        messages.success(self.request, 'Anggota tim baru berhasil ditambahkan!')
        return super().form_valid(form)

class TeamUpdateView(AdminRequiredMixin, UpdateView):
    model = TeamMember
    template_name = 'core/custom_admin/team/team_form.html'
    fields = ['nama', 'jabatan', 'bio', 'kategori', 'urutan', 'foto']
    success_url = reverse_lazy('team_list')

    def form_valid(self, form):
        messages.success(self.request, 'Data anggota tim berhasil diperbarui!')
        return super().form_valid(form)

class TeamDeleteView(AdminRequiredMixin, DeleteView):
    model = TeamMember
    template_name = 'core/custom_admin/team/team_confirm_delete.html'
    success_url = reverse_lazy('team_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Anggota tim berhasil dihapus!')
        return super().delete(request, *args, **kwargs)


# ==========================================
# PROTEKSI KHUSUS SUPERUSER
# ==========================================
class SuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_superuser


# ==========================================
# 11. MANAGEMENT USER / PENGGUNA
# ==========================================
class UserListView(SuperuserRequiredMixin, ListView):
    model = User
    template_name = 'core/custom_admin/user/user_list.html'
    context_object_name = 'users'

class UserCreateView(SuperuserRequiredMixin, CreateView):
    model = User
    template_name = 'core/custom_admin/user/user_form.html'
    fields = ['username', 'email', 'password', 'is_staff', 'is_active', 'is_superuser']
    success_url = reverse_lazy('user_list')
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        return super().form_valid(form)

class UserUpdateView(SuperuserRequiredMixin, UpdateView):
    model = User
    template_name = 'core/custom_admin/user/user_form.html'
    fields = ['username', 'email', 'is_staff', 'is_active', 'is_superuser']
    success_url = reverse_lazy('user_list')

class UserDeleteView(SuperuserRequiredMixin, DeleteView):
    model = User
    template_name = 'core/custom_admin/user/user_confirm_delete.html'
    success_url = reverse_lazy('user_list')


# ==========================================
# 12. FITUR EDIT PROFIL MANDIRI USER
# ==========================================
class ProfileProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['nama_lengkap', 'foto_profil']

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