{#
  Teste genérico: a combinação de colunas identifica a linha.
  Escrito à mão para não depender do dbt_utils (o projeto roda offline).

  Uso no schema.yml, no nível do modelo:
      tests:
        - chave_unica:
            colunas: [id_pedido, id_representante]
#}
{% test chave_unica(model, colunas) %}

select
    {{ colunas | join(', ') }},
    count(*) as n
from {{ model }}
group by {{ range(1, colunas | length + 1) | join(', ') }}
having count(*) > 1

{% endtest %}
