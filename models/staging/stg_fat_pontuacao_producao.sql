-- Triplicada na origem (fator 3,00x exato). ATENÇÃO à chave.
--
-- id_pontuacao NÃO identifica o registro, apesar do COMMENT dizer "chave
-- interna do registro": são 40.423 valores para 101.146 linhas distintas
-- (7,5x sobre o bruto). Um único id_pontuacao carrega 3.318 linhas distintas,
-- cobrindo 880 itens, 678 datas, 3 empresas e 4 tipos de ordem. É um id de
-- lote/apuração, não de linha.
--
-- Não existe chave natural nas colunas descritivas. A menor combinação que
-- fecha em 101.146 é id_pontuacao + id_item + data_referencia +
-- cod_faixa_pontuacao + quantidade — e quantidade é MEDIDA, não chave.
-- Sem ela sobram 92.204: 8.942 linhas legítimas seriam colapsadas.
-- A razão pontuacao/quantidade varia dentro do grupo em 2.618 de 4.173 casos,
-- ou seja as linhas não são réplicas proporcionais: são registros distintos.
--
-- Conclusão: a única dedup defensável é por LINHA INTEIRA, que remove
-- exatamente a triplicação (fator 3,00 confirmado). Particionamos por todas as
-- colunas explicitamente, em vez de DISTINCT, para o critério ficar legível.
-- Definir o grão real exige confirmar com o ERP o que é id_pontuacao.
--
-- 303.444 linhas -> 101.146.
select * exclude (_rn)
from (
    select
        *,
        row_number() over (
            partition by
                id_pontuacao, id_empresa, id_item, quantidade, pontuacao,
                tipo_ordem, pontos, data_referencia, cod_faixa_pontuacao
            order by id_pontuacao
        ) as _rn
    from {{ source('raw', 'fat_pontuacao_producao') }}
)
where _rn = 1
