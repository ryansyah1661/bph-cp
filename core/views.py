from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Article, Project, Client, Story, Service, Location, Category, Modul, ContactMessage, Gallery

# ==========================================
# JALUR FRONTEND WEBSITE (NAVBAR & MENUS)
# ==========================================
def homepage(request):
    # Ambil 3 artikel terbaru berdasarkan tanggal terbit untuk section "Artikel Terbaru"
    articles = Article.objects.order_by('-tanggal')[:3]
    return render(request, 'core/homepage.html', {'articles': articles})

def about_view(request):
    return render(request, 'core/about.html')

def services_view(request):
    # Pisahkan berdasarkan portfolio karena section tampilan memang dibagi 2: NRM & NRU
    services_nrm = Service.objects.filter(portfolio='NRM').prefetch_related('categories')
    services_nru = Service.objects.filter(portfolio='NRU').prefetch_related('categories')
    return render(request, 'core/services.html', {
        'services_nrm': services_nrm,
        'services_nru': services_nru,
    })

def experience_view(request):
    projects = Project.objects.select_related('client', 'location').prefetch_related('categories').order_by('-tahun')
    # Kategori yang benar-benar dipakai minimal 1 proyek (untuk tombol filter dinamis)
    categories = Category.objects.filter(projects__isnull=False).distinct().order_by('name')
    # Tahun yang benar-benar ada datanya (untuk dropdown filter tahun dinamis)
    years = Project.objects.order_by('-tahun').values_list('tahun', flat=True).distinct()
    return render(request, 'core/experience.html', {
        'projects': projects,
        'categories': categories,
        'years': years,
    })

def gallery_view(request):
    # Ambil semua artikel, cerita lapangan, galeri dokumentasi, modul, dan kategori dari database
    articles = Article.objects.order_by('-tanggal')
    stories = Story.objects.order_by('-tanggal')
    gallery_items = Gallery.objects.select_related('kategori').order_by('-tanggal_upload')
    documents = Modul.objects.order_by('-tanggal_rilis')
    # Hanya ambil kategori yang benar-benar dipakai di minimal 1 item galeri,
    # supaya tidak ada tombol filter "kosong" yang tidak menampilkan apapun
    categories = Category.objects.filter(galleries__isnull=False).distinct().order_by('name')
    return render(request, 'core/gallery.html', {
        'articles': articles,
        'stories': stories,
        'gallery_items': gallery_items,
        'documents': documents,
        'categories': categories,
    })

def contact_view(request):
    return render(request, 'core/contact.html')

# ==========================================
# JALUR FRONTEND HALAMAN DETAIL (DINAMIS QUERY DB)
# ==========================================
def detail_articles_view(request, slug):
    article_data = get_object_or_404(Article, slug=slug)
    return render(request, 'core/detail-articles.html', {'article': article_data})

def detail_experience_view(request, slug):
    project_data = get_object_or_404(
        Project.objects.select_related('client', 'location', 'service_portfolio').prefetch_related('categories', 'metrics'),
        slug=slug
    )
    # Proyek lain yang berbagi kategori yang sama, untuk section "Pengalaman Terkait"
    related_projects = Project.objects.filter(
        categories__in=project_data.categories.all()
    ).exclude(pk=project_data.pk).distinct().order_by('-tahun')[:3]
    return render(request, 'core/detail-experience.html', {
        'project': project_data,
        'related_projects': related_projects,
    })

def detail_services_view(request, slug):
    service_data = get_object_or_404(Service, slug=slug)
    # Untuk sidebar navigasi dinamis (dulu hardcoded 6 NRM + 6 NRU manual)
    nrm_services = Service.objects.filter(portfolio='NRM')
    nru_services = Service.objects.filter(portfolio='NRU')
    return render(request, 'core/detail-services.html', {
        'service': service_data,
        'nrm_services': nrm_services,
        'nru_services': nru_services,
    })

def detail_story_view(request, slug):
    story_data = get_object_or_404(Story, slug=slug)
    return render(request, 'core/detail-story.html', {'story': story_data})

# ==========================================
# PROTEKSI & SECURITY MIXIN (FIXED PATH CORE)
# ==========================================
@user_passes_test(lambda u: u.is_staff, login_url='/bph-panel/login/')
def custom_dashboard(request):
    context = {
        'total_articles': Article.objects.count(),
        'total_projects': Project.objects.count(),
        'total_clients': Client.objects.count(),
        'total_stories': Story.objects.count(),
        'total_documents': Modul.objects.count(),  
        'total_messages': ContactMessage.objects.count(),
        'total_gallery': Gallery.objects.count(),
        'recent_articles': Article.objects.order_by('-id')[:5],
        'recent_projects': Project.objects.order_by('-id')[:5],
    }
    return render(request, 'core/custom_admin/dashboard.html', context)

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/bph-panel/login/'
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
    fields = '__all__'
    success_url = reverse_lazy('article_list')

class ArticleUpdateView(AdminRequiredMixin, UpdateView):
    model = Article
    template_name = 'core/custom_admin/articles/articles_form.html'
    fields = '__all__'
    success_url = reverse_lazy('article_list')

class ArticleDeleteView(AdminRequiredMixin, DeleteView):
    model = Article
    template_name = 'core/custom_admin/articles/article_confirm_delete.html'
    success_url = reverse_lazy('article_list')

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
    fields = '__all__'
    success_url = reverse_lazy('project_list')

class ProjectUpdateView(AdminRequiredMixin, UpdateView):
    model = Project
    template_name = 'core/custom_admin/experience/experience_form.html'
    fields = '__all__'
    success_url = reverse_lazy('project_list')

class ProjectDeleteView(AdminRequiredMixin, DeleteView):
    model = Project
    template_name = 'core/custom_admin/experience/experience_confirm_delete.html'
    success_url = reverse_lazy('project_list')

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
    fields = '__all__'
    success_url = reverse_lazy('client_list')

class ClientUpdateView(AdminRequiredMixin, UpdateView):
    model = Client
    template_name = 'core/custom_admin/client/client_form.html'
    fields = '__all__'
    success_url = reverse_lazy('client_list')

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
    fields = '__all__'
    success_url = reverse_lazy('service_list')

class ServiceUpdateView(AdminRequiredMixin, UpdateView):
    model = Service
    template_name = 'core/custom_admin/services/services_form.html'
    fields = '__all__'
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
    context_object_name = 'messages'

class ContactDeleteView(AdminRequiredMixin, DeleteView):
    model = ContactMessage
    template_name = 'core/custom_admin/contact/contact_confirm_delete.html'
    success_url = reverse_lazy('contact_list')

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
    fields = '__all__'
    success_url = reverse_lazy('gallery_admin_list')

class GalleryUpdateView(AdminRequiredMixin, UpdateView):
    model = Gallery
    template_name = 'core/custom_admin/gallery/gallery_form.html'
    fields = '__all__'
    success_url = reverse_lazy('gallery_admin_list')

class GalleryDeleteView(AdminRequiredMixin, DeleteView):
    model = Gallery
    template_name = 'core/custom_admin/gallery/gallery_confirm_delete.html'
    success_url = reverse_lazy('gallery_admin_list')