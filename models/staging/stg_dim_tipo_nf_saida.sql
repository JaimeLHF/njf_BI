-- Íntegra na origem: sem duplicação de carga, sem órfão.
select * from {{ source('raw', 'dim_tipo_nf_saida') }}
