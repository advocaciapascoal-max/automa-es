"""
Vincula os modelos (Google Docs) do escritorio ao config/.env.

Rode DEPOIS de subir os 4 modelos na pasta MODELOS do Drive
(criada por config/setup_google_drive.py).

O script procura na pasta MODELOS um Google Doc por tipo de documento,
usando as palavras-chave abaixo, e grava o ID nas variaveis do .env.

Uso:
    .venv\\Scripts\\python.exe config/vincular_modelos.py
"""
import os
import sys

CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(CONFIG_DIR, '..')))

from dotenv import load_dotenv

ENV_PATH = os.path.join(CONFIG_DIR, '.env')
load_dotenv(ENV_PATH)

from googleapiclient.errors import HttpError

from setup_google_drive import (
    autenticar, conferir_conta, achar_pasta, gravar_env,
    PASTA_RAIZ, MIME_PASTA,
)

MIME_DOC = 'application/vnd.google-apps.document'

# tipo -> (palavras-chave no nome do arquivo, variaveis do .env que recebem o ID)
MODELOS = {
    'Ficha do Cliente': (
        ['ficha'],
        ['GOOGLE_TEMPLATE_ID'],
    ),
    'Contrato de Honorarios': (
        ['contrato', 'honorar'],
        ['GOOGLE_TEMPLATE_CONTRATO_ID', 'GOOGLE_TEMPLATE_CONTRATO'],
    ),
    'Procuracao': (
        ['procura'],
        ['GOOGLE_TEMPLATE_PROCURACAO_ID', 'GOOGLE_TEMPLATE_PROCURACAO'],
    ),
    'Declaracao de Hipossuficiencia': (
        ['declara', 'hipossufic'],
        ['GOOGLE_TEMPLATE_DECLARACAO_ID', 'GOOGLE_TEMPLATE_DECLARACAO'],
    ),
}


def normalizar(texto):
    """Minusculas e sem acento, para casar nome de arquivo sem frescura."""
    import unicodedata
    sem_acento = unicodedata.normalize('NFKD', texto)
    sem_acento = ''.join(c for c in sem_acento if not unicodedata.combining(c))
    return sem_acento.lower()


def listar_docs(drive, pasta_id):
    """Lista os Google Docs da pasta."""
    docs = []
    token = None
    while True:
        res = drive.files().list(
            q=f"'{pasta_id}' in parents and mimeType = '{MIME_DOC}' and trashed = false",
            fields='nextPageToken, files(id, name)',
            pageSize=100, pageToken=token,
            supportsAllDrives=True, includeItemsFromAllDrives=True,
        ).execute()
        docs.extend(res.get('files', []))
        token = res.get('nextPageToken')
        if not token:
            break
    return docs


def main():
    print('=' * 68)
    print('  VINCULAR MODELOS DO DRIVE - Pascoal & Dyandra Advocacia')
    print('=' * 68)
    print()

    drive = autenticar()
    conferir_conta(drive)
    print()

    raiz_id = achar_pasta(drive, PASTA_RAIZ, None)
    if not raiz_id:
        print(f'ERRO: pasta "{PASTA_RAIZ}" nao encontrada no Drive.')
        print('Rode antes: .venv\\Scripts\\python.exe config/setup_google_drive.py')
        sys.exit(1)

    modelos_id = achar_pasta(drive, 'MODELOS', raiz_id)
    if not modelos_id:
        print('ERRO: pasta MODELOS nao encontrada dentro da raiz.')
        sys.exit(1)

    docs = listar_docs(drive, modelos_id)
    if not docs:
        print('Nenhum Google Doc encontrado na pasta MODELOS.')
        print()
        print('Suba os modelos do escritorio la e rode de novo.')
        print('IMPORTANTE: precisa ser Google Doc, nao .docx. Se subir .docx,')
        print('abra no Drive e use Arquivo > Salvar como Documentos Google.')
        print(f'   https://drive.google.com/drive/folders/{modelos_id}')
        sys.exit(1)

    print(f'{len(docs)} documento(s) na pasta MODELOS:')
    for doc in docs:
        print(f'   - {doc["name"]}')
    print()

    valores_env = {}
    nao_encontrados = []

    for tipo, (palavras, chaves) in MODELOS.items():
        achado = None
        for doc in docs:
            nome = normalizar(doc['name'])
            if any(p in nome for p in palavras):
                achado = doc
                break

        if achado:
            print(f'   [OK        ] {tipo}  ->  {achado["name"]}')
            for chave in chaves:
                valores_env[chave] = achado['id']
        else:
            print(f'   [FALTANDO  ] {tipo}  (nenhum arquivo com: {", ".join(palavras)})')
            nao_encontrados.append(tipo)

    if valores_env:
        gravar_env(valores_env)
    else:
        print('\nNada vinculado - o .env nao foi alterado.')

    if nao_encontrados:
        print()
        print('Ainda faltam modelos:')
        for tipo in nao_encontrados:
            print(f'   * {tipo}')
        print()
        print(f'Suba na pasta MODELOS e rode de novo:')
        print(f'   https://drive.google.com/drive/folders/{modelos_id}')
    else:
        print('\nTodos os 4 modelos vinculados.')


if __name__ == '__main__':
    try:
        main()
    except HttpError as erro:
        print(f'\nERRO da API do Google: {erro}')
        sys.exit(1)
    except KeyboardInterrupt:
        print('\nCancelado.')
        sys.exit(1)
