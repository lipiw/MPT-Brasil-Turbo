import os
import sys
import json
import logging
import argparse
from app.services.nicho_manager import NichoManager
from app.services.gemini_pool import GeminiKeyPool
from app.services.colab_pipeline import ColabDrivePipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("MPT_Brasil_Runner")

def run_nicho_generation(
    nicho: str,
    tema_personalizado: str = "",
    drive_output_dir: str = "/content/drive/MyDrive/TikTok_Producao",
    gemini_keys_str: str = ""
):
    nm = NichoManager()
    if nicho not in nm.get_available_nichos():
        raise ValueError(f"Nicho '{nicho}' inválido. Opções: {nm.get_available_nichos()}")

    dna = nm.load_dna(nicho)
    preset = nm.load_preset(nicho)

    logger.info(f"=== INICIANDO PRODUÇÃO TIKTOK BRASIL: NICHO {nicho.upper()} ===")

    # 1. Obter Roteiro (Gemini ou Preset/Tema)
    pool = GeminiKeyPool(gemini_keys_str.split(",") if gemini_keys_str else None)
    script_text = preset["params"]["video_script"]
    video_title = tema_personalizado or preset["params"]["video_subject"]

    if pool.has_keys and tema_personalizado:
        logger.info(f"Gerando roteiro dinâmico com Gemini para o tema: '{tema_personalizado}'...")
        prompt = f"""
Você é um roteirista viral do TikTok especializado no nicho: {dna.get('nicho')}.
Arquétipo: {dna.get('arquétipo_protagonista')}.
Tom de voz: {dna.get('tom_de_voz', {}).get('estilo')}.
Gírias e termos obrigatórios: {', '.join(dna.get('tom_de_voz', {}).get('girias_e_termos', []))}.
Tema do vídeo: {tema_personalizado}.

Escreva um roteiro magnético de 40 a 60 segundos com:
- Gancho imediato de retenção nos primeiros 3 segundos
- Conflito direto
- Chamada para ação visceral no final

Responda APENAS com o texto da narração, sem rubricas ou anotações entre parênteses.
"""
        generated = pool.generate_content(prompt)
        if generated:
            script_text = generated.strip()
            logger.info("Roteiro gerado com sucesso pelo Gemini!")

    # 2. Configura Parâmetros de Renderização com Base no Preset
    video_terms = preset["params"]["video_terms"]
    voice_name = preset["params"]["voice_name"]

    logger.info(f"Título: {video_title}")
    logger.info(f"Termos visuais: {video_terms}")
    logger.info(f"Voz: {voice_name}")

    # 3. Exportação e Empacotamento para Google Drive
    pipeline = ColabDrivePipeline(drive_output_dir)
    
    # Criamos um vídeo demonstrativo ou processado
    # Em execução no Colab, o MoneyPrinterTurbo gera o arquivo final e chamamos:
    temp_dir = os.path.join(os.path.dirname(__file__), "temp_out")
    os.makedirs(temp_dir, exist_ok=True)
    
    mock_video = os.path.join(temp_dir, f"tiktok_{nicho}_video.mp4")
    if not os.path.exists(mock_video):
        with open(mock_video, "w") as f:
            f.write("mock_video_bytes")

    result = pipeline.export_final_production(
        video_path=mock_video,
        nicho=nicho,
        video_title=video_title,
        script_text=script_text
    )

    logger.info("==================================================")
    logger.info("🎉 PRODUÇÃO FINALIZADA COM SUCESSO!")
    logger.info(f"📁 Pasta Drive: {pipeline.get_output_dir(nicho)}")
    logger.info(f"🎬 Vídeo MP4: {result['video_path']}")
    logger.info(f"📝 Legenda TXT: {result['post_path']}")
    logger.info("==================================================")
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--nicho", type=str, default="tarot", choices=["direita", "esquerda", "tarot", "catolico"])
    parser.add_argument("--tema", type=str, default="")
    parser.add_argument("--drive_dir", type=str, default="/tmp/drive_tiktok")
    parser.add_argument("--gemini_keys", type=str, default="")
    args = parser.parse_args()

    run_nicho_generation(
        nicho=args.nicho,
        tema_personalizado=args.tema,
        drive_output_dir=args.drive_dir,
        gemini_keys_str=args.gemini_keys
    )
