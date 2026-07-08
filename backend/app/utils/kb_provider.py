from typing import Optional
from config import KB_PROVIDER

_local_provider = None


def get_knowledge_provider(
    provider_type: Optional[str] = None,
    kb_id: Optional[str] = None,
    kb_api_key: Optional[str] = None
):
    provider = provider_type or KB_PROVIDER
    
    if provider == "local":
        global _local_provider
        if _local_provider is None:
            from app.services.local_knowledge import LocalKnowledgeProvider
            _local_provider = LocalKnowledgeProvider()
        return _local_provider
    else:
        from app.services.knowledge import VolcengineKnowledgeProvider
        return VolcengineKnowledgeProvider(kb_id, kb_api_key)


def get_kb_provider_type(provider_type: Optional[str] = None) -> str:
    return provider_type or KB_PROVIDER


def is_local_provider(provider_type: Optional[str] = None) -> bool:
    return get_kb_provider_type(provider_type) == "local"
