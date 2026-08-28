{{ config(materialized='table') }}

-- Grão: um item de pedido de venda.
--
-- O ponto desta tabela é a carteira em aberto. Ela NÃO usa
-- `fat_pedido_item.quantidade_saldo`: essa coluna não é baixada no faturamento
-- e 96,6% dos itens com saldo positivo já foram faturados
-- (docs/qualidade.md, seção 7). A coluna original fica ao lado, renomeada,
-- para a diferença ficar visível.
--
-- Carteira = quantidade do item, menos o cancelado, menos o efetivamente
-- faturado via ponte deduplicada.
--
-- ATENÇÃO À CARTEIRA: `origem_pedido` muda tudo. 'SIM' são 176.559 itens e
-- R$ 2,6 bilhões com **0,0% de conversão em nota fiscal** — nenhum item dessa
-- origem virou NF em cinco anos, e ela está quase perfeitamente correlacionada
-- com situacao_pedido = 'PE' e status_liberacao = 'BLQ'. 'PDV' é o fluxo que
-- realmente fatura (75,9% dos itens). Somar carteira sem separar por origem dá
-- R$ 2,8 bi em aberto contra R$ 1,3 bi faturados em todo o período, o que não
-- se sustenta.
--
-- O mart NÃO filtra: expõe `origem_pedido` e a flag
-- `origem_converte_em_nf` para a decisão ficar visível na query. O que 'SIM'
-- significa é pergunta aberta para a empresa (docs/qualidade.md, seção 8).
--
-- Ressalva de cardinalidade: a ponte é praticamente 1:1 no sentido NF -> pedido
-- (187.594 dos 187.615 itens de NF atendem um único item de pedido; 21 atendem
-- 2 ou 3). Somar a quantidade do item de NF por item de pedido superestima
-- nesses 21 casos — 0,01%, aceito conscientemente. No sentido inverso o 1:N é
-- normal e esperado: 16.790 itens de pedido são atendidos por mais de uma nota,
-- que é exatamente o caso de entrega parcial.

with pedido as (
    select * from {{ ref('stg_fat_pedido') }}
),

item as (
    select * from {{ ref('stg_fat_pedido_item') }}
),

ponte as (
    select * from {{ ref('stg_ponte_nota_item_pedido_item') }}
),

nota_item as (
    select * from {{ ref('stg_fat_nota_saida_item') }}
),

nota as (
    select * from {{ ref('stg_fat_nota_saida') }}
),

tipo as (
    select * from {{ ref('stg_dim_tipo_nf_saida') }}
),

estabelecimento as (
    select * from {{ ref('stg_dim_estabelecimento') }}
),

cliente as (
    select * from {{ ref('stg_dim_cliente') }}
),

item_empresa as (
    select * from {{ ref('stg_dim_item_empresa') }}
),

-- taxa de conversão observada por origem, calculada do próprio dado em vez de
-- chumbada: se a empresa corrigir a carga, a flag acompanha.
conversao_origem as (
    select
        pedido.origem_pedido,
        count(*) filter (
            where exists (
                select 1 from ponte
                where ponte.id_pedido_item = item.id_pedido_item
                  and ponte.id_nota_saida_item is not null
            )
        ) * 1.0 / count(*) as taxa_conversao
    from item
    inner join pedido on pedido.id_pedido = item.id_pedido
    group by 1
),

-- o que cada item de pedido efetivamente virou nota.
-- Só notas que geram financeiro contam como faturamento: remessa e
-- bonificação não baixam carteira.
faturado as (
    select
        ponte.id_pedido_item,
        sum(nota_item.quantidade)                as quantidade_faturada,
        sum(nota_item.valor_liquido)             as valor_faturado,
        count(distinct nota_item.id_nota_saida)  as qtd_notas,
        min(nota.data_emissao)                   as data_primeiro_faturamento,
        max(nota.data_emissao)                   as data_ultimo_faturamento
    from ponte
    inner join nota_item
        on nota_item.id_nota_saida_item = ponte.id_nota_saida_item
    inner join nota
        on nota.id_nota_saida = nota_item.id_nota_saida
    inner join tipo
        on tipo.id_tipo_nf_saida = nota_item.id_tipo_nf_saida
    where ponte.id_nota_saida_item is not null
      and tipo.flag_gera_financeiro = 1
      and lower(tipo.descricao_tipo_nf) not like '%devolu%'
    group by 1
),

base as (
    select
        -- chave
        item.id_pedido_item,
        item.id_pedido,
        item.num_item,
        pedido.num_pedido,

        -- datas do pedido
        pedido.data_emissao,
        pedido.data_inclusao,
        pedido.data_entrega_prevista,

        -- situação
        pedido.situacao_pedido,
        pedido.status_liberacao,
        pedido.cod_situacao_detalhe,
        pedido.origem_pedido,

        -- origem: separa o que vira nota do que nunca virou
        conversao_origem.taxa_conversao as taxa_conversao_da_origem,
        conversao_origem.taxa_conversao > 0.01 as origem_converte_em_nf,

        -- empresa e canal
        pedido.id_empresa,
        pedido.id_empresa_faturamento,
        pedido.id_representante,
        pedido.id_condicao_pagamento,
        pedido.id_tipo_nf_saida,

        -- cliente: só se alcança pelo estabelecimento
        pedido.id_estabelecimento,
        estabelecimento.id_cliente,
        cliente.canal_venda,
        cliente.tipo_cliente,

        -- produto
        item.id_item_empresa,
        item_empresa.cod_item,
        item_empresa.cod_familia,

        -- medidas do pedido
        item.quantidade,
        item.quantidade_cancelada,
        item.valor_unitario,
        item.valor_unitario_liquido,
        item.percentual_desconto,
        item.quantidade * item.valor_unitario_liquido as valor_item_liquido,

        -- a coluna que não serve, mantida com o nome corrigido
        item.quantidade_saldo as quantidade_saldo_origem_nao_confiavel,

        -- faturamento
        coalesce(faturado.quantidade_faturada, 0) as quantidade_faturada,
        coalesce(faturado.valor_faturado, 0)      as valor_faturado,
        coalesce(faturado.qtd_notas, 0)           as qtd_notas,
        faturado.data_primeiro_faturamento,
        faturado.data_ultimo_faturamento

    from item
    inner join pedido           on pedido.id_pedido = item.id_pedido
    left  join conversao_origem on conversao_origem.origem_pedido
                                   = pedido.origem_pedido
    left  join faturado        on faturado.id_pedido_item = item.id_pedido_item
    left  join estabelecimento on estabelecimento.id_estabelecimento
                                  = pedido.id_estabelecimento
    left  join cliente         on cliente.id_cliente = estabelecimento.id_cliente
    left  join item_empresa    on item_empresa.id_item_empresa
                                  = item.id_item_empresa
)

select
    base.*,

    -- carteira: nunca negativa. Onde o faturado passa do pedido menos o
    -- cancelado, a sobra é zero e o excedente fica visível em
    -- quantidade_faturada_acima_do_pedido.
    greatest(
        base.quantidade - coalesce(base.quantidade_cancelada, 0)
            - base.quantidade_faturada,
        0
    ) as quantidade_em_aberto,

    greatest(
        base.quantidade - coalesce(base.quantidade_cancelada, 0)
            - base.quantidade_faturada,
        0
    ) * base.valor_unitario_liquido as valor_em_aberto,

    greatest(
        base.quantidade_faturada
            - (base.quantidade - coalesce(base.quantidade_cancelada, 0)),
        0
    ) as quantidade_faturada_acima_do_pedido,

    -- status do item
    case
        when base.situacao_pedido = 'C' then 'cancelado'
        when base.quantidade_faturada = 0 then 'nao faturado'
        when base.quantidade_faturada
             >= base.quantidade - coalesce(base.quantidade_cancelada, 0)
            then 'faturado total'
        else 'faturado parcial'
    end as status_faturamento,

    -- tempo entre a venda e a primeira nota
    date_diff('day', base.data_emissao, base.data_primeiro_faturamento)
        as dias_ate_primeiro_faturamento,

    -- atraso contra a entrega prometida ao cliente
    date_diff(
        'day', base.data_entrega_prevista, base.data_primeiro_faturamento
    ) as dias_vs_entrega_prevista,

    base.data_primeiro_faturamento is not null as tem_faturamento

from base
