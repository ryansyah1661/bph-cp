from django.utils import translation
from django.conf import settings

class LanguageSwitchMiddleware:
    """
    Middleware untuk menangkap parameter ?lang=en atau ?lang=id dari URL,
    lalu mengaktifkan bahasa tersebut dan menyimpannya ke dalam Session dan Cookie pengguna.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = request.GET.get('lang')
        available_languages = [code for code, name in getattr(settings, 'LANGUAGES', [('id', 'Bahasa Indonesia'), ('en', 'English')])]

        # Jika pengguna memilih bahasa melalui URL (?lang=en atau ?lang=id)
        if lang and lang in available_languages:
            if hasattr(request, 'session'):
                request.session['django_language'] = lang
            translation.activate(lang)
        # Jika tidak ada parameter ?lang, coba ambil dari session
        elif hasattr(request, 'session') and 'django_language' in request.session:
            session_lang = request.session['django_language']
            if session_lang in available_languages:
                translation.activate(session_lang)
            else:
                translation.activate(settings.LANGUAGE_CODE)
        # Jika tidak ada di session, gunakan bahasa default dari settings
        else:
            translation.activate(settings.LANGUAGE_CODE)
            
        request.LANGUAGE_CODE = translation.get_language()
        
        response = self.get_response(request)
        
        # Simpan cookie pilihan bahasa agar konsisten antar kunjungan browser
        if lang and lang in available_languages:
            response.set_cookie(
                getattr(settings, 'LANGUAGE_COOKIE_NAME', 'django_language'),
                lang,
                max_age=365 * 24 * 60 * 60,  # 1 tahun
                samesite='Lax'
            )
        return response
