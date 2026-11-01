import json
import os
from django.db import migrations
from django.utils.text import slugify

def populate_regencies(apps, schema_editor):
    Location = apps.get_model('core', 'Location')
    Regency = apps.get_model('core', 'Regency')

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    geojson_path = os.path.join(base_dir, 'static', 'data', 'indonesia_kabkot.json')

    if not os.path.exists(geojson_path):
        return

    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    prov_dict = {}
    for feat in data['features']:
        props = feat['properties']
        kp = str(props['kode_prov']).strip()
        pname = str(props['Prov_name']).strip()
        if kp not in prov_dict:
            loc, _ = Location.objects.get_or_create(
                kode_wilayah=kp,
                defaults={
                    'nama_provinsi': pname,
                    'nama_provinsi_ind': pname,
                    'nama_provinsi_en': pname,
                    'slug': slugify(pname),
                    'slug_ind': slugify(pname),
                    'slug_en': slugify(pname),
                }
            )
            prov_dict[kp] = loc

    for feat in data['features']:
        props = feat['properties']
        coords = feat['geometry']['coordinates']
        lon, lat = coords[0], coords[1]
        kp = str(props['kode_prov']).strip()
        kk = str(props['kode_kab']).strip()
        kname = str(props['KabKot_Name']).strip()
        prov = prov_dict.get(kp)
        if not prov:
            continue
        Regency.objects.update_or_create(
            kode_kab=kk,
            defaults={
                'provinsi': prov,
                'nama': kname,
                'nama_ind': kname,
                'nama_en': kname,
                'latitude': lat,
                'longitude': lon,
            }
        )

def unpopulate_regencies(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_alter_project_locations_alter_service_portfolio_and_more'),
    ]

    operations = [
        migrations.RunPython(populate_regencies, unpopulate_regencies),
    ]
