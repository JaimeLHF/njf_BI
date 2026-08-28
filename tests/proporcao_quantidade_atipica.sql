{{ config(severity='warn') }}

-- Defeito conhecido da origem, documentado em docs/qualidade.md seção 11, sem
-- correção possível na fonte. Não quebra o build: avisa se a proporção saltar,
-- o que indicaria mudança na carga ou um novo lote de digitação errada.
--
-- Limiar: 0,1% dos itens. A linha de base é 0,04% (155 de 379.754), então há
-- folga de mais que o dobro antes do aviso disparar.

select
    count(*)                                          as itens_atipicos,
    count(*) * 100.0 / (select count(*) from {{ ref('fct_pedido') }})
                                                      as pct_atipicos,
    0.1                                               as limiar_pct
from {{ ref('fct_pedido') }}
where not valor_pedido_plausivel
having count(*) * 100.0 / (select count(*) from {{ ref('fct_pedido') }}) > 0.1
