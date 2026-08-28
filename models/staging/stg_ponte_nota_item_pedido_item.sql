-- Triplicada na origem (fator 3,023x). O excedente sobre 3x é duplicidade
-- legítima da origem: o mesmo par item-de-pedido / item-de-NF pode ter mais de
-- um vínculo, com cod_referencia e data_vinculo diferentes.
-- A chave natural são as quatro colunas: com id_pedido_item + id_nota_saida_item
-- apenas, 1.744 vínculos distintos seriam colapsados.
-- 652.017 linhas -> 215.658.
select * exclude (_rn)
from (
    select
        *,
        row_number() over (
            partition by
                id_pedido_item, id_nota_saida_item, cod_referencia, data_vinculo
            order by id_pedido_item
        ) as _rn
    from {{ source('raw', 'ponte_nota_item_pedido_item') }}
)
where _rn = 1
