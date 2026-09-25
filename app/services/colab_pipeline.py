import os
import shutil
import glob
import logging
from typing import Optional, Dict, Any
from app.services.nicho_manager import NichoManager
from app.services.gemini_pool import GeminiKeyPool

logger = logging.getLogger(__name__)

class ColabDrivePipeline:
    """
    Controlador para execução limpa no Google Colab:
    - Salva o vídeo .mp4 final na pasta /content/drive/MyDrive/TikTok_Producao/{nicho}/
    - Salva o arquivo .txt com copy de engajamento e 5 hashtags virais dinâmicas
    - Remove arquivos temporários de renderização mantendo apenas a entrega final
    """
    def __init__(self, drive_root: str = "/content/drive/MyDrive/TikTok_Producao"):
        self.drive_root = drive_root
        self.nicho_manager = NichoManager()

    def get_output_dir(self, nicho: str) -> str:
        out_dir = os.path.join(self.drive_root, nicho)
        os.makedirs(out_dir, exist_ok=True)
        return out_dir

    def export_final_production(self, video_path: str, nicho: str, video_title: str, script_text: str) -> Dict[str, str]:
        """
        Copia o vídeo final para o Google Drive e cria o .txt com a postagem pronta.
        """
        target_dir = self.get_output_dir(nicho)
        video_filename = os.path.basename(video_path)
        base_name, _ = os.path.splitext(video_filename)

        # Destino do vídeo
        target_video = os.path.join(target_dir, video_filename)
        shutil.copy2(video_path, target_video)

        # Destino do TXT de postagem
        post_filename = f"{base_name}_postagem.txt"
        target_post = os.path.join(target_dir, post_filename)
        post_copy = self.nicho_manager.build_post_copy(nicho, video_title, script_text)

        with open(target_post, "w", encoding="utf-8") as f:
            f.write(post_copy)

        logger.info(f"Produção salva com sucesso no Drive: {target_dir}")
        return {
            "video_path": target_video,
            "post_path": target_post,
            "copy": post_copy
        }
