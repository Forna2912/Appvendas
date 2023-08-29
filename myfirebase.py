import requests
from kivy.app import App
import json

class MyFireBase():
    API_KEY='AIzaSyAHYHqSiZDcwQFUVPoGo5X7TjO9p9dXKtM'
    def fazer_login(self,email,senha):
        try:
            meu_aplicativo=App.get_running_app()
            pagina_login=meu_aplicativo.root.ids['paginalogin']
            link=f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.API_KEY}'
            info={'email':email,
                'password':senha,
                'returnSecureToken':True}
            requisição=requests.post(link,data=info)
            requisição_dict=requisição.json()
            if requisição.ok:
                id_token=requisição_dict['idToken']
                local_id=requisição_dict['localId']
                refresh_token=requisição_dict['refreshToken']
                meu_aplicativo.id_token=id_token
                meu_aplicativo.local_id=local_id
                with open('refreshtoken.txt','w') as arquivo:
                    arquivo.write(refresh_token)
                meu_aplicativo.carregar_infos_usuario()
                meu_aplicativo.mudar_pagina('homepage')

            else:
                mensagem_erro=requisição_dict['error']['message']
                pagina_login.ids['mensagem_login'].text=mensagem_erro
                pagina_login.ids['mensagem_login'].color=(1,0,0,1)
            
        except requests.exceptions.ConnectionError:
            pagina_login.ids['mensagem_login'].text='SEM CONEXÃO DE INTERNET'
            pagina_login.ids['mensagem_login'].color=(1,0,0,1)


    def criar_conta(self,email,senha):
        try:
            meu_aplicativo=App.get_running_app()
            pagina_login=meu_aplicativo.root.ids['paginalogin']
            link=f'https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.API_KEY}'
            info={'email':email,
                'password':senha,
                'returnSecureToken':True}
            requisição=requests.post(link,data=info)
            requisição_dict=requisição.json()
        
            if requisição.ok:
                id_token=requisição_dict['idToken']
                local_id=requisição_dict['localId']
                refresh_token=requisição_dict['refreshToken']
                meu_aplicativo.id_token=id_token
                meu_aplicativo.local_id=local_id
                with open('refreshtoken.txt','w') as arquivo:
                    arquivo.write(refresh_token)
                req_id=requests.get(f'https://aplicativo-kung-fu-default-rtdb.firebaseio.com/ids.json?auth={id_token}')
                id_vendedor=req_id.json()
                link=f'https://aplicativo-kung-fu-default-rtdb.firebaseio.com/{local_id}.json?auth={id_token}'
                info_usuario={'foto':'foto1.png','equipe':'','total_vendas':'0','vendas':'','id_vendedor':f'{id_vendedor}'}
                requests.patch(link,data=json.dumps(info_usuario))
                id_vendedor+=1
                requests.patch(f'https://aplicativo-kung-fu-default-rtdb.firebaseio.com/.json?auth={id_token}', data=json.dumps({'ids':id_vendedor}))
                meu_aplicativo.carregar_infos_usuario()
                meu_aplicativo.mudar_pagina('homepage')

            else:
                mensagem_erro=requisição_dict['error']['message']
                pagina_login.ids['mensagem_login'].text=mensagem_erro
                pagina_login.ids['mensagem_login'].color=(1,0,0,1)

        except requests.exceptions.ConnectionError:
            pagina_login.ids['mensagem_login'].text='SEM CONEXÃO DE INTERNET'
            pagina_login.ids['mensagem_login'].color=(1,0,0,1)

    def trocar_token(self,refresh_token):
        link=f'https://securetoken.googleapis.com/v1/token?key={self.API_KEY}'
        info={'grant_type': 'refresh_token','refresh_token':refresh_token}
        requisição=requests.post(link,data=info)
        requisição_dict=requisição.json()
        local_id=requisição_dict['user_id']
        id_token=requisição_dict['id_token']
        return local_id,id_token
