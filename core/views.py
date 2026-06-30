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
    return render(request, 'core/homepage.html')

def about_view(request):
    return render(request, 'core/about.html')

def services_view(request):
    return render(request, 'core/services.html')

def experience_view(request):
    return render(request, 'core/experience.html')

def gallery_view(request):
    return render(request, 'core/gallery.html')

def contact_view(request):
    return render(request, 'core/contact.html')

# ==========================================
# JALUR FRONTEND HALAMAN DETAIL (DINAMIS QUERY DB)
# ==========================================
def detail_articles_view(request, slug):
    article_data = get_object_or_404(Article, slug=slug)
    return render(request, 'core/detail-articles.html', {'article': article_data})

def detail_experience_view(request, slug):
    project_data = get_object_or_404(Project, slug=slug)
    return render(request, 'core/detail-experience.html', {'project': project_data})

def detail_services_view(request, slug):
    service_data = get_object_or_404(Service, slug=slug)
    return render(request, 'core/detail-services.html', {'service': service_data})

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