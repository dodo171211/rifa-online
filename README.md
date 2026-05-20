# Rifa online

Site da rifa (números 1–700) com reserva no banco de dados.

## Arquivos do projeto

| Arquivo | Função |
|---------|--------|
| `app.py` | Servidor (site + API) |
| `rifa_db.py` | Banco SQLite |
| `index.html` | Página da rifa |
| `schema.sql` | Estrutura das tabelas |
| `render.yaml` | Configuração deploy Render |
| `Procfile` | Comando de start na nuvem |
| `requirements.txt` | Dependências Python |

## Colocar na internet (Render + GitHub)

### 1. GitHub

1. Crie um repositório em [github.com](https://github.com) (ex: `rifa-online`).
2. Envie **todos os arquivos desta pasta**, exceto `rifa.db`.

### 2. Render

1. Conta em [render.com](https://render.com) → login com GitHub.
2. **New +** → **Web Service** → escolha o repositório.
3. Configuração:

| Campo | Valor |
|--------|--------|
| Build Command | `pip install -r requirements.txt && python init_db.py` |
| Start Command | `gunicorn app:app --bind 0.0.0.0:$PORT` |
| Plano | Free |

4. **Create Web Service** → aguarde ficar **Live**.

Link final: `https://seu-app.onrender.com` — compartilhe no WhatsApp.

### Observações (plano grátis)

- Primeira visita após parado pode demorar ~30–50 s.
- Reinício do servidor pode apagar compras novas; para rifa grande use plano pago ou PythonAnywhere.

## API

- `GET /api/estatisticas` — números reservados
- `POST /api/reservar` — `{ nome, telefone, email, numeros: [1,2,3] }`
- `GET /api/compras` — lista de compradores
