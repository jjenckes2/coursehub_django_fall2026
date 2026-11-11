from html import escape
from textwrap import wrap

import pandas as pd
import plotly.express as px
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .models import AssignmentResult


@staff_member_required(login_url="login")
def grade_dashboard(request):
    # Read individual results. Plotly handles the averages and histogram counts.
    results = list(
        AssignmentResult.objects
        .filter(cohort="fall_2026")
        .order_by("assignment_id", "learner_code")
        .values(
            "assignment_id",
            "assignment__title",
            "learner_code",
            "grade_percent",
            "actual_minutes",
        )
    )

    if not results:
        return render(request, "insights/grade_dashboard.html", {"results": []})

    df = pd.DataFrame(results)
    df["assignment_label"] = (
        df["assignment__title"] + " (#" + df["assignment_id"].astype(str) + ")"
    )


    average_fig = px.histogram(
        df,
        x="assignment_label",
        y="grade_percent",
        histfunc="avg",
        barmode="group",
        title="Average grade by assignment",
        labels={"assignment_label": "Assignment", "grade_percent": "Grade (%)"},
    )
    average_fig.update_yaxes(title="Average grade (%)", range=[0, 100])

    histogram_fig = px.histogram(
        df,
        x="grade_percent",
        title="Distribution of individual grades",
        labels={"grade_percent": "Grade (%)"},
    )

    histogram_fig.update_layout(bargap=0)
    histogram_fig.update_yaxes(title="Number of results", dtick=1)


    scatter_fig = px.scatter(
        df,
        x="actual_minutes",
        y="grade_percent",
        hover_name="assignment_label",
        title="Completion time and grade",
        labels={"actual_minutes": "Completion time (minutes)", "grade_percent": "Grade (%)"},
    )
    scatter_fig.update_xaxes(rangemode="tozero")
    scatter_fig.update_yaxes(range=[0, 100])


    for figure in (average_fig, histogram_fig, scatter_fig):
        figure.update_layout(template="plotly_white", height=360, font_color="#102535")
        figure.update_traces(marker_color="#15628f")

    # Wrap only the displayed ticks, preserving the full labels for grouping and hover.
    assignment_labels = df["assignment_label"].drop_duplicates().tolist()
    average_fig.update_xaxes(
        tickmode="array",
        tickvals=assignment_labels,
        ticktext=[
            "<br>".join(escape(line) for line in wrap(label, width=20))
            for label in assignment_labels
        ],
        tickangle=0,
        automargin=True,
    )
    average_fig.update_layout(height=600, margin={"b": 120})

    return render(request, "insights/grade_dashboard.html", {
        "results": results,
        "average_chart": average_fig.to_html(full_html=False, include_plotlyjs="cdn"),
        "histogram_chart": histogram_fig.to_html(full_html=False, include_plotlyjs=False),
        "scatter_chart": scatter_fig.to_html(full_html=False, include_plotlyjs=False),
    })
