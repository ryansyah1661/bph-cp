from django.shortcuts import render, redirect

def index(request):
    return render(request, 'core/homepage.html')

def about(request):
    return render(request, 'core/about.html')

def contact(request):
    return render(request, 'core/contact.html')

def experience(request):
    return render(request, 'core/experience.html')

def services(request):
    return render(request, 'core/services.html')

def gallery(request):
    return render(request, 'core/gallery.html')

def articles(request):
    return render(request, 'core/articles.html')

def detail_experience(request, slug):
    # Jika sementara masih pakai data dummy / statis biar ga error:
    return render(request, 'core/detail-experience.html')

def detail_story(request, slug):
    # Jika sementara masih pakai data dummy / statis biar ga error:
    return render(request, 'core/detail-story.html')

# FIXED: Menambahkan fungsi detail artikel independen agar melempar ke file template detail_artikel.html
def detail_article(request, slug):
    # Jika pakai database asli kedepannya tinggal un-comment baris bawah:
    # article = get_object_or_404(Article, slug=slug)
    # return render(request, 'core/detail_artikel.html', {'artikel': article})
    
    return render(request, 'core/detail-articles.html')

# Fungsi Detail Layanan Dinamis
def service_detail(request, slug):
    # Gudang data lokal untuk mencocokkan slug URL dengan isi konten halaman
    DATA_LAYANAN = {
        # === KATEGORI NRM ===
        'rehabilitasi-hutan': {
            'portfolio': 'NRM',
            'title': 'Rehabilitasi Hutan & Lahan',
            'bg_image': 'images/services1.jpg',
            'intro': 'Layanan Rehabilitasi Hutan dan Lahan (RHL) kami dirancang untuk memulihkan, mempertahankan, dan meningkatkan fungsi hutan...',
            'approach': 'Kami menerapkan pendekatan holistik yang mengintegrasikan aspek ekologi, sosial, dan ekonomi. Proses rehabilitasi bukan sekadar penanaman pohon, melainkan pemulihan ekosistem secara utuh.',
            'steps': [
                {'icon': 'analytics', 'title': 'Perencanaan dan Penilaian Tapak', 'desc': 'Survei detail untuk menentukan strategi pemulihan yang tepat sasaran.'},
                {'icon': 'nature_people', 'title': 'Pemberdayaan Masyarakat', 'desc': 'Melibatkan komunitas lokal dalam setiap tahap untuk keberlanjutan jangka panjang.'},
                {'icon': 'monitoring', 'title': 'Pemantauan dan Evaluasi', 'desc': 'Monitoring berkala menggunakan teknologi GIS untuk mengukur tingkat keberhasilan.'}
            ]
        },
        'inventarisasi-lahan': {
            'portfolio': 'NRM',
            'title': 'Inventarisasi Sumberdaya Lahan',
            'bg_image': 'images/services2.jpg',
            'intro': 'Layanan Inventarisasi Sumberdaya Lahan kami menyediakan pemetaan komprehensif serta pengumpulan aset data spasial...',
            'approach': 'Melalui survei terestrial modern dan pemodelan kartografi tingkat tinggi untuk memastikan akurasi zonasi wilayah kerja Anda.',
            'steps': [
                {'icon': 'map', 'title': 'Pemetaan Spasial', 'desc': 'Zonasi digital untuk tata ruang wilayah hijau.'}
            ]
        },
        'penguatan-kelembagaan': {
            'portfolio': 'NRM',
            'title': 'Penguatan Kelembagaan',
            'bg_image': 'images/services3.jpg',
            'intro': 'Membangun kerangka kerja kelembagaan yang kokoh untuk mendukung tata kelola lingkungan yang efektif.',
            'approach': 'Menyelaraskan regulasi korporasi dengan kepatuhan kebijakan hukum lingkungan nasional secara berkelanjutan.',
            'steps': [
                {'icon': 'gavel', 'title': 'Compliance Audit', 'desc': 'Pemeriksaan kepatuhan hukum tata kelola.'}
            ]
        },
        'perencanaan-sda': {
            'portfolio': 'NRM',
            'title': 'Perencanaan SDA & Lingkungan',
            'bg_image': 'images/services4.jpg',
            'intro': 'Cetak biru strategis pemanfaatan sumber daya alam yang menyeimbangkan target ekonomi dengan batas ekologis.',
            'approach': 'Analisis daya dukung lingkungan jangka panjang demi kelangsungan operasional bisnis yang ramah alam.',
            'steps': [
                {'icon': 'insights', 'title': 'Analisis Daya Dukung', 'desc': 'Penilaian batasan aman eksploitasi alam.'}
            ]
        },
        'pengelolaan-tanaman': {
            'portfolio': 'NRM',
            'title': 'Pengelolaan Kesehatan Tanaman',
            'bg_image': 'images/services5.jpg',
            'intro': 'Manajemen terpadu pengendalian hama dan penyakit vegetasi hutan komersial maupun kawasan konservasi.',
            'approach': 'Penerapan bioteknologi ramah lingkungan tanpa merusak ekosistem mikro tanah di sekitarnya.',
            'steps': [
                {'icon': 'bug_report', 'title': 'Pest Mitigation', 'desc': 'Deteksi dini dan isolasi penyebaran patogen flora.'}
            ]
        },
        'perizinan-lingkungan': {
            'portfolio': 'NRM',
            'title': 'Perizinan Lingkungan',
            'bg_image': 'images/services6.jpg',
            'intro': 'Amanat regulasi perizinan AMDAL, UKL-UPL, dan clearances regulatif di tingkat daerah maupun pusat.',
            'approach': 'Asistensi teknis dokumen lingkungan hidup agar proses kelayakan usaha berjalan lancar dan legal.',
            'steps': [
                {'icon': 'verified', 'title': 'Legal Clearence', 'desc': 'Penyusunan dokumen AMDAL resmi.'}
            ]
        },

        # === KATEGORI NRU ===
        'penilaian-keanekaragaman': {
            'portfolio': 'NRU',
            'title': 'Penilaian Keanekaragaman Hayati',
            'bg_image': 'images/services7.jpg',
            'intro': 'Survei dasar (baseline) tingkat tinggi terhadap indeks populasi flora dan fauna lokal dilindungi.',
            'approach': 'Metode sampling ilmiah berstandar internasional untuk menghitung kekayaan taksonomi ekosistem.',
            'steps': [
                {'icon': 'pets', 'title': 'Taxonomy Mapping', 'desc': 'Sensus spesies endemik rawan punah.'}
            ]
        },
        'penilaian-sosial': {
            'portfolio': 'NRU',
            'title': 'Penilaian Sosial',
            'bg_image': 'images/services8.jpg',
            'intro': 'Evaluasi dampak sosial ekonomi dari keberadaan proyek lingkungan terhadap dinamika masyarakat lingkar hutan.',
            'approach': 'FGD interaktif dan mediasi konflik komunitas lokal demi terciptanya jaminan sosial sosiologis.',
            'steps': [
                {'icon': 'diversity_3', 'title': 'Community Engagement', 'desc': 'Studi kelayakan sosiokultural daerah.'}
            ]
        },
        'tanah-hidrologi': {
            'portfolio': 'NRU',
            'title': 'Kajian Tanah & Hidrologi',
            'bg_image': 'images/services9.jpg',
            'intro': 'Analisis mekanika tanah, infiltrasi, dan siklus air daerah aliran sungai untuk mencegah bahaya erosi.',
            'approach': 'Pemetaan hidrologis terkomputerisasi untuk mengelola daerah tangkapan air hulu secara presisi.',
            'steps': [
                {'icon': 'water', 'title': 'Watershed Management', 'desc': 'Analisis debit dan kestabilan struktur tanah.'}
            ]
        },
        'kajian-iklim': {
            'portfolio': 'NRU',
            'title': 'Kajian Iklim',
            'bg_image': 'images/services10.jpg',
            'intro': 'Pemodelan perubahan iklim mikro dan makro guna merumuskan strategi adaptasi bisnis berkelanjutan.',
            'approach': 'Proyeksi data cuaca historis untuk membaca anomali pergeseran musim industri agrikultur.',
            'steps': [
                {'icon': 'thermostat', 'title': 'Climate Modeling', 'desc': 'Kalkulasi risiko anomali cuaca ekstrem.'}
            ]
        },
        'kesehatan-tanaman-nru': {
            'portfolio': 'NRU',
            'title': 'Penilaian Kesehatan Tanaman (NRU)',
            'bg_image': 'images/services11.jpg',
            'intro': 'Evaluasi diagnostik indikator kesehatan ekosistem hutan primer secara berkala.',
            'approach': 'Menggunakan pemindaian sensor multispektoral drone udara untuk melihat klorofil vegetasi skala luas.',
            'steps': [
                {'icon': 'center_focus_weak', 'title': 'Drone Spectral Scan', 'desc': 'Analisis vegetasi berbasis data inframerah.'}
            ]
        },
        'energi-terbarukan': {
            'portfolio': 'NRU',
            'title': 'Energi Terbarukan',
            'bg_image': 'images/services12.jpg',
            'intro': 'Studi kelayakan teknis dan analisis dampak lingkungan untuk infrastruktur energi bersih baru terbarukan.',
            'approach': 'Penilaian komparatif potensi pasokan biomassa, hidro mikro, atau solar panel pedesaan.',
            'steps': [
                {'icon': 'bolt', 'title': 'Feasibility Study', 'desc': 'Kalkulasi konversi efisiensi energi hijau.'}
            ]
        },
    }

    service_data = DATA_LAYANAN.get(slug)
    if not service_data:
        return redirect('services')

    context = { 'service': service_data }
    return render(request, 'core/detail-services.html', context)