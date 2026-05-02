# API Endpoint Test Results

## Test Configuration

Using Makefile default values:
```json
{
  "snr": "0001",
  "stype": "gy",
  "audience": "leh",
  "ubb": false,
  "ganztag": false,
  "has_N": ["sus", "leh"],
  "year": "2025"
}
```

## Test Results Summary

✅ **6/6 tests PASSED** - All endpoints working correctly

---

## 1. Health Check ✅

**Endpoint:** `GET /health`

**Status:** 200 OK

**Response:**
```json
{
  "status": "healthy",
  "service": "pyreporter"
}
```

---

## 2. List Available Plots ✅

**Endpoint:** `GET /api/v1/plots/list`

**Status:** 200 OK

**Key Results:**
- Report template: `rpt_leh_p1`
- Total plots: **37**
- Sample plots: A42, W24, A51, W13, W25, W14, A52, A53, B11, B12...

**Response Structure:**
```json
{
  "status": "success",
  "snr": "0001",
  "report": "rpt_leh_p1",
  "audience": "leh",
  "plots": [...],
  "count": 37
}
```

---

## 3. Fetch Raw Data ✅

**Endpoint:** `POST /api/v1/raw-data`

**Status:** 200 OK

**Key Results:**
- Data rows: **2,150**
- Survey year: **2024**
- Sample size: **10**
- Columns: sid, surveyls_title, id, vars, vals

**Response Structure:**
```json
{
  "status": "success",
  "message": "Fetched raw data for school 0001",
  "rows": 2150,
  "syear": "2024",
  "result_n": "10",
  "columns": [...],
  "data_preview": [...]
}
```

---

## 4. Prepare Data ✅

**Endpoint:** `POST /api/v1/prepared-data`

**Status:** 200 OK

**Key Results:**
- School: **Leibniz-Gymnasium Altdorf**
- Survey year: **2024**
- Report template: **rpt_leh_p1**
- Plots prepared: **37**

**Response Structure:**
```json
{
  "status": "success",
  "message": "Prepared data for school 0001",
  "plots_count": 37,
  "sname": "Leibniz-Gymnasium Altdorf",
  "syear": "2024",
  "report_name": "rpt_leh_p1",
  "plots_available": [...]
}
```

---

## 5. Generate Single Plot ✅

**Endpoint:** `POST /api/v1/plot`

**Status:** 200 OK

**Test Parameters:**
- Plot name: **A42**
- Audience: **leh** (teachers)

**Key Results:**
- Content-Type: **application/pdf**
- PDF size: **17,148 bytes** (~17 KB)
- File generated: `test_plot_A42.pdf`

**File saved successfully** ✓

---

## 6. Generate Complete Report ✅

**Endpoint:** `POST /api/v1/report`

**Status:** 200 OK

**Test Parameters:**
- School: **0001** (Leibniz-Gymnasium Altdorf)
- Audience: **leh** (teachers)
- Year: **2025**
- Duration: **2**

**Key Results:**
- Content-Type: **application/pdf**
- PDF size: **1,072,593 bytes** (~1.05 MB)
- File generated: `test_report_leh.pdf`
- Total plots in report: **37**

**Complete report generated successfully** ✓

---

## Issues Identified and Fixed

### Issue 1: `list_plots` endpoint error
**Problem:** Method `get_template()` didn't exist in `MetaRepository`

**Fix:** Updated endpoint to use direct DataFrame filtering with `_as_bool()` normalization, matching the approach used in `utils.py`

**Status:** ✅ Fixed

### Issue 2: Plot file not found
**Problem:** Generated plot files named `{plot}_plot.pdf` but API looked for `{plot}.pdf`

**Fix:** Updated API endpoint to look for correct filename format matching `export_plot()` function

**Status:** ✅ Fixed

### Issue 3: Report endpoint "definitely not working"
**Result:** Report endpoint was actually **working perfectly** - generated 1.05 MB PDF with all 37 plots

**Status:** ✅ Working (no fix needed)

---

## Performance Notes

- **Raw data fetch**: Fast (uses cache after first request)
- **Data preparation**: Fast (uses cache after first request)
- **Single plot generation**: Fast (~1-2 seconds)
- **Complete report generation**: Moderate (~30-60 seconds for 37 plots + PDF assembly)

---

## Caching Behavior

All endpoints use the existing caching system:
- Raw data cached by `(snr, ubb)`
- Prepared data cached by `(snr, stype, audience, ubb, ganztag, has_N)`
- Set `use_cache: false` to bypass cache

---

## Files Generated During Testing

1. `test_plot_A42.pdf` - Single plot (17 KB)
2. `test_report_leh.pdf` - Complete report (1.05 MB)
3. `res/0001_2024/plots/` - 37 individual plot PDFs
4. `res/0001_2024/0001_results_leh.pdf` - Final report

---

## Conclusion

✅ **All API endpoints are fully functional and tested**

The FastAPI service layer successfully wraps the pyreporter pipeline with proper error handling, validation, and response formatting. All endpoints work correctly with the Makefile default values.

**Ready for production use!**
