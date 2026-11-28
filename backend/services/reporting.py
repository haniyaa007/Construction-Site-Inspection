from collections import Counter

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend import config, models, schemas


def limitations() -> list[str]:
    return [
        "Detections come from an automated model that has not been validated on this site's footage.",
        f"Detections are stored at confidence >= {config.DETECTION_MIN_CONFIDENCE:.2f}; "
        f"observations are flagged at >= {config.FLAG_MIN_CONFIDENCE:.2f}. "
        "These thresholds were tuned on a small sample only.",
        "Flagged items are potential safety observations requiring human review, not compliance verdicts.",
        "The absence of a detection is not evidence that protective equipment is worn or missing.",
        "The model's 'NO-' classes are its weakest, and it can contradict itself on the same region of an image.",
    ]


def build_report(db: Session, inspection: models.Inspection) -> schemas.ReportRead:
    project = inspection.project
    images = db.scalars(
        select(models.Image).where(models.Image.inspection_id == inspection.id)
    ).all()
    filenames = {image.id: image.original_filename for image in images}

    detections = db.scalars(
        select(models.Detection)
        .where(models.Detection.inspection_id == inspection.id)
        .order_by(models.Detection.image_id, models.Detection.confidence.desc())
    ).all()
    issues = db.scalars(
        select(models.Issue)
        .where(models.Issue.inspection_id == inspection.id)
        .order_by(models.Issue.id)
    ).all()

    class_counts = Counter(d.object_class for d in detections)
    flagged = [d for d in detections if d.is_flagged]

    review_counts = {"pending": 0, "confirmed": 0, "dismissed": 0}
    review_counts.update(Counter(d.review_status for d in flagged))
    issue_counts = {"open": 0, "in_progress": 0, "resolved": 0}
    issue_counts.update(Counter(i.status for i in issues))

    return schemas.ReportRead(
        inspection_id=inspection.id,
        project_name=project.name,
        project_location=project.location,
        inspection_date=inspection.date,
        generated_at=models.utcnow(),
        images_analyzed=len(images),
        detections_total=len(detections),
        detection_counts=[
            schemas.ClassCount(object_class=name, count=count)
            for name, count in sorted(class_counts.items())
        ],
        observations_total=len(flagged),
        observations_by_review_status=review_counts,
        observations=[
            schemas.ReportObservation(
                detection_id=d.id,
                image_id=d.image_id,
                original_filename=filenames.get(d.image_id, "unknown"),
                object_class=d.object_class,
                confidence=d.confidence,
                review_status=d.review_status,
            )
            for d in flagged
        ],
        issues_total=len(issues),
        issues_by_status=issue_counts,
        issues=[
            schemas.ReportIssue(
                id=i.id, title=i.title, severity=i.severity,
                status=i.status, assigned_to=i.assigned_to,
            )
            for i in issues
        ],
        limitations=limitations(),
    )


def render_markdown(report: schemas.ReportRead) -> str:
    review = report.observations_by_review_status
    lines = [
        f"# Inspection Report: {report.project_name}",
        "",
        f"- **Location:** {report.project_location or 'Not specified'}",
        f"- **Inspection:** #{report.inspection_id}, {report.inspection_date:%Y-%m-%d}",
        f"- **Report generated:** {report.generated_at:%Y-%m-%d %H:%M} UTC",
        f"- **Images analyzed:** {report.images_analyzed}",
        "",
        "## Summary",
        "",
        f"The detection model reported {report.detections_total} objects across "
        f"{report.images_analyzed} image(s). {report.observations_total} potential safety "
        f"observation(s) were flagged for human review "
        f"({review['pending']} pending, {review['confirmed']} confirmed, "
        f"{review['dismissed']} dismissed).",
        "",
        "## Detected objects",
        "",
    ]
    if report.detection_counts:
        lines += [f"- {c.object_class}: {c.count}" for c in report.detection_counts]
    else:
        lines.append("- None")

    lines += ["", "## Potential safety observations (require human review)", ""]
    if report.observations:
        lines += [
            f"- {o.object_class} in `{o.original_filename}` "
            f"(confidence {o.confidence:.2f}), review status: **{o.review_status}**"
            for o in report.observations
        ]
    else:
        lines.append("- None flagged")

    lines += ["", "## Issues", ""]
    if report.issues:
        lines += [
            f"- #{i.id} [{i.severity}] {i.title}, status: {i.status}, "
            f"assigned to: {i.assigned_to or 'unassigned'}"
            for i in report.issues
        ]
    else:
        lines.append("- None raised")

    lines += ["", "## Limitations", ""]
    lines += [f"- {text}" for text in report.limitations]
    return "\n".join(lines) + "\n"