from __future__ import annotations

from pathlib import Path
from typing import Dict

from crewai import Agent, Task, Crew, Process

try:
    import yaml  # type: ignore
except Exception as e:  # pragma: no cover
    raise ImportError(
        "Falta la dependencia PyYAML para cargar configuraciones YAML. "
        "Instala con: pip install PyYAML"
    ) from e

from fraude_incapacidades.tools.extraction_tools import extract_document_info_tool
from fraude_incapacidades.tools.verification_tools import validar_rethus_tool, validar_cie10_tool

def _load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

# Rutas a los YAML de configuración
_BASE = Path(__file__).parent / "config"
_AGENTS_YAML = _BASE / "agents.yaml"
_TASKS_YAML = _BASE / "tasks.yaml"

agents_cfg = _load_yaml(_AGENTS_YAML)
tasks_cfg = _load_yaml(_TASKS_YAML)

def _build_agents(cfg: dict) -> Dict[str, Agent]:
    agents: Dict[str, Agent] = {}
    for name, data in cfg.items():
        tools = []
        if name == "perito_forense":
            tools = [extract_document_info_tool]
        elif name == "auditor_medico":
            tools = [validar_rethus_tool, validar_cie10_tool]
            
        agents[name] = Agent(
            role=data.get("role", ""),
            goal=data.get("goal", ""),
            backstory=data.get("backstory", ""),
            tools=tools,
            verbose=True,
        )
    return agents


def _build_tasks(cfg: dict, agents: Dict[str, Agent]) -> Dict[str, Task]:
    tasks: Dict[str, Task] = {}
    for name, data in cfg.items():
        agent_key = data.get("agent", "")
        agent = agents.get(agent_key)
        if agent is None:
            raise ValueError(f"La tarea '{name}' referencia un agente desconocido: '{agent_key}'")
        tasks[name] = Task(
            description=data.get("description", ""),
            agent=agent,
            expected_output=data.get("expected_output", ""),
        )
    return tasks


_agents = _build_agents(agents_cfg)
_tasks = _build_tasks(tasks_cfg, _agents)


# Orden lógico de ejecución (secuencial)
crew = Crew(
    agents=[
        _agents["perito_forense"],
        _agents["auditor_medico"],
        _agents["investigador_redes"],
    ],
    tasks=[
        _tasks["extraccion_datos_task"],
        _tasks["verificacion_institucional_task"],
        _tasks["dictamen_final_task"],
    ],
    process=Process.sequential,
)
