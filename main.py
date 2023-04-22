#!/usr/bin/python

import os
import shutil
import sys
import time
from PIL import Image

# extrai o diretório de origem da linha de comando
try:
    PRIMEIRO_PARAMETRO = sys.argv[1]
except IndexError as e:
    print(f'\nNenhum parametro especificado.\n\n'
          f'Para copiar os arquivos use:'
          f'\n{sys.argv[0].split("/")[-1]} <diretorio de origem>\n\n'
          f'Para gerar índice use:\n'
          f'{sys.argv[0].split("/")[-1]} index\n')
    sys.exit(1)

DIR_ORIGEM = PRIMEIRO_PARAMETRO
DIR_DESTINO = '/home/arquivos/webserver'
TIPOS_DE_ARQUIVOS = 'jpg', 'arw', 'mp4'
EXTENSAO_RAW = 'arw'
EXTENSAO_JPEG = 'jpg'
EXTENSAO_VIDEO = 'mp4'
ESTILO = 'style="background:#d5d6ea;padding-top:20px; \
            padding-bottom: 5px; width:720px; \
            font-family: Verdana, Arial, Helvetica, sans-serif; border: 1px solid darkgray;"'

TOPO_HTML = '''<html>
                    <head>
                        <title>FOTOS</title>
                        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
                    </head>
                    <body>
            '''
RODAPE_HTML = '''</body></html>'''

def cria_indice_de_diretorios():
    dir_destino = os.listdir(DIR_DESTINO)
    arquivo_indice = os.path.join(DIR_DESTINO, 'index.html')
    if os.path.exists(arquivo_indice):
        os.remove(arquivo_indice)
    with open(arquivo_indice, 'a') as novo_arquivo_indice:
        novo_arquivo_indice.write(TOPO_HTML)
        for item in sorted(dir_destino, reverse=True):
            if os.path.isdir(os.path.join(DIR_DESTINO, item)):
                arquivo_info = os.path.join(DIR_DESTINO, item, 'info.txt')
                if os.path.exists(arquivo_info):
                    with open(arquivo_info, 'r') as info:
                        texto_do_arquivo_info = f'{info.readline()}'
                else:
                    with open(arquivo_info, 'w') as info:
                        info.write('')
                    texto_do_arquivo_info = 'preencher no arquivo info.txt e rodar o script novamente'
                html_arquivo_indice = \
                    f'<a style="font-family: Verdana, Arial, Helvetica, sans-serif;"' \
                    f'href={item}>{item} - {texto_do_arquivo_info}</a><br>'
                novo_arquivo_indice.write(html_arquivo_indice)
        novo_arquivo_indice.write(RODAPE_HTML)


def extrai_tipo_do_arquivo(arquivo: str) -> str:
    return arquivo.split('.')[-1].lower()


def extrai_nome_do_arquivo(arquivo: str) -> str:
    return arquivo.split('/')[-1]


def lista_arquivos_do_diretorio() -> list:
    lista_de_arquivos = []
    for path, _, arquivos in os.walk(DIR_ORIGEM):
        for arquivo in arquivos:
            if extrai_tipo_do_arquivo(arquivo) in TIPOS_DE_ARQUIVOS:
                lista_de_arquivos.append(os.path.join(path, arquivo))
    return lista_de_arquivos


def cria_diretorios(arquivo: str):
    diretorio_destino = os.path.join(
        DIR_DESTINO,
        extrai_data_do_arquivo(arquivo)
    )
    if not os.path.exists(diretorio_destino):
        os.makedirs(diretorio_destino)
        os.makedirs(os.path.join(diretorio_destino, 'thumbs'))
        for tipo in TIPOS_DE_ARQUIVOS:
            os.makedirs(os.path.join(diretorio_destino, tipo))


def extrai_data_do_arquivo(arquivo: str) -> str:
    t = time.localtime(os.path.getmtime(arquivo))
    ano = str(t.tm_year)
    mes = str(t.tm_mon) if t.tm_mon > 9 else "0" + str(t.tm_mon)
    dia = str(t.tm_mday) if t.tm_mday > 9 else "0" + str(t.tm_mday)
    return f'{ano}-{mes}-{dia}'


def adiciona_arquivos_no_html(arquivo: str):
    arquivo_destino = os.path.join(
        DIR_DESTINO,
        extrai_data_do_arquivo(arquivo),
        'index.html'
    )

    if extrai_tipo_do_arquivo(arquivo) == EXTENSAO_JPEG:
        adiciona_foto_no_html(arquivo, arquivo_destino)
    if extrai_tipo_do_arquivo(arquivo) == EXTENSAO_VIDEO:
        adiciona_video_no_html(arquivo, arquivo_destino)


def adiciona_video_no_html(arquivo: str, arquivo_destino: str):
    path_para_video = os.path.join(
        extrai_tipo_do_arquivo(arquivo),
        extrai_nome_do_arquivo(arquivo)
    )
    with open(arquivo_destino, 'a') as index_html:
        index_html.write(
            f'<div {ESTILO}>'
            f'<center><a href="{path_para_video}">'
            f'<b>[ {extrai_nome_do_arquivo(arquivo)} ]</b></a></center>'
            f'</div><p>'
        )


def adiciona_foto_no_html(arquivo: str, arquivo_destino: str):
    with open(arquivo_destino, 'a') as index_html:
        path_para_jpg = os.path.join(
            extrai_tipo_do_arquivo(arquivo),
            extrai_nome_do_arquivo(arquivo)
        )
        path_para_raw = os.path.join(
            EXTENSAO_RAW,
            extrai_nome_do_arquivo(arquivo).split('.')[0] + "." + EXTENSAO_RAW.upper()
        )
        path_para_thumbs = os.path.join(
            'thumbs',
            extrai_nome_do_arquivo(arquivo)
        )
        index_html.write(
            f'<div {ESTILO}>'
            f'<center><a href="{path_para_jpg}">'
            f'<img src="{path_para_thumbs}"></a>'
            f'<p><a href="{path_para_raw}">'
            f'<b>[ baixar o arquivo {EXTENSAO_RAW.upper()} se ele existir ]</b></a></center>'
            f'</div><p>'
        )


def copia_arquivo_para_destino(arquivo: str):
    arquivo_destino = os.path.join(
        DIR_DESTINO,
        extrai_data_do_arquivo(arquivo),
        extrai_tipo_do_arquivo(arquivo),
        extrai_nome_do_arquivo(arquivo)
    )
    if not os.path.exists(arquivo_destino):
        print(f'Copiando {extrai_nome_do_arquivo(arquivo)} para {arquivo_destino}...')
        shutil.copyfile(arquivo, arquivo_destino)
        adiciona_arquivos_no_html(arquivo)


def redimensiona_imagem(arquivo: str):
    if extrai_tipo_do_arquivo(arquivo) == 'jpg':
        arquivo_destino = os.path.join(
            DIR_DESTINO,
            extrai_data_do_arquivo(arquivo),
            'thumbs',
            extrai_nome_do_arquivo(arquivo)
        )
        if not os.path.exists(arquivo_destino):
            imagem = Image.open(arquivo)
            imagem.thumbnail((640, 640), Image.LANCZOS)
            imagem.save(arquivo_destino, "JPEG")


if __name__ == '__main__':
    print('Em execução...')
    if PRIMEIRO_PARAMETRO == 'index':
        cria_indice_de_diretorios()
    else:
        for i in lista_arquivos_do_diretorio():
            cria_diretorios(i)
            copia_arquivo_para_destino(i)
            redimensiona_imagem(i)
        cria_indice_de_diretorios()
