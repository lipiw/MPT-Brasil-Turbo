import os
import random
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class GeminiKeyPool:
    """
    Gerencia um pool de até 15 API Keys gratuitas do Google Gemini com rotação
    automática (round-robin) e tolerância a limite de cota (HTTP 429).
    """
    def __init__(self, keys: Optional[List[str]] = None):
        if keys is None:
            raw_keys = os.environ.get("GEMINI_API_KEYS", "")
            if raw_keys.strip():
                # Aceita separado por vírgula, ponto e vírgula ou quebra de linha
                for sep in [",", ";", "\n"]:
                    if sep in raw_keys:
                        keys = [k.strip() for k in raw_keys.split(sep) if k.strip()]
                        break
                if not keys and raw_keys.strip():
                    keys = [raw_keys.strip()]
            else:
                keys = []

        self.keys: List[str] = [k for k in keys if k and len(k) > 10]
        self.exhausted_keys: set = set()
        self.current_idx: int = 0
        logger.info(f"GeminiKeyPool inicializado com {len(self.keys)} chave(s).")

    @property
    def has_keys(self) -> bool:
        return len(self.keys) > 0

    def get_active_key(self) -> Optional[str]:
        """Retorna a próxima chave válida não esgotada."""
        available = [k for k in self.keys if k not in self.exhausted_keys]
        if not available:
            if self.keys:
                logger.warning("Todas as chaves Gemini do pool foram marcadas como esgotadas. Resetando pool...")
                self.exhausted_keys.clear()
                available = self.keys
            else:
                return None

        self.current_idx = (self.current_idx + 1) % len(available)
        selected_key = available[self.current_idx]
        return selected_key

    def mark_key_exhausted(self, key: str):
        """Marca uma chave como esgotada por atingir limite 429."""
        if key in self.keys:
            self.exhausted_keys.add(key)
            logger.warning(f"Chave Gemini ...{key[-6:]} marcada como esgotada. Chaves restantes: {len(self.keys) - len(self.exhausted_keys)}")

    def generate_content(self, prompt: str, model_name: str = "gemini-1.5-flash") -> Optional[str]:
        """
        Executa a geração de texto pelo Google Generative AI tentando as chaves
        do pool em sequência até obter sucesso.
        """
        if not self.has_keys:
            return None

        import google.generativeai as genai

        tentativas = len(self.keys)
        for _ in range(tentativas):
            key = self.get_active_key()
            if not key:
                break
            try:
                genai.configure(api_key=key)
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                if response and response.text:
                    return response.text
            except Exception as e:
                err_msg = str(e).lower()
                if "429" in err_msg or "quota" in err_msg or "resource_exhausted" in err_msg:
                    self.mark_key_exhausted(key)
                    continue
                else:
                    logger.error(f"Erro na chamada Gemini com chave ...{key[-6:]}: {e}")
                    raise e
        return None
