# Obter credenciais da AWS:
- Clique no seu usuário no canto superior direito
- Depois em **Security credentials**
- Role até **Access keys**
- Clique em **Create Access key**
- Selecione **Application running on an AWS compute service**
- Marque a caixa **I understand the above recommendation and want to proceed to create an access key.**
- Clique em **Next**

# Como executar:
## Praparação do ambiente:
Para executar o servidor é necessário ter as seguintes variáveis de ambiente configuradas:
- aws_access_key_id
- aws_secret_access_key
- CAPCOBOT_API_KEY
- OPENAI_API_KEY
> Obs.: essas variáveis da AWS podem ser obtidas no passo anterior

> Obs.2: a variável CAPCOBOT_API_KEY pode ser qualquer valor, desde que seja o mesmo inserido na chave 'key' no Postman

> Obs.3: verificar com o time qual chave OPENAI_API_KEY que estamos utilizando

Com as variáveis configuradas, abra o terminal, entre na pasta do projeto e crie o ambiente virtual:
```
python.exe -m venv .venv
```

em seguida ative o ambiente virtual:
```
.venv\Scripts\activate.bat
```

com o ambiente virtual criado, instale as dependências:
```
pip install -r requirements.txt
```

## Iniciar o servidor e realizar teste:
### Configuração de ambiente:
É possível armazenar os arquivos no S3, na pasta de desenvolvimento, ou localmente. Para isso é necessário ajusta a constante **STORAGE** no arquivo *src\capcobot_question_manager\config.py*, podendo escolher entre **'S3'** e **'LOCAL'**. 

Também é possível criar uma variável de ambiente com o mesmo nome para indicar o local padrão de armazenamento.

## Executanto aplicação:
Para iniciar o servidor execute o arquivo **application.py** ou execute o comando:
```
flask --app application run
```

Quando o servidor estiver sendo executado será exibido o endereço e a porta para fazer as requisições.
> Obs.: Quando executar o applicantion.py o servidor executará na porta 443: *http://127.0.0.1:443*

Para saber quais rotas estão disponíveis, utilize o comando:
```
flask --app application routes
```

## Configurar o Postman
### Get answer
**Rotas utilizadas para fazer as perguntas:** 
 - **Rota antiga:** http://{ip_do_servidor}:{porta_do_servigor}/generate_answer

    **Método:** POST

    Selecione **'Body'**, marque a opção **'raw'** e **JSON**.

    O conteúdo do JSON deve ter as seguintes chaves:
    - **key:** Chave cadastrada na variável de ambiente CAPCOBOT_API_KEY
    - **question:** Pergunta a ser respondida
    - **files:** Arquivo a ser analisado (opcional)
    - **role:** Perfil de quem está realizando a pergunta (opcional)

- **Rota atual:** http://{ip_do_servidor}:{porta_do_servigor}/api/v1/questions
    
    **Método:** POST

    Selecione **'Body'**, marque a opção **'form-data'**.

    As chaves devem ser:
    - **key:** Chave cadastrada na variável de ambiente CAPCOBOT_API_KEY
    - **question:** Pergunta a ser respondida
    - **files:** Arquivo a ser analisado (opcional)
    - **role:** Perfil de quem está realizando a pergunta (opcional)

### Get available files
**Rota utilizada para verificar arquivos disponíveis:**
 - **Rota antiga:** http://{ip_do_servidor}:{porta_do_servigor}/get_available_files

    **Método:** POST

    Selecione **'Body'**, marque a opção **'raw'** e **JSON**.

    O conteúdo do JSON deve ter a seguinte chave:
    - **key:** Chave cadastrada na variável de ambiente CAPCOBOT_API_KEY

 - **Rota atual:** http://{ip_do_servidor}:{porta_do_servigor}/api/v1/files
    
    **Método:** GET

    Selecione **'Body'**, marque a opção **'form-data'**.

    As chaves devem ser:
    - **key:** Chave cadastrada na variável de ambiente CAPCOBOT_API_KEY
    - **language:** De qual idioma os arquivos devem ser listados 
        > Obs.: para listar todos passar o parâmetro 'ALL'

### Upload file
**Rota utilizada para enviar arquivos:** 
 - **Rota antiga:** http://{ip_do_servidor}:{porta_do_servigor}/upload_file

 - **Rota atual:** http://{ip_do_servidor}:{porta_do_servigor}/api/v1/files
 
    **Método:** POST

    Selecione **'Body'**, marque a opção **'form-data'**.

    As chaves devem ser:
    - **key:** Chave cadastrada na variável de ambiente CAPCOBOT_API_KEY
    - **files:** Aqui é necessário alterar o tipo de dados para 'file' (aparece uma seta para baixo ao posicionar o mouse no campo 'Key') e em Value selecionar o arquivos a ser enviado
        > Obs.: Sistema aceita apenas PDF

### Delete file
**Rota utilizada para excluir arquivos:**
 - **Rota:** http://{ip_do_servidor}:{porta_do_servigor}/api/v1/files

    **Método:** DELETE

    Selecione **'Body'**, marque a opção **'form-data'**.

    As chaves devem ser:
    - **key:** Chave cadastrada na variável de ambiente CAPCOBOT_API_KEY
    - **language:** Idioma do arquivo que deseja excluir
    - **name:** Nome do arquivo que deseja excluir

    >Obs.: A exclusão não é imediada. Devido à complexidade é feita uma marcação no arquivo para que seja processado durante a noite.
    
    >Obs. 2: Para teste local é necessário criar um arquivo com nome 'exclude_flag.flg' na pasta 'data' e iniciar o processo do [BRSP-CAPCO-BOT-DOC-TAXONOMY](https://bitbucket.org/boldrocket/brsp-capco-bot-doc-taxonomy/src/master/)

# Deploy
O sistema é executado na AWS em uma EC2 e o gerenciamento é feito pelo Elastic Beanstalk.

Para fazer o deploy é necessário instalar e configurar o EB CLI

## Instalação do EB Cli
Documentação: https://github.com/aws/aws-elastic-beanstalk-cli-setup
> Obs.: A instalação **não** deve ser feita na pasta do projeto

> Obs.2: Por padrão o PowerShell é bloqueado para executar scripts. Melhor utilizar o *CMD*
 - Instalar pipx: https://pypi.org/project/pipx/
    ```
    python -m pip install --user pipx
    ```
    > Obs.: Se a instalação terminar com um WARNING, verifiar a solução na documentação da biblioteca
- Adicionar o pipx nas variáveis de ambiente
    ```
    python -m pipx ensurepath
    ```
- Reiniciar o terminal para recarregar as variáveis de ambiente
- Instalar virtualenv: https://pypi.org/project/virtualenv/
    ```
    pipx install virtualenv
    ```
- Clonar o repositório de instalação do Elastic Beanstalk cli:
    ```
    git clone https://github.com/aws/aws-elastic-beanstalk-cli-setup.git
    ```
- Instalar o EB CLI:
    ```
    python .\aws-elastic-beanstalk-cli-setup\scripts\ebcli_installer.py
    ```
    > Obs.: Se ocorrer o erro *"AttributeError: cython_sources"* siga os passos a seguir, sugeridos por IamAmitE (https://github.com/aws/aws-cli/issues/8036#issuecomment-1657305401):
        
    - Fixe o pyyaml=5.3.1
    - Remova as linhas **556** e **557** ( def_install_ebcli() ) no arquivo **ebcli_installer.py**
        ```
        '--upgrade'
        '--upgrade-strategy', 'eager',
        ```
    
            
- Adicionar os eb cli nas variáveis de ambiente:
    ```
    cmd.exe /c "C:\Users\{pasta_do_usuário}\.ebcli-virtual-env\executables\path_exporter.bat"
    ```
    > Obs.: Se estiver utilizando PowerShell o comando é um pouco diferente. Verifique a mensagem ao final da instalação.
- Feche e abra o CMD (ou a IDE) para atualizar as variáveis de ambiente
    > Obs.: Se a instalação foi feita com sucesso foi criado uma entrada *C:\Users\\{pasta_do_usuário}\\.ebcli-virtual-env\executables* na variável de ambiente do usuário PATH
    - Verifique se o EB CLI está instalado corretamente:
        ```
        eb --version
        ```

## Configuração do EB Cli
Para fazer o deploy é necessário ter os seguintes arquivos:
```
pasta .ebextensions:
    - cloudwath.config
    - environment.config
pasta .elasticbeanstalk:
    - config.yml
    - poc-vanilla-env.env.yml
```
> Obs.: Arquivos não versionados por conterem conteúdos sensíveis.

Para fazer o deploy execute o seguinte comado na raíz do projeto:
```
eb deploy
```

