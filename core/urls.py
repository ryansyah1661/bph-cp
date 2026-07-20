from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core import views

urlpatterns = [
    # Jembatan Utama bawaan Django Admin
    path('admin/', admin.site.urls),

    # ROUTING FRONTEND WEBSITE (Halaman Utama Pengunjung)
    path('', views.homepage, name='homepage'),
    path('about/', views.about_view, name='about'),
    path('services/', views.services_view, name='services'),
    path('experience/', views.experience_view, name='experience'),
    path('gallery/', views.gallery_view, name='gallery'),
    path('contact/', views.contact_view, name='contact'),
    path('stories/', views.story_view, name='stories'),

    # ROUTING FRONTEND HALAMAN DETAIL (Versi Pengunjung)
    path('articles/detail/<slug:slug>/', views.detail_articles_view, name='detail-articles'),
    path('experience/detail/<slug:slug>/', views.detail_experience_view, name='detail-experience'),
    path('services/detail/<slug:slug>/', views.detail_services_view, name='detail-services'),
    path('story/detail/<slug:slug>/', views.detail_story_view, name='detail-story'),

    # =========================================================================
    # URL ROUTING BACKEND CUSTOM ADMIN PANEL
    # =========================================================================
    path('be/', views.custom_dashboard, name='custom_dashboard'),

    # URL ROUTING UNTUK LOGIN & LOGOUT ADMIN
    path('be/login/', auth_views.LoginView.as_view(template_name='core/custom_admin/login.html'), name='admin_login'),
    path('be/logout/', auth_views.LogoutView.as_view(next_page='admin_login'), name='admin_logout'),

    # URL ROUTING CRUD USER
    path('be/users/', views.UserListView.as_view(), name='user_list'),
    path('be/users/add/', views.UserCreateView.as_view(), name='user_create'),
    path('be/users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='user_update'),
    path('be/users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),

    # URL ROUTING EDIT PROFILE
    path('be/profile/edit/', views.user_edit_profile, name='user_edit_profile'),

    # URL ROUTING CRUD ARTIKEL
    path('be/articles/', views.ArticleListView.as_view(), name='article_list'),
    path('be/articles/add/', views.ArticleCreateView.as_view(), name='article_create'),
    path('be/articles/<int:pk>/edit/', views.ArticleUpdateView.as_view(), name='article_update'),
    path('be/articles/<int:pk>/delete/', views.ArticleDeleteView.as_view(), name='article_delete'),

    # URL ROUTING CRUD PROYEK / EXPERIENCES
    path('be/experiences/', views.ProjectListView.as_view(), name='project_list'),
    path('be/experiences/add/', views.ProjectCreateView.as_view(), name='project_create'),
    path('be/experiences/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('be/experiences/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),

    # URL ROUTING CRUD CERITA LAPANGAN
    path('be/stories/', views.StoryListView.as_view(), name='story_list'),
    path('be/stories/add/', views.StoryCreateView.as_view(), name='story_create'),
    path('be/stories/<int:pk>/edit/', views.StoryUpdateView.as_view(), name='story_update'),
    path('be/stories/<int:pk>/delete/', views.StoryDeleteView.as_view(), name='story_delete'),

    # URL ROUTING CRUD KLIEN / MITRA
    path('be/clients/', views.ClientListView.as_view(), name='client_list'),
    path('be/clients/add/', views.ClientCreateView.as_view(), name='client_create'),
    path('be/clients/<int:pk>/edit/', views.ClientUpdateView.as_view(), name='client_update'),
    path('be/clients/<int:pk>/delete/', views.ClientDeleteView.as_view(), name='client_delete'),

    # URL ROUTING CRUD LAYANAN (SERVICES)
    path('be/services-panel/', views.ServiceListView.as_view(), name='service_list'),
    path('be/services-panel/add/', views.ServiceCreateView.as_view(), name='service_create'),
    path('be/services-panel/<int:pk>/edit/', views.ServiceUpdateView.as_view(), name='service_update'),
    path('be/services-panel/<int:pk>/delete/', views.ServiceDeleteView.as_view(), name='service_delete'),

    # URL ROUTING CRUD LOKASI WILAYAH
    path('be/locations/', views.LocationListView.as_view(), name='location_list'),
    path('be/locations/add/', views.LocationCreateView.as_view(), name='location_create'),
    path('be/locations/<int:pk>/edit/', views.LocationUpdateView.as_view(), name='location_update'),
    path('be/locations/<int:pk>/delete/', views.LocationDeleteView.as_view(), name='location_delete'),

    # URL ROUTING CRUD KATEGORI
    path('be/categories/', views.CategoryListView.as_view(), name='category_list'),
    path('be/categories/add/', views.CategoryCreateView.as_view(), name='category_create'),
    path('be/categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('be/categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),

    # URL ROUTING CRUD DOKUMEN (MODUL)
    path('be/documents/', views.DocumentListView.as_view(), name='document_list'),
    path('be/documents/add/', views.DocumentCreateView.as_view(), name='document_create'),
    path('be/documents/<int:pk>/edit/', views.DocumentUpdateView.as_view(), name='document_update'),
    path('be/documents/<int:pk>/delete/', views.DocumentDeleteView.as_view(), name='document_delete'),

    # URL ROUTING CRUD PESAN KONTAK
    path('be/messages/', views.ContactListView.as_view(), name='contact_list'),
    path('be/messages/<int:pk>/delete/', views.ContactDeleteView.as_view(), name='contact_delete'),
    path('be/messages/<int:pk>/read/', views.mark_message_as_read, name='mark_message_as_read'),

    # URL ROUTING CRUD GALERI DOKUMENTASI
    path('be/gallery/', views.GalleryListView.as_view(), name='gallery_admin_list'),
    path('be/gallery/add/', views.GalleryCreateView.as_view(), name='gallery_admin_create'),
    path('be/gallery/<int:pk>/edit/', views.GalleryUpdateView.as_view(), name='gallery_admin_update'),
    path('be/gallery/<int:pk>/delete/', views.GalleryDeleteView.as_view(), name='gallery_admin_delete'),

    # URL ROUTING CRUD FOLDER GALERI DOKUMENTASI
    path('be/folders/', views.FolderListView.as_view(), name='folder_list'),
    path('be/folders/add/', views.FolderCreateView.as_view(), name='folder_create'),
    path('be/folders/<int:pk>/edit/', views.FolderUpdateView.as_view(), name='folder_update'),
    path('be/folders/<int:pk>/delete/', views.FolderDeleteView.as_view(), name='folder_delete'),

    # =========================================================================
    # ALUR SISTEM LUPA PASSWORD (AUTHENTICATION FLOW)
    # =========================================================================
    
    # 1. Halaman minta reset password (input email) + Template HTML E-mail Kustom
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='core/registration/password_reset_form.html',
             html_email_template_name='core/registration/password_reset_email.html'
         ), 
         name='password_reset'),
         
    # 2. Halaman konfirmasi email terkirim
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='core/registration/password_reset_done.html'), 
         name='password_reset_done'),
         
    # 3. Link unik token dari email yang diklik user (Sekarang dengan Icon Mata & Name Input Valid)
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='core/registration/password_reset_confirm.html'), 
         name='password_reset_confirm'),
         
    # 4. Halaman sukses setelah password berhasil diubah
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='core/registration/password_reset_complete.html'), 
         name='password_reset_complete'),
]