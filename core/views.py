from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Article, Project, Client, Story, Service, Location

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
    project_data = get_object_or_404(Project, slug=slug) # Sesuaikan jika field di model bernama slug
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
    template_name = 'core/custom_admin/article_list.html'
    context_object_name = 'articles'

class ArticleCreateView(AdminRequiredMixin, CreateView):
    model = Article
    template_name = 'core/custom_admin/article_form.html'
    fields = '__all__'
    success_url = reverse_lazy('article_list')

class ArticleUpdateView(AdminRequiredMixin, UpdateView):
    model = Article
    template_name = 'core/custom_admin/article_form.html'
    fields = '__all__'
    success_url = reverse_lazy('article_list')

class ArticleDeleteView(AdminRequiredMixin, DeleteView):
    model = Article
    template_name = 'core/custom_admin/article_confirm_delete.html'
    success_url = reverse_lazy('article_list')

# ==========================================
# 2. MANAGEMENT PROYEK (EXPERIENCE)
# ==========================================
class ProjectListView(AdminRequiredMixin, ListView):
    model = Project
    template_name = 'core/custom_admin/project_list.html'
    context_object_name = 'projects'

class ProjectCreateView(AdminRequiredMixin, CreateView):
    model = Project
    template_name = 'core/custom_admin/project_form.html'
    fields = '__all__'
    success_url = reverse_lazy('project_list')

class ProjectUpdateView(AdminRequiredMixin, UpdateView):
    model = Project
    template_name = 'core/custom_admin/project_form.html'
    fields = '__all__'
    success_url = reverse_lazy('project_list')

class ProjectDeleteView(AdminRequiredMixin, DeleteView):
    model = Project
    template_name = 'core/custom_admin/project_confirm_delete.html'
    success_url = reverse_lazy('project_list')

# ==========================================
# 3. MANAGEMENT CERITA LAPANGAN
# ==========================================
class StoryListView(AdminRequiredMixin, ListView):
    model = Story
    template_name = 'core/custom_admin/story_list.html'
    context_object_name = 'stories'

class StoryCreateView(AdminRequiredMixin, CreateView):
    model = Story
    template_name = 'core/custom_admin/story_form.html'
    fields = '__all__'
    success_url = reverse_lazy('story_list')

class StoryUpdateView(AdminRequiredMixin, UpdateView):
    model = Story
    template_name = 'core/custom_admin/story_form.html'
    fields = '__all__'
    success_url = network = reverse_lazy('story_list')

class StoryDeleteView(AdminRequiredMixin, DeleteView):
    model = Story
    template_name = 'core/custom_admin/story_confirm_delete.html'
    success_url = reverse_lazy('story_list')

# ==========================================
# 4. MANAGEMENT MITRA / KLIEN
# ==========================================
class ClientListView(AdminRequiredMixin, ListView):
    model = Client
    template_name = 'core/custom_admin/client_list.html'
    context_object_name = 'clients'

class ClientCreateView(AdminRequiredMixin, CreateView):
    model = Client
    template_name = 'core/custom_admin/client_form.html'
    fields = '__all__'
    success_url = reverse_lazy('client_list')

class ClientUpdateView(AdminRequiredMixin, UpdateView):
    model = Client
    template_name = 'core/custom_admin/client_form.html'
    fields = '__all__'
    success_url = reverse_lazy('client_list')

class ClientDeleteView(AdminRequiredMixin, DeleteView):
    model = Client
    template_name = 'core/custom_admin/client_confirm_delete.html'
    success_url = reverse_lazy('client_list')

# ==========================================
# 5. MANAGEMENT LAYANAN (SERVICES)
# ==========================================
class ServiceListView(AdminRequiredMixin, ListView):
    model = Service
    template_name = 'core/custom_admin/service_list.html'
    context_object_name = 'services'

class ServiceCreateView(AdminRequiredMixin, CreateView):
    model = Service
    template_name = 'core/custom_admin/service_form.html'
    fields = '__all__'
    success_url = reverse_lazy('service_list')

class ServiceUpdateView(AdminRequiredMixin, UpdateView):
    model = Service
    template_name = 'core/custom_admin/service_form.html'
    fields = '__all__'
    success_url = reverse_lazy('service_list')

class ServiceDeleteView(AdminRequiredMixin, DeleteView):
    model = Service
    template_name = 'core/custom_admin/service_confirm_delete.html'
    success_url = reverse_lazy('service_list')

# ==========================================
# 6. MANAGEMENT LOKASI WILAYAH
# ==========================================
class LocationListView(AdminRequiredMixin, ListView):
    model = Location
    template_name = 'core/custom_admin/location_list.html'
    context_object_name = 'locations'

class LocationCreateView(AdminRequiredMixin, CreateView):
    model = Location
    template_name = 'core/custom_admin/location_form.html'
    fields = '__all__'
    success_url = reverse_lazy('location_list')

class LocationUpdateView(AdminRequiredMixin, UpdateView):
    model = Location
    template_name = 'core/custom_admin/location_form.html'
    fields = '__all__'
    success_url = reverse_lazy('location_list')

class LocationDeleteView(AdminRequiredMixin, DeleteView):
    model = Location
    template_name = 'core/custom_admin/location_confirm_delete.html'
    success_url = reverse_lazy('location_list')