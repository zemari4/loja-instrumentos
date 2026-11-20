# Redis (django-redis) como cache compartilhado do rate limit

## Status

accepted (issue #14, 2026-11-20). Decidido pelo dono do projeto.

## Decisão

1. O cache `default` passa a ser **Redis via `django-redis`** em todos os ambientes: desenvolvimento, testes, CI e produção. Quem roda o projeto precisa de um Redis (ver `README.md`).
2. A configuração vem de variáveis de ambiente: `CACHE_LOCATION` (URL do Redis) e `REDIS_PASSWORD`. **Produção não sobe sem `CACHE_LOCATION`.**
3. O rate limit de login e cadastro usa esse cache (`RATELIMIT_USE_CACHE = "default"`). Os silenciamentos de `django_ratelimit.E003` e `django_ratelimit.W001` são removidos. `security.W019` continua silenciado, porque `X_FRAME_OPTIONS = "SAMEORIGIN"` é uma escolha deliberada do projeto.
4. Os testes usam o banco 15 do Redis (`TEST_CACHE_LOCATION`) e limpam o cache antes de cada teste.

## Contexto

Os `@ratelimit` em `authentication/views.py` (login e cadastro) dependiam do `LocMemCache`, que não é compartilhado entre processos: com mais de um worker o contador não é confiável, e ele se perde a cada restart. O próprio `django-ratelimit` acusa isso (`E003`), mas o check estava silenciado.

O `django-ratelimit` só aceita oficialmente `PyMemcacheCache`, `PyLibMCCache` e `django_redis.cache.RedisCache`. Ele rejeita `DatabaseCache` e `FileBasedCache` com `E003` (sem incremento atômico), e o `RedisCache` nativo do Django passa no `E003`, mas gera `W001`.

Alternativas consideradas:

- **Memcached (`pymemcache`):** também suportado. Menos comum que Redis e sem outros usos previstos.
- **Limitador próprio sobre `LoginHistory`:** sem infraestrutura nova, mas troca a biblioteca por código nosso, não cobre o cadastro e transforma cada tentativa numa escrita no banco.
- **Adiar até decidir o deploy:** o risco continuaria aberto.

O dono escolheu Redis e decidiu exigi-lo também em desenvolvimento, aceitando o custo de todo ambiente precisar de um Redis, em troca de dev, CI e produção se comportarem do mesmo jeito.

## Consequência

- **Todo ambiente precisa de Redis**, inclusive a CI (serviço no workflow) e quem roda `pytest`. Sem Redis a suíte para cedo, com uma mensagem que explica como subir um (`docker run`).
- **Redis fora do ar:** os `POST` de login e cadastro devolvem **500** (verificado e fixado em `authentication/tests/test_rate_limit.py`). As páginas de leitura (home, catálogo, carrinho) continuam funcionando, porque a sessão é guardada no banco. O `django-ratelimit` falha "fechado" (`RATELIMIT_FAIL_OPEN` no padrão `False`), que é o modo seguro: falhar aberto deixaria o login sem limite de tentativas durante a queda. Se esse é o comportamento certo, ou se vale uma página 503, está na issue #46.
- **O allauth também usa esse cache** (`allauth/core/internal/ratelimit.py`) para os limites dele em `/accounts/`: eles passam a ser compartilhados, e também falham quando o Redis cai.
- **O host de deploy precisa oferecer Redis.** A decisão de deploy segue em aberto (ver `docs/adr/README.md`). Se o host escolhido não oferecer Redis, vale um novo ADR que substitui este.
- Dependências novas: `django-redis==7.0.0` e `redis==8.1.0`.
- As variáveis `DISABLE_CACHE` e `DISABLE_REDIS` não eram lidas por nenhum código e foram removidas, porque agora contradiriam a decisão.
- O Redis fica disponível para outros usos (por exemplo filas), sem decidir isso agora.

### Sinais para rever esta decisão

- O host de deploy escolhido não oferece Redis.
- Quedas do Redis passam a derrubar o login com frequência.
- Depender de um Redis para rodar a suíte vira um custo maior que o benefício.
