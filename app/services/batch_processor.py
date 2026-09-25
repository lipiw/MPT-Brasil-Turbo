import os
import glob
import json
import logging
from typing import List, Dict, Any, Optional
from app.services.mpt_brasil_runner import run_nicho_generation
from app.services.nicho_manager import NichoManager

logger = logging.getLogger("BatchProcessor")

class BatchTemplateProcessor:
    """
    Processa em lote templates de vídeos prontos a partir de uma pasta no Google Drive.
    Suporta:
    1. Arquivos .txt contendo o roteiro/tema (1 arquivo = 1 vídeo).
       Se a primeira linha começar com 'TEMA:' ou '#', ela é usada como título.
    2. Arquivos .json contendo campos como {"tema": "...", "nicho": "...", "roteiro": "..."}
    3. Arquivo batch.csv ou prompts.txt com 1 linha por vídeo.
    """
    def __init__(self, drive_output_dir: str = "/content/drive/MyDrive/TikTok_Producao", gemini_keys_str: str = ""):
        self.drive_output_dir = drive_output_dir
        self.gemini_keys_str = gemini_keys_str
        self.nicho_manager = NichoManager()

    def process_folder(self, folder_path: str, default_nicho: str = "tarot") -> List[Dict[str, Any]]:
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Pasta de templates não encontrada: {folder_path}")

        logger.info(f"📂 Iniciando processamento em BATCH da pasta: {folder_path}")
        results = []

        # 1. Busca arquivos .json
        json_files = glob.glob(os.path.join(folder_path, "*.json"))
        for j_file in sorted(json_files):
            try:
                with open(j_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Se for lista de itens
                items = data if isinstance(data, list) else [data]
                for item in items:
                    nicho = item.get("nicho", default_nicho)
                    tema = item.get("tema") or item.get("video_subject") or os.path.basename(j_file)
                    roteiro = item.get("roteiro") or item.get("video_script") or ""
                    
                    logger.info(f"▶️ Executando template JSON: [{nicho}] {tema}")
                    res = run_nicho_generation(
                        nicho=nicho,
                        tema_personalizado=tema,
                        drive_output_dir=self.drive_output_dir,
                        gemini_keys_str=self.gemini_keys_str
                    )
                    results.append(res)
            except Exception as e:
                logger.error(f"Erro ao processar template JSON {j_file}: {e}")

        # 2. Busca arquivos .txt individuais (1 arquivo = 1 vídeo)
        txt_files = [f for f in glob.glob(os.path.join(folder_path, "*.txt")) if not f.endswith("_postagem.txt")]
        for t_file in sorted(txt_files):
            try:
                with open(t_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                if not content:
                    continue

                lines = [l.strip() for l in content.split("\n") if l.strip()]
                first_line = lines[0] if lines else "Vídeo em Lote"
                
                # Extrai tema e nicho se anotados no início do arquivo
                nicho = default_nicho
                tema = first_line.replace("TEMA:", "").replace("#", "").strip()
                
                for line in lines[:3]:
                    if line.lower().startswith("nicho:"):
                        nicho_val = line.split(":", 1)[1].strip().lower()
                        if nicho_val in self.nicho_manager.get_available_nichos():
                            nicho = nicho_val

                logger.info(f"▶️ Executando template TXT '{os.path.basename(t_file)}': [{nicho}] {tema}")
                res = run_nicho_generation(
                    nicho=nicho,
                    tema_personalizado=tema,
                    drive_output_dir=self.drive_output_dir,
                    gemini_keys_str=self.gemini_keys_str
                )
                results.append(res)
            except Exception as e:
                logger.error(f"Erro ao processar template TXT {t_file}: {e}")

        logger.info(f"✅ BATCH CONCLUÍDO! Total de vídeos gerados: {len(results)}")
        return results
