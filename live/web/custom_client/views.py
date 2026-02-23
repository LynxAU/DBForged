from django.shortcuts import render

def custom_client(request):
    """
    Returns the custom DBForged HTML/JS client instead of the default Evennia webclient.
    """
    return render(request, "custom_client/index.html")
