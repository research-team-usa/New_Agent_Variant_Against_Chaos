import json
import uuid
import sys
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

# ==========================================
# 1. ARCHITECTURE DATACLASSES (Immutable State)
# ==========================================


@dataclass(frozen=True)
class PipelineContext:
    """P4: Immutable State. Once created, the context cannot be changed."""

    run_id: str
    stage_index: int
    input_data: str
    upstream_results: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskResult:
    status: str  # "success" or "failure"
    output_data: Optional[str] = None
    error_code: Optional[str] = None


# ==========================================
# 2. TRACE LOGGING ENGINE
# ==========================================


def log_trace(
    run_id: str, agent_id: str, event_type: str, status: str, payload: Dict[str, Any]
):
    """Standardized JSON Trace Log (Task B)"""
    trace_entry = {
        "schema_version": "1.0.0",
        "trace_id": str(uuid.uuid4()),  # Unique ULID/UUID per event
        "run_id": run_id,
        "agent_id": agent_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "status": status,
        "payload": payload,
    }
    # Print as JSON-Lines to stdout for Prometheus/Grafana log scrapers
    print(json.dumps(trace_entry))


# ==========================================
# 3. AGENT TASK INTERFACE & IMPLEMENTATIONS
# ==========================================


class AgentTask:
    def __init__(self, task_id: str, description: str):
        self.task_id = task_id
        self.description = description

    def execute(self, context: PipelineContext) -> TaskResult:
        raise NotImplementedError("Each specific agent must implement this.")


class ReadTask(AgentTask):
    def execute(self, context: PipelineContext) -> TaskResult:
        log_trace(
            context.run_id,
            self.task_id,
            "action_start",
            "success",
            {"action": "parse_text"},
        )
        output = f"Parsed: {context.input_data}"
        log_trace(
            context.run_id,
            self.task_id,
            "action_end",
            "success",
            {"output_length": len(output)},
        )
        return TaskResult(status="success", output_data=output)


class RewriteTask(AgentTask):
    def execute(self, context: PipelineContext) -> TaskResult:
        log_trace(
            context.run_id,
            self.task_id,
            "action_start",
            "success",
            {"action": "structure_text"},
        )
        input_from_read = context.upstream_results.get("ID-001-READ", "")
        output = f"<structured>{input_from_read}</structured>"
        log_trace(
            context.run_id,
            self.task_id,
            "action_end",
            "success",
            {"status": "formatted"},
        )
        return TaskResult(status="success", output_data=output)


class ConvertTask(AgentTask):
    def __init__(self, task_id: str, description: str, inject_fault: bool = False):
        super().__init__(task_id, description)
        self.inject_fault = inject_fault

    def execute(self, context: PipelineContext) -> TaskResult:
        log_trace(
            context.run_id,
            self.task_id,
            "action_start",
            "success",
            {"action": "render_pdf"},
        )

        # TASK C Integration Test: Fault Injection
        if self.inject_fault:
            error_msg = "PDF Engine Timeout: Unresponsive rendering service."
            log_trace(
                context.run_id,
                self.task_id,
                "error",
                "failure",
                {"error_code": "RENDER_TIMEOUT", "error_message": error_msg},
            )
            return TaskResult(status="failure", error_code="RENDER_TIMEOUT")

        output = "[PDF_BINARY_DATA]"
        log_trace(
            context.run_id,
            self.task_id,
            "action_end",
            "success",
            {"bytes_rendered": 1024},
        )
        return TaskResult(status="success", output_data=output)


class DeployTask(AgentTask):
    def execute(self, context: PipelineContext) -> TaskResult:
        log_trace(
            context.run_id,
            self.task_id,
            "action_start",
            "success",
            {"action": "upload_to_storage"},
        )
        output = "https://storage.enterprise.local/docs/output.pdf"
        log_trace(
            context.run_id, self.task_id, "action_end", "success", {"url": output}
        )
        return TaskResult(status="success", output_data=output)


# ==========================================
# 4. DETERMINISTIC PIPELINE ORCHESTRATOR
# ==========================================


class AgentPipeline:
    def __init__(self, name: str):
        self.name = name
        self.tasks = []

    def add_task(self, task: AgentTask):
        self.tasks.append(task)

    def run(self, initial_input: str) -> None:
        run_id = str(uuid.uuid4())
        print(f"\n{'='*60}\n🚀 STARTING PIPELINE RUN: {run_id}\n{'='*60}")

        upstream_results = {}

        for index, task in enumerate(self.tasks):
            # 1. Create Immutable Context for this specific stage
            context = PipelineContext(
                run_id=run_id,
                stage_index=index + 1,
                input_data=initial_input,
                upstream_results=upstream_results.copy(),
            )

            # 2. Execute Task
            result = task.execute(context)

            # 3. Deterministic Checkpoint Evaluation
            if result.status == "failure":
                print(f"\n❌ PIPELINE HALTED AT CHECKPOINT: {task.task_id}")
                print(f"Error Code: {result.error_code}")
                print(
                    "Subsequent stages (e.g. ID-004-DEPLOY) have been blocked from executing to prevent cascading failures."
                )
                log_trace(
                    run_id,
                    "Orchestrator",
                    "pipeline_halt",
                    "error",
                    {"failed_stage": task.task_id},
                )
                return  # Pipeline bricht hier hart ab (Circuit Breaker)

            # 4. Sequential Handover
            upstream_results[task.task_id] = result.output_data

        print(f"\n✅ PIPELINE COMPLETED SUCCESSFULLY")
        print(f"Final Output: {upstream_results[self.tasks[-1].task_id]}\n")


# ==========================================
# 5. EXECUTION & INTEGRATION TEST
# ==========================================

if __name__ == "__main__":
    # Test 1: Successful Run
    pipeline_success = AgentPipeline("PDF_Generator_HappyPath")
    pipeline_success.add_task(ReadTask("ID-001-READ", "Read raw text"))
    pipeline_success.add_task(RewriteTask("ID-002-REWRITE", "Format to markup"))
    pipeline_success.add_task(
        ConvertTask("ID-003-CONVERT", "Render PDF", inject_fault=False)
    )
    pipeline_success.add_task(DeployTask("ID-004-DEPLOY", "Upload PDF"))

    pipeline_success.run("Initial unformatted document text.")

    # Test 2: Fault Injection (Simulating Agent Chaos)
    pipeline_fail = AgentPipeline("PDF_Generator_ChaosSimulation")
    pipeline_fail.add_task(ReadTask("ID-001-READ", "Read raw text"))
    pipeline_fail.add_task(RewriteTask("ID-002-REWRITE", "Format to markup"))
    pipeline_fail.add_task(
        ConvertTask("ID-003-CONVERT", "Render PDF", inject_fault=True)
    )  # <--- FEHLER WIRD INJIZIERT
    pipeline_fail.add_task(DeployTask("ID-004-DEPLOY", "Upload PDF"))

    pipeline_fail.run("Initial unformatted document text.")
