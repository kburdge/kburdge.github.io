"""
Ultra‑thin FastAPI wrapper:  /lc?ra=…&dec=…&radius=…
returns the CSV produced by Rubin_LC.py as JSON.
"""
import subprocess, json, tempfile, os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse

# Path to your existing script & data
SCRIPT = Path(__file__).parent / "Rubin_LC.py"

app = FastAPI(
    title="Rubin LC service",
    description="Wraps Rubin_LC.py so the browser can fetch light‑curves",
    version="0.1.0",
)

@app.get("/lc")
def get_lightcurve(ra: float, dec: float, radius: float = 1.0):
    """
    Run Rubin_LC.py and return the resulting table as JSON.
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp_csv = Path(tmp) / "out.csv"
        cmd = [
            "python", str(SCRIPT),
            f"{ra}", f"{dec}",
            "--radius", f"{radius}"
        ]
        try:
            subprocess.run(cmd, check=True, cwd=SCRIPT.parent,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500,
                                detail=e.stderr.decode()[:4000])

        # Rubin_LC names the file <ra>_<dec>_<ID>.csv in cwd
        # find it & stream back as JSON
        generated = max(SCRIPT.parent.glob(f"{ra:.8f}_{dec:.8f}_*.csv"),
                        key=os.path.getmtime, default=None)
        if generated is None:
            raise HTTPException(status_code=500,
                                detail="Light‑curve file not produced")

        # Convert to JSON (≈30 kB) so JS can plot directly
        import pandas as pd
        df = pd.read_csv(generated)
        return JSONResponse(df.to_dict(orient="list"))
