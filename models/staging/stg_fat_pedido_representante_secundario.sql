-- Triplicada na origem (fator 3,00x). Grão = pedido x representante
-- (rateio de comissão). 2.880 linhas -> 960.
-- Somar valor de pedido por esta tabela duplica faturamento mesmo depois
-- do dedup: ela é intencionalmente 1:N com o pedido.
select * exclude (_rn)
from (
    select
        *,
        row_number() over (
            partition by id_pedido, id_representante order by id_pedido
        ) as _rn
    from {{ source('raw', 'fat_pedido_representante_secundario') }}
)
where _rn = 1
