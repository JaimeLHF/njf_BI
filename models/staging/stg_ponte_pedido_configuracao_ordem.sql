-- Triplicada na origem (fator 3,00x). Único caminho pedido <-> ordem de
-- fabricação. Grão = pedido x configuração x ordem, as três colunas da tabela.
-- 1.024.551 linhas -> 341.517.
select * exclude (_rn)
from (
    select
        *,
        row_number() over (
            partition by id_pedido, id_configuracao, id_ordem_fabricacao
            order by id_pedido
        ) as _rn
    from {{ source('raw', 'ponte_pedido_configuracao_ordem') }}
)
where _rn = 1
