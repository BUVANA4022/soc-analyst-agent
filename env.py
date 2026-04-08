import random
from models import Action, Observation

class SOCEnvironment:
    def __init__(self):
        # State variables to track what the agent has done
        self.reset()

    def reset(self, task_id="easy"):
        self.task_id = task_id
        self.step_count = 0
        self.quarantined_ips = []
        self.killed_pids = []
        self.is_done = False
        self.current_reward = 0.0
        
        initial_msg = f"Task {task_id.upper()} Started: Suspicious activity detected on workstation-01."
        return self._get_obs(initial_msg)

    def step(self, action: Action):
        self.step_count += 1
        cmd = action.command.lower().strip()
        args = [a.lower() for a in action.args]
        output = "Command not recognized."
        reward = 0.0

        # 1. BASIC COMMANDS (Discovery)
        if cmd == "ps":
            output = "PID: 4022 | Process: powershell.exe | User: Admin | Path: C:\\Windows\\temp\nPID: 1024 | Process: svchost.exe | User: System"
            reward = 0.05  # Small reward for using the right discovery tool

        elif cmd == "netstat":
            if self.task_id == "hard":
                output = "Active Connections:\nTCP 192.168.1.15:4444 -> 103.45.12.9:8080 (ESTABLISHED)"
                reward = 0.1
            else:
                output = "Active Connections:\nTCP 192.168.1.15:443 -> 52.12.3.4:443 (ESTABLISHED)"

        # 2. EASY TASK LOGIC (Signature Verification)
        elif cmd == "verify_sig":
            target_pid = args[0] if args else ""
            if target_pid == "4022":
                output = "Verification Result: UNSIGNED / UNKNOWN PUBLISHER"
                if self.task_id == "easy":
                    reward = 0.95  # Total reward will be 1.0 (with discovery)
                    self.is_done = True
            else:
                output = f"Verification Result: Verified (Microsoft Corporation)"

        # 3. MEDIUM TASK LOGIC (Lateral Movement Trace)
        elif cmd == "get_logs":
            if self.task_id == "medium":
                output = "LOG: 10:05 AM - SSH login from 192.168.1.50\nLOG: 10:10 AM - File 'payload.ps1' copied from 192.168.1.50"
                reward = 0.2
            else:
                output = "No unusual log entries found."

        elif cmd == "isolate_ip":
            target_ip = args[0] if args else ""
            if self.task_id == "medium" and target_ip == "192.168.1.50":
                output = f"SUCCESS: Host {target_ip} quarantined from network."
                reward = 0.8
                self.is_done = True
            else:
                output = f"ERROR: Could not isolate {target_ip}."

        # 4. HARD TASK LOGIC (Remediation)
        elif cmd == "kill":
            target_pid = args[0] if args else ""
            if target_pid == "4022":
                output = "SUCCESS: Process 4022 terminated."
                self.killed_pids.append(4022)
                if self.task_id == "hard":
                    reward = 0.4 # Partial progress
            else:
                output = f"Error: PID {target_pid} not found."

        elif cmd == "block_ip":
            target_ip = args[0] if args else ""
            if self.task_id == "hard" and target_ip == "103.45.12.9":
                output = f"SUCCESS: IP {target_ip} blocked at firewall."
                if 4022 in self.killed_pids:
                    reward = 0.6 # Completion reward
                    self.is_done = True
                else:
                    reward = 0.2 # Blocked IP but forgot to kill process
            else:
                output = f"Invalid IP or Firewall error."

        # 5. LIMITS & PENALTIES
        if not self.is_done:
            reward -= 0.01  # Time penalty to encourage efficiency
            
        if self.step_count >= 15:
            output = "TIMEOUT: Incident escalated to Senior Analyst. Agent Failed."
            self.is_done = True
            reward = -1.0

        return self._get_obs(output, reward)

    def _get_obs(self, output, reward=0.0):
        # This keeps the total score in the required 0.0 - 1.0 range
        self.current_reward = max(0.0, min(1.0, self.current_reward + reward))
        
        return Observation(
            terminal_output=output,
            active_alerts=["Suspicious PowerShell Execution"] if not self.is_done else [],
            system_status="Stable" if not self.is_done else "Remediated",
            reward=self.current_reward
        )
