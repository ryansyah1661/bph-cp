from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core import views

urlpatterns = [
    # Jembatan Utama bawaan Django Admin
    path('admin/', admin.site.urls),

    # ROUTING FRONTEND WEBSITE
    path('', views.homepage, name='homepage'),
    path('about/', views.about_view, name='about'),
    path('services/', views.services_view, name='services'),
    path('experience/', views.experience_view, name='experience'),
    path('gallery/', views.gallery_view, name='gallery'),
    path('contact/', views.contact_view, name='contact'),

    # ROUTING FRONTEND HALAMAN DETAIL
    path('articles/detail/<slug:slug>/', views.detail_articles_view, name='detail-articles'),
    path('experience/detail/<slug:slug>/', views.detail_experience_view, name='detail-experience'),
    path('services/detail/<slug:slug>/', views.detail_services_view, name='detail-services'),
    path('story/detail/<slug:slug>/', views.detail_story_view, name='detail-story'),

    # URL ROUTING UNTUK LOGIN & LOGOUT
    path('bph-panel/login/', auth_views.LoginView.as_view(template_name='core/custom_admin/login.html'), name='admin_login'),
    path('bph-panel/logout/', auth_views.LogoutView.as_view(next_page='admin_login'), name='admin_logout'),

    # URL ROUTING PANEL DASHBOARD UTAMA
    path('bph-panel/', views.custom_dashboard, name='custom_dashboard'),

    # URL ROUTING CRUD ARTIKEL (FIXED NAME)
    path('bph-panel/articles/', views.ArticleListView.as_view(), name='article_list'),
    path('bph-panel/articles/add/', views.ArticleCreateView.as_view(), name='article_create'), # ← Ubah ke article_create
    path('bph-panel/articles/<int:pk>/edit/', views.ArticleUpdateView.as_view(), name='article_update'), # ← Ubah ke article_update
    path('bph-panel/articles/<int:pk>/delete/', views.ArticleDeleteView.as_view(), name='article_delete'),

    # URL ROUTING CRUD PROYEK / EXPERIENCES (FIXED NAME)
    path('bph-panel/experiences/', views.ProjectListView.as_view(), name='project_list'),
    path('bph-panel/experiences/add/', views.ProjectCreateView.as_view(), name='project_create'), # ← Ubah ke project_create
    path('bph-panel/experiences/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project_update'), # ← Ubah ke project_update
    path('bph-panel/experiences/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),

    # URL ROUTING CRUD CERITA LAPANGAN (FIXED NAME)
    path('bph-panel/stories/', views.StoryListView.as_view(), name='story_list'),
    path('bph-panel/stories/add/', views.StoryCreateView.as_view(), name='story_create'), # ← Ubah ke story_create
    path('bph-panel/stories/<int:pk>/edit/', views.StoryUpdateView.as_view(), name='story_update'), # ← Ubah ke story_update
    path('bph-panel/stories/<int:pk>/delete/', views.StoryDeleteView.as_view(), name='story_delete'),

    # URL ROUTING CRUD KLIEN / MITRA (FIXED NAME)
    path('bph-panel/clients/', views.ClientListView.as_view(), name='client_list'),
    path('bph-panel/clients/add/', views.ClientCreateView.as_view(), name='client_create'), # ← Ubah ke client_create
    path('bph-panel/clients/<int:pk>/edit/', views.ClientUpdateView.as_view(), name='client_update'), # ← Ubah ke client_update
    path('bph-panel/clients/<int:pk>/delete/', views.ClientDeleteView.as_view(), name='client_delete'),

    # URL ROUTING CRUD LAYANAN (SERVICES) (FIXED NAME)
    path('bph-panel/services-panel/', views.ServiceListView.as_view(), name='service_list'),
    path('bph-panel/services-panel/add/', views.ServiceCreateView.as_view(), name='service_create'), # ← Ubah ke service_create
    path('bph-panel/services-panel/<int:pk>/edit/', views.ServiceUpdateView.as_view(), name='service_update'), # ← Ubah ke service_update
    path('bph-panel/services-panel/<int:pk>/delete/', views.ServiceDeleteView.as_view(), name='service_delete'),

    # URL ROUTING CRUD LOKASI WILAYAH (FIXED NAME)
    path('bph-panel/locations/', views.LocationListView.as_view(), name='location_list'),
    path('bph-panel/locations/add/', views.LocationCreateView.as_view(), name='location_create'), # ← Ubah ke location_create
    path('bph-panel/locations/<int:pk>/edit/', views.LocationUpdateView.as_view(), name='location_update'), # ← Ubah ke location_update
    path('bph-panel/locations/<int:pk>/delete/', views.LocationDeleteView.as_view(), name='location_delete'),
]