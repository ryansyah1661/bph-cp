from django.contrib import admin
from .models import Category, Service, ServiceStep, Location, Client, Project, Story, Article

base_index = admin.site.index

def custom_admin_index(request, extra_context=None):
    if extra_context is None:
        extra_context = {}
        
    extra_context['total_articles'] = Article.objects.count()
    extra_context['total_projects'] = Project.objects.count()
    extra_context['total_clients'] = Client.objects.count()
    extra_context['total_stories'] = Story.objects.count()
    
    extra_context['recent_articles'] = Article.objects.order_by('-tanggal')[:5]
    extra_context['recent_projects'] = Project.objects.order_by('-tahun')[:5]
    
    return base_index(request, extra_context=extra_context)

admin.site.index = custom_admin_index


# ==============================================================================
# REGISTRASI MODEL ADMIN
# ==============================================================================
class ServiceStepInline(admin.TabularInline):
    model = ServiceStep
    extra = 1

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'portfolio')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('categories',)
    inlines = [ServiceStepInline]

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'tahun', 'client')
    list_filter = ('tahun', 'categories')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('locations', 'categories')
    
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

admin.site.register(Category)
admin.site.register(Location)
admin.site.register(Client)