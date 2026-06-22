from django.contrib import admin
from .models import Category, Service, ServiceStep, Location, Client, Project, Story, Article

# Konfigurasi input tahapan pelaksanaan langsung di dalam halaman detail Service (Inline)
class ServiceStepInline(admin.TabularInline):
    model = ServiceStep
    extra = 1

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'portfolio')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('categories',)  # Antarmuka boks geser kanan-kiri untuk pilih multi-kategori
    inlines = [ServiceStepInline]

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'tahun', 'location', 'client')
    list_filter = ('tahun', 'location', 'categories')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('categories',)  # Antarmuka boks geser kanan-kiri untuk pilih multi-kategori

@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('judul', 'tanggal', 'author')
    search_fields = ('judul', 'deskripsi')
    prepopulated_fields = {'slug': ('judul',)}

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('judul', 'tanggal', 'author')
    search_fields = ('judul', 'deskripsi')
    prepopulated_fields = {'slug': ('judul',)}

# Registrasi tabel master pendukung lainnya
admin.site.register(Category)
admin.site.register(Location)
admin.site.register(Client)