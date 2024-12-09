from pathlib import Path


def get_sql(path: Path) -> str:
    with open(path, 'r') as file:
        return file.read()

CONSULTA_SQL = get_sql(Path('sql/SELECT_DATA.sql'))
