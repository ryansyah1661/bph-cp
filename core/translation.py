from modeltranslation.translator import register, TranslationOptions
from .models import Article, Project, Story, Service, ServiceStep, Modul, Category, Location, Client, Gallery, Folder, TeamMember

@register(Article)
class ArticleTranslationOptions(TranslationOptions):
    fields = ('judul', 'slug', 'short', 'deskripsi')

@register(Project)
class ProjectTranslationOptions(TranslationOptions):
    fields = ('name', 'slug', 'description', 'intro', 'challenge', 'methodology', 'result')

@register(Story)
class StoryTranslationOptions(TranslationOptions):
    fields = ('judul', 'slug', 'short', 'deskripsi')

@register(Service)
class ServiceTranslationOptions(TranslationOptions):
    fields = ('title', 'slug', 'approach')

@register(ServiceStep)
class ServiceStepTranslationOptions(TranslationOptions):
    fields = ('title', 'desc')

@register(Modul)
class ModulTranslationOptions(TranslationOptions):
    fields = ('judul',)

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'slug')

@register(Location)
class LocationTranslationOptions(TranslationOptions):
    fields = ('nama_provinsi', 'slug')

@register(Client)
class ClientTranslationOptions(TranslationOptions):
    fields = ('nama',)

@register(Gallery)
class GalleryTranslationOptions(TranslationOptions):
    fields = ('caption',)

@register(Folder)
class FolderTranslationOptions(TranslationOptions):
    fields = ('nama',)

@register(TeamMember)
class TeamMemberTranslationOptions(TranslationOptions):
    fields = ('jabatan', 'bio', 'kategori')
