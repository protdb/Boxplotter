import pandas as pd
import io
import gzip
import base64

test_df = pd.read_csv('/home/gluck/sh3_barrels.csv')

def encode_to_transfer(df: pd.DataFrame) -> str:
    buff = io.BytesIO()
    df.to_pickle(buff)
    return base64.b64encode(gzip.compress(buff.getvalue())).decode()


def decode_from_transfer(encoded: str) -> pd.DataFrame:
    pickled = gzip.decompress(base64.b64decode(encoded))
    buff = io.BytesIO(initial_bytes=pickled)
    return pd.read_pickle(buff)


encoded = encode_to_transfer(test_df)
decoded = decode_from_transfer(encoded)

print(decoded)