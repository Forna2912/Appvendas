from kivy.app import App
from kivy.lang import Builder
from telas import *
from botoes import *
import requests
from BanerVenda import *
from BannerVendedor import *
import os
from functools import partial
import json
from myfirebase import MyFireBase
from datetime import date
from kivy.core.window import Window

GUI=Builder.load_file('main.kv')

    
class MainApp(App):
    produto=None
    cliente=None
    unidade=None

    def build(self):
        self.firebase=MyFireBase()
        Window.softinput_mode='below_target'
        return GUI

    def on_start(self):
        #carregar foto perfil
        arquivos=os.listdir('icones/fotos_perfil')
        pagina_foto_perfil=self.root.ids['mudarperfil']
        lista_fotos=pagina_foto_perfil.ids['lista_foto_perfil']
        for foto in arquivos:
            imagem=ImageButton(source=f'icones/fotos_perfil/{foto}',on_release=partial(self.mudar_foto_perfil,foto))
            lista_fotos.add_widget(imagem)

        #carregar fotos clientes
        arquivos=os.listdir('icones/fotos_clientes')
        pagina_adicionarvendas=self.root.ids['adicionarvendas']
        lista_fotos=pagina_adicionarvendas.ids['lista_clientes']
        for foto_clientes in arquivos:
            imagem=ImageButton(source=f'icones/fotos_clientes/{foto_clientes}',on_release=partial(self.selecionar_cliente,foto_clientes,lista_fotos))
            label=LabelButton(text=foto_clientes.replace('.png','').capitalize(),on_release=partial(self.selecionar_cliente,foto_clientes,lista_fotos))
            lista_fotos.add_widget(imagem)
            lista_fotos.add_widget(label)

        #carregar fotos produtos
        arquivos=os.listdir('icones/fotos_produtos')
        lista_fotos=pagina_adicionarvendas.ids['lista_produtos']
        for foto_produtos in arquivos:
            imagem=ImageButton(source=f'icones/fotos_produtos/{foto_produtos}',on_release=partial(self.selecionar_produto,foto_produtos,lista_fotos))
            label=LabelButton(text=foto_produtos.replace('.png','').capitalize(),on_release=partial(self.selecionar_produto,foto_produtos,lista_fotos))
            lista_fotos.add_widget(imagem)
            lista_fotos.add_widget(label)

        #carregar data
        label_data=pagina_adicionarvendas.ids['data']
        label_data.text=f'Data: {date.today().strftime("%d/%m/%y")}'

        self.carregar_infos_usuario()

    def carregar_infos_usuario(self):
        try:
            with open('refreshtoken.txt','r') as arquivo:
                refresh_token=arquivo.read()
            local_id,id_token=self.firebase.trocar_token(refresh_token)
            self.local_id=local_id
            self.id_token=id_token

            #pega informação
            requisicao=requests.get(f'https://aplicativo-kung-fu-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}')
            requisicao_dict=requisicao.json()

            #preencher foto perfil
            self.avatar=requisicao_dict['foto']
            foto_perfil=self.root.ids['foto_perfil']
            foto_perfil.source=f'icones/fotos_perfil/{self.avatar}'

            #Id Unico
            self.Id_unico=requisicao_dict['id_vendedor']
            pagina_ajustes=self.root.ids['ajustespage']
            pagina_ajustes.ids['id_vendedor'].text=f'SEU ID UNICO : {self.Id_unico}'

            #Total de vendas
            self.total_vendas=float(requisicao_dict['total_vendas'])
            homepage=self.root.ids['homepage']
            homepage.ids['total_vendas'].text=f'TOTAL DE VENDAS : R$:{self.total_vendas:.2f}'


            #preencher vendas
            try:
                self.vendas = requisicao_dict["vendas"]
                pagina_homepage = self.root.ids['homepage']
                lista_vendas = pagina_homepage.ids['lista_vendas']

                #deletar vendas
                for item in list(lista_vendas.children):
                    lista_vendas.remove_widget(item)

                for id_venda in self.vendas:
                    venda=self.vendas[id_venda]
                    baner = BanerVenda(
                        cliente=venda['cliente'],
                        fotocliente=venda['foto_cliente'],
                        produto=venda['produto'],
                        fotoproduto=venda['foto_produto'],
                        data=venda['data'],
                        preco=venda['preco'],
                        unidade=venda['unidade'],
                        quantidade=venda['quantidade']
                    )
                    lista_vendas.add_widget(baner)
            except:
                pass

            #preencher lista vendedores
            self.equipe=requisicao_dict['equipe']
            lista_equipe=self.equipe.split(',')
            pagina_listavendedores=self.root.ids['salesmano']
            lista_vendedores=pagina_listavendedores.ids['lista_vendas']
            for item in list(lista_vendedores.children):
                lista_vendedores.remove_widget(item)
            for id_vendedor_equipe in lista_equipe:
                if id_vendedor_equipe != '':
                    banner_vendedor=BannerVendedor(id_vendedor=id_vendedor_equipe)
                    lista_vendedores.add_widget(banner_vendedor)


            self.mudar_pagina('homepage')
        except:
            pass

    def mudar_pagina(self,destino):
        Gerenciador_telas=self.root.ids['screen_manager']
        Gerenciador_telas.current=destino

    def esconder_senha(self):
        paginalogin=self.root.ids['paginalogin']
        if paginalogin.ids['imagem_senha'].source=='icones/senha_visivel.png':
            paginalogin.ids['imagem_senha'].source='icones/senha_invisivel.png'
            paginalogin.ids['senha'].password=True
        else:
            paginalogin.ids['imagem_senha'].source='icones/senha_visivel.png'
            paginalogin.ids['senha'].password=False

    #adiciona vendedor a equipe
    def adicionarvendedor(self,id_vendedor_adicionado):
        link=f'https://aplicativo-kung-fu-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"&equalTo="{id_vendedor_adicionado}"'
        requisicao=requests.get(link)
        requisicao_dict=requisicao.json()
        pagina_adicionarvendedor=self.root.ids['acompanharvendedor']
        mensagem_texto=pagina_adicionarvendedor.ids['mensagem_outrovendedor']

        if requisicao_dict =={}:
            mensagem_texto.text='Usuario não encontrado'
        else:
            equipe=self.equipe.split(',')
            if id_vendedor_adicionado in equipe:
                mensagem_texto.text='Vendedor ja faz parte da equipe'
            else:
                if self.equipe=='':
                    self.equipe=self.equipe + f'{id_vendedor_adicionado}'
                else:
                    self.equipe=self.equipe + f',{id_vendedor_adicionado}'
                requests.patch(f'https://aplicativo-kung-fu-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}',data=json.dumps({'equipe':self.equipe}))
                mensagem_texto.text='Vendedor adicionado'

                #adiciona uma banner na lista
                pagina_listavendedores=self.root.ids['salesmano']
                lista_vendedores=pagina_listavendedores.ids['lista_vendas']
                banner_vendedor=BannerVendedor(id_vendedor=id_vendedor_adicionado)
                lista_vendedores.add_widget(banner_vendedor)

        
    def mudar_foto_perfil(self,foto,*args):
        foto_perfil=self.root.ids['foto_perfil']
        self.avatar=foto
        foto_perfil.source=f'icones/fotos_perfil/{foto}'
        requests.patch(f'https://aplicativo-kung-fu-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}',data=json.dumps({'foto':foto}))
        self.mudar_pagina('ajustespage')
    
    def selecionar_cliente(self,foto,lista_fotos,*args):
        self.cliente=foto
        pagina_adicionarvendas=self.root.ids['adicionarvendas']
        #pintar tudo de branco
        for item in list(lista_fotos.children):
            item.color=(1,1,1,1)
        #pintar selecionado
            try:
                texto=item.text
                texto=texto.lower()+'.png'
                if foto==texto:
                    item.color=(0,207/255,219/255,1)
                    pagina_adicionarvendas.ids['selecionar_cliente'].color=(1,1,1,1)

            except:
                pass

    def selecionar_produto(self,foto,lista_fotos,*args):
        self.produto=foto
        pagina_adicionarvendas=self.root.ids['adicionarvendas']
        #pintar tudo de branco
        for item in list(lista_fotos.children):
            item.color=(1,1,1,1)
        #pintar selecionado
            try:
                texto=item.text
                texto=texto.lower()+'.png'
                if foto==texto:
                    item.color=(0,207/255,219/255,1)
                    pagina_adicionarvendas.ids['selecionar_produto'].color=(1,1,1,1)

            except:
                pass

    def selecionar_unidade(self,id,*args):
        pagina_adicionarvendas=self.root.ids['adicionarvendas']
        self.unidade=id
        #pinta geral de branco
        pagina_adicionarvendas.ids['unidades'].color=(1,1,1,1)
        pagina_adicionarvendas.ids['litros'].color=(1,1,1,1)
        pagina_adicionarvendas.ids['Kg'].color=(1,1,1,1)

        #pinta o proprio de azul
        pagina_adicionarvendas.ids[id].color=(0,207/255,219/255,1)
    
    def adicionar_venda(self):
        foto_produto=self.produto
        foto_cliente=self.cliente
        unidade=self.unidade
    
        pagina_adicionarvendas=self.root.ids['adicionarvendas']
        label_data=pagina_adicionarvendas.ids['data'].text.replace('Data: ','')
        preco=pagina_adicionarvendas.ids['preco_total'].text
        quantidade=pagina_adicionarvendas.ids['quantidade'].text
        if not foto_cliente:
            pagina_adicionarvendas.ids['selecionar_cliente'].color=(1,0,0,1)

        if not foto_produto:
            pagina_adicionarvendas.ids['selecionar_produto'].color=(1,0,0,1)

        if not unidade:
            pagina_adicionarvendas.ids['Kg'].color=(1,0,0,1)
            pagina_adicionarvendas.ids['unidades'].color=(1,0,0,1)
            pagina_adicionarvendas.ids['litros'].color=(1,0,0,1)

        if not preco:
            pagina_adicionarvendas.ids['preco_total_label'].color=(1,0,0,1)
        else:
            try:
                if float(preco)>0 and float(preco)<1000000:
                    preco=float(preco)
                    pagina_adicionarvendas.ids['preco_total_label'].color=(1,1,1,1)
                else:
                    pagina_adicionarvendas.ids['preco_total_label'].color=(1,0,0,1)
            except:
                pagina_adicionarvendas.ids['preco_total_label'].color=(1,0,0,1)

        if not quantidade:
            pagina_adicionarvendas.ids['quantidade_total_label'].color=(1,0,0,1)
        else:
            try:
                if float(quantidade)>0 and float(quantidade)<1000000:
                    quantidade=float(quantidade)
                    pagina_adicionarvendas.ids['quantidade_total_label'].color=(1,1,1,1)
                else:
                    pagina_adicionarvendas.ids['quantidade_total_label'].color=(1,0,0,1)
            except:
                pagina_adicionarvendas.ids['quantidade_total_label'].color=(1,0,0,1)

        
        if preco and unidade and quantidade and foto_cliente and foto_produto and type(preco)==float and type(quantidade)==float:
            produto=foto_produto.replace('.png','')
            cliente=foto_cliente.replace('.png','')
            info={'cliente':cliente,'produto':produto,'foto_cliente':foto_cliente,'foto_produto':foto_produto,'data':label_data,'unidade':unidade,'preco':preco,'quantidade':quantidade}
            requests.post(f'https://aplicativo-kung-fu-default-rtdb.firebaseio.com/{self.local_id}/vendas.json?auth={self.id_token}',data=json.dumps(info))
            self.mudar_pagina('homepage')
            self.reset_adicionarvendas()
            baner=BanerVenda(cliente=cliente,
                    fotocliente=foto_cliente,
                    produto=produto,
                    fotoproduto=foto_produto,
                    data=label_data,
                    preco=preco,
                    unidade=unidade,
                    quantidade=quantidade)
            pagina_homepage = self.root.ids['homepage']
            lista_vendas = pagina_homepage.ids['lista_vendas']
            lista_vendas.add_widget(baner)
            requisicao=requests.get(f'https://aplicativo-kung-fu-default-rtdb.firebaseio.com/{self.local_id}/total_vendas.json?auth={self.id_token}')
            requisicao_dict=float(requisicao.json())
            self.total_vendas=requisicao_dict+preco
            requests.patch(f'https://aplicativo-kung-fu-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}',data=json.dumps({'total_vendas':self.total_vendas}))
            pagina_homepage.ids['total_vendas'].text=f'TOTAL DE VENDAS : R$:{self.total_vendas:.2f}'
            self.produto=None
            self.cliente=None
            self.unidade=None

    def reset_adicionarvendas(self):
        pagina_adicionarvendas=self.root.ids['adicionarvendas']
        listas_vendas=[pagina_adicionarvendas.ids['lista_clientes'],pagina_adicionarvendas.ids['lista_produtos']]
        #pintar tudo de branco
        for lista in listas_vendas:
            for item in list(lista.children):
                item.color=(1,1,1,1)

        pagina_adicionarvendas.ids['preco_total_label'].color=(1,1,1,1)
        pagina_adicionarvendas.ids['quantidade_total_label'].color=(1,1,1,1)
        pagina_adicionarvendas.ids['selecionar_cliente'].color=(1,1,1,1)
        pagina_adicionarvendas.ids['selecionar_produto'].color=(1,1,1,1)
        pagina_adicionarvendas.ids['unidades'].color=(1,1,1,1)
        pagina_adicionarvendas.ids['litros'].color=(1,1,1,1)
        pagina_adicionarvendas.ids['Kg'].color=(1,1,1,1)
        pagina_adicionarvendas.ids['preco_total'].text=''
        pagina_adicionarvendas.ids['quantidade'].text=''

        self.produto=None
        self.cliente=None
        self.unidade=None

    def carregar_vendas(self):
        #pega informação
        requisicao = requests.get(f'https://aplicativo-kung-fu-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"')
        requisicao_dict=requisicao.json()
        pagina_todasvendas=self.root.ids['vervendas']
        lista_vendas=pagina_todasvendas.ids['lista_vendas']
        
        #preencher foto perfil
        foto_perfil=self.root.ids['foto_perfil']
        foto_perfil.source=f'icones/fotos_perfil/hash.png'

        for item in list(lista_vendas.children):
            lista_vendas.remove_widget(item)

        total_vendas=0
        for local_id in requisicao_dict:
            try:
                vendas=requisicao_dict[local_id]['vendas']
                for id_venda in vendas:
                    venda=vendas[id_venda]
                    total_vendas+=float(venda['preco'])
                    baner = BanerVenda(
                        cliente=venda['cliente'],
                        fotocliente=venda['foto_cliente'],
                        produto=venda['produto'],
                        fotoproduto=venda['foto_produto'],
                        data=venda['data'],
                        preco=venda['preco'],
                        unidade=venda['unidade'],
                        quantidade=venda['quantidade']
                    )
                    lista_vendas.add_widget(baner)
            except:
                pass

        #Total de vendas
        pagina_todasvendas.ids['total_vendas'].text=f'TOTAL DE VENDAS : R$:{total_vendas:.2f}'

        self.mudar_pagina('vervendas')

    def sair_todasvendas(self,id_tela):
        foto_perfil=self.root.ids['foto_perfil']
        foto_perfil.source=f'icones/fotos_perfil/{self.avatar}'
        self.mudar_pagina(id_tela)
    
    def carregar_vendas_vendedor(self,id_vendedor,*args):
        link=f'https://aplicativo-kung-fu-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"&equalTo="{id_vendedor}"'
        requisicao=requests.get(link)
        requisicao_dict=requisicao.json()
        dict_info_vendedor=list(requisicao_dict.values())[0]
        try:
            vendas = dict_info_vendedor["vendas"]
            vendasoutrovendedor = self.root.ids['vendasoutrovendedor']
            lista_vendas = vendasoutrovendedor.ids['lista_vendas']
            
            for item in list(lista_vendas.children):
                lista_vendas.remove_widget(item)
            for id_venda in vendas:
                venda=vendas[id_venda]
                baner = BanerVenda(
                    cliente=venda['cliente'],
                    fotocliente=venda['foto_cliente'],
                    produto=venda['produto'],
                    fotoproduto=venda['foto_produto'],
                    data=venda['data'],
                    preco=venda['preco'],
                    unidade=venda['unidade'],
                    quantidade=venda['quantidade']
                )
                lista_vendas.add_widget(baner)
        except:
            pass
        total_vendas=dict_info_vendedor['total_vendas']
        vendasoutrovendedor.ids['total_vendas'].text=f'TOTAL DE VENDAS : R$:{total_vendas:.2f}'
        foto=dict_info_vendedor['foto']
        foto_perfil=self.root.ids['foto_perfil']
        foto_perfil.source=f'icones/fotos_perfil/{foto}'

        self.mudar_pagina('vendasoutrovendedor')
    
    def sair(self):
        paginalogin=self.root.ids['paginalogin']
        email=paginalogin.ids['email']
        senha=paginalogin.ids['senha']
        email.text=""
        senha.text=""
        foto_perfil=self.root.ids['foto_perfil']
        foto_perfil.source=f'icones/fotos_perfil/hash.png'
        os.remove('refreshtoken.txt')
        self.mudar_pagina("paginalogin")

    

MainApp().run()
