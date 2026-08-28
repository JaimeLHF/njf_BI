-- Triplicada na origem (fator 3,00x). Grão = item de NF x pedido de origem;
-- um item pode atender mais de um pedido, por isso a chave é o par.
-- 562.914 linhas -> 187.615.
select * exclude (_rn)
from (
    select
        *,
        row_number() over (
            partition by id_nota_saida_item, id_pedido
            order by id_nota_saida_item
        ) as _rn
    from {{ source('raw', 'fat_nota_saida_item_pedido') }}
)
where _rn = 1
