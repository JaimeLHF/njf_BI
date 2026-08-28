{{ config(materialized='table') }}

-- Grão: um item de nota fiscal de saída.
--
-- Não filtra nada. `dim_tipo_nf_saida` tem 412 tipos e só 158 geram
-- financeiro: somar tudo mistura remessa, bonificação e devolução com venda.
-- Em vez de escolher pelo consumidor, o filtro fica exposto em
-- `gera_financeiro`, `movimenta_estoque` e `eh_devolucao` — a decisão é de
-- quem consulta, e fica visível na query.
--
-- O pedido de origem NÃO entra aqui: um item de NF pode atender mais de um
-- pedido, e trazer o vínculo multiplicaria o valor. Use
-- stg_ponte_nota_item_pedido_item quando precisar do elo.

with item as (
    select * from {{ ref('stg_fat_nota_saida_item') }}
),

nota as (
    select * from {{ ref('stg_fat_nota_saida') }}
),

tipo as (
    select * from {{ ref('stg_dim_tipo_nf_saida') }}
),

cliente as (
    select * from {{ ref('stg_dim_cliente') }}
),

estabelecimento as (
    select * from {{ ref('stg_dim_estabelecimento') }}
),

item_empresa as (
    select * from {{ ref('stg_dim_item_empresa') }}
),

catalogo as (
    select * from {{ ref('stg_dim_item') }}
)

select
    -- chave
    item.id_nota_saida_item,
    item.id_nota_saida,
    item.num_item,

    -- datas
    nota.data_emissao,
    nota.data_saida,

    -- empresa e canal
    nota.id_empresa,
    nota.id_representante,
    nota.id_estabelecimento,
    estabelecimento.id_cidade,

    -- cliente
    nota.id_cliente,
    cliente.canal_venda,
    cliente.tipo_cliente,

    -- produto: as duas visões, porque os ids são diferentes
    item.id_item                  as id_item_global,
    item.id_item_empresa,
    catalogo.cod_item,
    item_empresa.cod_familia,

    -- natureza da operação, exposta para o consumidor filtrar
    item.id_tipo_nf_saida,
    tipo.cod_tipo_nf_saida,
    tipo.descricao_tipo_nf,
    tipo.flag_gera_financeiro = 1   as gera_financeiro,
    tipo.flag_movimenta_estoque = 1 as movimenta_estoque,
    -- heurística de texto: 59 dos 412 tipos trazem "devolu" na descrição.
    -- Frágil de propósito e sinalizado como tal — a lista definitiva de CFOPs
    -- de devolução precisa vir da fiscal (docs/qualidade.md, seção 8).
    lower(tipo.descricao_tipo_nf) like '%devolu%' as eh_devolucao_heuristica,

    -- situação da nota
    nota.situacao_nota,

    -- medidas
    item.quantidade,
    item.valor_bruto,
    item.valor_desconto,
    item.valor_ipi,
    item.valor_icms,
    item.valor_liquido

from item
inner join nota            on nota.id_nota_saida = item.id_nota_saida
left  join tipo            on tipo.id_tipo_nf_saida = item.id_tipo_nf_saida
left  join cliente         on cliente.id_cliente = nota.id_cliente
left  join estabelecimento on estabelecimento.id_estabelecimento
                              = nota.id_estabelecimento
left  join item_empresa    on item_empresa.id_item_empresa = item.id_item_empresa
left  join catalogo        on catalogo.id_item = item.id_item
