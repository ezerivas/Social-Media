# resuelve tenant desde request

def resolve_tenant(request):
    tenant = request.headers.get("X-Tenant-ID")

    if tenant:
        return int(tenant)

    return 1  # fallback