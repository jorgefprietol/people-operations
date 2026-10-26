"""Explicit onboarding dependencies and approvals, with minimal employee data."""
import json
import os
import re
import uuid
from datetime import date, timedelta

TITLE = "People Operations"
DESCRIPTION = "Onboarding con dependencias, aprobaciones y consultas de políticas con fuentes verificables."
DEMO = {"action": "create", "employee_ref": "EMP-DEMO-042", "role": "engineering", "start_date": "2026-10-26"}

TASKS = {
    "policy_acknowledged": {"depends_on": [], "approval_required": False, "due_business_days": 0},
    "identity_verified": {"depends_on": [], "approval_required": False, "due_business_days": 0},
    "account_provisioned": {"depends_on": ["policy_acknowledged", "identity_verified"], "approval_required": True, "due_business_days": 1},
    "workspace_ready": {"depends_on": ["account_provisioned"], "approval_required": False, "due_business_days": 2},
}


def _schema(store):
    store.connection.execute("CREATE TABLE IF NOT EXISTS onboarding (id TEXT PRIMARY KEY, employee_ref TEXT UNIQUE NOT NULL, role TEXT NOT NULL, start_date TEXT NOT NULL, state TEXT NOT NULL, tasks TEXT NOT NULL)")


def _due(start, days):
    result = date.fromisoformat(start)
    while result.weekday() >= 5:
        result += timedelta(days=1)
    while days:
        result += timedelta(days=1)
        if result.weekday() < 5:
            days -= 1
    return result.isoformat()


def _view(row):
    tasks = json.loads(row["tasks"])
    finished = sum(t["state"] == "completed" for t in tasks.values())
    return {"case_id": row["id"], "employee_ref": row["employee_ref"], "role": row["role"], "start_date": row["start_date"], "state": row["state"], "tasks": tasks, "progress": {"completed": finished, "total": len(tasks)}}


def process(payload, store):
    _schema(store)
    action = payload.get("action", "create")
    if not isinstance(action, str):
        raise ValueError("action debe ser texto")
    if action in {"policy_ingest", "policy_delete", "query_policy", "policy_demo"}:
        from .retrieval import process as policy_process
        return policy_process(payload, store)
    if action == "create":
        employee_ref, role, start = payload.get("employee_ref"), payload.get("role"), payload.get("start_date")
        if not isinstance(employee_ref, str) or not re.fullmatch(r"[A-Z0-9][A-Z0-9_-]{2,39}", employee_ref):
            raise ValueError("employee_ref debe ser un identificador interno de 3 a 40 caracteres")
        if role not in ("engineering", "operations", "sales"):
            raise ValueError("role debe ser engineering, operations o sales")
        try:
            if not isinstance(start, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", start):
                raise ValueError("Formato de fecha inválido")
            date.fromisoformat(start)
        except (ValueError, TypeError):
            raise ValueError("start_date debe usar YYYY-MM-DD") from None
        if set(payload) - {"action", "employee_ref", "role", "start_date"}:
            raise ValueError("No enviar nombres, documentos, correos ni otros datos personales")
        previous = store.connection.execute("SELECT * FROM onboarding WHERE employee_ref=?", (employee_ref,)).fetchone()
        if previous:
            if previous["role"] != role or previous["start_date"] != start:
                raise ValueError("Referencia de empleado ya registrada con otros datos")
            return dict(_view(previous), duplicate=True)
        tasks = {key: dict(spec, state="pending", approved_by=None, due_date=_due(start, spec["due_business_days"])) for key, spec in TASKS.items()}
        if role == "engineering":
            tasks["repository_access"] = {"depends_on": ["account_provisioned"], "approval_required": True, "due_business_days": 2, "due_date": _due(start, 2), "state": "pending", "approved_by": None}
        case_id = str(uuid.uuid4())
        store.connection.execute("INSERT INTO onboarding VALUES (?,?,?,?,?,?)", (case_id, employee_ref, role, start, "planned", json.dumps(tasks)))
        store.event("onboarding_created", {"case_id": case_id, "role": role, "task_count": len(tasks)})
        return dict(_view(store.connection.execute("SELECT * FROM onboarding WHERE id=?", (case_id,)).fetchone()), duplicate=False)
    if not isinstance(payload.get("case_id"), str):
        raise ValueError("case_id requerido")
    row = store.connection.execute("SELECT * FROM onboarding WHERE id=?", (payload.get("case_id"),)).fetchone()
    if not row:
        raise ValueError("Expediente inexistente")
    if action == "status":
        return _view(row)
    if action == "summary":
        view = _view(row)
        pending = [key for key, task in view["tasks"].items() if task["state"] != "completed"]
        answer = "Estado: " + row["state"] + ". Pendientes: " + (", ".join(pending) or "ninguno") + "."
        backend = os.environ.get("MODEL_BACKEND", "local")
        if backend != "local":
            from .providers import generate
            answer = generate(json.dumps({"state": row["state"], "pending_tasks": pending}), system="Resume únicamente el estado del onboarding recibido. No inventes tareas ni instrucciones. No incluyas datos personales.")
        return {"case_id": row["id"], "summary": answer, "backend": backend, "authoritative_state": view}
    state = row["state"]
    tasks = json.loads(row["tasks"])
    if action == "activate":
        if state != "planned":
            raise ValueError("Solo se pueden activar expedientes planificados")
        state = "active"
    elif action == "cancel":
        if state not in ("planned", "active"):
            raise ValueError("No se puede cancelar un expediente cerrado")
        if not isinstance(payload.get("reason"), str) or not payload["reason"].strip():
            raise ValueError("Motivo de cancelación requerido")
        state = "cancelled"
    elif action in ("approve", "complete"):
        task_id = payload.get("task_id")
        if not isinstance(task_id, str) or task_id not in tasks:
            raise ValueError("Tarea inexistente")
        task = tasks[task_id]
        actor = payload.get("actor")
        if not isinstance(actor, str) or not re.fullmatch(r"[A-Za-z0-9._-]{2,60}", actor):
            raise ValueError("actor interno requerido")
        if action == "complete" and state in ("active", "completed") and task["state"] == "completed":
            return dict(_view(row), duplicate=True)
        if state != "active":
            raise ValueError("El expediente debe estar activo")
        if action == "approve":
            if not task["approval_required"] or task["state"] == "completed":
                raise ValueError("Esta tarea no admite aprobación")
            task["approved_by"] = actor
        else:
            if any(tasks[dep]["state"] != "completed" for dep in task["depends_on"]):
                raise ValueError("Dependencias pendientes")
            if task["approval_required"] and not task["approved_by"]:
                raise ValueError("Aprobación requerida antes de completar")
            task.update(state="completed", completed_by=actor)
            if all(t["state"] == "completed" for t in tasks.values()):
                state = "completed"
    else:
        raise ValueError("Acción desconocida")
    store.connection.execute("UPDATE onboarding SET state=?, tasks=? WHERE id=?", (state, json.dumps(tasks), row["id"]))
    audit = {"case_id": row["id"], "task_id": payload.get("task_id"), "state": state, "actor": payload.get("actor")}
    if action == "cancel":
        audit["reason"] = payload["reason"][:300]
    store.event("onboarding_" + action, audit)
    return _view(store.connection.execute("SELECT * FROM onboarding WHERE id=?", (row["id"],)).fetchone())
