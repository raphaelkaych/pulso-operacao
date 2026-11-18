# Instruções para agentes

Estudo de caso em SQL sobre fila de suporte e SLA, parte do portfólio de Raphael Kaych. O [README](README.md) é a documentação vigente; o relatório interativo e o estudo de caso ficam no repositório [farol-de-integracoes](https://github.com/raphaelkaych/farol-de-integracoes) (`/demos/pulso-operacao` e `/projetos/pulso-operacao`).

## Comandos

Python 3.10 ou superior, só a biblioteca padrão.

```sh
python -m unittest -v
python relatorio.py
```

`python relatorio.py` regenera `docs/index.html` com a referência padrão de 8 de maio de 2026, 18h UTC. Com os dados atuais, o arquivo sai idêntico ao versionado.

## Regras

- As regras de agregação ficam em `indicadores.sql`; os registros fictícios, em `chamados.csv`.
- A demo do portfólio usa resultados pré-calculados (`lib/pulso-snapshots.json` no farol, gerado por `scripts/exportar-pulso.py`). Se a consulta ou a base mudar, atualize os dois repositórios juntos.
- Mantenha o SLA em tempo corrido e UTC, com o prazo exato contando como dentro do SLA, ou documente a mudança no README.
- Trabalhe em branch própria e abra PR para `main`.
