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
        fields = it['fields']
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
        fields = it['fields']
        Client.objects.update_or_create(id=it['pk'], defaults=fields)
print("Clients processed")

# 4. Team Members
for it in items:
    if it['model'] == 'core.teammember':
        fields = it['fields']
        TeamMember.objects.update_or_create(id=it['pk'], defaults=fields)
print("Team members processed")

# 5. Articles
for it in items:
    if it['model'] == 'core.article':
        fields = it['fields']
        Article.objects.update_or_create(id=it['pk'], defaults=fields)
print("Articles processed")

# 6. Programs
for it in items:
    if it['model'] == 'core.program':
        fields = it['fields']
        Program.objects.update_or_create(id=it['pk'], defaults=fields)
print("Programs processed")

# 7. Stories
for it in items:
    if it['model'] == 'core.story':
        fields = it['fields']
        Story.objects.update_or_create(id=it['pk'], defaults=fields)
print("Stories processed")

# 8. Modul / Documents
for it in items:
    if it['model'] == 'core.modul':
        fields = it['fields']
        Modul.objects.update_or_create(id=it['pk'], defaults=fields)
print("Moduls processed")

# 9. Folders & Gallery
for it in items:
    if it['model'] == 'core.folder':
        fields = it['fields'].copy()
        kat_id = fields.pop('kategori', None)
        if kat_id:
            fields['kategori_id'] = kat_id
        Folder.objects.update_or_create(id=it['pk'], defaults=fields)

for it in items:
    if it['model'] == 'core.gallery':
        fields = it['fields'].copy()
        folder_id = fields.pop('folder', None)
        if folder_id:
            fields['folder_id'] = folder_id
        Gallery.objects.update_or_create(id=it['pk'], defaults=fields)
print("Gallery & Folders processed")

# 10. Videos & Infografis
for it in items:
    if it['model'] == 'core.video':
        fields = it['fields']
        Video.objects.update_or_create(id=it['pk'], defaults=fields)

for it in items:
    if it['model'] == 'core.infografis':
        fields = it['fields']
        Infografis.objects.update_or_create(id=it['pk'], defaults=fields)
print("Videos & Infografis processed")

# 11. Projects
for it in items:
    if it['model'] == 'core.project':
        fields = it['fields'].copy()
        client_id = fields.pop('client', None)
        if client_id:
            fields['client_id'] = client_id
        locations = fields.pop('locations', [])
        categories = fields.pop('categories', [])
        obj, _ = Project.objects.update_or_create(id=it['pk'], defaults=fields)
        if categories:
            obj.categories.set(categories)
        if locations:
            valid_locs = Location.objects.filter(id__in=locations).values_list('id', flat=True)
            obj.locations.set(valid_locs)
print("Projects processed")

print("\nALL DATA SUCCESSFULLY IMPORTED!")
