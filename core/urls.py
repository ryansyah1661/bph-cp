from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='homepage'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('experience/', views.experience, name='experience'),
    path('services/', views.services, name='services'),
    path('gallery/', views.gallery, name='gallery'),
    path('articles/', views.articles, name='articles'),
    
    # Route dinamis menggunakan parameter <slug:slug>
    path('experience/<slug:slug>/', views.detail_experience, name='detail-experience'),
    path('services/<slug:slug>/', views.service_detail, name='detail-services'),
    
    # FIXED: Mendaftarkan rute dinamis baru khusus untuk detail rilis artikel & cerita lapangan BPH
    path('articles/<slug:slug>/', views.detail_article, name='detail-articles'),
]