import os
import asyncio
import json
from openai import OpenAI
from dotenv import load_dotenv
from env.environment import MedTriageEnv
from env.models import TriageAction

# Load environment variables
load_dotenv()

# Read environment variables with defaults where required
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4.1-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

# Initialize OpenAI client
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN
)

TASKS = ["task_01_basic_triage", "task_02_differential", "task_03_critical_triage"]
SYSTEM_PROMPT = """You are an AI triage nurse. Assess the patient and respond with JSON only:
{"action_type": "...", "parameters": {...}}
Actions: ask_question | order_test | flag_critical | assign_triage | request_vitals
Assign ESI 1 (critical) to 5 (non-urgent)."""

async def run_episode(task_id: str):
    env = MedTriageEnv(task_id=task_id)
    benchmark = "medtriage-env"
    
    # [START] task=<task_name> env=<benchmark> model=<model_name>
    print(f"[START] task={task_id} env={benchmark} model={MODEL_NAME}", flush=True)
    
    result = await env.reset()
    rewards = []
    step_n = 0
    success = False
    
    try:
        while not result.done:
            step_n += 1
            obs_json = result.observation.model_dump_json()
            
            action_str = "null"
            error_msg = "null"
            
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"Patient State: {obs_json}\nNext Action:"}
                    ],
                    max_tokens=150,
                    temperature=0.1
                )
                action_str = response.choices[0].message.content.strip()
                # Parse action
                clean_action = action_str
                if "```json" in clean_action:
                    clean_action = clean_action.split("```json")[1].split("```")[0].strip()
                elif "```" in clean_action:
                    clean_action = clean_action.split("```")[1].split("```")[0].strip()
                
                action_data = json.loads(clean_action)
                # Sanitize for log (single line, compact JSON to avoid spaces)
                log_action = json.dumps(action_data, separators=(',', ':'))
                
                action = TriageAction(**action_data)
                
                # Step the environment
                result = await env.step(action)
                reward = result.reward
                rewards.append(reward)
                
                # [STEP] step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
                print(f"[STEP]  step={step_n} action={log_action} reward={reward:.2f} done={'true' if result.done else 'false'} error=null", flush=True)
                
                if result.done:
                    # Success if final score from grader is high enough
                    final_score = result.info.get("final_score", 0.0)
                    success = final_score >= 0.7
                    
            except Exception as e:
                error_msg = str(e).replace("\n", " ").replace("\r", " ")
                print(f"[STEP]  step={step_n} action={action_str.replace('\\n', ' ')} reward=0.00 done=true error={error_msg}", flush=True)
                rewards.append(0.0)
                break
                
    except Exception as e:
        # Catch unexpected errors to ensure [END] is printed
        pass
    finally:
        # [END] success=<true|false> steps=<n> rewards=<r1,r2,...,rn>
        rewards_csv = ",".join([f"{r:.2f}" for r in rewards]) if rewards else "0.00"
        print(f"[END]   success={'true' if success else 'false'} steps={step_n} rewards={rewards_csv}", flush=True)

async def main():
    for task in TASKS:
        await run_episode(task)

if __name__ == "__main__":
    asyncio.run(main())

