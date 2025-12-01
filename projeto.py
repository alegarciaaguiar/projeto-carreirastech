import os
import csv
from flask import Flask, render_template, url_for, request, send_from_directory, abort, session, redirect
import traceback

app = Flask(__name__)

# secret key for session. In production set FLASK_SECRET env var to a secure value.
app.secret_key = os.environ.get('FLASK_SECRET', 'dev_secret_change_me')

#Definindo ambiente para modo desenvolvimento (debug)
os.environ['FLASK_DEBUG'] = 'True'
app.debug = os.environ.get('FLASK_DEBUG', 'True') == 'True'


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/historia')
def historia():
    return render_template("historia.html")

@app.route('/sobre')
def sobre():
    return render_template("sobre.html")

@app.route('/ranking')
def glossario():

    glossario_de_termos = []

    with open('carreiras_tech.csv', newline='', encoding='utf-8') as arquivo:
        reader = csv.reader(arquivo, delimiter=',')
        for linha in reader:
            glossario_de_termos.append(linha)

    return render_template("glossario.html",
                           glossario=glossario_de_termos)

@app.route('/contato')
def contato():
    return render_template("contato.html")


# Serve arquivos estáticos que estejam na pasta raiz `imagens/`
@app.route('/imagens/<path:filename>')
def imagens_static(filename):
    try:
        base = os.path.join(app.root_path, 'imagens')
        return send_from_directory(base, filename)
    except Exception:
        abort(404)

@app.route( "/criar_termo", methods=['POST', ])
def criar_termo():
    nome = request.form.get('nome', '')
    email = request.form.get('email', '')
    assunto = request.form.get('assunto', '')
    mensagem = request.form.get('mensagem', '')

    # Salva contato em arquivo CSV como fallback simples
    try:
        with open('contatos.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([nome, email, assunto, mensagem])
    except Exception:
        # se falhar ao salvar, apenas continue (apenas placeholder)
        pass

    return render_template('contato.html', sucesso=True)


@app.route('/gemini', methods=['GET', 'POST'])
def gemini():
    """Página de interação com IA: exibe um formulário e tenta usar Gemini/Vertex AI.

    A função tenta usar a biblioteca `google-generativeai` se estiver instalada
    e se houver credenciais configuradas (variáveis de ambiente `GOOGLE_API_KEY`
    ou `GOOGLE_APPLICATION_CREDENTIALS`). Caso contrário mostra instruções.
    """
    question = None
    ai_response = None
    error = None

    # detecta se a biblioteca google-genai está disponível e se as credenciais estão setadas
    genai_installed = False
    genai_configured = False
    try:
        from google import genai  # type: ignore
        genai_installed = True
    except Exception:
        genai = None

    if os.environ.get('GOOGLE_API_KEY') or os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
        genai_configured = True

    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        if question:
            if not genai_installed:
                error = (
                    'Biblioteca `google-genai` não está instalada. '
                    'Execute: pip install google-genai'
                )
            elif not genai_configured:
                error = (
                    'Credenciais do Google não configuradas. Defina a variável '
                    '`GOOGLE_API_KEY` ou `GOOGLE_APPLICATION_CREDENTIALS`.'
                )
            else:
                try:
                    # configurar API key se fornecida
                    api_key = os.environ.get('GOOGLE_API_KEY')
                    try:
                        if api_key and hasattr(genai, 'configure'):
                            genai.configure(api_key=api_key)
                    except Exception:
                        pass

                    # cria client e chama o modelo Gemini
                    try:
                        client = genai.Client()
                        # gera o conteúdo; o parâmetro contents pode variar por versão
                        resp = client.models.generate_content(
                            model=os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash'),
                            contents=[{"type": "text", "text": question}],
                        )
                    except Exception:
                        # fallback para chamada simplificada
                        resp = client.models.generate_content(model=os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash'), contents=question)

                    # tenta extrair texto da resposta
                    ai_text = None
                    if resp is None:
                        ai_text = None
                    else:
                        ai_text = getattr(resp, 'text', None)
                        if not ai_text:
                            # algumas versões retornam dict-like
                            try:
                                # resp.output[0].content[0].text
                                out = getattr(resp, 'output', None) or getattr(resp, 'result', None) or resp
                                if isinstance(out, (list, tuple)) and len(out) > 0:
                                    candidate = out[0]
                                elif isinstance(out, dict):
                                    candidate = out.get('output') or out
                                else:
                                    candidate = out
                                # attempt nested extraction defensively
                                if isinstance(candidate, dict):
                                    ai_text = candidate.get('text') or candidate.get('content') or str(candidate)
                                else:
                                    ai_text = str(candidate)
                            except Exception:
                                ai_text = str(resp)

                    if not ai_text:
                        ai_response = f"(Fallback) Recebi sua pergunta: {question}"
                    else:
                        ai_response = ai_text

                    # persist conversation in session
                    try:
                        conv = session.get('conversation', [])
                        conv.append({'role': 'user', 'text': question})
                        conv.append({'role': 'gemini', 'text': ai_response})
                        session['conversation'] = conv
                    except Exception:
                        # if session storage fails, ignore and continue
                        pass
                except Exception as e:
                    error = 'Erro ao chamar a API de geração: ' + str(e)
                    error += '\n' + traceback.format_exc()

    # load conversation to display
    conversation = session.get('conversation', [])

    return render_template(
        'gemini.html',
        question=question,
        ai_response=ai_response,
        error=error,
        genai_installed=genai_installed,
        genai_configured=genai_configured,
        conversation=conversation,
    )


@app.route('/gemini/clear', methods=['POST', 'GET'])
def gemini_clear():
    session.pop('conversation', None)
    return redirect(url_for('gemini'))


if __name__ == '__main__':
    app.run()


