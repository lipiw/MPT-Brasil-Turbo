import json
import os
import random
from typing import Dict, Any, List

class NichoManager:
    """
    Gerencia carregamento de DNAs de nicho, presets e geração de legendas virais com hashtags.
    """
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "nichos_br")
        self.base_dir = base_dir
        self.hashtags_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "hashtags_nichos.json"
        )
        self.hashtags_data = self._load_hashtags()

    def _load_hashtags(self) -> Dict[str, List[str]]:
        if os.path.exists(self.hashtags_file):
            try:
                with open(self.hashtags_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def get_available_nichos(self) -> List[str]:
        return ["direita", "esquerda", "tarot", "catolico"]

    def load_dna(self, nicho: str) -> Dict[str, Any]:
        filepath = os.path.join(self.base_dir, f"dna_{nicho}.json")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"DNA do nicho '{nicho}' não encontrado em {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_preset(self, nicho: str) -> Dict[str, Any]:
        filepath = os.path.join(self.base_dir, f"preset_{nicho}.json")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Preset do nicho '{nicho}' não encontrado em {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_random_hashtags(self, nicho: str, count: int = 5) -> List[str]:
        tags = self.hashtags_data.get(nicho, [])
        if not tags:
            # Fallbacks seguros
            fallbacks = {
                "direita": ["#brasil", "#patriotas", "#liberdade", "#politica", "#noticias"],
                "esquerda": ["#brasil", "#democracia", "#justicasocial", "#politica", "#noticias"],
                "tarot": ["#tarot", "#espiritualidade", "#leidaatracao", "#universo", "#signos"],
                "catolico": ["#fe", "#oracao", "#deus", "#jesus", "#evangelho"]
            }
            tags = fallbacks.get(nicho, ["#tiktok", "#viral", "#foryou", "#brasil", "#video"])
        sample_count = min(count, len(tags))
        return random.sample(tags, sample_count)

    def build_post_copy(self, nicho: str, video_title: str, script_text: str) -> str:
        """
        Gera o texto completo pronto para colar na legenda do TikTok.
        """
        dna = self.load_dna(nicho)
        ctas = dna.get("ctas_validados", [])
        selected_cta = random.choice(ctas) if ctas else "Curta e compartilhe com quem precisa ouvir isso hoje!"
        
        # Sorteia exatamente 5 hashtags
        hashtags = self.get_random_hashtags(nicho, count=5)
        hashtags_str = " ".join(hashtags)

        # Monta a estrutura da postagem
        post_lines = [
            f"⚡ {video_title.upper()}",
            "",
            f"👉 {selected_cta}",
            "",
            "Comente abaixo o que você acha! 👇",
            "",
            hashtags_str
        ]
        return "\n".join(post_lines)
