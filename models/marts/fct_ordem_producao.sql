{{ config(materialized='table') }}

-- Grão: uma ordem de fabricação.
--
-- O ponto desta tabela é `data_conclusao_real`. As colunas de data da ordem não
-- servem para medir prazo: `data_fim` é anterior ao último apontamento em 98,7%
-- das ordens encerradas, com mediana de -43 dias — ela é planejamento, não
-- realizado (docs/qualidade.md, seção 7). A conclusão real vem do chão de
-- fábrica: o último apontamento de produção da ordem, via roteiro.
--
-- Por isso `atraso_dias` e `no_prazo` comparam data_prevista_fim com
-- data_conclusao_real, nunca com data_fim. Quem quiser reproduzir o número
-- ingênuo tem `atraso_dias_por_data_fim` ao lado, para a diferença ficar
-- visível em vez de virar discussão.

with ordem as (
    select * from {{ ref('stg_fat_ordem_fabricacao') }}
),

roteiro as (
    select * from {{ ref('stg_fat_ordem_roteiro') }}
),

movimento as (
    select * from {{ ref('stg_fat_ordem_movimento') }}
),

item_ordem as (
    select * from {{ ref('stg_dim_item_ordem') }}
),

catalogo as (
    select * from {{ ref('stg_dim_item') }}
),

-- roteiro agregado por ordem: quantas operações e quanto tempo foi planejado.
-- tempo_realizado do roteiro é ignorado de propósito: está preenchido em 2.894
-- de 3,7M linhas.
roteiro_agg as (
    select
        id_ordem_fabricacao,
        count(*)                     as qtd_operacoes,
        count(distinct id_operacao)  as qtd_operacoes_distintas,
        sum(tempo_previsto)          as tempo_previsto_total,
        sum(tempo_setup)             as tempo_setup_total
    from roteiro
    group by 1
),

-- apontamento agregado por ordem: é daqui que sai o prazo real
apontamento_agg as (
    select
        roteiro.id_ordem_fabricacao,
        min(movimento.data_apontamento) as data_primeiro_apontamento,
        max(movimento.data_apontamento) as data_conclusao_real,
        count(*)                        as qtd_apontamentos,
        sum(movimento.tempo_apontado)   as tempo_apontado_total,
        sum(movimento.quantidade)       as quantidade_apontada
    from movimento
    inner join roteiro
        on roteiro.id_ordem_roteiro = movimento.id_ordem_roteiro
    group by 1
)

select
    -- chave
    ordem.id_ordem_fabricacao,
    ordem.num_ordem,
    ordem.id_empresa,

    -- produto
    ordem.id_item_ordem,
    item_ordem.id_item as id_item_global,
    catalogo.cod_item,
    item_ordem.peso,

    -- classificação da ordem
    ordem.tipo_ordem,
    ordem.origem_ordem,
    ordem.cod_prioridade,
    ordem.cod_linha_producao,

    -- situação: as duas leituras, porque significam coisas diferentes e a
    -- empresa ainda não confirmou qual define "em aberto"
    ordem.cod_situacao,
    ordem.cod_situacao = 1  as situacao_ativa,
    ordem.flag_encerrada = 1 as encerrada_administrativamente,

    -- datas de planejamento, como estão na origem
    ordem.data_abertura,
    ordem.data_prevista_fim,
    ordem.data_inicio,
    ordem.data_fim,
    ordem.data_entrega,

    -- datas reais, derivadas do apontamento
    apontamento_agg.data_primeiro_apontamento,
    apontamento_agg.data_conclusao_real,

    -- prazo: sempre contra a conclusão real
    -- Dois lead times, porque data_abertura não é o começo do processo:
    -- 24,7% das ordens têm o primeiro apontamento ANTES da abertura, e
    -- data_inicio é anterior à abertura em 41%. A abertura parece ser um
    -- registro administrativo posterior. Use lead_time_producao_dias para
    -- tempo de chão de fábrica; lead_time_dias só onde a abertura fizer sentido
    -- (ver apontamento_antes_da_abertura).
    date_diff(
        'day', ordem.data_abertura, apontamento_agg.data_conclusao_real
    ) as lead_time_dias,
    date_diff(
        'day', apontamento_agg.data_primeiro_apontamento,
        apontamento_agg.data_conclusao_real
    ) as lead_time_producao_dias,
    apontamento_agg.data_primeiro_apontamento < ordem.data_abertura
        as apontamento_antes_da_abertura,
    date_diff(
        'day', ordem.data_prevista_fim, apontamento_agg.data_conclusao_real
    ) as atraso_dias,
    case
        when apontamento_agg.data_conclusao_real is null then null
        when ordem.data_prevista_fim is null then null
        else apontamento_agg.data_conclusao_real <= ordem.data_prevista_fim
    end as no_prazo,

    -- o número ingênuo, ao lado, para a diferença ficar explícita
    date_diff('day', ordem.data_prevista_fim, ordem.data_fim)
        as atraso_dias_por_data_fim,

    -- quantidades da ordem
    ordem.quantidade_prevista,
    ordem.quantidade_produzida,
    ordem.quantidade_cancelada,
    -- quantidade_refugada NÃO entra como medida: é maior que a produzida em
    -- 54.439 de 54.494 ordens, semântica não confirmada (qualidade.md, seção 8).
    ordem.quantidade_refugada as quantidade_refugada_nao_confiavel,

    -- roteiro e apontamento
    roteiro_agg.qtd_operacoes,
    roteiro_agg.qtd_operacoes_distintas,
    roteiro_agg.tempo_previsto_total,
    roteiro_agg.tempo_setup_total,
    apontamento_agg.qtd_apontamentos,
    apontamento_agg.tempo_apontado_total,
    apontamento_agg.quantidade_apontada,

    -- previsto x realizado, só onde os dois existem
    case
        when coalesce(roteiro_agg.tempo_previsto_total, 0) > 0
        then apontamento_agg.tempo_apontado_total
             / roteiro_agg.tempo_previsto_total
    end as razao_tempo_realizado_previsto,

    apontamento_agg.id_ordem_fabricacao is not null as tem_apontamento

from ordem
left join roteiro_agg     on roteiro_agg.id_ordem_fabricacao
                             = ordem.id_ordem_fabricacao
left join apontamento_agg on apontamento_agg.id_ordem_fabricacao
                             = ordem.id_ordem_fabricacao
left join item_ordem      on item_ordem.id_item_ordem = ordem.id_item_ordem
left join catalogo        on catalogo.id_item = item_ordem.id_item
