-- Triplicada na origem (fator 3,00x). Chave natural: id_contrato_parcela.
-- 107.970 linhas -> 35.990.
select * exclude (_rn)
from (
    select
        *,
        row_number() over (
            partition by id_contrato_parcela order by id_contrato_parcela
        ) as _rn
    from {{ source('raw', 'fat_contrato_loja_parcela') }}
)
where _rn = 1
