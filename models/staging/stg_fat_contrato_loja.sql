-- Triplicada na origem (fator 3,00x). Chave natural: id_contrato.
-- 31.875 linhas -> 10.625. A chave fecha exatamente com o dedup de linha
-- inteira, então nenhuma linha legítima é perdida.
select * exclude (_rn)
from (
    select
        *,
        row_number() over (partition by id_contrato order by id_contrato) as _rn
    from {{ source('raw', 'fat_contrato_loja') }}
)
where _rn = 1
