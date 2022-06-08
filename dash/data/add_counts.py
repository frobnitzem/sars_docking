import pandas as pd

def get_tors(x : str) -> int:
    return x.count('\nBRANCH')

def get_atoms(x : str) -> int:
    return x.count('\nATOM')

def main(argv):
    df = pd.read_parquet(argv[1])
    print(f"Operating on {argv[1]}")
    mod = False
    if 'atoms' not in df.columns:
        mod = True
        df['atoms'] = df['conf'].map(get_atoms)
    if 'tors' not in df.columns:
        mod = True
        df['tors'] = df['conf'].map(get_tors)

    if mod:
        print("Writing modified result.")
        df.to_parquet(argv[1])

if __name__=="__main__":
    import sys
    main(sys.argv)
