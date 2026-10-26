"""Core extraction logic for the Tecolutla Colab notebook (colab/tecolutla_seismic_extract.ipynb).

Runs where the large Drive files can be read (Google Colab, signed in as the data owner) and writes
small outputs (< ~4 MB each) that the Drive connector can return to the analysis repository:
  - ZGY (DMI PSDM 2019): metadata JSON and an int16-quantised sub-cube over the field, split into parts
  - SEG-Y (PEMEX PSTM cuts 554702/554703): textual and binary headers, trace-header summary and
    geometry arrays, and the same field-window sub-cube
  - large LAS files: gzip copies (split if needed)
Every source file and every output gets a SHA256 in manifest.json.

The field window is fixed in UTM 14N WGS84 (the CRS of the repository's well coordinates and of the
Jan 2019 Top El Abra grid). If a volume's coordinates do not overlap it (different CRS or no
coordinates), the window falls back to the centre of the volume and the metadata says so.
"""
import gzip, hashlib, io, json, os, shutil, zipfile
import numpy as np

FIELD = dict(xmin=706000.0, xmax=709000.0, ymin=2261300.0, ymax=2264400.0)  # UTM 14N WGS84, m
DEPTH_WIN = (1900.0, 2800.0)  # m, PSDM depth window around the El Abra (~2,290-2,400 mSS)
TIME_WIN = (1200.0, 2400.0)   # ms, PSTM time window (El Abra expected ~1,600-1,800 ms)
PART_BYTES = 3_800_000        # target raw size of each output part (connector limit is ~6 MB)
PART_MAX_UPLOAD = 4_500_000   # any uploaded file larger than this is split into .partNN pieces


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def quantise(a):
    """float32 array -> (int16 array, scale) with a = q * scale."""
    m = float(np.nanmax(np.abs(a))) if a.size else 0.0
    scale = m / 32000.0 if m > 0 else 1.0
    q = np.round(np.nan_to_num(a) / scale).astype(np.int16)
    return q, scale


def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return jsonable(o.tolist())
    if isinstance(o, (str, int, float, bool)) or o is None:
        return o
    return str(o)


# ------------------------------------------------------------------ ZGY
def zgy_extract(path, outdir, stem="psdm2019"):
    """Write <stem>_meta.json and <stem>_cube_partNN.npz; return list of written paths."""
    from openzgy.api import ZgyReader
    out = []
    with ZgyReader(path) as r:
        meta = {k: jsonable(v) for k, v in r.meta.items()}
        meta["indexcorners"] = jsonable(r.indexcorners)
        meta["annotcorners"] = jsonable(r.annotcorners)
        try:
            st = r.statistics
            meta["statistics"] = dict(cnt=st.cnt, min=st.min, max=st.max)
        except Exception as e:  # older files may lack statistics
            meta["statistics"] = f"unavailable: {e}"
        nil, nxl, nz = r.size
        # field window -> index ranges
        pts = [(FIELD["xmin"], FIELD["ymin"]), (FIELD["xmin"], FIELD["ymax"]),
               (FIELD["xmax"], FIELD["ymin"]), (FIELD["xmax"], FIELD["ymax"])]
        try:
            idx = np.array([r.worldToIndex(p) for p in pts], dtype=float)
            i0, i1 = int(np.floor(idx[:, 0].min())), int(np.ceil(idx[:, 0].max())) + 1
            j0, j1 = int(np.floor(idx[:, 1].min())), int(np.ceil(idx[:, 1].max())) + 1
            overlap = i1 > 0 and j1 > 0 and i0 < nil and j0 < nxl
        except Exception:  # degenerate corners (no world coordinates in the file)
            overlap, i0 = False, 0
        if not overlap:
            meta["window_note"] = "field window does not overlap the volume coordinates; central window used"
            ci, cj, h = nil // 2, nxl // 2, 60
            i0, i1, j0, j1 = ci - h, ci + h, cj - h, cj + h
        i0, j0 = max(i0, 0), max(j0, 0)
        i1, j1 = min(i1, nil), min(j1, nxl)
        z = r.zstart + r.zinc * np.arange(nz)
        unit = str(r.zunitdim).lower()
        win = TIME_WIN if "time" in unit else DEPTH_WIN
        k = np.where((z >= win[0]) & (z <= win[1]))[0]
        if k.size < 10:  # window outside the sampled range: keep everything
            meta["z_window_note"] = f"z window {win} outside the volume z range; full range kept"
            k = np.arange(nz)
        k0, k1 = int(k[0]), int(k[-1]) + 1
        meta["window_index"] = dict(il=[i0, i1], xl=[j0, j1], z=[k0, k1])
        meta["window_z"] = [float(z[k0]), float(z[k1 - 1])]
        # world coordinates of every trace in the window
        ii, jj = np.meshgrid(np.arange(i0, i1), np.arange(j0, j1), indexing="ij")
        xy = np.array([r.indexToWorld((float(a), float(b))) for a, b in zip(ii.ravel(), jj.ravel())]).reshape(ii.shape + (2,))
        ia = np.array([r.indexToAnnot((float(a), float(b))) for a, b in zip(ii.ravel(), jj.ravel())]).reshape(ii.shape + (2,))
        nzw = k1 - k0
        rows_per_part = max(1, PART_BYTES // max(1, (j1 - j0) * nzw * 2))
        parts = []
        for p, a in enumerate(range(i0, i1, rows_per_part)):
            b = min(a + rows_per_part, i1)
            buf = np.zeros((b - a, j1 - j0, nzw), dtype=np.float32)
            r.read((a, j0, k0), buf)
            q, scale = quantise(buf)
            fn = os.path.join(outdir, f"{stem}_cube_part{p:02d}.npz")
            np.savez_compressed(fn, data=q, scale=np.float64(scale), il_index=np.arange(a, b), xl_index=np.arange(j0, j1),
                                z=z[k0:k1], x=xy[a - i0:b - i0, :, 0], y=xy[a - i0:b - i0, :, 1],
                                inline=ia[a - i0:b - i0, :, 0], crossline=ia[a - i0:b - i0, :, 1])
            parts.append(os.path.basename(fn)); out.append(fn)
        meta["parts"] = parts
        meta["note"] = "data = int16, amplitude = data * scale; arrays (il, xl, z); x, y in the volume's world CRS"
    fn = os.path.join(outdir, f"{stem}_meta.json")
    json.dump(meta, open(fn, "w"), indent=1)
    return [fn] + out


# ------------------------------------------------------------------ SEG-Y
HDR = {  # candidate header words (segyio TraceField byte positions)
    "inline_189": 189, "crossline_193": 193, "fldr_9": 9, "ensemble_21": 21, "tracf_13": 13, "seqline_5": 5,
    "cdp_x_181": 181, "cdp_y_185": 185, "src_x_73": 73, "src_y_77": 77, "scalco_71": 71,
    "ns_115": 115, "dt_117": 117, "delrt_109": 109,
}


def _scaled(v, s):
    s = np.where(s == 0, 1, s).astype(np.float64)
    return np.where(s < 0, v / np.abs(s), v * s)


def segy_extract(path, outdir, stem):
    """Headers, geometry and a field-window sub-cube for one SEG-Y file."""
    import segyio
    out = []
    with segyio.open(path, ignore_geometry=True) as f:
        # textual header(s), EBCDIC or ASCII
        txt = segyio.tools.wrap(f.text[0])
        fn = os.path.join(outdir, f"{stem}_textheader.txt"); open(fn, "w").write(txt); out.append(fn)
        binh = {str(k): int(v) for k, v in f.bin.items()}
        n = f.tracecount
        H = {name: np.asarray(f.attributes(b)[:]) for name, b in HDR.items()}
        ns, dt = len(f.samples), float(f.samples[1] - f.samples[0]) if len(f.samples) > 1 else 0.0
        t = np.asarray(f.samples, dtype=np.float64)
        x = _scaled(H["cdp_x_181"].astype(np.float64), H["scalco_71"])
        y = _scaled(H["cdp_y_185"].astype(np.float64), H["scalco_71"])
        if np.nanmax(np.abs(x)) == 0:  # no CDP coordinates: try source coordinates
            x = _scaled(H["src_x_73"].astype(np.float64), H["scalco_71"]); y = _scaled(H["src_y_77"].astype(np.float64), H["scalco_71"])
        summary = dict(file=os.path.basename(path), tracecount=n, samples=ns, sample_interval=dt, t0=float(t[0]), t1=float(t[-1]),
                       format=int(f.format) if hasattr(f, "format") else None, binary_header=binh,
                       headers={k: dict(min=int(v.min()), max=int(v.max()), n_unique=int(np.unique(v).size)) for k, v in H.items()},
                       x_range=[float(np.nanmin(x)), float(np.nanmax(x))], y_range=[float(np.nanmin(y)), float(np.nanmax(y))])
        # geometry arrays (compressed, int32/float32)
        fn = os.path.join(outdir, f"{stem}_trace_headers.npz")
        np.savez_compressed(fn, **{k: v.astype(np.int32) for k, v in H.items()}, x=x.astype(np.float64), y=y.astype(np.float64))
        out.append(fn)
        # field window selection
        sel = np.where((x >= FIELD["xmin"]) & (x <= FIELD["xmax"]) & (y >= FIELD["ymin"]) & (y <= FIELD["ymax"]))[0]
        if sel.size == 0:
            summary["window_note"] = "no traces inside the field window (coordinates absent or another CRS); central traces used"
            c = n // 2; sel = np.arange(max(0, c - 7500), min(n, c + 7500))
        k = np.where((t >= TIME_WIN[0]) & (t <= TIME_WIN[1]))[0]
        if k.size < 10:
            summary["z_window_note"] = f"time window {TIME_WIN} outside {t[0]}-{t[-1]}; full range kept"
            k = np.arange(ns)
        k0, k1 = int(k[0]), int(k[-1]) + 1
        summary["window"] = dict(traces=int(sel.size), t=[float(t[k0]), float(t[k1 - 1])])
        per = max(1, PART_BYTES // ((k1 - k0) * 2))
        parts = []
        for p, a in enumerate(range(0, sel.size, per)):
            ids = sel[a:a + per]
            tr = np.stack([f.trace[int(i)][k0:k1] for i in ids]).astype(np.float32)
            q, scale = quantise(tr)
            fn = os.path.join(outdir, f"{stem}_window_part{p:02d}.npz")
            np.savez_compressed(fn, data=q, scale=np.float64(scale), trace_index=ids.astype(np.int32), t=t[k0:k1],
                                x=x[ids], y=y[ids], **{k_: H[k_][ids].astype(np.int32) for k_ in ("inline_189", "crossline_193", "fldr_9", "ensemble_21", "tracf_13")})
            parts.append(os.path.basename(fn)); out.append(fn)
        summary["parts"] = parts
        summary["note"] = "data = int16 (traces, samples), amplitude = data * scale; x, y from CDP (or source) coordinates with scalco applied"
    fn = os.path.join(outdir, f"{stem}_summary.json")
    json.dump(jsonable(summary), open(fn, "w"), indent=1)
    return [fn] + out


# ------------------------------------------------------------------ LAS and archives
def gzip_file(src, dst):
    with open(src, "rb") as a, gzip.open(dst, "wb", compresslevel=9) as b:
        shutil.copyfileobj(a, b)
    return dst


def split_if_large(path, limit=PART_MAX_UPLOAD):
    """Return [path] or a list of .partNN files (rejoin with: cat name.part* > name)."""
    size = os.path.getsize(path)
    if size <= limit:
        return [path]
    parts = []
    with open(path, "rb") as f:
        for i, chunk in enumerate(iter(lambda: f.read(limit), b"")):
            pn = f"{path}.part{i:02d}"; open(pn, "wb").write(chunk); parts.append(pn)
    os.remove(path)
    return parts


def zip_listing(path):
    with zipfile.ZipFile(path) as z:
        return [dict(name=i.filename, size=i.file_size, compressed=i.compress_size) for i in z.infolist()]
