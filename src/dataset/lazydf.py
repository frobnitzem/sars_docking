import multiprocessing
import pandas as pd
import pyarrow.parquet as parquet

def load_and_run(args):
    f, fname, read_args, read_kws = args
    df = pd.read_parquet(fname, *read_args, **read_kws)
    ans = f(df)
    del df
    return ans

class LazyDataFrame:
    """ A Lazy DataFrame does not keep large parquet files
        in memory.  Instead, it loads the data from disk
        every time it is called.
    """
    min_cache_size = 10*1024*1024 # 10 M
    def __init__(self, fname, *read_args, **read_kws):
        self.fname = fname
        self.read_args = read_args
        self.read_kws = read_kws

        pq = parquet.ParquetFile(fname)
        self.pq = pq
        # size in bytes
        self.sz = pq.metadata.num_rows*pq.metadata.serialized_size
        self.rows = pq.metadata.num_rows

        self.cleanup = False # delete self.df on __exit__
        if self.sz >= self.min_cache_size:
            self.cleanup = True
        self.df = None

    def __call__(self, f):
        return multiprocessing.Pool(1).map(load_and_run, \
                [(f, self.fname, self.read_args, self.read_kws)])[0]

    def load(self):
        if self.df is None:
            self.df = pd.read_parquet(self.fname, *self.read_args, **self.read_kws)
            # note: pyarrow.parquet.read_pandas would work,
            # but closes the file after read succeeds.
        return self.df

    def __len__(self):
        return self.rows

    # Note: using LazyDataFrame as a context manager
    # in this way still throws OOM on common use cases
    # since it doesn't release all the memory.
    #
    # with ldf as df:
    #   ans = do_something(df)
    def __enter__(self):
        # ensure loaded
        return self.load()

    def __exit__(self, exception_type, exception_value, traceback):
        if self.cleanup:
            del self.df
            self.df = None
        return None

