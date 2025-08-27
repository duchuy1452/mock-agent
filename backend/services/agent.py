import asyncio
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List
from models import (
    SlideFieldSelection,
    FieldItem,
    AgentAnalysisResult,
    LLMSlideReader,
    TableDefinition,
    TableRow,
    SlideCommentary,
)
from database import async_session, Project, Slide
from sqlalchemy import select, update
import uuid
from services.powerpoint_service import PowerPointService


class AnalysisAgent:
    def __init__(self, project_id: str, websocket_manager):
        self.project_id = project_id
        self.websocket_manager = websocket_manager

    async def start_initial_analysis(self):
        """Start initial analysis when WebSocket connects"""
        try:
            async with async_session() as session:
                # Get project data
                result = await session.execute(
                    select(Project).where(Project.id == self.project_id)
                )
                project = result.scalar_one_or_none()

                if not project:
                    await self._send_error("Project not found")
                    return

                # Update project status
                await session.execute(
                    update(Project)
                    .where(Project.id == self.project_id)
                    .values(status="agent_analyzing")
                )
                await session.commit()

                await self._send_status(
                    "AGENT_ANALYZING", "Agent is analyzing your data...", 0
                )

                # Load and analyze data
                data_df = pd.read_csv(project.data_source_path)
                schema_data = json.loads(Path(project.schema_path).read_text())

                # Create slides with agent analysis
                slide_analyses = await self._analyze_slides(data_df, schema_data)

                # Save slides to database
                for analysis in slide_analyses:
                    # Convert Pydantic objects to dict for JSON serialization
                    agent_fields_dict = [
                        field.dict() for field in analysis.selected_fields
                    ]

                    slide = Slide(
                        project_id=self.project_id,
                        slide_number=analysis.slide_number,
                        slide_title=analysis.slide_title,
                        status="agent_analyzed",
                        agent_selected_fields=agent_fields_dict,
                        final_fields=agent_fields_dict,
                    )
                    session.add(slide)

                await session.commit()

                # Generate complete PowerPoint presentation
                await self._send_status(
                    "GENERATING_POWERPOINT", "Generating PowerPoint presentation...", 80
                )

                try:
                    powerpoint_service = PowerPointService(self.project_id)
                    ppt_path = await powerpoint_service.generate_complete_presentation()

                    # Send PowerPoint ready notification
                    download_url = f"/downloads/{self.project_id}/analysis_report.pptm"
                    await self.websocket_manager.send_to_project(
                        self.project_id,
                        {
                            "type": "powerpoint_ready",
                            "download_url": download_url,
                            "message": "Complete PowerPoint presentation is ready for download",
                        },
                    )

                except Exception as e:
                    await self._send_error(f"PowerPoint generation failed: {str(e)}")
                    print(f"PowerPoint generation error: {e}")  # Debug logging

                # Update project status
                await session.execute(
                    update(Project)
                    .where(Project.id == self.project_id)
                    .values(status="waiting_for_user")
                )
                await session.commit()

                # Send results to client with PowerPoint download URL
                await self._send_analysis_results(
                    slide_analyses
                )

        except Exception as e:
            await self._send_error(f"Analysis failed: {str(e)}")

    async def _analyze_slides(
        self, data_df: pd.DataFrame, schema_data: dict
    ) -> List[AgentAnalysisResult]:
        """Analyze data and suggest fields for each slide"""
        await asyncio.sleep(2)  # Simulate AI processing

        # Constants for repeated strings
        RATIONALE_TOTAL = "Selected fields represent comprehensive financial totals and components relevant to the total loss component analysis."
        RATIONALE_LOB1 = "Fields selected are key components for calculating loss reserves and payments specific to LOB1."
        RATIONALE_LOB2 = "Fields selected are key components for calculating loss reserves and payments specific to LOB2."
        RATIONALE_LOB3 = "Fields selected are key components for calculating loss reserves and payments specific to LOB3."
        RATIONALE_LOB4 = "Fields selected are key components for calculating loss reserves and payments specific to LOB4."
        RATIONALE_LOB5 = "Fields selected are key components for calculating loss reserves and payments specific to LOB5."
        RATIONALE_CHANGE = "Selected fields represent changes in financial totals and components relevant to the loss component analysis."
        LABEL_TOTAL_LOSS_COMPONENT = "Total Loss Component"
        LABEL_LOSS_COMPONENT_CHANGE = "Loss Component Change"

        analyses = []

        # Slide 1: Reserves Overview
        slide1_fields = [
            SlideFieldSelection(
                row_label="Total",
                metric_fields=[
                    "ActuarialIBNR",
                    "PaidLossandALAE",
                    "CaseReserves",
                    "ULAE",
                    "NonCatLosses",
                    "ChangeInReservesForPolicyholderDividends",
                    "LargeLosses1",
                ],
                is_group_header=True,
                spans_all_columns=True,
                is_aggregate=False,
                filters=[],
                aggregation="sum",
                rationale=RATIONALE_TOTAL,
                component_rows=[],
            ),
            SlideFieldSelection(
                row_label="LOB1",
                metric_fields=["ActuarialIBNR", "PaidLossandALAE", "CaseReserves"],
                is_group_header=False,
                spans_all_columns=False,
                is_aggregate=False,
                filters=[{"field": "LoB_masked", "value": 1}],
                aggregation="sum",
                rationale=RATIONALE_LOB1,
                component_rows=[],
            ),
            SlideFieldSelection(
                row_label="LOB2",
                metric_fields=["ActuarialIBNR", "PaidLossandALAE", "CaseReserves"],
                is_group_header=False,
                spans_all_columns=False,
                is_aggregate=False,
                filters=[{"field": "LoB_masked", "value": 2}],
                aggregation="sum",
                rationale=RATIONALE_LOB2,
                component_rows=[],
            ),
            SlideFieldSelection(
                row_label="LOB3",
                metric_fields=["ActuarialIBNR", "PaidLossandALAE", "CaseReserves"],
                is_group_header=False,
                spans_all_columns=False,
                is_aggregate=False,
                filters=[{"field": "LoB_masked", "value": 3}],
                aggregation="sum",
                rationale=RATIONALE_LOB3,
                component_rows=[],
            ),
            SlideFieldSelection(
                row_label="LOB4",
                metric_fields=["ActuarialIBNR", "PaidLossandALAE", "CaseReserves"],
                is_group_header=False,
                spans_all_columns=False,
                is_aggregate=False,
                filters=[{"field": "LoB_masked", "value": 4}],
                aggregation="sum",
                rationale=RATIONALE_LOB4,
                component_rows=[],
            ),
            SlideFieldSelection(
                row_label="LOB5",
                metric_fields=["ActuarialIBNR", "PaidLossandALAE", "CaseReserves"],
                is_group_header=False,
                spans_all_columns=False,
                is_aggregate=False,
                filters=[{"field": "LoB_masked", "value": 5}],
                aggregation="sum",
                rationale=RATIONALE_LOB5,
                component_rows=[],
            ),
            SlideFieldSelection(
                row_label=LABEL_TOTAL_LOSS_COMPONENT,
                metric_fields=["ActuarialIBNR", "CaseReserves", "PaidLossandALAE"],
                is_group_header=False,
                spans_all_columns=False,
                is_aggregate=True,
                filters=[],
                aggregation="sum",
                rationale=RATIONALE_TOTAL,
                component_rows=["LOB1", "LOB2", "LOB3", "LOB4", "LOB5"],
            ),
            SlideFieldSelection(
                row_label=LABEL_LOSS_COMPONENT_CHANGE,
                metric_fields=[
                    "ActuarialIBNR",
                    "PaidLossandALAE",
                    "CaseReserves",
                    "ULAE",
                    "NonCatLosses",
                    "ChangeInReservesForPolicyholderDividends",
                    "LargeLosses1",
                ],
                is_group_header=True,
                spans_all_columns=True,
                is_aggregate=False,
                filters=[],
                aggregation="sum",
                rationale=RATIONALE_CHANGE,
                component_rows=[],
            ),
        ]

        analyses.append(
            AgentAnalysisResult(
                slide_number=1,
                slide_title="Reserves Summary",
                selected_fields=slide1_fields,
                rationale="High-level overview of reserve positions and claims liability",
            )
        )

        # Slide 2: Line of Business Analysis
        slide2_fields = [
            SlideFieldSelection(
                row_label="Total",
                metric_fields=[
                    "ActuarialIBNR",
                    "PaidLossandALAE",
                    "CaseReserves",
                    "ULAE",
                    "NonCatLosses",
                    "ChangeInReservesForPolicyholderDividends",
                    "LargeLosses1",
                ],
                is_group_header=True,
                spans_all_columns=True,
                is_aggregate=False,
                filters=[],
                aggregation="sum",
                rationale=RATIONALE_TOTAL,
                component_rows=[],
            ),
            SlideFieldSelection(
                row_label="LOB1",
                metric_fields=["ActuarialIBNR", "PaidLossandALAE", "CaseReserves"],
                is_group_header=False,
                spans_all_columns=False,
                is_aggregate=False,
                aggregation="sum",
                filters=[{"field": "LoB_masked", "value": 1}],
                rationale=RATIONALE_LOB1,
                component_rows=[],
            ),
            SlideFieldSelection(
                row_label="LOB2",
                metric_fields=["ActuarialIBNR", "PaidLossandALAE", "CaseReserves"],
                is_group_header=False,
                spans_all_columns=False,
                is_aggregate=False,
                aggregation="sum",
                filters=[{"field": "LoB_masked", "value": 2}],
                rationale=RATIONALE_LOB2,
                component_rows=[],
            ),
            SlideFieldSelection(
                row_label="LOB3",
                metric_fields=["ActuarialIBNR", "PaidLossandALAE", "CaseReserves"],
                is_group_header=False,
                spans_all_columns=False,
                is_aggregate=False,
                aggregation="sum",
                filters=[{"field": "LoB_masked", "value": 3}],
                rationale=RATIONALE_LOB3,
                component_rows=[],
            ),
            SlideFieldSelection(
                row_label="LOB4",
                metric_fields=["ActuarialIBNR", "PaidLossandALAE", "CaseReserves"],
                is_group_header=False,
                spans_all_columns=False,
                is_aggregate=False,
                aggregation="sum",
                filters=[{"field": "LoB_masked", "value": 4}],
                rationale=RATIONALE_LOB4,
                component_rows=[],
            ),
            SlideFieldSelection(
                row_label="LOB5",
                metric_fields=["ActuarialIBNR", "PaidLossandALAE", "CaseReserves"],
                is_group_header=False,
                spans_all_columns=False,
                is_aggregate=False,
                aggregation="sum",
                filters=[{"field": "LoB_masked", "value": 5}],
                rationale=RATIONALE_LOB5,
                component_rows=[],
            ),
            SlideFieldSelection(
                row_label=LABEL_TOTAL_LOSS_COMPONENT,
                metric_fields=["ActuarialIBNR", "CaseReserves", "PaidLossandALAE"],
                is_group_header=False,
                spans_all_columns=False,
                is_aggregate=True,
                filters=[],
                aggregation="sum",
                rationale=RATIONALE_TOTAL,
                component_rows=["LOB1", "LOB2", "LOB3", "LOB4", "LOB5"],
            ),
            SlideFieldSelection(
                row_label=LABEL_LOSS_COMPONENT_CHANGE,
                metric_fields=[
                    "ActuarialIBNR",
                    "PaidLossandALAE",
                    "CaseReserves",
                    "ULAE",
                    "NonCatLosses",
                    "ChangeInReservesForPolicyholderDividends",
                    "LargeLosses1",
                ],
                is_group_header=True,
                spans_all_columns=True,
                is_aggregate=False,
                filters=[],
                aggregation="sum",
                rationale=RATIONALE_CHANGE,
                component_rows=[],
            ),
        ]

        analyses.append(
            AgentAnalysisResult(
                slide_number=2,
                slide_title="Line of Business Breakdown",
                selected_fields=slide2_fields,
                rationale="Detailed breakdown of outstanding claims by line of business",
            )
        )

        # Slide 3: Reserve Development
        slide3_fields = [
            SlideFieldSelection(
                row_label="Total",
                metric_fields=[
                    "ActuarialIBNR",
                    "PaidLossandALAE",
                    "CaseReserves",
                    "ULAE",
                    "NonCatLosses",
                    "ChangeInReservesForPolicyholderDividends",
                    "LargeLosses1",
                ],
                is_group_header=True,
                spans_all_columns=True,
                is_aggregate=False,
                filters=[],
                aggregation="sum",
                rationale=RATIONALE_TOTAL,
                component_rows=[],
            ),
            SlideFieldSelection(
                row_label="LOB1",
                metric_fields=["ActuarialIBNR", "PaidLossandALAE", "CaseReserves"],
                is_group_header=False,
                spans_all_columns=False,
                is_aggregate=False,
                aggregation="sum",
                filters=[{"field": "LoB_masked", "value": 1}],
                rationale=RATIONALE_LOB1,
                component_rows=[],
            ),
            SlideFieldSelection(
                row_label="LOB2",
                metric_fields=["ActuarialIBNR", "PaidLossandALAE", "CaseReserves"],
                is_group_header=False,
                spans_all_columns=False,
                is_aggregate=False,
                aggregation="sum",
                filters=[{"field": "LoB_masked", "value": 2}],
                rationale=RATIONALE_LOB2,
                component_rows=[],
            ),
            SlideFieldSelection(
                row_label="LOB3",
                metric_fields=["ActuarialIBNR", "PaidLossandALAE", "CaseReserves"],
                is_group_header=False,
                spans_all_columns=False,
                is_aggregate=False,
                aggregation="sum",
                filters=[{"field": "LoB_masked", "value": 3}],
                rationale=RATIONALE_LOB3,
                component_rows=[],
            ),
            SlideFieldSelection(
                row_label="LOB4",
                metric_fields=["ActuarialIBNR", "PaidLossandALAE", "CaseReserves"],
                is_group_header=False,
                spans_all_columns=False,
                is_aggregate=False,
                aggregation="sum",
                filters=[{"field": "LoB_masked", "value": 4}],
                rationale=RATIONALE_LOB4,
                component_rows=[],
            ),
            SlideFieldSelection(
                row_label="LOB5",
                metric_fields=["ActuarialIBNR", "PaidLossandALAE", "CaseReserves"],
                is_group_header=False,
                spans_all_columns=False,
                is_aggregate=False,
                aggregation="sum",
                filters=[{"field": "LoB_masked", "value": 5}],
                rationale=RATIONALE_LOB5,
                component_rows=[],
            ),
            SlideFieldSelection(
                row_label=LABEL_TOTAL_LOSS_COMPONENT,
                metric_fields=["ActuarialIBNR", "CaseReserves", "PaidLossandALAE"],
                is_group_header=False,
                spans_all_columns=False,
                is_aggregate=True,
                filters=[],
                aggregation="sum",
                rationale=RATIONALE_TOTAL,
                component_rows=["LOB1", "LOB2", "LOB3", "LOB4", "LOB5"],
            ),
            SlideFieldSelection(
                row_label=LABEL_LOSS_COMPONENT_CHANGE,
                metric_fields=[
                    "ActuarialIBNR",
                    "PaidLossandALAE",
                    "CaseReserves",
                    "ULAE",
                    "NonCatLosses",
                    "ChangeInReservesForPolicyholderDividends",
                    "LargeLosses1",
                ],
                is_group_header=True,
                spans_all_columns=True,
                is_aggregate=False,
                filters=[],
                aggregation="sum",
                rationale=RATIONALE_CHANGE,
                component_rows=[],
            ),
        ]

        analyses.append(
            AgentAnalysisResult(
                slide_number=3,
                slide_title="Reserve Development",
                selected_fields=slide3_fields,
                rationale="Analysis of reserve development and discounting impact",
            )
        )

        return analyses

    def _convert_to_llm_slide_reader(
        self, analysis: AgentAnalysisResult, data_df: pd.DataFrame
    ) -> LLMSlideReader:
        """Convert AgentAnalysisResult to LLMSlideReader format"""
        # Create table headers based on data columns and country columns
        headers = [
            "LOB / Loss Component (in USD millions)",
            "M_country1",
            "M_country2",
            "M_country3",
            "M_country4",
            "M_country5",
            "M_country6",
            "M_country7",
            "M_country8",
            "M_country9",
            "Q4-2023",
            "Q3-23 Close",
        ]

        # Create table rows from selected fields
        rows = []
        for field in analysis.selected_fields:
            if field.is_group_header and field.spans_all_columns:
                # Total row that spans all columns
                row = TableRow(
                    cells=[field.row_label],
                    is_aggregate=False,
                    spans_all_columns=True,
                    if_total_what_row_labels=[],
                )
            elif field.is_aggregate:
                # Aggregate row (Total Loss Component)
                row = TableRow(
                    cells=[field.row_label, "", "", "", "", "", "", "", "", "", "", ""],
                    is_aggregate=True,
                    spans_all_columns=False,
                    if_total_what_row_labels=field.component_rows,
                )
            else:
                # Regular data row (LOB1, LOB2, etc.)
                row = TableRow(
                    cells=[field.row_label, "", "", "", "", "", "", "", "", "", "", ""],
                    is_aggregate=False,
                    spans_all_columns=False,
                    if_total_what_row_labels=[],
                )
            rows.append(row)

        # Create table definition
        table = TableDefinition(headers=headers, rows=rows, position="top")

        # Create commentary based on slide type
        commentary_text = ""
        if "Reserves" in analysis.slide_title:
            commentary_text = "Comments on Loss Component: Comment on the Total Loss Component and the change since previous quarter, outlining the main drivers by segment, BU / Country and LoB combination Include moves driven by FX revaluation Identify key portfolios which may become onerous (e.g. portfolios with combined ratio of 95%+)"
        elif "Line of Business" in analysis.slide_title:
            commentary_text = "Detailed breakdown of outstanding claims by line of business. Analysis includes reserve development and impact by business segment."
        elif "Reserve Development" in analysis.slide_title:
            commentary_text = "Analysis of reserve development patterns and discounting impact across all lines of business."

        commentary = [SlideCommentary(text=commentary_text, position="middle")]

        # Determine if complex visuals are needed
        complex_visuals = len(analysis.selected_fields) > 5

        return LLMSlideReader(
            slide_number=analysis.slide_number,
            slide_header=analysis.slide_title,
            tables=[table],
            commentary=commentary,
            complex_visuals=complex_visuals,
        )

    def _convert_fields_to_llm_slide_reader(
        self,
        slide_number: int,
        slide_title: str,
        fields: List[SlideFieldSelection],
        data_df: pd.DataFrame,
    ) -> LLMSlideReader:
        """Convert SlideFieldSelection list to LLMSlideReader format"""
        # Create table headers based on data columns and country columns
        headers = [
            "LOB / Loss Component (in USD millions)",
            "M_country1",
            "M_country2",
            "M_country3",
            "M_country4",
            "M_country5",
            "M_country6",
            "M_country7",
            "M_country8",
            "M_country9",
            "Q4-2023",
            "Q3-23 Close",
        ]

        # Create table rows from selected fields
        rows = []
        for field in fields:
            if field.is_group_header and field.spans_all_columns:
                # Total row that spans all columns
                row = TableRow(
                    cells=[field.row_label],
                    is_aggregate=False,
                    spans_all_columns=True,
                    if_total_what_row_labels=[],
                )
            elif field.is_aggregate:
                # Aggregate row (Total Loss Component)
                row = TableRow(
                    cells=[field.row_label, "", "", "", "", "", "", "", "", "", "", ""],
                    is_aggregate=True,
                    spans_all_columns=False,
                    if_total_what_row_labels=field.component_rows,
                )
            else:
                # Regular data row (LOB1, LOB2, etc.)
                row = TableRow(
                    cells=[field.row_label, "", "", "", "", "", "", "", "", "", "", ""],
                    is_aggregate=False,
                    spans_all_columns=False,
                    if_total_what_row_labels=[],
                )
            rows.append(row)

        # Create table definition
        table = TableDefinition(headers=headers, rows=rows, position="top")

        # Create commentary based on slide type
        commentary_text = ""
        if "Reserves" in slide_title:
            commentary_text = "Comments on Loss Component: Comment on the Total Loss Component and the change since previous quarter, outlining the main drivers by segment, BU / Country and LoB combination Include moves driven by FX revaluation Identify key portfolios which may become onerous (e.g. portfolios with combined ratio of 95%+)"
        elif "Line of Business" in slide_title:
            commentary_text = "Detailed breakdown of outstanding claims by line of business. Analysis includes reserve development and impact by business segment."
        elif "Reserve Development" in slide_title:
            commentary_text = "Analysis of reserve development patterns and discounting impact across all lines of business."

        commentary = [SlideCommentary(text=commentary_text, position="middle")]

        # Determine if complex visuals are needed
        complex_visuals = len(fields) > 5

        return LLMSlideReader(
            slide_number=slide_number,
            slide_header=slide_title,
            tables=[table],
            commentary=commentary,
            complex_visuals=complex_visuals,
        )

    async def process_slide_update(
        self, slide_number: int, user_fields: List[SlideFieldSelection]
    ):
        """Process user modifications for a specific slide"""
        try:
            async with async_session() as session:
                # Convert Pydantic objects to dict for JSON serialization
                user_fields_dict = [field.dict() for field in user_fields]

                # Update slide with user modifications
                await session.execute(
                    update(Slide)
                    .where(
                        Slide.project_id == self.project_id,
                        Slide.slide_number == slide_number,
                    )
                    .values(
                        user_modified_fields=user_fields_dict,
                        final_fields=user_fields_dict,
                        status="processing",
                    )
                )
                await session.commit()

                await self._send_status(
                    "SLIDE_PROCESSING", f"Processing slide {slide_number}...", 50
                )

                # Regenerate complete PowerPoint presentation with all slides
                await self._send_status(
                    "UPDATING_POWERPOINT",
                    "Updating complete PowerPoint presentation...",
                    70,
                )

                powerpoint_service = PowerPointService(self.project_id)
                ppt_path = await powerpoint_service.generate_complete_presentation()

                # Mark slide as completed
                await session.execute(
                    update(Slide)
                    .where(
                        Slide.project_id == self.project_id,
                        Slide.slide_number == slide_number,
                    )
                    .values(status="completed")
                )
                await session.commit()

                # Send updated slide data back to client
                await self._send_slide_update_complete(slide_number, user_fields)

                await self._send_slide_completed(slide_number)

        except Exception as e:
            await self._send_error(f"Failed to process slide {slide_number}: {str(e)}")

    async def _update_powerpoint_slide(
        self, slide_number: int, fields: List[SlideFieldSelection]
    ):
        """Update specific slide in the consolidated PowerPoint file"""
        # Create downloads directory
        output_dir = Path(f"downloads/{self.project_id}")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Load project data to create table content
        async with async_session() as session:
            result = await session.execute(
                select(Project).where(Project.id == self.project_id)
            )
            project = result.scalar_one()

            # Load data for table generation
            data_df = pd.read_csv(project.data_source_path)

            # Generate table content for this slide
            table_content = self._generate_table_content(slide_number, fields, data_df)

            # Save slide table content
            slide_file = output_dir / f"slide_{slide_number}_table.json"
            with open(slide_file, "w") as f:
                json.dump(table_content, f, indent=2)

        # Update the consolidated PowerPoint file
        await self._update_consolidated_pptm(output_dir)

    def _generate_table_content(
        self,
        slide_number: int,
        fields: List[SlideFieldSelection],
        data_df: pd.DataFrame,
    ):
        """Generate table content for a slide based on selected fields"""
        table_data = {
            "slide_number": slide_number,
            "table_rows": [],
            "updated_at": pd.Timestamp.now().isoformat(),
        }

        for field_selection in fields:
            row_data = {
                "label": field_selection.row_label,
                "is_group_header": field_selection.is_group_header,
                "values": {},
            }

            if field_selection.is_group_header:
                # Group header row - spans all columns
                row_data["spans_all_columns"] = True
                row_data["values"] = {"header": field_selection.row_label}
            else:
                # Data row - calculate values based on metric fields
                for metric_field in field_selection.metric_fields:
                    if metric_field in data_df.columns:
                        if field_selection.aggregation == "sum":
                            value = data_df[metric_field].sum()
                        elif field_selection.aggregation == "average":
                            value = data_df[metric_field].mean()
                        elif field_selection.aggregation == "count":
                            value = data_df[metric_field].count()
                        else:
                            value = data_df[metric_field].sum()

                        # Format value based on field type
                        if metric_field in [
                            "ActuarialIBNR",
                            "PaidLossandALAE",
                            "CaseReserves",
                            "ULAE",
                            "NonCatLosses",
                            "ChangeInReservesForPolicyholderDividends",
                            "LargeLosses1",
                        ]:
                            row_data["values"][metric_field] = f"${value:,.2f}"
                        else:
                            row_data["values"][metric_field] = f"{value:,.0f}"
                    else:
                        row_data["values"][metric_field] = "N/A"

            table_data["table_rows"].append(row_data)

        return table_data

    async def _update_consolidated_pptm(self, output_dir: Path):
        """Update the consolidated PowerPoint file with all slides"""
        pptm_file = output_dir / "analysis_report.pptm"

        # Collect all slide table data
        all_slides_data = {}
        for slide_file in output_dir.glob("slide_*_table.json"):
            with open(slide_file, "r") as f:
                slide_data = json.load(f)
                all_slides_data[slide_data["slide_number"]] = slide_data

        # Create consolidated PowerPoint structure (mock)
        pptm_content = {
            "presentation_title": f"Analysis Report - Project {self.project_id}",
            "slides": all_slides_data,
            "generated_at": pd.Timestamp.now().isoformat(),
            "total_slides": len(all_slides_data),
        }

        # Save consolidated file
        with open(pptm_file, "w") as f:
            json.dump(pptm_content, f, indent=2)

    async def _send_analysis_results(
        self, analyses: List[AgentAnalysisResult]
    ):
        """Send analysis results with data preview to client"""
        # Get project data for preview
        async with async_session() as session:
            result = await session.execute(
                select(Project).where(Project.id == self.project_id)
            )
            project = result.scalar_one()

            # Load data for preview
            data_df = pd.read_csv(project.data_source_path)
            data_preview = data_df.head(10).to_dict("records")  # First 10 rows

        for analysis in analyses:
            # Convert to LLMSlideReader format
            llm_slide_reader = self._convert_to_llm_slide_reader(analysis, data_df)

            await self.websocket_manager.send_to_project(
                self.project_id,
                {
                    "type": "slide_analysis",
                    "slide_number": analysis.slide_number,
                    "slide_title": analysis.slide_title,
                    "row_logic": [
                        field.dict() for field in analysis.selected_fields
                    ],
                    "llm_slide_reader": llm_slide_reader.dict(),
                    "rationale": analysis.rationale,
                    "status": "agent_analyzed",
                    "data_preview": (
                        data_preview if analysis.slide_number == 1 else None
                    ),  # Only send data preview once
                },
            )

        await self._send_status(
            "WAITING_FOR_USER",
            "Analysis complete. PowerPoint ready. Please review and modify slides as needed.",
            100,
        )

    async def _send_slide_update_complete(
        self, slide_number: int, user_fields: List[SlideFieldSelection]
    ):
        """Send updated slide data back to client after update"""
        try:
            async with async_session() as session:
                # Get project data for available fields
                result = await session.execute(
                    select(Project).where(Project.id == self.project_id)
                )
                project = result.scalar_one()

                # Load data for preview
                data_df = pd.read_csv(project.data_source_path)
                data_preview = data_df.head(10).to_dict("records")  # First 10 rows

                # Get updated slide data
                slide_result = await session.execute(
                    select(Slide).where(
                        Slide.project_id == self.project_id,
                        Slide.slide_number == slide_number,
                    )
                )
                slide_data = slide_result.scalar_one()

                # Convert to LLMSlideReader format
                llm_slide_reader = self._convert_fields_to_llm_slide_reader(
                    slide_number, slide_data.slide_title, user_fields, data_df
                )

                await self.websocket_manager.send_to_project(
                    self.project_id,
                    {
                        "type": "slide_update_complete",
                        "slide_number": slide_number,
                        "slide_title": slide_data.slide_title,
                        "user_modified_fields": [field.dict() for field in user_fields],
                        "final_fields": [field.dict() for field in user_fields],
                        "llm_slide_reader": llm_slide_reader.dict(),
                        "status": "completed",
                        "data_preview": data_preview,
                        "message": f"Slide {slide_number} has been updated with your changes",
                    },
                )
        except Exception as e:
            await self._send_error(f"Failed to send slide update data: {str(e)}")

    async def _send_slide_completed(self, slide_number: int):
        """Send slide completion notification"""
        download_url = f"/downloads/{self.project_id}/analysis_report.pptm"

        await self.websocket_manager.send_to_project(
            self.project_id,
            {
                "type": "slide_completed",
                "slide_number": slide_number,
                "status": "completed",
                "download_url": download_url,
                "message": f"Complete PowerPoint presentation updated with all slides including slide {slide_number} changes",
            },
        )

    async def _send_status(self, status: str, message: str, progress: int):
        """Send status update"""
        await self.websocket_manager.send_to_project(
            self.project_id,
            {
                "type": "status_update",
                "status": status,
                "message": message,
                "progress": progress,
            },
        )

    async def _send_error(self, message: str):
        """Send error message"""
        await self.websocket_manager.send_to_project(
            self.project_id, {"type": "error", "message": message}
        )
