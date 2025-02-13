def footer_copyright(request):
    user = request.user  # Mengambil user dari request

    # Membuat string username dengan format yang diinginkan
    if user.first_name or user.last_name:
        username = f"{user.first_name.capitalize()} {user.last_name.capitalize()}".strip()
    else:
        username = user.username.capitalize()

    return {
        'footer_copyright': '© 2025 - IT Frina Lestari Nusantara, Inc. All rights reserved.',
        'footer': '<li class="list-inline-item"><a class="text-muted" href="https://github.com/itsmeabimanyu/fln-online-invitation" target="_blank"><i class="align-middle me-2" data-feather="github"></i></a></li>',
        'username': username
    }