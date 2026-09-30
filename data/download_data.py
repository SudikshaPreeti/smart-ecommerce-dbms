import os
import requests

def download():
    os.makedirs("data/raw", exist_ok=True)
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail.xlsx"
    out = "data/raw/online_retail.xlsx"
    expected_size = 23_000_000  # ~23 MB

    # Delete the truncated file
    if os.path.exists(out):
        size = os.path.getsize(out)
        print(f"Existing file: {size/1_000_000:.1f} MB")
        if size < expected_size:
            print("File is incomplete. Deleting and re-downloading...")
            os.remove(out)
        else:
            print("✅ Dataset already complete:", out)
            return

    print("Downloading Online Retail dataset (~23 MB)...")
    headers = {"User-Agent": "Mozilla/5.0"}

    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            print(f"\nAttempt {attempt}/{max_attempts}...")
            with requests.get(url, headers=headers, stream=True, timeout=180) as r:
                r.raise_for_status()
                total = int(r.headers.get("content-length", 0))
                downloaded = 0
                with open(out, "wb") as f:
                    for chunk in r.iter_content(chunk_size=64 * 1024):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total:
                                pct = downloaded * 100 // total
                                print(f"\r  {pct}% ({downloaded/1_000_000:.1f} MB)",
                                      end="", flush=True)

            final_size = os.path.getsize(out)
            print(f"\n  Downloaded: {final_size/1_000_000:.1f} MB")
            if final_size >= expected_size:
                print("\n✅ Dataset ready:", out)
                return
            else:
                print(f"  Incomplete. Retrying...")
                os.remove(out)

        except Exception as e:
            print(f"\n  Error: {e}")
            if os.path.exists(out):
                os.remove(out)

    print("\n❌ All attempts failed. Use manual download (Solution 2).")

if __name__ == "__main__":
    download()