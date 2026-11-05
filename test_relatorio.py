import unittest

from relatorio import RAIZ, REFERENCIA, calcular, renderizar


class RelatorioTest(unittest.TestCase):
    def test_indicadores_no_recorte(self):
        areas = calcular(RAIZ / "chamados.csv", REFERENCIA)
        self.assertEqual(sum(area["total"] for area in areas), 18)
        self.assertEqual(sum(area["vencidos"] for area in areas), 3)
        self.assertEqual(sum(area["resolvidos"] for area in areas), 12)
        por_area = {area["area"]: area for area in areas}
        self.assertEqual(por_area["ERP"]["no_prazo"], 2)
        self.assertEqual(por_area["Integrações"]["resolvidos"], 0)
        self.assertIn("75%", renderizar(areas, REFERENCIA))

    def test_recorte_anterior_ao_primeiro_chamado(self):
        referencia = "2026-05-04 07:59"
        areas = calcular(RAIZ / "chamados.csv", referencia)
        self.assertEqual(areas, [])
        self.assertIn("Nenhum chamado", renderizar(areas, referencia))


if __name__ == "__main__":
    unittest.main()
