-- Íntegra na origem: sem duplicação de carga, sem órfão.
select * from {{ source('raw', 'fat_nota_saida_item') }}
