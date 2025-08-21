import asyncio
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List
from models import SlideFieldSelection, FieldItem, AgentAnalysisResult
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
                    agent_fields_dict = [field.dict() for field in analysis.selected_fields]
                    
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
                    slide_analyses, list(schema_data.keys())
                )

        except Exception as e:
            await self._send_error(f"Analysis failed: {str(e)}")

    async def _analyze_slides(
        self, data_df: pd.DataFrame, schema_data: dict
    ) -> List[AgentAnalysisResult]:
        """Analyze data and suggest fields for each slide"""
        await asyncio.sleep(2)  # Simulate AI processing

        analyses = []

        # Slide 1: Overview/Summary
        slide1_fields = [
            SlideFieldSelection(
                row_label="Total Revenue",
                metric_fields=["sales_amount"],
                is_group_header=False,
                aggregation="sum",
                rationale="Primary revenue metric for overview",
            ),
            SlideFieldSelection(
                row_label="Units Sold",
                metric_fields=["units_sold"],
                is_group_header=False,
                aggregation="sum",
                rationale="Volume metric to complement revenue",
            ),
        ]

        analyses.append(
            AgentAnalysisResult(
                slide_number=1,
                slide_title="Executive Summary",
                selected_fields=slide1_fields,
                rationale="Overview slide showing key performance indicators",
            )
        )

        # Slide 2: Regional Analysis
        slide2_fields = [
            SlideFieldSelection(
                row_label="Revenue by Region",
                metric_fields=["sales_amount", "region"],
                is_group_header=True,
                aggregation="sum",
                rationale="Regional breakdown is crucial for geographic insights",
            ),
            SlideFieldSelection(
                row_label="Units by Region",
                metric_fields=["units_sold", "region"],
                is_group_header=False,
                aggregation="sum",
                rationale="Volume metrics by region to understand market penetration",
            ),
        ]

        analyses.append(
            AgentAnalysisResult(
                slide_number=2,
                slide_title="Regional Performance",
                selected_fields=slide2_fields,
                rationale="Regional analysis helps identify top-performing markets",
            )
        )

        # Slide 3: Product Analysis
        slide3_fields = [
            SlideFieldSelection(
                row_label="Product Performance",
                metric_fields=["sales_amount", "product"],
                is_group_header=True,
                aggregation="sum",
                rationale="Product-level insights for portfolio analysis",
            ),
            SlideFieldSelection(
                row_label="Product Volume",
                metric_fields=["units_sold", "product"],
                is_group_header=False,
                aggregation="sum",
                rationale="Understanding product popularity by volume",
            ),
        ]

        analyses.append(
            AgentAnalysisResult(
                slide_number=3,
                slide_title="Product Analysis",
                selected_fields=slide3_fields,
                rationale="Product analysis reveals bestsellers and underperformers",
            )
        )

        return analyses

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
                    "UPDATING_POWERPOINT", "Updating complete PowerPoint presentation...", 70
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
            result = await session.execute(select(Project).where(Project.id == self.project_id))
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

    def _generate_table_content(self, slide_number: int, fields: List[SlideFieldSelection], data_df: pd.DataFrame):
        """Generate table content for a slide based on selected fields"""
        table_data = {
            "slide_number": slide_number,
            "table_rows": [],
            "updated_at": pd.Timestamp.now().isoformat()
        }
        
        for field_selection in fields:
            row_data = {
                "label": field_selection.row_label,
                "is_group_header": field_selection.is_group_header,
                "values": {}
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
                        if metric_field in ["sales_amount"]:
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
            "total_slides": len(all_slides_data)
        }
        
        # Save consolidated file
        with open(pptm_file, "w") as f:
            json.dump(pptm_content, f, indent=2)

    async def _send_analysis_results(
        self, analyses: List[AgentAnalysisResult], all_fields: List[str]
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
            
        # Convert all fields to FieldItem format
        field_items = [
            FieldItem(
                field_name=field,
                description=f"Description for {field}",
                type=(
                    "numeric"
                    if field in ["sales_amount", "units_sold"] or data_df[field].dtype in ['int64', 'float64']
                    else "categorical"
                ),
            )
            for field in all_fields if field in data_df.columns
        ]

        for analysis in analyses:
            # Generate table preview for this slide
            table_preview = await self._generate_table_preview(analysis, data_df)
            
            await self.websocket_manager.send_to_project(
                self.project_id,
                {
                    "type": "slide_analysis",
                    "slide_number": analysis.slide_number,
                    "slide_title": analysis.slide_title,
                    "agent_selected_fields": [
                        field.dict() for field in analysis.selected_fields
                    ],
                    "all_available_fields": [field.dict() for field in field_items],
                    "rationale": analysis.rationale,
                    "status": "agent_analyzed",
                    "table_preview": table_preview,
                    "data_preview": data_preview if analysis.slide_number == 1 else None,  # Only send data preview once
                },
            )

        await self._send_status(
            "WAITING_FOR_USER",
            "Analysis complete. PowerPoint ready. Please review and modify slides as needed.",
            100,
        )

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

    async def _generate_table_preview(self, analysis: AgentAnalysisResult, data_df: pd.DataFrame) -> Dict:
        """Generate table preview for a slide"""
        try:
            # Get all unique metric fields for this slide
            all_metric_fields = []
            for field in analysis.selected_fields:
                if field.metric_fields:
                    for metric in field.metric_fields:
                        if metric not in all_metric_fields and metric in data_df.columns:
                            all_metric_fields.append(metric)
            
            if not all_metric_fields:
                return {"headers": [], "rows": []}
            
            # Create table structure
            headers = [""] + [field.replace("_", " ").title() for field in all_metric_fields]
            rows = []
            
            for field in analysis.selected_fields:
                row = [field.row_label]
                
                for metric_field in all_metric_fields:
                    if metric_field in (field.metric_fields or []):
                        # Calculate value
                        if field.aggregation == "sum":
                            value = data_df[metric_field].sum()
                        elif field.aggregation == "average" or field.aggregation == "mean":
                            value = data_df[metric_field].mean()
                        elif field.aggregation == "count":
                            value = data_df[metric_field].count()
                        else:
                            value = data_df[metric_field].sum()
                        
                        # Format value
                        if "amount" in metric_field.lower() or "sales" in metric_field.lower():
                            formatted_value = f"${value:,.2f}"
                        elif metric_field in ["units_sold", "quantity"]:
                            formatted_value = f"{value:,.0f}"
                        else:
                            formatted_value = f"{value:,.2f}"
                        
                        row.append(formatted_value)
                    else:
                        row.append("")
                
                rows.append({
                    "values": row,
                    "is_group_header": field.is_group_header,
                    "spans_all_columns": getattr(field, 'spans_all_columns', False)
                })
            
            return {
                "headers": headers,
                "rows": rows,
                "metric_fields": all_metric_fields
            }
            
        except Exception as e:
            print(f"Error generating table preview: {e}")
            return {"headers": [], "rows": [], "error": str(e)}

    async def _send_error(self, message: str):
        """Send error message"""
        await self.websocket_manager.send_to_project(
            self.project_id, {"type": "error", "message": message}
        )
