import pandas as pd
import argparse

def find_closest_timestamp(target_time, df_timestamps):
    """Find the closest timestamp in df_timestamps for a given target_time."""
    while True:
        closest_idx = (df_timestamps["datetime"] - target_time).abs().idxmin()
        closest_row = df_timestamps.loc[closest_idx]
        if pd.notna(closest_row["datetime"]):
            return closest_row
        target_time += pd.Timedelta(milliseconds=1)  # Increment by 1 ms and search again

def align_files():
    image_csv = "vector_result.csv"  # Change to your actual file path
    data_txt = "spoles.txt"  # Change to your actual file path
    output_csv = "aligned_output.csv"  # Change to your desired output file path
    
    # Load image CSV file
    df_images = pd.read_csv(image_csv)
    
    # Extract initial timestamp from the first image
    df_images["datetime"] = pd.to_datetime(df_images["Image"].str.extract(r"_(\d{8}_\d{6})")[0], format="%Y%m%d_%H%M%S")
    initial_timestamp = df_images["datetime"].min()
    
    # Extract frame numbers and compute actual timestamps
    df_images["frame_number"] = df_images["Image"].str.extract(r"_(\d+)\.tiff")[0].astype(float)
    df_images["computed_datetime"] = initial_timestamp + pd.to_timedelta(df_images["frame_number"] * 30, unit="ms")
    
    # Load the timestamped data file
    df_timestamps = pd.read_csv(data_txt, sep='\s+', header=None,
                                names=["Nr", "date", "time", "Ux", "Uy", "Uz", "U3"], engine="python")
    
    # Convert timestamps into proper datetime format with explicit format
    df_timestamps["datetime"] = pd.to_datetime(df_timestamps["date"] + " " + df_timestamps["time"], format="%Y.%m.%d %H:%M:%S.%f", errors="coerce")
    df_timestamps.dropna(subset=["datetime"], inplace=True)
    
    # Ensure timestamps are sorted for efficient searching
    df_timestamps_sorted = df_timestamps.sort_values("datetime").reset_index(drop=True)
    
    # Find the closest timestamp for each image timestamp
    aligned_data = []
    for _, row in df_images.iterrows():
        closest_match = find_closest_timestamp(row["computed_datetime"], df_timestamps_sorted)
        merged_row = {**row.to_dict(), **closest_match.to_dict()}  # Merge dictionaries
        aligned_data.append(merged_row)
    
    # Convert to DataFrame and save
    merged_df = pd.DataFrame(aligned_data)
    merged_df.to_csv(output_csv, index=False)
    print(f"Aligned data saved to {output_csv}")

if __name__ == "__main__":
    align_files()
