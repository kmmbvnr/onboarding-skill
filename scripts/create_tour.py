#!/usr/bin/env python3
"""Create a local self-tour for the onboarding skill."""

from __future__ import annotations

import argparse
import json
import webbrowser
from pathlib import Path

from render_map import render, validate


TEXT = {
    "en": {
        "name": "Learn $onboarding",
        "goal": "Learn to create a map, follow nodes, ask for help, and report progress.",
        "role": "New onboarding skill user",
        "labels": {
            "filter_all": "All",
            "filter_ready": "Ready",
            "filter_active": "Active",
            "filter_done": "Done",
            "filter_revisit": "Revisit",
            "details": "Node details",
            "why": "Why",
            "evidence": "Evidence",
            "requires": "Requires",
            "none": "None",
            "nodes": "nodes",
            "minutes": "min",
            "footer": "Open a node and use its command to continue the tour.",
        },
        "nodes": [
            ("TOUR-START", "Open the map", "Find the ready node and its codename.", "The map shows your route and current status.", "The user names the first ready node and explains how to open it.", "🗺️"),
            ("TOUR-LEAD", "Prepare supervisor input", "Learn how a supervisor gives expectations to a new developer.", "Clear expectations make the learner plan relevant to the role.", "The user knows that $onboarding lead creates a message from the supervisor to the developer.", "👤"),
            ("TOUR-MAP", "Create a project map", "Run the skill in a project and provide role, experience, and optional supervisor input.", "The skill needs the project and learner context before it can build a useful route.", "The user knows where project state and the HTML map are stored.", "🌱"),
            ("TOUR-NODE", "Choose a learning node", "Continue the next node or open one codename from the map.", "A codename lets the learner choose a specific part of the route.", "The user can distinguish $onboarding from $onboarding CODENAME.", "🧭"),
            ("TOUR-ASK", "Ask a useful question", "Check local evidence, then prepare one precise question for a buddy.", "A precise question helps a buddy answer the missing fact quickly.", "The user knows when and how to use $onboarding ask.", "💬"),
            ("TOUR-REPORT", "Report progress", "Create a daily status or a final onboarding result.", "A supervisor needs verified capabilities, blockers, and the next action.", "The user can choose between $onboarding report and $onboarding report final.", "📋"),
            ("TOUR-DONE", "Start real onboarding", "Change to the project root and start a real project path.", "A real plan must use the repository and the developer's role.", "The user names the first action to take in a real project.", "🚀"),
        ],
    },
    "ru": {
        "name": "Знакомство с $onboarding",
        "goal": "Научиться создавать карту, проходить узлы, задавать вопросы и сообщать о прогрессе.",
        "role": "Новый пользователь навыка onboarding",
        "labels": {
            "filter_all": "Все",
            "filter_ready": "Можно начать",
            "filter_active": "Сейчас",
            "filter_done": "Пройдено",
            "filter_revisit": "Повторить",
            "details": "Подробности узла",
            "why": "Зачем",
            "evidence": "Результат",
            "requires": "Сначала",
            "none": "Нет",
            "nodes": "узлов",
            "minutes": "мин",
            "footer": "Откройте узел и используйте его команду, чтобы продолжить тур.",
        },
        "nodes": [
            ("TOUR-START", "Откройте карту", "Найдите готовый узел и его кодовое имя.", "Карта показывает маршрут и текущий статус.", "Пользователь называет первый готовый узел и объясняет, как его открыть.", "🗺️"),
            ("TOUR-LEAD", "Подготовьте вводные руководителя", "Узнайте, как руководитель передаёт ожидания новому разработчику.", "Ясные ожидания связывают план с рабочей ролью.", "Пользователь знает, что $onboarding lead создаёт сообщение от руководителя разработчику.", "👤"),
            ("TOUR-MAP", "Создайте карту проекта", "Запустите навык в проекте и сообщите роль, опыт и необязательные вводные руководителя.", "Для полезного маршрута навыку нужен контекст проекта и разработчика.", "Пользователь знает, где хранятся рабочий стейт и HTML-карта.", "🌱"),
            ("TOUR-NODE", "Выберите учебный узел", "Продолжите следующий узел или откройте кодовое имя с карты.", "Кодовое имя позволяет выбрать конкретную часть маршрута.", "Пользователь различает $onboarding и $onboarding CODENAME.", "🧭"),
            ("TOUR-ASK", "Задайте полезный вопрос", "Проверьте локальные данные, затем подготовьте один точный вопрос наставнику.", "Точный вопрос помогает наставнику быстро сообщить недостающий факт.", "Пользователь знает, когда и как применять $onboarding ask.", "💬"),
            ("TOUR-REPORT", "Сообщите о прогрессе", "Создайте ежедневный статус или итоговый результат онбординга.", "Руководителю нужны подтверждённые навыки, блокеры и следующий шаг.", "Пользователь выбирает между $onboarding report и $onboarding report final.", "📋"),
            ("TOUR-DONE", "Начните реальный онбординг", "Перейдите в корень проекта и запустите рабочий маршрут.", "Рабочий план должен учитывать репозиторий и роль разработчика.", "Пользователь называет первое действие в реальном проекте.", "🚀"),
        ],
    },
}


THEME = {
    "ink": "#243047",
    "muted": "#667085",
    "paper": "#fffdf7",
    "background_top": "#d9ecff",
    "background_bottom": "#b7d9c5",
    "path": "#ffd784",
    "accent": "#e45f59",
    "done": "#3f8f68",
    "locked": "#a7afb9",
    "revisit": "#7965a8",
    "logo": "",
}


def make_state(language: str, root: Path) -> dict:
    text = TEXT[language]
    nodes = []
    previous = None
    for index, (code, title, summary, why, evidence, icon) in enumerate(text["nodes"]):
        nodes.append(
            {
                "codename": code,
                "title": title,
                "summary": summary,
                "why": why,
                "kind": "orientation" if index in {0, 6} else "check",
                "target": "recognize" if index < 2 else "operate",
                "status": "ready" if index == 0 else "locked",
                "requires": [] if previous is None else [previous],
                "estimated_minutes": 4,
                "icon": icon,
                "image": "",
                "evidence": evidence,
                "project_paths": [],
            }
        )
        previous = code
    return {
        "version": 1,
        "language": language,
        "labels": text["labels"],
        "theme": THEME,
        "project": {"name": text["name"], "root": str(root), "goal": text["goal"]},
        "learner": {"role": text["role"], "experience": [], "placed_out": []},
        "nodes": nodes,
        "sessions": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language", choices=sorted(TEXT), default="en")
    parser.add_argument("--output-dir", type=Path, default=Path(".onboarding-demo"))
    parser.add_argument("--open", action="store_true", help="Open the map in the default browser")
    args = parser.parse_args()

    output_dir = args.output_dir.resolve()
    state_path = output_dir / "state.json"
    map_path = output_dir / "map.html"

    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
        validate(state)
        map_path.write_text(render(state), encoding="utf-8")
        print(f"Tour already exists. Rendered map: {map_path}")
        if args.open:
            webbrowser.open(map_path.resolve().as_uri(), new=2)
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    state = make_state(args.language, Path.cwd().resolve())
    validate(state)
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    map_path.write_text(render(state), encoding="utf-8")
    print(f"Created onboarding tour: {map_path}")
    if args.open:
        webbrowser.open(map_path.resolve().as_uri(), new=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
