from pydantic import BaseModel, Field
from typing import List, Optional

class Action(BaseModel):
    command: str = Field(..., description="The terminal command to run (e.g., 'ps', 'netstat', 'kill')")
    args: List[str] = Field(default_factory=list, description="Arguments for the command (e.g., ['4022'])")

class Observation(BaseModel):
    terminal_output: str = Field(..., description="The text shown on the terminal screen")
    active_alerts: List[str] = Field(..., description="List of current security alerts")
    system_status: str = Field(..., description="Current status of the system (e.g., Stable, Remediated)")
    reward: float = Field(..., description="The numerical reward for the current step")

# Required for OpenEnv metadata compliance
class EnvMetadata(BaseModel):
    name: str
    version: str
    description: str