from .models import ContactMessage

def unread_messages_count(request):
    if request.user.is_authenticated:
        # 🚨 SEKARANG HANYA HITUNG YANG BELUM DIBACA
        count = ContactMessage.objects.filter(is_read=False).count()
        return {'unread_messages_count': count}
    return {'unread_messages_count': 0}