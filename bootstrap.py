#!/usr/bin/env python

import sys
import logging

from pathlib import Path
from astroquery.vizier import Vizier
from astroquery.utils import TableList


logger = logging.getLogger(__name__)

def fetch(catalogs: str, columns: list[str], *args, **kwargs) -> TableList:
    vizier = Vizier(*args, columns=columns, **kwargs)
    tables = vizier.get_catalogs(catalogs)
    if len(tables) == 0:
        raise LookupError(f'VizieR return no tables for {catalogs}!')

    return tables

def save(tables: TableList, overwrite: bool = False, *args, **kwargs) -> None:
    for table in tables:
         name = table.meta['name'].split('/')[-1]
         path = Path(f'{name}.parquet')
         if path.exists() and not overwrite:
             logger.info(f'{path} aleardy exists.')

         table.to_pandas().to_parquet(path, index=False)
         logger.info(f'wrote {len(table)} rows to {path}')

    return None


def main() -> None:
    catalogs = [
            'J/A+A/686/A42/clusters',
            'J/A+A/686/A42/members',
            'J/MNRAS/508/3877/maincat'
            ]

    for catalog in catalogs:
        logging.info(f'Fetching {catalog}')
        tables = fetch(catalog, ['*'], row_limit=5)
        save(tables)

    return None


if __name__ == '__main__':

    logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt="%H:%M:%S"
            )
    try:
        main()
    except KeyboardInterrupt:
        sys.exit('Interrupted!')
