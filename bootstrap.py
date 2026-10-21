#!/usr/bin/env python

import sys
import logging

from pathlib import Path
from astroquery.vizier import Vizier
from astroquery.utils import TableList

logger = logging.getLogger(__name__)


def fetch(catalogs: str | list[str], columns: list[str], *args, **kwargs) -> TableList:
    vizier = Vizier(*args, columns=columns, **kwargs)
    tables = vizier.get_catalogs(catalogs)
    if len(tables) == 0:
        raise LookupError(f'VizieR returned no tables for {catalogs}!')

    return tables


def save(tables: TableList, overwrite: bool = False, **kwargs) -> None:
    # TODO: write a tmp file and replace.
    for table in tables:
        try:
            name = table.meta['name'].split('/')[-1]
        except (KeyError, AttributeError):
            logger.warning('Missing table name!')
            continue

        path = Path(f'./tables/{name}.parquet')
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and not overwrite:
            logger.warning(f'{path} already exists. {name} skipped.')
            continue

        table.to_pandas().to_parquet(path, index=False, **kwargs)
        logger.info(f'Wrote {len(table)} rows to {path}')


def main() -> None:
    catalogs = [
            'J/A+A/686/A42/clusters',
            'J/A+A/686/A42/members',
            'J/MNRAS/508/3877/maincat'
            ]

    failures = []

    for catalog in catalogs:
        logger.info(f'Fetching {catalog}')
        try:
            tables = fetch(catalog, ['*'], row_limit=-1)
        except Exception as exc:
            logger.error(exc)
            failures.append(catalog)
            continue

        try:
            save(tables)
        except Exception as exc:
            logger.error(exc)
            failures.append(catalog)
            continue

    if failures:
        sys.exit(f'{len(failures)}/{len(catalogs)} catalogs failed: {", ".join(failures)}')
    else:
        logger.info(f'{len(catalogs)} catalogs saved successfully or already exist.')
        sys.exit(0)

if __name__ == '__main__':

    logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%H:%M:%S'
            )
    try:
        main()
    except KeyboardInterrupt:
        sys.exit('Interrupted!')
