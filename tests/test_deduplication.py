from sales_yuler.domain.sales.deduplication import build_dedup_key, filter_new_rows


def test_build_dedup_key_matches_equivalent_rows_from_sheet_and_pipeline():
    incoming_row = {
        "fecha": "06/05/2026",
        "fuente": "ventas_mayo",
        "documento": "Ventas Mayo",
        "hoja": "06",
        "hora": "9:05 pm",
        "descripcion": "Anillo",
        "monto": 50.0,
        "cliente": "Maria",
    }
    existing_row = {
        "fecha": "06/05/2026",
        "fuente": "ventas_mayo",
        "documento": "Ventas Mayo",
        "hoja": "06",
        "hora": "21:05:00",
        "descripcion": "Anillo",
        "monto": "S/.50,00",
        "cliente": "MARIA",
    }

    assert build_dedup_key(incoming_row) == build_dedup_key(existing_row)


def test_filter_new_rows_skips_existing_and_repeated_rows():
    existing_rows = [
        {
            "fecha": "06/05/2026",
            "fuente": "ventas_mayo",
            "documento": "Ventas Mayo",
            "hoja": "06",
            "hora": "21:05:00",
            "descripcion": "Anillo",
            "monto": "50.00",
            "cliente": "MARIA",
        }
    ]
    incoming_rows = [
        {
            "fecha": "06/05/2026",
            "fuente": "ventas_mayo",
            "documento": "Ventas Mayo",
            "hoja": "06",
            "hora": "9:05 pm",
            "descripcion": "Anillo",
            "monto": 50.0,
            "cliente": "Maria",
        },
        {
            "fecha": "06/05/2026",
            "fuente": "ventas_mayo",
            "documento": "Ventas Mayo",
            "hoja": "06",
            "hora": "10:00",
            "descripcion": "Pulsera",
            "monto": 80.0,
            "cliente": "Luisa",
        },
        {
            "fecha": "06/05/2026",
            "fuente": "ventas_mayo",
            "documento": "Ventas Mayo",
            "hoja": "06",
            "hora": "10:00:00",
            "descripcion": "Pulsera",
            "monto": "80.00",
            "cliente": "LUISA",
        },
    ]

    filtered_rows, duplicates_skipped = filter_new_rows(incoming_rows, existing_rows)

    assert duplicates_skipped == 2
    assert len(filtered_rows) == 1
    assert filtered_rows[0]["descripcion"] == "Pulsera"
