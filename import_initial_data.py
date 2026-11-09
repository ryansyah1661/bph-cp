import os
import json
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bph_project.settings')
django.setup()

from core.models import (
    Category, Folder, Service, Client, Project,
    Story, Article, Modul, ContactMessage, Gallery,
    Profile, TeamMember, Infografis, Video, Program, Location, Regency
)

with open('datadump.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

print(f"Total items in dump: {len(items)}")

# 1. Categories
for it in items:
    if it['model'] == 'core.category':
        fields = it['fields'].copy()
        Category.objects.update_or_create(id=it['pk'], defaults=fields)
print("Categories processed")

# 2. Services
for it in items:
    if it['model'] == 'core.service':
        fields = it['fields'].copy()
        categories = fields.pop('categories', [])
        obj, _ = Service.objects.update_or_create(id=it['pk'], defaults=fields)
        if categories:
            obj.categories.set(categories)
print("Services processed")

# 3. Clients
for it in items:
    if it['model'] == 'core.client':
        fields = it['fields'].copy()
        Client.objects.update_or_create(id=it['pk'], defaults=fields)
print("Clients processed")

# 4. Team Members
for it in items:
    if it['model'] == 'core.teammember':
        fields = it['fields'].copy()
        TeamMember.objects.update_or_create(id=it['pk'], defaults=fields)
print("Team members processed")

# 5. Articles
for it in items:
    if it['model'] == 'core.article':
        fields = it['fields'].copy()
        Article.objects.update_or_create(id=it['pk'], defaults=fields)
print("Articles processed")

# 6. Programs
for it in items:
    if it['model'] == 'core.program':
        fields = it['fields'].copy()
        Program.objects.update_or_create(id=it['pk'], defaults=fields)
print("Programs processed")

# 7. Projects
for it in items:
    if it['model'] == 'core.project':
        fields = it['fields'].copy()
        client_id = fields.pop('client', None)
        if client_id and Client.objects.filter(id=client_id).exists():
            fields['client_id'] = client_id
        else:
            fields['client_id'] = None

        sp_id = fields.pop('service_portfolio', None)
        if sp_id and Service.objects.filter(id=sp_id).exists():
            fields['service_portfolio_id'] = sp_id
        else:
            fields['service_portfolio_id'] = None

        locations = fields.pop('locations', [])
        categories = fields.pop('categories', [])
        obj, _ = Project.objects.update_or_create(id=it['pk'], defaults=fields)
        if categories:
            obj.categories.set(categories)
        if locations:
            valid_locs = Location.objects.filter(id__in=locations).values_list('id', flat=True)
            obj.locations.set(valid_locs)
print("Projects processed")

# 8. Stories
for it in items:
    if it['model'] == 'core.story':
        fields = it['fields'].copy()
        lok_id = fields.pop('lokasi', None)
        if lok_id and Location.objects.filter(id=lok_id).exists():
            fields['lokasi_id'] = lok_id
        else:
            fields['lokasi_id'] = Location.objects.first().id if Location.objects.exists() else None

        proj_id = fields.pop('project', None)
        if proj_id and Project.objects.filter(id=proj_id).exists():
            fields['project_id'] = proj_id
        else:
            fields['project_id'] = None

        Story.objects.update_or_create(id=it['pk'], defaults=fields)
print("Stories processed")

# 9. Modul / Documents
for it in items:
    if it['model'] == 'core.modul':
        fields = it['fields'].copy()
        Modul.objects.update_or_create(id=it['pk'], defaults=fields)
print("Moduls processed")

# 10. Folders & Gallery
for it in items:
    if it['model'] == 'core.folder':
        fields = it['fields'].copy()
        kat_id = fields.pop('kategori', None)
        if kat_id and Category.objects.filter(id=kat_id).exists():
            fields['kategori_id'] = kat_id
        else:
            fields['kategori_id'] = None
        Folder.objects.update_or_create(id=it['pk'], defaults=fields)

for it in items:
    if it['model'] == 'core.gallery':
        fields = it['fields'].copy()
        folder_id = fields.pop('folder', None)
        if folder_id and Folder.objects.filter(id=folder_id).exists():
            fields['folder_id'] = folder_id
        else:
            fields['folder_id'] = None

        kat_id = fields.pop('kategori', None)
        if kat_id and Category.objects.filter(id=kat_id).exists():
            fields['kategori_id'] = kat_id
        else:
            fields['kategori_id'] = None

        Gallery.objects.update_or_create(id=it['pk'], defaults=fields)
print("Gallery & Folders processed")

# 11. Videos & Infografis
for it in items:
    if it['model'] == 'core.video':
        fields = it['fields'].copy()
        Video.objects.update_or_create(id=it['pk'], defaults=fields)

for it in items:
    if it['model'] == 'core.infografis':
        fields = it['fields'].copy()
        Infografis.objects.update_or_create(id=it['pk'], defaults=fields)
print("Videos & Infografis processed")

print("\nALL DATA SUCCESSFULLY IMPORTED!")
