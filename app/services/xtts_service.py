import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class XTTSService:
    """
    Motor de síntese e clonagem de voz baseado em XTTS v2 para execução em GPU (Google Colab / Kaggle).
    Utiliza áudios semente (.wav) da ElevenLabs para obter máxima naturalidade em Português Brasileiro.
    """
    _model_instance = None

    def __init__(self, voice_samples_dir: Optional[str] = None):
        if voice_samples_dir is None:
            voice_samples_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "voice_samples"
            )
        self.voice_samples_dir = voice_samples_dir
        os.makedirs(self.voice_samples_dir, exist_ok=True)

    @classmethod
    def get_model(cls):
        if cls._model_instance is None:
            try:
                import torch
                from TTS.api import TTS
                device = "cuda" if torch.cuda.is_available() else "cpu"
                logger.info(f"Carregando modelo XTTS v2 no dispositivo: {device}")
                cls._model_instance = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
            except Exception as e:
                logger.error(f"Falha ao inicializar XTTS v2: {e}")
                return None
        return cls._model_instance

    def get_reference_audio(self, nicho: str) -> Optional[str]:
        """Busca o áudio de referência .wav correspondente ao nicho."""
        candidates = [
            os.path.join(self.voice_samples_dir, f"{nicho}_ref.wav"),
            os.path.join(self.voice_samples_dir, f"{nicho}.wav"),
            os.path.join(self.voice_samples_dir, "default_ref.wav")
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        return None

    def synthesize(self, text: str, output_path: str, nicho: str = "tarot") -> bool:
        """
        Sintetiza a fala utilizando XTTS v2 e a amostra do nicho.
        Retorna True se gerado com sucesso, ou False caso necessite de fallback (EdgeTTS).
        """
        ref_audio = self.get_reference_audio(nicho)
        if not ref_audio:
            logger.warning(f"Nenhum áudio de referência encontrado para '{nicho}'. Será utilizado fallback.")
            return False

        model = self.get_model()
        if model is None:
            logger.warning("Modelo XTTS indisponível. Usando fallback.")
            return False

        try:
            model.tts_to_file(
                text=text,
                speaker_wav=ref_audio,
                language="pt",
                file_path=output_path
            )
            return os.path.exists(output_path) and os.path.getsize(output_path) > 0
        except Exception as e:
            logger.error(f"Erro na síntese com XTTS v2: {e}")
            return False
