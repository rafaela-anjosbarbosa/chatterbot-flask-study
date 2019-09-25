# -*- coding: utf-8 -*-

import os
from flask import Flask, render_template, request
from chatterbot.trainers import ListTrainer
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot.conversation import Statement
import wikipedia

app = Flask(__name__)

bot = ChatBot('Botzin')
nome_pasta='treino'
wikipedia.set_lang("pt")
pesquisar=False
aprender=False
escolha_opcao=False
	
@app.route("/")
def home():
    return render_template("index.html")

def treina(nome_pasta):
        trainer = ChatterBotCorpusTrainer(bot)
        trainer.train("chatterbot.corpus.portuguese")       
        trainer = ListTrainer(bot)
        for treino in os.listdir(nome_pasta):
            arquivos = open(nome_pasta+'/'+treino, 'r', encoding="utf-8").readlines()
            trainer.train(arquivos)
treina(nome_pasta)


def ensinar_bot(resposta_correta,pergunta_aprender):
    if resposta_correta.lower() == 'n':
        return str('ok')
    else:
        bot.learn_response(Statement(resposta_correta), pergunta_aprender)
        arquivo_aprendizado(resposta_correta,pergunta_aprender)
        return str('Resposta adicionada ao bot!')

def realizar_pesquisa(pergunta):
    global pesquisar
    global escolha_opcao
    global opcoes
    global termo_pesquisado
    if (pergunta.lower()!='nada' and escolha_opcao == False):
        termo_pesquisado = pergunta
        try:
            pesquisar = False
            return str((wikipedia.summary(termo_pesquisado)))
        except:
            opcoes = wikipedia.search(termo_pesquisado)
            lista_opcoes = ''
            for i, item in enumerate(opcoes):
                if i > 0:
                    lista_opcoes += str(str(i)+'-'+item+'\n')
            escolha_opcao = True
            return str('Escolha uma opção: '+lista_opcoes)
        return True
    elif (escolha_opcao == True):

        try:
            opcoes = wikipedia.search(termo_pesquisado)
            opcao = int(request.args.get('msg'))
            assert opcao in range(len(opcoes))
            escolha_opcao = False
            pesquisar = False
            return (str(wikipedia.summary(opcoes[opcao])))
        except:
            opcao = request.args.get('msg')
            return str('Opção inválida')
    elif 'nada' in pergunta.lower():
        return str('ok')
    else:
        return str('O que você deseja pesquisar? Digita NADA para voltarmos a conversar.')
    
def arquivo_aprendizado(resposta_correta,pergunta_aprender):
        trainer = ListTrainer(bot)
        arquivo = open(nome_pasta+'/'+'aprendizados.txt', 'a+', encoding='UTF-8')
        conteudo = arquivo.readlines()
        conteudo.append(str(pergunta_aprender)+'\n'+str(resposta_correta)+'\n')
        arquivo.writelines(conteudo)
        arquivo.close()
        arquivo = open(nome_pasta+'/'+'aprendizados.txt', 'r', encoding='UTF-8').readlines()
        trainer.train(arquivo)
        print('arquivo editado')
        return True
      
@app.route("/get")		

def resposta():
    global pesquisar
    global aprender
    global pergunta_aprender
    while True:
        pergunta = request.args.get('msg')
        if (pergunta!='sair'):
            if (pergunta != '' and pergunta.lower() != 'pesquisar' and pesquisar == False and aprender == False and escolha_opcao == False): 
                resposta = bot.get_response(pergunta)
                if float(resposta.confidence) >= 0.1:
                  return str(resposta)
                else:
                    aprender = True
                    pergunta_aprender = pergunta
                    return str('Ainda não sei responder esta pergunta. Gostaria de me ensinar? Escreva a resposta correta para: '+pergunta_aprender+' ou responda "N" para continuar')
            elif (pergunta.lower() == 'pesquisar'):
                pesquisar = True
                return str('O que você deseja pesquisar? Digita NADA para voltarmos a conversar.')
            elif (pesquisar == True):
                pergunta = request.args.get('msg')
                return realizar_pesquisa(pergunta)
            elif (aprender == True):
                resposta_correta = request.args.get('msg')
                aprender = False
                return ensinar_bot(resposta_correta,pergunta_aprender)
        else:
            print(bot.name+': Até logo!')
            return str('Até logo!')
            break

if __name__ == "__main__":
    app.run(debug=True)