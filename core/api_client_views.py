from django.shortcuts import render
from django.views.decorators.http import require_GET


@require_GET
def api_client(request):
    return render(request, "core/api_client.html", {"page_title": "Assignment titles"})
