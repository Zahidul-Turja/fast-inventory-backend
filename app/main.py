from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder

app = FastAPI(
    title="Fast Inventory",
    description="API for Fast Inventory management system",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {"message": "Fast Inventory API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Handle validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    messages = []

    for err in errors:
        loc = err.get("loc", [])
        msg = err.get("msg", "")
        field_name = None

        # Check if the error refers to a specific field in the body
        if len(loc) > 1 and loc[0] == "body":
            field_name = loc[1]
        elif loc == ("body",):
            # Whole body missing
            field_name = None

        # Build clean messages
        if msg.lower() == "field required":
            if field_name:
                messages.append(f"{field_name} is required")
            else:
                messages.append("Request body is required")
        else:
            if field_name:
                messages.append(f"{field_name}: {msg}")
            else:
                messages.append(msg)

    # Combine multiple messages if necessary
    return JSONResponse(
        status_code=422,
        content={"message": ", ".join(messages)},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
