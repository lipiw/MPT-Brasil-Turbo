import re
from typing import List, Dict, Any

class SafeMediaFilter:
    """
    Filtra termos e tags de mídias de Pexels/Pixabay para evitar contaminação
    de narrativas (ex: protestos opostos ou imagens de escárnio no nicho político).
    """
    BLACKLIST_TAGS = {
        "direita": [
            "lula", "pt", "comunismo", "vermelho", "manifestacao contra bolsonaro",
            "esquerda", "anti bolsonaro", "corrupcao bolsonaro", "ditadura"
        ],
        "esquerda": [
            "bolsonaro", "pl", "direitista", "golpe", "manifestacao contra lula",
            "direita", "anti lula", "corrupcao lula", "militarismo"
        ],
        "tarot": [
            "terror", "horror", "violencia", "medo"
        ],
        "catolico": [
            "satanismo", "terror", "pecado", "ocultismo"
        ]
    }

    @classmethod
    def is_safe_item(cls, item_tags: str, nicho: str) -> bool:
        tags_lower = item_tags.lower() if item_tags else ""
        blacklist = cls.BLACKLIST_TAGS.get(nicho, [])
        for term in blacklist:
            if re.search(r'\b' + re.escape(term) + r'\b', tags_lower):
                return False
        return True

    @classmethod
    def filter_media_list(cls, media_items: List[Dict[str, Any]], nicho: str) -> List[Dict[str, Any]]:
        safe_items = []
        for item in media_items:
            tags = item.get("tags", "") or item.get("description", "")
            if cls.is_safe_item(tags, nicho):
                safe_items.append(item)
        return safe_items
