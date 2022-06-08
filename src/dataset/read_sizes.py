import sys
from pathlib import Path
from lazydf import LazyDataFrame

base = Path(sys.argv[1])

for name in ['AD', 'rf3', 'ADrf3', 'v2rf3', 'v2AD']:
    df = LazyDataFrame(base / f'{name}.out.pq')
    print(f"{name} {len(df)}")
