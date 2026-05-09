# Justificativa de Uso da API Anthropic (Claude)

**Projeto:** LangChain Stack Boilerplate — Infraestrutura Interna de Agentes de IA
**Responsável:** França Mac Dowell

---
# 1. Resumo Executivo

## O que é o projeto

O LangChain Stack Boilerplate é uma base de código para construção de agentes conversacionais com LLMs. Entrega um agente capaz de raciocinar e usar ferramentas externas, memória e uma API REST. Se necessário, trocar de provedor (Gemini, OpenAI) é uma mudança de uma linha utilizando essa arquitetura e framework.

## Como será realizado

O stack é Python 3.12 + DeepAgents + LangChain/LangGraph + FastAPI, com `uv` como gerenciador de pacotes. O custo da API é pay-per-use (cobrança por token, sem mensalidade) e nesta fase se restringe a desenvolvimento local com repositório no GitHub: chamadas em volume baixo e controlado, limitadas a testes e exploração técnica.

## Benefícios para a Cheesecake Labs

Cada novo projeto de IA na Cheesecake hoje começa do zero: configuração de LLM, memória, API e streaming. Com o boilerplate, esse setup vai de vários dias para horas, tempo que volta a ser horas faturáveis na entrega ao cliente. Engenheiros aprendem padrões de IA de produção em tempo interno, não no orçamento do cliente, e times distintos passam a usar as mesmas convenções, reduzindo onboarding e revisão entre projetos. Em conversas comerciais, a Cheesecake passa a demonstrar infraestrutura de IA funcional, agente, API e streaming, em vez de apresentações conceituais.

# 2. Visão Geral do Projeto

### O que entrega hoje

| Componente | Descrição |
|---|---|
| **Agente conversacional** | Capaz de raciocinar, usar ferramentas externas e responder perguntas complexas |
| **Memória de sessão** | Mantém contexto entre turnos da conversa via LangGraph checkpointers |
| **API REST** | Endpoints prontos para integração com qualquer frontend ou sistema externo |
| **Streaming de respostas** | Respostas em tempo real via Server-Sent Events (SSE), como ChatGPT |
| **Suporte a ferramentas** | O agente pode buscar dados externos, processar documentos e invocar APIs |

### Endpoints disponíveis

```
GET  /health        → verificação de saúde do serviço
POST /chat          → conversa síncrona (request/response completo)
POST /chat/stream   → conversa com streaming em tempo real
```

### Roadmap planejado

- [ ] **Observabilidade com Langfuse** — rastreamento de tokens, latência e custo por requisição
- [ ] **Interface de usuário (UI)** — frontend para demonstração e testes internos
- [ ] **Estrutura de deployment configurada** — pipeline de implantação em ambiente cloud

---

# 3. Por que Anthropic e o Modelo Claude

### Escolha técnica

O modelo configurado é o **Claude Sonnet 4.6**, da família Claude, o ponto de equilíbrio entre capacidade de raciocínio e custo dentro do portfólio atual da Anthropic. Suas características principais relevantes para este projeto:

- **Contexto longo:** até 200.000 tokens por requisição — essencial para processar documentos extensos
- **Uso de ferramentas (tool use):** suporte nativo a funções externas, sem workarounds
- **Instrução e seguimento de regras:** Claude é consistentemente avaliado como superior em precisão de seguimento de instruções complexas

### Perfil adequado para clientes enterprise

O Claude tem política clara de **não usar dados de clientes para treinar modelos**, o que é um requisito frequente em contratos com clientes corporativos. Isso remove fricção comercial.

---

# 4. Justificativa de Custo

### Modelo de cobrança

A API da Anthropic é **pay-per-use**: cobrança por token processado (entrada + saída), sem mensalidade fixa ou custo de assento. Não há custo quando o sistema não está sendo usado.

### Custo em fase de R&D

Durante o desenvolvimento interno do boilerplate, o volume de chamadas à API é baixo e controlado — limitado a testes de funcionalidade e exploração técnica. O custo nesta fase é marginal.

Com a integração planejada do **Langfuse** (observabilidade), será possível rastrear exatamente:
- Tokens consumidos por requisição
- Custo por sessão de usuário
- Latência média por modelo

Isso elimina surpresas no faturamento e permite ajuste fino de parâmetros (temperatura, max_tokens) para otimização de custo.

---

## 5. Anexo Técnico

### Stack completo

| Camada | Tecnologia | Versão mínima |
|---|---|---|
| Linguagem | Python | 3.12 |
| Framework de agentes | DeepAgents | 0.5.7 |
| Orquestração | LangChain + LangGraph | 1.2.17 / 0.4.25 |
| API web | FastAPI + Uvicorn | 0.136.1 |
| Modelo de IA | Claude Sonnet 4.6 (Anthropic) | — |
| Gerenciador de pacotes | uv | — |
| Observabilidade (roadmap) | Langfuse | — |

### Arquitetura simplificada

```
Cliente (frontend / script)
        │
        ▼
   FastAPI (api.py)
        │
        ▼
  LangGraph StateGraph
        │
        ▼
  DeepAgents (create_deep_agent)
        │
        ▼
  Claude Sonnet 4.6 ←→ Ferramentas externas (fetch_text_from_url, etc.)
```

### Configuração do modelo (agent.py)

```python
model = init_chat_model(
    "claude-sonnet-4-6",
    temperature=0.5,
    timeout=600,
    max_tokens=25000,
    streaming=True,
)
```

### Comandos principais

```bash
uv run python main.py      # executa o agente em modo script
uv run uvicorn api:app     # sobe a API REST
uv run langgraph dev       # ambiente de desenvolvimento com UI do LangGraph
```

---