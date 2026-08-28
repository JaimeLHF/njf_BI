-- Triplicada na origem, mas o fator aparente é 3,817x. Investigado: NÃO há
-- duplicidade extra nos dados úteis. O excedente e os "22% de órfãos" são o
-- mesmo fenômeno, uma linha só:
--
--   8.850 das 40.206 linhas (22,0%) têm id_nota_saida_item = 0, um valor
--   sentinela que não existe em fat_nota_saida_item. Todos os 70 pares que
--   aparecem mais de 3x são desse sentinela (até 384x na origem). Fora dele,
--   a repetição é uniformemente 3x e os órfãos são zero.
--
-- Por isso o sentinela é descartado aqui: um vínculo a um item de NF
-- inexistente não se junta a nada e reapareceria como órfão em todo relatório.
-- O rastro fica em raw.ponte_nota_saida_item_servico e em docs/qualidade.md.
--
-- 40.206 linhas -> 10.452 pares úteis (10.534 menos os 82 do sentinela).
select * exclude (_rn)
from (
    select
        *,
        row_number() over (
            partition by id_nota_saida_item, id_servico
            order by id_nota_saida_item
        ) as _rn
    from {{ source('raw', 'ponte_nota_saida_item_servico') }}
    where id_nota_saida_item <> 0
)
where _rn = 1
