import os
import feedparser
from google import genai
from google.genai import types

rss_feeds = [
    "https://news.ycombinator.com/rss",
    "https://feeds.arstechnica.com/arstechnica/index",
    "https://www.theverge.com/rss/index.xml",
    "https://pplware.sapo.pt/feed/",
    "https://openai.com/news/rss.xml",
    "https://observador.pt/feed/",  # Corrigido o ']' no final
    "https://www.publico.pt/api/feed/rss/actualidade",
]

system_prompt = """
És um gerador de resumos de notícias focado em evitar o doomscrolling, especializado para um perfil de Platform Engineer, DevOps e profissionais de IT.
A tua tarefa é ler a lista de artigos fornecida em bruto e gerar uma síntese altamente estruturada em Português de Portugal.

Regras de Formatação:
1. Agrupa as notícias prioritariamente e estritamente nas seguintes categorias (usando os respetivos ícones):
   - ☁️ Platform Engineering & Cloud (Kubernetes, AWS/GCP/Azure, IaC, CI/CD, Observabilidade)
   - 🤖 IA & DevTools (Modelos, automação, ferramentas de desenvolvimento, LLMs)
   - 🛡️ Cibersegurança & Infraestrutura (Vulnerabilidades, redes, Linux, SysAdmin)
   - 💻 Indústria IT & Open Source (Notícias do setor de tecnologia, licenças, grandes empresas de tech)
   - ⚖️ Política & Economia (Apenas se tiver impacto relevante ou geral)
   - 🌍 Geral & Sociedade (Outros temas relevantes que não se enquadrem nas categorias de IT acima)

2. Para cada notícia selecionada:
   - Escreve um resumo conciso de 1 a 3 frases.
   - Destaca em **negrito** as entidades principais, tecnologias, ferramentas, números ou nomes próprios.
   - Funde notícias repetidas ou sobre o mesmo tema num único ponto coeso.

3. Restrições:
   - Mantém um tom neutro, direto e técnico quando aplicável.
   - Não adiciones introduções ("Aqui está o resumo..."), conclusões ou comentários meta.
   - Se uma categoria não tiver notícias relevantes nos feeds recolhidos, omite essa categoria.
"""

news = []

for url in rss_feeds:
    feed = feedparser.parse(url)
    for entry in feed.entries[:10]:
        title = entry.get("title", "")
        summary = entry.get("summary", entry.get("description", ""))
        news.append(f"Título: {title}\nResumo: {summary}\n---")

texto_artigos = "\n".join(news)

client = genai.Client(api_key=os.environ.get("GEMINI_API"))

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=f"Aqui está a lista de notícias em bruto para sintetizares:\n\n{texto_artigos} e depois disso gera uma pagina estatica index.html local",
    config=types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.2,
    ),
)

print(response.text)
