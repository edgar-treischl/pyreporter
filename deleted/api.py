"""
FastAPI service layer for pyreporter pipeline.

Provides REST endpoints for:
1. Fetching raw survey data
2. Preparing plot-ready data
3. Generating individual plots
4. Creating complete PDF reports
"""

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from pathlib import Path
import pandas as pd
import json
import io
import base64

from pyreporter.fetch import fetch_raw_data
from pyreporter.prepare import prepare_data
from pyreporter.plot import export_plot
from pyreporter.render_pdf import render_pdf
from pyreporter.utils import create_directories, get_directory, clean_files
from pyreporter.meta_repository import MetaRepository


app = FastAPI(
    title="PyReporter API",
    description="Survey report generation pipeline API",
    version="1.0.0"
)


class PipelineRequest(BaseModel):
    """Base request model for pipeline operations."""
    snr: str = Field(..., description="School number (zero-padded string)", example="0001")
    stype: str = Field(..., description="School type", example="gy")
    audience: str = Field(..., description="Target audience (sus, elt, leh, ubb, aus, all)", example="sus")
    ubb: bool = Field(False, description="UBB flag")
    ganztag: bool = Field(False, description="Full-day school flag")
    has_N: List[str] = Field(default_factory=lambda: ["sus", "leh"], description="Available audiences")
    use_cache: bool = Field(True, description="Whether to use cached data")


class PlotRequest(PipelineRequest):
    """Request model for plot generation."""
    plot_name: str = Field(..., description="Plot ID (e.g., A12, A3a)", example="A12")


class ReportRequest(PipelineRequest):
    """Request model for full report generation."""
    year: str = Field("2025", description="Report year", example="2025")
    duration: str = Field("2", description="Survey duration string", example="2")


class RawDataResponse(BaseModel):
    """Response model for raw data endpoint."""
    status: str
    message: str
    rows: int
    syear: str
    result_n: str
    columns: List[str]
    data_preview: List[Dict[str, Any]] = Field(description="First 10 rows")


class PreparedDataResponse(BaseModel):
    """Response model for prepared data endpoint."""
    status: str
    message: str
    plots_count: int
    sname: str
    syear: str
    report_name: str
    plots_available: List[str]


class PlotResponse(BaseModel):
    """Response model for plot generation."""
    status: str
    message: str
    plot_name: str
    file_path: str


class ReportResponse(BaseModel):
    """Response model for report generation."""
    status: str
    message: str
    file_path: str
    plots_generated: int


@app.get("/")
async def root():
    """API root endpoint with service information."""
    return {
        "service": "PyReporter API",
        "version": "1.0.0",
        "endpoints": {
            "raw_data": "/api/v1/raw-data",
            "prepared_data": "/api/v1/prepared-data",
            "plot": "/api/v1/plot",
            "report": "/api/v1/report"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "pyreporter"}


@app.post("/api/v1/raw-data", response_model=RawDataResponse)
async def get_raw_data(request: PipelineRequest):
    """
    Fetch raw survey data from LimeSurvey.
    
    This endpoint connects to LimeSurvey, discovers relevant surveys,
    and returns raw response data with caching support.
    
    Returns
    -------
    RawDataResponse
        Contains row count, survey year, sample size, and data preview
    """
    try:
        result = fetch_raw_data(
            snr=request.snr,
            stype=request.stype,
            audience=request.audience,
            ubb=request.ubb,
            ganztag=request.ganztag,
            has_N=request.has_N,
            use_cache=request.use_cache
        )
        
        raw_data = result['raw_data']
        
        return RawDataResponse(
            status="success",
            message=f"Fetched raw data for school {request.snr}",
            rows=len(raw_data),
            syear=result['syear'],
            result_n=result['result_n'],
            columns=raw_data.columns.tolist(),
            data_preview=raw_data.head(10).to_dict(orient='records')
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching raw data: {str(e)}")


@app.post("/api/v1/prepared-data", response_model=PreparedDataResponse)
async def get_prepared_data(request: PipelineRequest):
    """
    Prepare plot-ready data from raw survey responses.
    
    This endpoint transforms raw data into normalized long-format,
    joins with metadata, and returns information about available plots.
    
    Returns
    -------
    PreparedDataResponse
        Contains plot count, school name, year, and available plots list
    """
    try:
        # First fetch raw data
        fetch_result = fetch_raw_data(
            snr=request.snr,
            stype=request.stype,
            audience=request.audience,
            ubb=request.ubb,
            ganztag=request.ganztag,
            has_N=request.has_N,
            use_cache=request.use_cache
        )
        
        # Then prepare it
        prepared = prepare_data(
            snr=request.snr,
            stype=request.stype,
            audience=request.audience,
            ubb=request.ubb,
            ganztag=request.ganztag,
            has_N=request.has_N,
            raw_data=fetch_result['raw_data'],
            use_cache=request.use_cache
        )
        
        return PreparedDataResponse(
            status="success",
            message=f"Prepared data for school {request.snr}",
            plots_count=len(prepared['plot_data']),
            sname=prepared['sname'],
            syear=fetch_result['syear'],
            report_name=prepared['report_meta']['report'],
            plots_available=prepared['report_meta']['meta']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error preparing data: {str(e)}")


@app.post("/api/v1/plot")
async def generate_plot(request: PlotRequest):
    """
    Generate a single plot and return as PDF.
    
    This endpoint creates a plotnine chart for the specified plot ID
    and returns it as a downloadable PDF file.
    
    Returns
    -------
    FileResponse
        PDF file of the generated plot
    """
    try:
        # Fetch and prepare data
        fetch_result = fetch_raw_data(
            snr=request.snr,
            stype=request.stype,
            audience=request.audience,
            ubb=request.ubb,
            ganztag=request.ganztag,
            has_N=request.has_N,
            use_cache=request.use_cache
        )
        
        prepared = prepare_data(
            snr=request.snr,
            stype=request.stype,
            audience=request.audience,
            ubb=request.ubb,
            ganztag=request.ganztag,
            has_N=request.has_N,
            raw_data=fetch_result['raw_data'],
            use_cache=request.use_cache
        )
        
        syear = fetch_result['syear']
        report_name = prepared['report_meta']['report']
        
        # Verify plot exists
        if request.plot_name not in prepared['report_meta']['meta']:
            raise HTTPException(
                status_code=404,
                detail=f"Plot '{request.plot_name}' not found. Available: {prepared['report_meta']['meta']}"
            )
        
        # Setup directories
        create_directories(snr=request.snr, audience=request.audience, ubb=request.ubb, syear=syear)
        
        # Generate the plot
        export_plot(
            meta=request.plot_name,
            snr=request.snr,
            audience=request.audience,
            report=report_name,
            data=fetch_result['raw_data'],
            ubb=request.ubb,
            year=syear,
            export=True
        )
        
        # Return the PDF file
        plot_dir = Path(get_directory(snr=request.snr, syear=syear)) / "plots"
        plot_file = plot_dir / f"{request.plot_name}_plot.pdf"
        
        if not plot_file.exists():
            raise HTTPException(status_code=500, detail=f"Plot file not created: {plot_file}")
        
        return FileResponse(
            path=str(plot_file),
            media_type="application/pdf",
            filename=f"{request.snr}_{request.plot_name}.pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating plot: {str(e)}")


@app.post("/api/v1/report")
async def create_report(request: ReportRequest):
    """
    Generate complete PDF report with all plots.
    
    This endpoint runs the full pipeline: fetch, prepare, plot, and render
    a complete PDF report with all charts and metadata.
    
    Returns
    -------
    FileResponse
        Complete PDF report
    """
    try:
        # Step 1: Fetch raw data
        fetch_result = fetch_raw_data(
            snr=request.snr,
            stype=request.stype,
            audience=request.audience,
            ubb=request.ubb,
            ganztag=request.ganztag,
            has_N=request.has_N,
            use_cache=request.use_cache
        )
        
        raw_data = fetch_result['raw_data']
        syear = fetch_result['syear']
        result_n = fetch_result['result_n']
        
        # Step 2: Prepare data
        prepared = prepare_data(
            snr=request.snr,
            stype=request.stype,
            audience=request.audience,
            ubb=request.ubb,
            ganztag=request.ganztag,
            has_N=request.has_N,
            raw_data=raw_data,
            use_cache=request.use_cache
        )
        
        report_meta = prepared['report_meta']
        header_report = prepared['header_report']
        sname = prepared['sname']
        
        # Step 3: Create directories
        create_directories(snr=request.snr, audience=request.audience, ubb=request.ubb, syear=syear)
        
        # Step 4: Generate all plots
        from pyreporter.plot import create_plotlist
        
        create_plotlist(
            meta_list=report_meta['meta'],
            snr=request.snr,
            year=syear,
            audience=request.audience,
            report=report_meta['report'],
            data=raw_data,
            ubb=request.ubb,
            export=True
        )
        
        # Step 5: Render PDF
        render_pdf(
            audience=request.audience,
            snr=request.snr,
            year=syear,
            sname=sname,
            survey_n=result_n,
            duration=request.duration,
            header_report=header_report
        )
        
        # Step 6: Return the PDF
        tmpdir = Path(get_directory(snr=request.snr, syear=syear))
        pdf_file = tmpdir / f"{request.snr}_results_{request.audience}.pdf"
        
        if not pdf_file.exists():
            raise HTTPException(status_code=500, detail=f"Report PDF not created: {pdf_file}")
        
        # Clean temporary files (but keep PDF and plots)
        clean_files(where=str(tmpdir))
        
        return FileResponse(
            path=str(pdf_file),
            media_type="application/pdf",
            filename=f"{request.snr}_results_{request.audience}.pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating report: {str(e)}")


@app.get("/api/v1/plots/list")
async def list_available_plots(
    snr: str = Query(..., description="School number"),
    stype: str = Query(..., description="School type"),
    audience: str = Query(..., description="Target audience"),
    ubb: bool = Query(False, description="UBB flag"),
    ganztag: bool = Query(False, description="Full-day school flag")
):
    """
    List all available plots for a given configuration.
    
    This is a lightweight endpoint that returns plot metadata
    without actually generating any plots.
    """
    try:
        from pyreporter.utils import get_metadata, _as_bool
        
        meta_repo = MetaRepository()
        
        # Get metadata using the same logic as prepare.py
        meta_templates = meta_repo.meta_templates.copy()
        meta_templates["ubb"] = _as_bool(meta_templates["ubb"])
        meta_templates["ganztag"] = _as_bool(meta_templates["ganztag"])
        
        # Find matching template
        tmpl_mask = (
            (meta_templates["stype"] == stype) &
            (meta_templates["type"] == audience) &
            (meta_templates["ubb"] == bool(ubb)) &
            (meta_templates["ganztag"] == bool(ganztag))
        )
        
        report_templates = meta_templates.loc[tmpl_mask, "report_tmpl"].unique()
        
        if len(report_templates) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No template found for stype={stype}, audience={audience}, ubb={ubb}, ganztag={ganztag}"
            )
        
        report_name = report_templates[0]
        
        # Get plots for this report
        report_meta_df = meta_repo.meta_reports[
            meta_repo.meta_reports["report"] == report_name
        ]
        
        # Filter by audience if needed
        if audience == "all":
            # For 'all', we'd need data_avail, but for listing we show all possible
            plots = report_meta_df["plot"].unique().tolist()
        else:
            # Filter by audience type
            plots = report_meta_df[
                report_meta_df["type"] == audience
            ]["plot"].unique().tolist()
        
        return {
            "status": "success",
            "snr": snr,
            "report": report_name,
            "audience": audience,
            "plots": plots,
            "count": len(plots)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing plots: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
