import os
import feedparser
from google import genai
from google.genai import types

rss_feeds = [
    # Tech Internacional
    "https://news.ycombinator.com/rss",
    "https://feeds.arstechnica.com/arstechnica/index",
    "https://www.theverge.com/rss/index.xml",
    "https://openai.com/news/rss.xml",
    # Tech Portugal
    "https://pplware.sapo.pt/feed/",
    "https://tek.sapo.pt/rss",
    "https://leak.pt/feed/",
    "https://www.meiobit.com/feed/",
    "https://www.abertoatedemadrugada.com/feed/",
    "https://www.noticiasaominuto.com/rss/tech",
    # Geral Portugal
    "https://observador.pt/feed/",
    "https://www.publico.pt/api/feed/rss/actualidade",
]

system_prompt = """
És um gerador de resumos de notícias focado em evitar o doomscrolling, especializado para um perfil de Platform Engineer, DevOps e profissionais de IT.
A tua tarefa é ler a lista de artigos fornecida em bruto e gerar uma síntese altamente estruturada em Português de Portugal (PT-PT), preferencialmente sobre notícias de origem portuguesa ou com relevância direta para Portugal.

Regras de Formatação:
1. Agrupa as notícias nas seguintes categorias:
   - ☁️ IT News
   - ⚖️ Política & Economia
   - 🌍 Geral & Sociedade
2. Para cada notícia selecionada:
   - Escreve um resumo conciso de 1 a 3 frases.
   - Destaca em **negrito** as entidades principais, tecnologias, ferramentas, números ou nomes próprios.
   - Funde notícias repetidas ou sobre o mesmo tema num único ponto coeso.
3. Restrições:
   - Mantém um tom neutro, direto e técnico quando aplicável.
   - Não adiciones introduções ("Aqui está o resumo..."), conclusões ou comentários meta.
   - Se uma categoria não tiver notícias relevantes, omite essa categoria.

FORMATO HTML OBRIGATÓRIO — usar EXATAMENTE estas tags e classes:

<section>
    <h2 class="category-title it">☁️ IT News</h2>
    <div class="news-list">
        <article class="news-card">
            <p class="news-content">A <strong>Google</strong> lançou o novo modelo...</p>
        </article>
        <article class="news-card">
            <p class="news-content">A <strong>Microsoft</strong> anunciou...</p>
        </article>
    </div>
</section>

<section>
    <h2 class="category-title soc">🌍 Geral & Sociedade</h2>
    <div class="news-list">
        <article class="news-card">
            <p class="news-content">O <strong>Governo</strong> aprovou...</p>
        </article>
    </div>
</section>

REGRAS HTML ESTRITAS:
- Cada categoria deve estar numa <section> separada.
- O título da categoria deve ser <h2> com class="category-title it" (ou pol, ou soc).
- Cada notícia deve estar dentro de <article class="news-card">.
- O texto de cada notícia deve estar dentro de <p class="news-content">.
- Usa <strong> para negrito.
- NÃO uses listas Markdown (-, *, #), nem headings Markdown.
- NÃO uses <main>, <html>, <head>, <body>.
- O output final deve ser apenas e só HTML com as classes indicadas, sem explicações adicionais.
"""

news = []

for url in rss_feeds:
    feed = feedparser.parse(url)
    for entry in feed.entries[:10]:
        title = entry.get("title", "")
        summary = entry.get("summary", entry.get("description", ""))
        news.append(f"Título: {title}\nResumo: {summary}\n---")

articles = "\n".join(news)

client = genai.Client(api_key=os.environ.get("GEMINI_API"))

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=(
        "Aqui está a lista de notícias em bruto para sintetizares:\n\n"
        f"{articles}"
        "\n\nIMPORTANTE: Prioriza notícias de origem portuguesa ou com impacto direto em Portugal. "
        "O output deve ser em português de Portugal (PT-PT). "
        "Segue EXATAMENTE o formato HTML com as classes CSS definido nas instruções do sistema. "
        "Não incluas <html>, <head>, <body>, <main>, <style> ou <script>."
    ),
    config=types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.2,
    ),
)
result = response.text

# Load template and inject AI content
with open("templates/base.html", "r") as f:
    template = f.read()

html_output = template.replace("<!-- AI_GENERATED_CONTENT -->", result)

with open("index.html", "w") as f:
    f.write(html_output)
