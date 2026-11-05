from fastapi import FastAPI
from pydantic import BaseModel

from parsers.stack_parser import (
    extract_exception,
    extract_message,
    fingerprint as build_fingerprint,
)

from graph.diagnosis_graph import build_graph

app = FastAPI(title="TraceFix AI Service", version="0.1.0")
diagnosis_graph = build_graph()


class DiagnoseRequest(BaseModel):
    trace: str
    context: str | None = None


@app.get("/ai/health")
def health():
    return {"status": "ok"}


@app.post("/ai/diagnose")
def diagnose(req: DiagnoseRequest):

    extracted_exception = extract_exception(req.trace)
    extracted_message = extract_message(req.trace)
    fingerprint_value = build_fingerprint(
        extracted_exception, extracted_message, ""
    )

    state = {
        "trace": req.trace,
        "context": req.context,
        "exception": extracted_exception,
        "message": extracted_message,
        "fingerprint": fingerprint_value,
    }
    result = diagnosis_graph.invoke(state)
    diagnosis = result.get("diagnosis") or {}
    matched_case_ids = result.get("matched_case_ids") or []
    missing_info = result.get("missing_info") or []
    title = diagnosis.get("title") or "信息不足，暂时无法给出诊断"
    root_cause = diagnosis.get("rootCause") or ""
    fix_steps = diagnosis.get("fixSteps") or ""
    verification = diagnosis.get("verification") or ""
    confidence = diagnosis.get("confidence", 0.0)

    return {
        "title": title,
        "extractedException": extracted_exception,
        "extractedMessage": extracted_message,
        "fingerprint": fingerprint_value,
        "rootCause": root_cause,
        "fixSteps": fix_steps,
        "verification": verification,
        "matchedCaseIds": matched_case_ids,
        "confidence": confidence,
        "missingInfo": missing_info,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
