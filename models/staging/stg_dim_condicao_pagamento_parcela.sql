-- Íntegra na origem: sem duplicação de carga, sem órfão.
select * from {{ source('raw', 'dim_condicao_pagamento_parcela') }}
