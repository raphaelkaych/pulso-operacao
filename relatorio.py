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
        proporcao = area["no_prazo"] / area["resolvidos"] if area["resolvidos"] else 0
        linhas.append(
            f"<tr><th scope='row'>{escape(area['area'])}</th><td>{area['total']}</td>"
            f"<td>{area['resolvidos']}</td><td>{area['abertos']}</td>"
            f"<td class='atraso' data-vencidos='{area['vencidos']}'>{area['vencidos']}</td>"
            f"<td class='sla'><span>{sla}</span><i aria-hidden='true' style='--v:{proporcao:.2f}'></i></td></tr>"
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
  :root {{ color-scheme: dark; --fundo: #05070d; --superficie: #080f20; --navy: #102444; --azul: #377ffb; --acento: #75a9ff;
    --texto: #f1f6ff; --suave: #a9bad2; --linha: #1b2c47; --ok: #82dcb9; --alerta: #ffb481; }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; color: var(--texto); background: var(--fundo); font: 1rem/1.6 "Segoe UI", system-ui, sans-serif; }}
  header {{ padding: 3.5rem 1.25rem 2.5rem; border-bottom: 1px solid var(--linha);
    background: radial-gradient(ellipse at 85% 0%, #377ffb33, transparent 60%), linear-gradient(180deg, #071022, var(--fundo)); }}
  .wrap {{ max-width: 980px; margin: auto; }}
  .rotulo {{ display: flex; align-items: center; gap: .6rem; color: var(--suave); font-size: .95rem; }}
  .rotulo::before {{ content: ""; width: 2rem; height: 2px; border-radius: 2px; background: var(--azul); }}
  h1 {{ margin: .6rem 0 .4rem; font-size: clamp(2.4rem, 7vw, 4.2rem); font-weight: 650; line-height: 1; letter-spacing: -.05em; }}
  header p {{ margin: 0; color: var(--suave); }}
  main {{ padding: 2rem 1.25rem 3.5rem; }}
  .numeros {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); margin: 0 0 2.5rem; border-top: 1px solid var(--linha); }}
  .numero {{ padding: 1rem 1rem 0 0; color: var(--suave); }}
  .numero + .numero {{ padding-left: 1rem; border-left: 1px solid var(--linha); }}
  .numero strong {{ display: block; color: var(--texto); font-size: 2.6rem; font-weight: 650; line-height: 1.1; letter-spacing: -.04em; font-variant-numeric: tabular-nums; }}
  h2 {{ font-size: 1.4rem; font-weight: 620; letter-spacing: -.02em; margin: 0 0 .9rem; }}
  .tabela {{ overflow-x: auto; border: 1px solid #2b4469; border-radius: 14px; background: var(--superficie); }}
  .tabela:focus-visible {{ outline: 2px solid var(--acento); outline-offset: 3px; }}
  table {{ border-collapse: collapse; width: 100%; min-width: 560px; font-variant-numeric: tabular-nums; }}
  td, th {{ text-align: right; padding: .8rem 1rem; border-bottom: 1px solid var(--linha); }}
  tbody tr:last-child > * {{ border-bottom: 0; }}
  th:first-child {{ text-align: left; }}
  thead th {{ color: var(--suave); font-size: .85rem; font-weight: 560; background: #0a1529; }}
  tbody th {{ font-weight: 600; }}
  .atraso {{ color: var(--suave); }}
  .atraso:not([data-vencidos="0"]) {{ color: var(--alerta); font-weight: 700; }}
  .sla {{ min-width: 9rem; }}
  .sla span {{ display: inline-block; min-width: 3ch; }}
  .sla i {{ display: block; height: 4px; margin-top: .35rem; border-radius: 2px;
    background: linear-gradient(90deg, var(--ok) calc(var(--v) * 100%), var(--linha) 0); }}
  .nota {{ max-width: 68ch; margin-top: 1.1rem; color: var(--suave); font-size: .95rem; }}
</style>
<header><div class="wrap">
  <div class="rotulo">Laboratório de análise, dados fictícios</div>
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
