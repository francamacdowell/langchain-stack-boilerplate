# Justificativa de Uso da API Anthropic (Claude)
**Projeto:** LangChain Stack Boilerplate — Infraestrutura Interna de Agentes de IA  
**Data:** Maio de 2026 
**Responsável:** França Mac Dowell

---

## 1. Resumo Executivo

Este documento justifica o custo de uso da API da Anthropic (modelo Claude) no contexto do projeto interno **LangChain Stack Boilerplate**. O projeto consiste em uma base de infraestrutura reutilizável para construção de agentes de inteligência artificial, um ativo estratégico que reduz significativamente o tempo de entrega em projetos futuros com IA para clientes. O investimento na API é proporcional ao uso real (modelo pay-per-use), sem custo fixo de licença, e o retorno se materializa na forma de velocidade de entrega, padronização técnica e posicionamento competitivo da consultoria no mercado de IA, vale salientar que o será baixo e exclusivamente para desenvolvimento local.

---

## 2. Visão Geral do Projeto

### O que é

O **LangChain Stack Boilerplate** é uma base de código de produção para construção de agentes conversacionais inteligentes. Ele encapsula as melhores práticas de orquestração de LLMs (Large Language Models) em uma estrutura pronta para uso, eliminando o trabalho repetitivo de configuração que hoje acontece do zero a cada novo projeto de IA.

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

## 3. Por que Anthropic e o Modelo Claude

### Escolha técnica

O modelo configurado é o **Claude Sonnet 4.6**, da família Claude, o ponto de equilíbrio entre capacidade de raciocínio e custo dentro do portfólio atual da Anthropic. Suas características principais relevantes para este projeto:

- **Contexto longo:** até 200.000 tokens por requisição — essencial para processar documentos extensos
- **Uso de ferramentas (tool use):** suporte nativo a funções externas, sem workarounds
- **Instrução e seguimento de regras:** Claude é consistentemente avaliado como superior em precisão de seguimento de instruções complexas

### Flexibilidade de troca

A arquitetura usa `init_chat_model` do LangChain, o que significa que **trocar de modelo é uma mudança de uma linha de configuração** — sem reescrita de código. Gemini (Google) e modelos OpenAI são alternativas imediatas caso haja necessidade de mudança de provedor.

### Perfil adequado para clientes enterprise

O Claude tem política clara de **não usar dados de clientes para treinar modelos**, o que é um requisito frequente em contratos com clientes corporativos. Isso remove fricção comercial.

---

## 4. Valor para a Cheesecake Labs

### 4.1 Velocidade de entrega

Sem este boilerplate, cada novo projeto de IA na Cheesecake começa do zero: escolha de stack, configuração de LLM, implementação de memória, criação de API, testes de streaming. Com o boilerplate, **esse trabalho inicial cai de semanas para dias ou horas**.

Em uma consultoria, tempo é diretamente margem. Reduzir o tempo de setup libera horas faturáveis para a entrega real de valor ao cliente.

### 4.2 Padronização técnica

Com uma base comum, todos os engenheiros da Cheesecake que trabalham com IA usam os mesmos padrões: mesmos frameworks, mesmas abstrações, mesmas convenções. Isso reduz:

- Custo de onboarding em projetos de IA
- Tempo de revisão de código
- Risco de decisões técnicas inconsistentes entre projetos

### 4.3 Posicionamento comercial

A Cheesecake pode demonstrar infraestrutura real de IA em conversas de venda — não apenas apresentações conceituais. Um agente funcional, com API e streaming, é um diferencial tangível frente a concorrentes que ainda estão na fase de prova de conceito.

### 4.4 Multiplicador de receita

Um único investimento interno habilita cobrança em múltiplos projetos de clientes. O boilerplate é um ativo reutilizável — o custo de criação é diluído a cada novo projeto que o utiliza como base.

### 4.5 Desenvolvimento de time

Os engenheiros aprendem padrões de IA de produção (agentes, ferramentas, memória, streaming) em tempo interno — não às custas do orçamento ou da timeline de um cliente.

---

## 5. Justificativa de Custo

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

## 6. Anexo Técnico

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
