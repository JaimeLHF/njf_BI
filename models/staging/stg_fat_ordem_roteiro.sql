-- Íntegra na origem: sem duplicação de carga, sem órfão.
select * from {{ source('raw', 'fat_ordem_roteiro') }}
