"""
Management command untuk mengimpor data GeoJSON provinsi Indonesia ke database PostGIS.
File GeoJSON: static/data/indonesia-38-provinces.geojson
Sumber: https://github.com/denyherianto/indonesia-geojson-topojson-maps-with-38-provinces
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from core.models import Location


# Mapping nama provinsi di GeoJSON → kode_wilayah BPS yang digunakan di model Location.
# Kode ini mengikuti PROVINCE_CODE_CHOICES di model Location.
PROVINCE_NAME_TO_CODE = {
    'Aceh': '11',
    'Sumatera Utara': '12',
    'Sumatera Barat': '13',
    'Riau': '14',
    'Jambi': '15',
    'Sumatera Selatan': '16',
    'Bengkulu': '17',
    'Lampung': '18',
    'Kepulauan Bangka Belitung': '19',
    'Kepulauan Riau': '21',
    'DKI Jakarta': '31',
    'Jawa Barat': '32',
    'Jawa Tengah': '33',
    'Daerah Istimewa Yogyakarta': '34',
    'Jawa Timur': '35',
    'Banten': '36',
    'Bali': '51',
    'Nusa Tenggara Barat': '52',
    'Nusa Tenggara Timur': '53',
    'Kalimantan Barat': '61',
    'Kalimantan Tengah': '62',
    'Kalimantan Selatan': '63',
    'Kalimantan Timur': '64',
    'Kalimantan Utara': '65',
    'Sulawesi Utara': '71',
    'Sulawesi Tengah': '72',
    'Sulawesi Selatan': '73',
    'Sulawesi Tenggara': '74',
    'Gorontalo': '75',
    'Sulawesi Barat': '76',
    'Maluku': '81',
    'Maluku Utara': '82',
    'Papua': '91',
    'Papua Barat': '92',
    'Papua Selatan': '93',
    'Papua Tengah': '94',
    'Papua Pegunungan': '95',
    'Papua Barat Daya': '96',
}


class Command(BaseCommand):
    help = 'Impor data geometri provinsi Indonesia dari file GeoJSON ke kolom geom di tabel Location.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='static/data/indonesia-38-provinces.geojson',
            help='Path relatif ke file GeoJSON (default: static/data/indonesia-38-provinces.geojson)',
        )
        parser.add_argument(
            '--create-missing',
            action='store_true',
            default=False,
            help='Buat record Location baru jika belum ada di database.',
        )

    def handle(self, *args, **options):
        geojson_path = Path(options['file'])
        if not geojson_path.is_absolute():
            from django.conf import settings
            geojson_path = Path(settings.BASE_DIR) / geojson_path

        if not geojson_path.exists():
            self.stderr.write(self.style.ERROR(f'File tidak ditemukan: {geojson_path}'))
            return

        with open(geojson_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        features = data.get('features', [])
        self.stdout.write(f'Memproses {len(features)} fitur dari GeoJSON...\n')

        updated = 0
        created = 0
        skipped = 0

        for feature in features:
            props = feature.get('properties', {})
            nama_provinsi = props.get('PROVINSI', '').strip()

            if not nama_provinsi:
                self.stdout.write(self.style.WARNING(f'  [!] Fitur tanpa nama provinsi, dilewati.'))
                skipped += 1
                continue

            # Cari kode wilayah berdasarkan nama provinsi
            kode = PROVINCE_NAME_TO_CODE.get(nama_provinsi)
            if not kode:
                self.stdout.write(self.style.WARNING(f'  [!] Provinsi "{nama_provinsi}" tidak ada di mapping, dilewati.'))
                skipped += 1
                continue

            # Konversi geometry ke GEOSGeometry
            geom_json = json.dumps(feature['geometry'])
            try:
                geom = GEOSGeometry(geom_json, srid=4326)
                # Auto-konversi Polygon → MultiPolygon jika perlu
                if geom.geom_type == 'Polygon':
                    geom = MultiPolygon(geom, srid=4326)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  [X] Gagal parse geometry untuk {nama_provinsi}: {e}'))
                skipped += 1
                continue

            # Cari Location berdasarkan kode_wilayah
            try:
                location = Location.objects.get(kode_wilayah=kode)
                location.geom = geom
                location.save()
                self.stdout.write(self.style.SUCCESS(f'  [OK] Updated: {kode} - {nama_provinsi}'))
                updated += 1
            except Location.DoesNotExist:
                if options['create_missing']:
                    location = Location(
                        nama_provinsi=nama_provinsi,
                        kode_wilayah=kode,
                        geom=geom,
                    )
                    location.save()
                    self.stdout.write(self.style.SUCCESS(f'  + Created: {kode} - {nama_provinsi}'))
                    created += 1
                else:
                    self.stdout.write(self.style.WARNING(f'  [!] Tidak ada Location dengan kode {kode} ({nama_provinsi}), dilewati. Gunakan --create-missing untuk membuat otomatis.'))
                    skipped += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'===== SELESAI ====='))
        self.stdout.write(f'  Updated : {updated}')
        self.stdout.write(f'  Created : {created}')
        self.stdout.write(f'  Skipped : {skipped}')
