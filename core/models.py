from django.db import models
from django.utils.text import slugify

# === 1. TABEL MASTER KATEGORI ===
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nama Kategori")
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Kategori"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
# === 2. TABEL LAYANAN (Services) ===
class Service(models.Model):
    PORTFOLIO_CHOICES = [
        ('NRM', 'Natural Resources Management (NRM)'),
        ('NRU', 'Natural Resources Understanding (NRU)'),
    ]

    title = models.CharField(max_length=200, verbose_name="Nama Layanan")
    slug = models.SlugField(unique=True, blank=True)
    portfolio = models.CharField(max_length=3, choices=PORTFOLIO_CHOICES, default='NRM')
    icon = models.CharField(max_length=50, blank=True, help_text="Nama icon Material Symbols, misal: 'forest', 'travel_explore'", verbose_name="Nama Icon Kartu")
    thumbnail = models.ImageField(upload_to='services/thumbs/', blank=True, verbose_name="Foto Kartu Layanan")
    bg_image = models.ImageField(upload_to='services/banners/', blank=True, verbose_name="Foto Banner Atas")
    intro = models.TextField(verbose_name="Paragraf Ringkasan Atas")
    approach = models.TextField(verbose_name="Paragraf Pendekatan Komprehensif")
    
    # RELASI MANY-TO-MANY: 1 Layanan bisa memilih lebih dari 1 Kategori
    categories = models.ManyToManyField(Category, blank=True, related_name='services')

    class Meta:
        verbose_name_plural = "Layanan (Services)"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
# === 3. TABEL TAHAPAN PELAKSANAAN LAYANAN (Service Steps) ===
class ServiceStep(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='steps', verbose_name="Untuk Layanan")
    icon = models.CharField(max_length=50, help_text="Nama icon Material Symbols, misal: 'forest', 'ecg', 'map'", verbose_name="Nama Icon")
    title = models.CharField(max_length=200, verbose_name="Judul Tahapan")
    desc = models.TextField(verbose_name="Deskripsi Detail Tahapan")

    class Meta:
        verbose_name_plural = "Tahapan Pelaksanaan Layanan"

    def __str__(self):
        return f"{self.service.title} - {self.title}"
    
# === 4. TABEL LOKASI (Locations) ===
class Location(models.Model):
    nama_provinsi = models.CharField(max_length=150, verbose_name="Nama Provinsi")
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Lokasi Wilayah"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nama_provinsi)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nama_provinsi
    
# === 5. TABEL KLIEN (Clients) ===
class Client(models.Model):
    nama = models.CharField(max_length=200, verbose_name="Nama Instansi/Perusahaan")
    alamat = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    logo = models.ImageField(upload_to='clients/logos/', blank=True, help_text="Logo grup untuk bagian partner ticker")

    class Meta:
        verbose_name_plural = "Klien / Mitra Kolaborasi"

    def __str__(self):
        return self.nama
    
# === 6. TABEL PROYEK (Experiences) ===
class Project(models.Model):
    name = models.CharField(max_length=250, verbose_name="Nama Proyek")
    slug = models.SlugField(unique=True, blank=True)
    tahun = models.IntegerField(verbose_name="Tahun Pelaksanaan")
    image = models.ImageField(upload_to='projects/thumbs/', verbose_name="Foto Kartu Proyek")
    description = models.TextField(verbose_name="Deskripsi Project")

    # Field tambahan untuk isi halaman detail proyek
    intro = models.TextField(blank=True, verbose_name="Paragraf Pembuka Detail")
    challenge = models.TextField(blank=True, verbose_name="Tantangan & Kondisi Awal")
    methodology = models.TextField(blank=True, verbose_name="Pendekatan & Metodologi Kerja")
    result = models.TextField(blank=True, verbose_name="Hasil & Dampak Ekologis Terukur")
    pdf_cover = models.ImageField(upload_to='projects/pdf_covers/', blank=True, null=True, verbose_name="Sampul Modul PDF")
    pdf_file = models.FileField(upload_to='projects/pdf_files/', blank=True, null=True, verbose_name="Berkas Modul Laporan Teknis (PDF)")

    # RELASI FOREIGN KEY (One-to-Many)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, related_name='projects')
    service_portfolio = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, related_name='projects', verbose_name="Sesuai Portofolio Layanan")
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, related_name='projects')

    # RELASI MANY-TO-MANY: 1 Proyek bisa dicentang lebih dari 1 Kategori (Konservasi, Riset, dll)
    categories = models.ManyToManyField(Category, related_name='projects', verbose_name="Kategori Proyek")

    class Meta:
        verbose_name_plural = "Proyek (Experience)"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# === 6b. TABEL MATRIKS CAPAIAN KINERJA PROYEK ===
class ProjectMetric(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='metrics', verbose_name="Untuk Proyek")
    parameter = models.CharField(max_length=200, verbose_name="Parameter Monitoring")
    target = models.CharField(max_length=200, verbose_name="Target Awal")
    actual = models.CharField(max_length=200, verbose_name="Realisasi Akhir Lapangan")

    class Meta:
        verbose_name_plural = "Matriks Capaian Kinerja Proyek"

    def __str__(self):
        return f"{self.project.name} - {self.parameter}"

    
# === 7. TABEL CERITA LAPANGAN (Stories) ===
class Story(models.Model):
    judul = models.CharField(max_length=250)
    slug = models.SlugField(unique=True, blank=True)
    tanggal = models.DateField(verbose_name="Tanggal Rilis")
    author = models.CharField(max_length=100, default="Admin BPH")
    short = models.TextField(help_text="Ringkasan pendek yang muncul di kartu depan")
    deskripsi = models.TextField(verbose_name="Isi Cerita Lengkap")
    gambar = models.ImageField(upload_to='stories/', verbose_name="Foto Cerita")
    
    # Hubungkan ke proyek jika ada (Boleh Kosong / Nullable)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='stories')

    class Meta:
        verbose_name_plural = "Cerita Lapangan"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.judul)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.judul
    
# === 8. TABEL ARTIKEL (Articles) ===
class Article(models.Model):
    judul = models.CharField(max_length=250)
    slug = models.SlugField(unique=True, blank=True)
    tanggal = models.DateField(verbose_name="Tanggal Terbit")
    author = models.CharField(max_length=100, default="Admin BPH")
    short = models.TextField(help_text="Ringkasan pendek artikel")
    deskripsi = models.TextField(verbose_name="Konten Artikel Lengkap")
    gambar = models.ImageField(upload_to='articles/', verbose_name="Foto Utama Artikel")

    class Meta:
        verbose_name_plural = "Artikel & Wawasan Teknis"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.judul)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.judul

# === 9. TABEL MODUL DOKUMENTASI STRATEGIS (Modul) ===
class Modul(models.Model):
    judul = models.CharField(max_length=200, verbose_name="Judul Dokumen Publikasi")
    file_dokumen = models.FileField(upload_to='documents/', verbose_name="Berkas File (PDF/Docs)")
    tanggal_rilis = models.DateField(auto_now_add=True, verbose_name="Tanggal Unggah")

    class Meta:
        verbose_name_plural = "Modul Dokumentasi"

    def __str__(self):
        return self.judul

# === 10. TABEL PESAN KONTAK (Contact Messages) ===
class ContactMessage(models.Model):
    nama_lengkap = models.CharField(max_length=150, verbose_name="Nama Lengkap")
    email = models.EmailField(verbose_name="Alamat Email")
    subjek = models.CharField(max_length=200, verbose_name="Subjek / Nama Instansi")
    pesan = models.TextField(verbose_name="Detail Pesan / Pertanyaan")
    tanggal_kirim = models.DateTimeField(auto_now_add=True, verbose_name="Waktu Kirim")

    class Meta:
        verbose_name_plural = "Pesan Masuk Kontak"

    def __str__(self):
        return f"Pesan dari {self.nama_lengkap} - {self.subjek}"
    
# === 11. TABEL GALERI DOKUMENTASI (Gallery) ===
class Gallery(models.Model):
    caption = models.CharField(max_length=250, verbose_name="Keterangan Foto / Caption")
    gambar = models.ImageField(upload_to='gallery/', verbose_name="File Foto")
    
    # Hubungkan ke master Kategori biar filternya (NRM, NRU, dll) jalan dinamis di FE
    kategori = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='galleries', verbose_name="Kategori Filter")
    tanggal_upload = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Galeri Dokumentasi"

    def __str__(self):
        return self.caption