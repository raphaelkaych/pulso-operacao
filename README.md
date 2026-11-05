# Pulso da Operação

> Estudo de caso em SQL sobre fila de suporte e cumprimento de SLA.

Uma fila com muitos chamados nem sempre é a fila que pede atenção primeiro. Este laboratório usa uma amostra fictícia de 18 chamados. A consulta separa volume, prazos vencidos e cumprimento de SLA por área em um horário de corte.

| Área | Chamados | Abertos vencidos | Resolvidos no prazo |
| --- | ---: | ---: | ---: |
| ERP | 6 | 1 | 2 de 4 |
| Acessos | 6 | 0 | 5 de 5 |
| Infraestrutura | 4 | 1 | 2 de 3 |
| Integrações | 2 | 1 | Sem resoluções |

ERP e Acessos têm o mesmo volume. ERP concentra dois fechamentos fora do prazo e ainda tem um chamado vencido. Integrações tem só dois chamados, mas um deles já está vencido. A distribuição ajuda a decidir onde investigar primeiro.

## Reproduza a análise

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
