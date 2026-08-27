import os
import re
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def extrair_video_id(url):
    padroes = [
        r"(?:youtube\.com/watch\?v=)([^&]+)",
        r"(?:youtu\.be/)([^?&]+)",
        r"(?:youtube\.com/live/)([^?&]+)",
        r"(?:youtube\.com/shorts/)([^?&]+)"
    ]

    for padrao in padroes:
        resultado = re.search(padrao, url)

        if resultado:
            return resultado.group(1)

    return None


def obter_transcricao(video_id):
    try:
        api = YouTubeTranscriptApi()

        transcript = api.fetch(video_id)

        texto = " ".join(
            trecho.text for trecho in transcript
        )

        return texto

    except Exception as erro:
        print(f"Erro ao obter a transcrição: {erro}")
        return None


def gerar_resumo(transcricao):

    prompt = f"""
Você é um especialista em resumir vídeos.

Analise a transcrição abaixo e produza um resumo claro e organizado.

O resumo deve conter:

1. Tema principal
2. Principais pontos apresentados
3. Informações importantes
4. Conclusão

Não invente informações que não estejam presentes na transcrição.

Transcrição:

{transcricao}
"""

    resposta = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )

    return resposta.output_text


def main():

    print("=" * 50)
    print("       ANALISADOR DE VÍDEOS DO YOUTUBE")
    print("=" * 50)

    url = input("\nCole o link do vídeo: ")

    video_id = extrair_video_id(url)

    if not video_id:
        print("\n❌ Link do YouTube inválido.")
        return

    print("\n🔎 Obtendo transcrição do vídeo...")

    transcricao = obter_transcricao(video_id)

    if not transcricao:
        print("\n❌ Não foi possível obter a transcrição.")
        print("O vídeo pode não possuir legendas disponíveis.")
        return

    print("✅ Transcrição obtida!")

    print("\n🧠 Gerando resumo...")

    try:
        resumo = gerar_resumo(transcricao)

        print("\n" + "=" * 50)
        print("                 RESUMO")
        print("=" * 50)

        print(resumo)

        print("\n" + "=" * 50)

    except Exception as erro:
        print(f"\n❌ Erro ao gerar o resumo: {erro}")


if __name__ == "__main__":
    main()