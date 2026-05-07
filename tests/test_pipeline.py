from sales_yuler.application.pipeline import assign_record_ids
from sales_yuler.domain.schema import OUTPUT_COLUMNS


def test_assign_record_ids_adds_consecutive_id_without_changing_source_nro():
    rows = [
        {"nro": "1", "descripcion": "Anillo"},
        {"nro": "2", "descripcion": "Pulsera"},
        {"nro": "1", "descripcion": "Cadena"},
    ]

    assign_record_ids(rows)

    assert OUTPUT_COLUMNS[:2] == ["id registro", "nro"]
    assert [row["id registro"] for row in rows] == [1, 2, 3]
    assert [row["nro"] for row in rows] == ["1", "2", "1"]
