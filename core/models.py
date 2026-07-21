from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# === 1. TABEL MASTER KATEGORI ===
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nama Kategori")
    slug = models.SlugField(max_length=200, unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Kategori"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
# === 1b. TABEL FOLDER / ALBUM DOKUMENTASI ===
class Folder(models.Model):
    nama = models.CharField(max_length=255, verbose_name="Nama Folder / Album")
    tahun = models.IntegerField(verbose_name="Tahun Dokumentasi")
    kategori = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='folders', verbose_name="Kategori Filter")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Folder / Album Galeri"
        ordering = ['-tahun', '-id']

    def __str__(self):
        return f"{self.nama} ({self.tahun})"
    
# === 2. TABEL LAYANAN (Services) ===
class Service(models.Model):
    PORTFOLIO_CHOICES = [
        ('NRM', 'Natural Resources Management (NRM)'),
        ('NRU', 'Natural Resources Understanding (NRU)'),
    ]

    title = models.CharField(max_length=200, verbose_name="Nama Layanan")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    portfolio = models.CharField(max_length=3, choices=PORTFOLIO_CHOICES, default='NRM')
    icon = models.CharField(max_length=50, blank=True, help_text="Nama icon Material Symbols, misal: 'forest', 'travel_explore'", verbose_name="Nama Icon Kartu")
    thumbnail = models.ImageField(upload_to='services/thumbs/', blank=True, verbose_name="Foto Kartu Layanan")
    bg_image = models.ImageField(upload_to='services/banners/', blank=True, verbose_name="Foto Banner Atas")
    
    # Field intro sudah dihapus sesuai permintaan
    approach = models.TextField(verbose_name="Detail Deskripsi Cakupan Kerja")
    
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
    PROVINCE_CODE_CHOICES = [
        ('11', '11 - Aceh'), ('12', '12 - Sumatera Utara'), ('13', '13 - Sumatera Barat'),
        ('14', '14 - Riau'), ('15', '15 - Jambi'), ('16', '16 - Sumatera Selatan'),
        ('17', '17 - Bengkulu'), ('18', '18 - Lampung'), ('19', '19 - Kepulauan Bangka Belitung'),
        ('21', '21 - Kepulauan Riau'), ('31', '31 - DKI Jakarta'), ('32', '32 - Jawa Barat'),
        ('33', '33 - Jawa Tengah'), ('34', '34 - Daerah Istimewa Yogyakarta'), ('35', '35 - Jawa Timur'),
        ('36', '36 - Banten'), ('51', '51 - Bali'), ('52', '52 - Nusa Tenggara Barat'),
        ('53', '53 - Nusa Tenggara Timur'), ('61', '61 - Kalimantan Barat'), ('62', '62 - Kalimantan Tengah'),
        ('63', '63 - Kalimantan Selatan'), ('64', '64 - Kalimantan Timur'), ('65', '65 - Kalimantan Utara'),
        ('71', '71 - Sulawesi Utara'), ('72', '72 - Sulawesi Tengah'), ('73', '73 - Sulawesi Selatan'),
        ('74', '74 - Sulawesi Tenggara'), ('75', '75 - Gorontalo'), ('76', '76 - Sulawesi Barat'),
        ('81', '81 - Maluku'), ('82', '82 - Maluku Utara'), ('91', '91 - Papua'),
        ('92', '92 - Papua Barat'), ('93', '93 - Papua Selatan'), ('94', '94 - Papua Tengah'),
        ('95', '95 - Papua Pegunungan'), ('96', '96 - Papua Barat Daya'),
    ]

    nama_provinsi = models.CharField(max_length=150, verbose_name="Nama Provinsi")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    kode_wilayah = models.CharField(
        max_length=2, choices=PROVINCE_CODE_CHOICES, unique=True, null=True, blank=True, verbose_name="Kode Provinsi BPS"
    )

    class Meta:
        verbose_name_plural = "Lokasi Wilayah"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nama_provinsi)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nama_provinsi} ({self.kode_wilayah})"
    
# === 5. TABEL KLIEN (Clients) ===
class Client(models.Model):
    SECTOR_CHOICES = [
        ('swasta', 'Sektor Swasta'),
        ('publik', 'Sektor Publik'),
    ]

    nama = models.CharField(max_length=200, verbose_name="Nama Instansi/Perusahaan")
    sektor = models.CharField(
        max_length=10, 
        choices=SECTOR_CHOICES, 
        default='swasta', 
        verbose_name="Kategori Sektor"
    )
    logo = models.ImageField(upload_to='clients/logos/', blank=True, help_text="Logo grup untuk bagian partner ticker")

    class Meta:
        verbose_name_plural = "Klien / Mitra Kolaborasi"

    def __str__(self):
        return f"{self.nama} ({self.get_sektor_display()})"
    
# === 6. TABEL PROYEK (Experiences) ===
class Project(models.Model):
    name = models.CharField(max_length=250, verbose_name="Nama Proyek")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    tahun = models.IntegerField(verbose_name="Tahun Pelaksanaan")
    image = models.ImageField(upload_to='projects/thumbs/', verbose_name="Foto Kartu Proyek")
    description = models.TextField(verbose_name="Deskripsi Project")

    intro = models.TextField(blank=True, verbose_name="Paragraf Pembuka Detail")
    challenge = models.TextField(blank=True, verbose_name="Tantangan & Kondisi Awal")
    methodology = models.TextField(blank=True, verbose_name="Pendekatan & Metodologi Kerja")
    result = models.TextField(blank=True, verbose_name="Hasil & Dampak Ekologis Terukur")
    pdf_cover = models.ImageField(upload_to='projects/pdf_covers/', blank=True, null=True, verbose_name="Sampul Modul PDF")
    pdf_file = models.FileField(upload_to='projects/pdf_files/', blank=True, null=True, verbose_name="Berkas Modul Laporan Teknis (PDF)")

    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, related_name='projects')
    service_portfolio = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, related_name='projects', verbose_name="Sesuai Portofolio Layanan")
    
    locations = models.ManyToManyField(Location, related_name='projects', verbose_name="Lokasi Wilayah Provinsi")

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
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    tanggal = models.DateField(verbose_name="Tanggal Rilis")
    author = models.CharField(max_length=100, default="Admin BPH")
    
    lokasi = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, related_name='stories', verbose_name="Lokasi Wilayah")
    
    short = models.TextField(help_text="Ringkasan pendek yang muncul di kartu depan")
    deskripsi = models.TextField(verbose_name="Isi Cerita Lengkap")
    gambar = models.ImageField(upload_to='stories/', verbose_name="Foto Cerita")
    
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
    slug = models.SlugField(max_length=200, unique=True, blank=True)
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

    is_read = models.BooleanField(default=False, verbose_name="Sudah Dibaca")
    
    class Meta:
        verbose_name_plural = "Pesan Masuk Kontak"

    def __str__(self):
        return f"Pesan dari {self.nama_lengkap} - {self.subjek}"
    
# === 11. TABEL GALERI DOKUMENTASI ===
class Gallery(models.Model):
    caption = models.CharField(max_length=250, verbose_name="Keterangan Foto / Caption")
    gambar = models.ImageField(upload_to='gallery/', verbose_name="File Foto")
    
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='images', null=True, blank=True, verbose_name="Dimasukkan ke Folder")
    kategori = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='galleries', verbose_name="Kategori Filter")
    tanggal_upload = models.DateField(verbose_name="Tanggal Dokumentasi")

    class Meta:
        verbose_name_plural = "Galeri Dokumentasi"

    def __str__(self):
        return self.caption

# === 12. TABEL KUSTOM EKSTENSI PROFIL USER PENGGUNA ===
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nama_lengkap = models.CharField(max_length=150, blank=True, null=True, verbose_name="Nama Lengkap")
    foto_profil = models.ImageField(upload_to='profile_pics/', blank=True, null=True, verbose_name="Foto Profil")

    def __str__(self):
        return f"Profile {self.user.username}"

# === 13. TABEL TIM AHLI KAMI (Team Members) ===
class TeamMember(models.Model):
    CATEGORY_CHOICES = [
        ('advisors', 'Advisors'),
        ('executives', 'Executives'),
        ('staff', 'Staff'),
        ('associates', 'Associates'),
    ]

    nama = models.CharField(max_length=255, verbose_name="Nama Lengkap & Gelar")
    jabatan = models.CharField(max_length=255, verbose_name="Jabatan / Posisi")
    bio = models.TextField(blank=True, null=True, verbose_name="Bio / Cerita Singkat", help_text="Opsional. Boleh dikosongkan.")
    kategori = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='advisors', verbose_name="Kategori Tim")
    foto = models.ImageField(upload_to='team/', verbose_name="Foto Profil Anggota")
    urutan = models.IntegerField(default=0, help_text="Angka lebih kecil tampil lebih dulu (0, 1, 2...)", verbose_name="Urutan Tampil")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Tim Ahli Kami"
        ordering = ['urutan', 'id']

    def __str__(self):
        return f"{self.nama} - {self.jabatan} ({self.get_kategori_display()})"

# --- LOGIKA AUTOMATIC SIGNALS DJANGO ---
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()