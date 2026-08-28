-- Triplicada na origem (fator 3,00x exato). Mesmo problema de chave da
-- stg_fat_pontuacao_producao.
--
-- (id_nota_saida_item, id_ordem_fabricacao) colapsaria 223.373 linhas
-- distintas; acrescentar cod_faixa_pontuacao ainda colapsa 67.277. Só fecha em
-- 372.118 incluindo `pontuacao`, que é medida. Ou seja: o mesmo item de NF e a
-- mesma ordem aparecem com pontuações diferentes, e nada nas colunas
-- descritivas separa esses registros.
--
-- Dedup por linha inteira, portanto. 1.116.354 linhas -> 372.118.
--
-- Lembrete de junção: id_ordem_fabricacao guarda num_ordem, não a PK da ordem
-- (100% de órfãos contra id_ordem_fabricacao, 0% contra num_ordem).
select * exclude (_rn)
from (
    select
        *,
        row_number() over (
            partition by
                id_ordem_fabricacao, id_nota_saida_item, id_nota_saida,
                pontuacao, cod_faixa_pontuacao
            order by id_nota_saida_item
        ) as _rn
    from {{ source('raw', 'fat_nota_saida_item_pontuacao') }}
)
where _rn = 1
