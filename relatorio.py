import argparse
import csv
import sqlite3
from contextlib import closing
from datetime import datetime
from html import escape
from pathlib import Path


RAIZ = Path(__file__).resolve().parent
FORMATO = "%Y-%m-%d %H:%M"
REFERENCIA = "2026-05-08 18:00"


def data_iso(valor):
    return datetime.strptime(valor, FORMATO).strftime(FORMATO)


def calcular(arquivo, referencia):
    with closing(sqlite3.connect(":memory:")) as banco:
        banco.row_factory = sqlite3.Row
        banco.execute("""
            CREATE TABLE chamado (
                id INTEGER PRIMARY KEY, area TEXT NOT NULL, aberto_em TEXT NOT NULL,
                prazo_em TEXT NOT NULL CHECK (prazo_em >= aberto_em),
                fechado_em TEXT CHECK (fechado_em >= aberto_em)
            )
        """)
        with arquivo.open(encoding="utf-8-sig", newline="") as entrada, banco:
            for linha in csv.DictReader(entrada):
                banco.execute("INSERT INTO chamado VALUES (?, ?, ?, ?, ?)", (
                    int(linha["id"]), linha["area"], data_iso(linha["aberto_em"]),
                    data_iso(linha["prazo_em"]), data_iso(linha["fechado_em"]) if linha["fechado_em"] else None,
                ))
        consulta = (RAIZ / "indicadores.sql").read_text(encoding="utf-8")
        return banco.execute(consulta, {"referencia": data_iso(referencia)}).fetchall()


def percentual(parte, total):
    return f"{parte / total:.0%}" if total else "—"


def renderizar(areas, referencia):
    linhas = []
    for area in areas:
        sla = percentual(area["no_prazo"], area["resolvidos"])
        linhas.append(
            f"<tr><th scope='row'>{escape(area['area'])}</th><td>{area['total']}</td>"
            f"<td>{area['resolvidos']}</td><td>{area['abertos']}</td>"
            f"<td class='atraso'>{area['vencidos']}</td><td>{sla}</td></tr>"
        )
    corpo = "\n".join(linhas) or "<tr><td colspan='6'>Nenhum chamado neste recorte.</td></tr>"
    total = sum(area["total"] for area in areas)
    vencidos = sum(area["vencidos"] for area in areas)
    resolvidos = sum(area["resolvidos"] for area in areas)
    no_prazo = sum(area["no_prazo"] for area in areas)
    data = datetime.strptime(referencia, FORMATO).strftime("%d/%m/%Y às %H:%M")
    return f"""<!doctype html>
<html lang="pt-BR">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pulso da Operação</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; color: #1b3533; background: #f7f3eb; font: 1rem/1.55 system-ui, sans-serif; }}
  header {{ background: #102a2b; color: #fcf5e8; padding: 3.25rem 1.5rem 4rem; }}
  .wrap {{ max-width: 960px; margin: auto; }}
  .rotulo {{ color: #e9b976; font-size: .78rem; font-weight: bold; letter-spacing: .14em; }}
  h1 {{ margin: .4rem 0; font: bold clamp(2.4rem, 6vw, 4.5rem)/1.08 Georgia, serif; }}
  header p {{ margin: .5rem 0 0; }}
  main {{ padding: 0 1.5rem 3rem; }}
  .numeros {{ margin: -1.5rem 0 2rem; display: grid; grid-template-columns: repeat(auto-fit, minmax(145px, 1fr)); gap: .75rem; }}
  .numero {{ background: #fffdf8; border: 1px solid #d9dfd5; border-radius: .6rem; padding: .8rem 1rem; }}
  .numero strong {{ display: block; font-size: 2rem; line-height: 1.2; }}
  .tabela {{ overflow-x: auto; border: 1px solid #d9dfd5; border-radius: .6rem; background: #fffdf8; }}
  table {{ border-collapse: collapse; width: 100%; font-variant-numeric: tabular-nums; }}
  td, th {{ text-align: right; padding: .75rem; border-bottom: 1px solid #e2e6de; }}
  th:first-child {{ text-align: left; }}
  thead {{ background: #e7efe7; }}
  .atraso {{ color: #8a3827; font-weight: 700; }}
  .nota {{ max-width: 68ch; }}
</style>
<header><div class="wrap">
  <div class="rotulo">LABORATÓRIO DE ANÁLISE / DADOS FICTÍCIOS</div>
  <h1>Pulso da Operação</h1>
  <p>Fila e cumprimento de prazo em {data}, UTC.</p>
</div></header>
<main><div class="wrap">
  <section class="numeros" aria-label="Indicadores gerais">
    <div class="numero"><strong>{total}</strong>Chamados no recorte</div>
    <div class="numero"><strong>{vencidos}</strong>Abertos com prazo vencido</div>
    <div class="numero"><strong>{percentual(no_prazo, resolvidos)}</strong>Resolvidos no prazo</div>
  </section>
  <h2 id="areas">Chamados por área</h2>
  <div class="tabela" tabindex="0" role="region" aria-labelledby="areas"><table aria-labelledby="areas">
    <thead><tr><th scope="col">Área</th><th scope="col">Total</th><th scope="col">Resolvidos</th>
      <th scope="col">Abertos</th><th scope="col">Vencidos</th><th scope="col">Dentro do SLA</th></tr></thead>
    <tbody>{corpo}</tbody>
  </table></div>
  <p class="nota">O percentual de SLA usa apenas os chamados resolvidos até o horário do recorte. Chamados ainda abertos aparecem separadamente na fila. O travessão indica que a área não teve resoluções no recorte.</p>
</div></main>
</html>
"""


def main():
    parser = argparse.ArgumentParser(description="Gera um relatório HTML a partir do CSV e da consulta SQL.")
    parser.add_argument("--entrada", type=Path, default=RAIZ / "chamados.csv")
    parser.add_argument("--referencia", default=REFERENCIA, help="Data UTC no formato AAAA-MM-DD HH:MM")
    parser.add_argument("--saida", type=Path, default=RAIZ / "docs" / "index.html")
    args = parser.parse_args()
    try:
        areas = calcular(args.entrada, args.referencia)
        relatorio = renderizar(areas, args.referencia)
        args.saida.parent.mkdir(parents=True, exist_ok=True)
        args.saida.write_text(relatorio, encoding="utf-8", newline="\n")
    except (OSError, ValueError, KeyError, sqlite3.Error) as erro:
        parser.exit(1, f"Erro: {erro}\n")
    print(f"Relatório gerado em {args.saida}")


if __name__ == "__main__":
    main()
