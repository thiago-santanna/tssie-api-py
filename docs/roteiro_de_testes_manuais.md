# TSSie v2.1.0 - Roteiro de Testes Manuais (E2E)

> Este documento é vivo e acompanha a evolução das Sprints. O objetivo é que você (o usuário final ou QA) siga os testes de caixa preta com seu celular real e valide o comportamento orquestrado do banco de dados (Supabase) + API + Evolution.

---

## 🟢 Cenário 1: O Primeiro Contato (Caminho Feliz - Sprint 3)
**Objetivo:** Validar se a infraestrutura detecta uma nova mensagem, extrai os blocos das tabelas relativas e devolve o "Beep-Boop!" com segurança.

1. **Ação:** Envie uma mensagem do seu WhatsApp pessoal (ex: `"Oi, tem parabrisa pro Gol?"`) para o número cadastrado no seu ZAP da instância `TSSieDev`.
2. **Reação Esperada no WhatsApp:** O TSSie deve responder imediatamente com: `"Beep-Boop! Olá [Seu Nome]! O TSSie reconheceu seu número..."`.
3. **Auditoria no Postman / Banco de Dados (Supabase):**
   - Vá na tabela `inbound_events`. Verifique se a sua mensagem `"Oi, tem parabrisa..."` foi salva e se o `processing_status` está mudado de `PENDING` para `PROCESSED`.
   - Vá na tabela `contacts`. Verifique se seu número foi salvo lá como `LEAD`.
   - Vá na tabela `sessions`. Verifique se foi criada uma linha com `status` = `ACTIVE` atrelando você ao `TSSieDev` e last_seen_at atualizado.
   - Vá em `outbound_events`. Verifique se o disparo do "Beep-Boop" foi salvo lá como `SENT` e se pegou o `http_status` 201 da Evolution API.

---

## 🟡 Cenário 2: Defesa Contra Loop Conversacional (Sprint 3)
**Objetivo:** Certificar de que o webhook não fique jogando *ping-pong* com o bot após enviar o "Beep-Boop". Mensagens cujo dono for o próprio robô ou broadcast precisam ser mortas no ninho.

1. **Ação:** Siga o Cenário 1 e deixe a mensagem automática ser enviada para sua tela. Note que, ao ser enviada, a Evolution API fará o disparo de um NOVO webhook para nós onde a chave `fromMe` será `true`.
2. **Reação Esperada no WhatsApp:** 
   - A resposta "Beep-Boop!" chega pra você. 
   - O BOT do TSSie silencia instantaneamente. Ele NÃO PODE enviar um segundo "Beep-Boop!" confirmando que leu a própria resposta.
3. **Auditoria de Logs (Terminal ou Banco):**
   - Olhe o terminal do backend (`docker logs tssie_backend`), você deve ver nos bastidores a função de pipeline rejeitando esse webhook de "eu mesmo", caindo no `return {"status": "ignored", "reason": "invalid remote_jid or from_me"}`.
   - Na tabela `inbound_events` a mensagem enviada pelo próprio bot **não deve ser gravada** como processada.

---

## 🟡 Cenário 3: Defesa Contra Tenant (Instância) Desconhecida
**Objetivo:** E se hackearem a API de webhook ou mandarem um nome de instância que ainda não foi cadastrado no banco? O sistema precisa bloquear.

1. **Ação:** Abra o Postman importado e use a request chamada `Simular Webhook (Instância Falsa)`. Ela manda um JSON com `instance: "BoletoHackDev"`. Envie o Post.
2. **Reação API:** 
   - Status Code 200 pro webhook da evolution descansar (sempre), mas...
3. **Auditoria de Logs:**
   - No terminal `docker logs tssie_backend` tem que ser gerado um aviso `WARNING: Tenant for instance key 'BoletoHackDev' not discovered in db`.
   - Nenhuma linha adicional pode aparecer em `contacts` ou `sessions`. A barreira principal de domínimos fechou a porta para não "sujar" o banco de dados e misturar tickets.

---
*Fim do roteiro da Sprint 3. Novos cenários complexos (State Machine e LLM) entrarão aqui em breve!*
