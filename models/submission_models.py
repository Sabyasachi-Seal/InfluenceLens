from pydantic import BaseModel

class SubmissionRequest(BaseModel):
    campaign_id: str
    submission: str