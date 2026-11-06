# Pulso da Operação

> Estudo de caso em SQL sobre fila de suporte e cumprimento de SLA.

**[Abra o relatório interativo](https://raphael-kaych.raphaelvindex.chatgpt.site/demos/pulso-operacao)** para comparar três horários de corte calculados com a consulta deste repositório.

[Estudo de caso e arquitetura](https://raphael-kaych.raphaelvindex.chatgpt.site/projetos/pulso-operacao)

Uma fila com muitos chamados nem sempre é a fila que pede atenção primeiro. Este laboratório usa uma amostra fictícia de 18 chamados. A consulta separa volume, prazos vencidos e cumprimento de SLA por área em um horário de corte.

| Área | Chamados | Abertos vencidos | Resolvidos no prazo |
| --- | ---: | ---: | ---: |
| ERP | 6 | 1 | 2 de 4 |
| Acessos | 6 | 0 | 5 de 5 |
| Infraestrutura | 4 | 1 | 2 de 3 |
| Integrações | 2 | 1 | Sem resoluções |

ERP e Acessos têm o mesmo volume. ERP concentra dois fechamentos fora do prazo e ainda tem um chamado vencido. Integrações tem só dois chamados, mas um deles já está vencido. A distribuição ajuda a decidir onde investigar primeiro.

## Arquitetura

O Python valida e importa a base CSV para SQLite. A consulta SQL aplica a referência de tempo e agrega a fila por área. O script gera HTML, e a demo seleciona resultados pré-calculados pela mesma consulta.

## Requisitos e execução

Com Python 3.10 ou superior, execute na pasta do projeto.

```text
python relatorio.py
python relatorio.py --referencia "2026-05-08 20:00" --saida outro-recorte.html
python -m unittest -v
```

O primeiro comando gera `docs/index.html`, que abre no navegador sem conexão. O segundo gera um recorte diferente. As regras de agregação ficam em [`indicadores.sql`](indicadores.sql), e os registros fictícios ficam em [`chamados.csv`](chamados.csv).

## Como ler os números

- A data de referência padrão é 8 de maio de 2026 às 18h UTC. Só entram chamados abertos até esse instante.
- O SLA usa resolvidos no prazo dividido pelo total resolvido até a referência. Um fechamento posterior conta como aberto no recorte anterior.
- Um chamado ainda aberto fica vencido após o prazo. O prazo exato ainda conta como atendimento dentro do SLA.

## Testes e limites

`python -m unittest -v` verifica o recorte padrão e um horário anterior ao primeiro chamado. O conjunto é fictício e o SLA usa tempo corrido em UTC. Uma evolução seria comparar cortes contínuos com filtros por área e uma base maior de teste.
