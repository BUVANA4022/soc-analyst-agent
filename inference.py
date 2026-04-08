import os
from openai import OpenAI
from env import SOCEnvironment, Action

# These MUST be set in your HF Space variables
client = OpenAI(
    base_url=os.getenv("API_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY")
)

def run_baseline():
    env = SOCEnvironment()
    obs = env.reset(task_id="easy")
    
    # Simple loop for the AI to interact
    for _ in range(3):
        prompt = f"You are a SOC Analyst. Terminal output: {obs.terminal_output}. What command do you run next? Output only the command name."
        response = client.chat.completions.create(
            model=os.getenv("MODEL_NAME"),
            messages=[{"role": "user", "content": prompt}]
        )
        # Parse and step
        action_text = response.choices[0].message.content.strip()
        obs, reward, done, info = env.step(Action(command=action_text))
        print(f"Action: {action_text} | Reward: {reward}")
        if done: break

if __name__ == "__main__":
    run_baseline()