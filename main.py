from fastapi import FastAPI, HTTPException
from models import Action, Observation
from env import SOCEnvironment
import uvicorn

# Initialize the FastAPI app
app = FastAPI(
    title="SOC Analyst OpenEnv",
    description="A real-world cybersecurity incident response environment for AI agents.",
    version="1.0.0"
)

# Initialize the persistent environment state
# Note: In a production RL setting, you might handle multiple sessions, 
# but for the OpenEnv hackathon, a single global instance is standard.
env = SOCEnvironment()

@app.get("/")
def root():
    """Root endpoint for basic verification."""
    return {"message": "SOC Analyst Environment is Online", "spec": "OpenEnv v1.0"}

@app.get("/health")
def health():
    """
    The 'Health Check' - Crucial for Automated Validation.
    Tells judges/validators that the container is healthy and ready.
    """
    return {
        "status": "ready", 
        "model": "SOC-Analyst-v1",
        "tasks_loaded": ["easy", "medium", "hard"]
    }

@app.post("/reset", response_model=Observation)
def reset(task_id: str = "easy"):
    """
    Resets the environment to a clean state for a specific task.
    """
    try:
        observation = env.reset(task_id=task_id)
        return observation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/step", response_model=Observation)
def step(action: Action):
    """
    Executes an action in the environment and returns the next observation.
    """
    try:
        # env.step returns Observation
        observation = env.step(action)
        return observation
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid action or simulation error: {str(e)}")

@app.get("/state", response_model=Observation)
def state():
    """
    Returns the current observation without advancing the simulation.
    """
    # We call a private method or return current obs to satisfy 'state()' requirement
    return env._get_obs("Current state snapshot requested.")

if __name__ == "__main__":
    # Hugging Face Spaces usually look for port 7860
    uvicorn.run(app, host="0.0.0.0", port=7860)