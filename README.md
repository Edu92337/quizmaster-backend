# QuizMaster Backend

Backend Flask para a plataforma QuizMaster - Sistema de questões interativas para ENEM e Residência Médica.

## Funcionalidades

- **Autenticação JWT**: Sistema completo de registro e login de usuários
- **Banco de Questões**: Questões sobre ENEM e Residência Médica
- **Geração de Questões via IA**: Criação personalizada de questões usando OpenAI
- **Chat com IA**: Assistente especializado em estudos
- **Calendário de Progresso**: Rastreamento de atividades diárias
- **Integração Stripe**: Sistema de assinatura mensal

## Tecnologias

- Python 3.11
- Flask
- PostgreSQL
- SQLAlchemy
- Flask-JWT-Extended
- OpenAI API
- Stripe API

## Configuração Local

### 1. Instalar Dependências

```bash
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/quizdb
JWT_SECRET_KEY=your-super-secret-jwt-key
STRIPE_SECRET_KEY=sk_test_YOUR_STRIPE_SECRET_KEY
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET
FRONTEND_URL=http://localhost:5173
OPENAI_API_KEY=your-openai-api-key
```

### 3. Inicializar o Banco de Dados

```bash
python seed.py
```

### 4. Executar o Servidor

```bash
python run.py
```

O servidor estará disponível em `http://localhost:5000`.

## Deploy no Render

### 1. Criar um Web Service

1. Acesse [Render Dashboard](https://dashboard.render.com/)
2. Clique em "New +" e selecione "Web Service"
3. Conecte seu repositório GitHub
4. Configure:
   - **Name**: quizmaster-backend
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app`

### 2. Criar um PostgreSQL Database

1. No Render Dashboard, clique em "New +" e selecione "PostgreSQL"
2. Configure:
   - **Name**: quizmaster-db
   - **Database**: quizdb
   - **User**: (gerado automaticamente)
3. Copie a **Internal Database URL**

### 3. Configurar Variáveis de Ambiente

No painel do Web Service, vá em "Environment" e adicione:

- `DATABASE_URL`: (Cole a Internal Database URL do PostgreSQL)
- `JWT_SECRET_KEY`: (Gere uma chave secreta forte)
- `STRIPE_SECRET_KEY`: (Sua chave do Stripe)
- `STRIPE_WEBHOOK_SECRET`: (Seu webhook secret do Stripe)
- `FRONTEND_URL`: (URL do seu frontend na Vercel)
- `OPENAI_API_KEY`: (Sua chave da OpenAI)

### 4. Adicionar gunicorn ao requirements.txt

Certifique-se de que `gunicorn` está no arquivo `requirements.txt`:

```
gunicorn==21.2.0
```

### 5. Deploy

O Render fará o deploy automaticamente após o commit. Acesse a URL fornecida pelo Render para testar.

## Endpoints da API

### Autenticação
- `POST /auth/register` - Registrar novo usuário
- `POST /auth/login` - Login de usuário

### Questões
- `GET /questions` - Listar questões
- `POST /questions/generate` - Gerar questões via IA
- `POST /questions/<id>/answer` - Responder questão

### Progresso
- `GET /progress/<user_id>` - Obter progresso do usuário

### IA
- `POST /ai/chat` - Conversar com IA especializada

### Assinatura
- `POST /subscription/create-checkout-session` - Criar sessão de checkout
- `POST /subscription/webhook` - Webhook do Stripe

## Licença

MIT

