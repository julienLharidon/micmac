import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


def save_to_parquet(data, path):
    """Save tie-points or metadata to Parquet for cloud-native access."""
    table = pa.Table.from_pandas(pd.DataFrame(data))
    pq.write_table(table, path)

def load_from_parquet(path):
    return pq.read_table(path).to_pandas()

class LegacyGateway:
    """Helper to read/write legacy MicMac XML/DAT formats."""
    @staticmethod
    def write_xml_orientation(orient_data, path):
        print(f"Writing legacy XML to {path}")
        # XML generation logic

    @staticmethod
    def read_homol_dat(path):
        print(f"Reading legacy binary homol from {path}")
        return None
