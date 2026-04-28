from repositories.channels import get_channel_config


def resolve_channel_config(tenant_id: int, channel: str):
    config = get_channel_config(tenant_id, channel)

    if not config:
        raise Exception(f"Missing config for {channel} (tenant {tenant_id})")

    return config