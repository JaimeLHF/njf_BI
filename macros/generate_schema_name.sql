{#
  Sem esta macro o dbt cria `main_staging`. Aqui o schema custom vira o nome
  literal: os modelos de staging vivem em `staging`, ao lado de `raw`.
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
