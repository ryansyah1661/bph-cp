from modeltranslation.translator import register, TranslationOptions
from .models import Article, Project, Story, Service, ServiceStep, Modul

@register(Article)
class ArticleTranslationOptions(TranslationOptions):
    fields = ('judul', 'short', 'deskripsi')

@register(Project)
class ProjectTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'intro', 'challenge', 'methodology', 'result')

@register(Story)
class StoryTranslationOptions(TranslationOptions):
    fields = ('judul', 'short', 'deskripsi')

@register(Service)
class ServiceTranslationOptions(TranslationOptions):
    fields = ('title', 'approach')

@register(ServiceStep)
class ServiceStepTranslationOptions(TranslationOptions):
    fields = ('title', 'desc')

@register(Modul)
class ModulTranslationOptions(TranslationOptions):
    fields = ('judul',)
