from codealmanac.cli.render.common import print_json_model
from codealmanac.cli.render.style import style
from codealmanac.services.diagnostics.models import (
    DoctorCheck,
    DoctorReport,
    DoctorStatus,
)


def render_doctor(report: DoctorReport, json_output: bool) -> None:
    if json_output:
        print_json_model(report)
        return
    print(f"codealmanac v{report.version}")
    print("")
    render_doctor_section("Install", report.install)
    render_doctor_section("Current wiki", report.wiki)


def render_doctor_section(title: str, checks: tuple[DoctorCheck, ...]) -> None:
    if len(checks) == 0:
        return
    print(f"{style.BOLD}## {title}{style.RST}")
    for check in checks:
        icon, tint = status_icon(check.status)
        print(f"  {tint}{icon}{style.RST} {check.message}")
        if check.fix is not None:
            print(f"    {style.DIM}{check.fix}{style.RST}")
    print("")


def status_icon(status: DoctorStatus) -> tuple[str, str]:
    if status == DoctorStatus.OK:
        return "✓", style.GREEN
    if status == DoctorStatus.PROBLEM:
        return "✗", style.RED
    return "◇", style.BLUE
