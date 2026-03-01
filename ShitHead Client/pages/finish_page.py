def finish(event, pos, reason):
    from pages._client_ref import get_client_module

    pc = get_client_module()

    return pc.finish(event, pos, reason)
