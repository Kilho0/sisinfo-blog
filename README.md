# Arquivo Kilho: blog e portfólio em Django

Aplicação CRUD em Django feita para a segunda entrega de laboratório da disciplina de Sistemas de Informação da Poli-USP. O site é um blog e portfólio com posts, comentários e categorias, e não usa nenhuma extensão do Django.

## O que tem no site

| Página | URL | Nome da URL |
|---|---|---|
| Lista de posts | `/` | `post_list` |
| Post individual, com categorias e comentários | `/posts/<id>/` | `post_detail` |
| Novo post | `/posts/novo/` | `post_create` |
| Editar post | `/posts/<id>/editar/` | `post_update` |
| Confirmar remoção de post | `/posts/<id>/remover/` | `post_delete` |
| Novo comentário | `/posts/<id>/comentar/` | `comment_create` |
| Lista de categorias | `/categorias/` | `category_list` |
| Posts de uma categoria | `/categorias/<id>/` | `category_detail` |
| Entrar / sair | `/contas/login/`, `/contas/logout/` | `login`, `logout` |
| Administrador | `/admin/` | `admin:index` |

Qualquer pessoa pode ler os posts. Criar, editar e remover posts e comentar exige login. As contas são criadas pelo administrador do Django.

## Modelos

- `Post`: `title`, `content` (HTML, exibido com o filtro `safe`), `date` (`DateTimeField`) e `categories` (muitos para muitos com `Category`).
- `Comment`: `post`, `author` (referência a `settings.AUTH_USER_MODEL`), `text` e `date`. Os comentários aparecem do mais recente para o mais antigo.
- `Category`: `name` e `description`.

Os três modelos estão registrados no administrador.

## Histórico do repositório

O histórico segue as etapas do enunciado:

1. `Views v1`: views funcionais, sem Django forms e sem validação.
2. `Views v2`: views funcionais com `PostForm`.
3. `Views v3`: `ListView`, `DetailView`, `CreateView`, `UpdateView` e `DeleteView`.
4. Branch `comments`, com merge na `main`.
5. Branch `categories`, criada depois do merge anterior, também com merge na `main`.

Para ver cada versão do arquivo de views:

```bash
git log --oneline -- blog/views.py
git show <commit>:blog/views.py
```

## Como rodar localmente

```bash
python -m venv .venv
.venv\Scripts\activate          # no Linux ou macOS: source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata seed  # opcional: carrega posts, categorias e comentários de exemplo
python manage.py createsuperuser
python manage.py runserver
```

O site fica em http://127.0.0.1:8000 e o administrador em http://127.0.0.1:8000/admin/.

## Dados de exemplo e consultas SQL

A fixture `blog/fixtures/seed.json` cria 9 posts, 7 categorias e 17 comentários. Os comentários são de três usuários de teste, Fulano, Sicrano e Beltrano, que não têm senha utilizável.

| Post | Categorias | Comentários |
|---|---|---|
| Oficinas de Brinquedos | Oficinas, Educação | 3 |
| Oficina de Carrinhos de Rolimã | Oficinas | 2 |
| SEMOV | Eventos, Gestão estudantil | 0 |
| Dois anos de gestão no Centro Acadêmico | Gestão estudantil | 2 |
| Dormir mal na Poli (iniciação científica) | Pesquisa | 3 |
| Você é matutino, vespertino ou nem um nem outro? | Pesquisa | 0 |
| Filtro de Kalman na prática | Disciplinas, Programação | 2 |
| Fazendo o site do centro acadêmico | Programação, Gestão estudantil | 2 |
| Como este blog foi feito | Programação, Disciplinas | 3 |

As consultas da parte 4 estão em [`sql/consultas.sql`](sql/consultas.sql). O SQLite guarda as datas em UTC, por isso elas aparecem 3 horas à frente do horário de Brasília.

O arquivo `db.sqlite3` não entra no repositório. Ele é entregue à parte no Moodle.

## Deploy no Render

O arquivo `render.yaml` descreve o serviço. No Render, escolha **New > Blueprint**, conecte este repositório e preencha as variáveis pedidas:

| Variável | Para que serve |
|---|---|
| `DJANGO_SUPERUSER_USERNAME` e `DJANGO_SUPERUSER_PASSWORD` | Criam o superusuário a cada inicialização |
| `DJANGO_ALLOWED_HOSTS` | Domínios extras separados por vírgula, por exemplo um subdomínio próprio |

`DJANGO_SECRET_KEY` é gerada pelo próprio Render. O endereço `*.onrender.com` é liberado automaticamente.

O disco do plano gratuito é apagado a cada deploy ou reinício. Por isso o `start.sh` recria o banco e carrega a fixture toda vez que o serviço sobe. O que for criado pelo site no Render some no próximo reinício.

Os arquivos estáticos são servidos pela view `django.views.static.serve`, para não depender de pacotes externos.

### Domínio próprio

1. No Render, em **Settings > Custom Domains**, adicione o subdomínio.
2. No DNS do domínio, crie um registro `CNAME` apontando o subdomínio para o endereço `*.onrender.com` do serviço.
3. Inclua o subdomínio em `DJANGO_ALLOWED_HOSTS`.
