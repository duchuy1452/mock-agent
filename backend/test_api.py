#!/usr/bin/env python3
"""
Test script for Expert Sure Backend API
Demonstrates the complete workflow
"""

import asyncio
import aiohttp
import json
import websockets
from pathlib import Path

API_BASE = "http://localhost:8000"
WS_BASE = "ws://localhost:8000"

async def test_api_workflow():
    """Test the complete API workflow"""
    
    print("🧪 Testing Expert Sure Backend API")
    print("=" * 50)
    
    # Test 1: Check if server is running
    print("\n1. Testing server connection...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE}/") as response:
                data = await response.json()
                print(f"✅ Server is running: {data['message']}")
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        return
    
    # Test 2: Get projects list (should be empty initially)
    print("\n2. Getting projects list...")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE}/api/projects") as response:
            projects = await response.json()
            print(f"✅ Projects found: {len(projects['projects'])}")
    
    # Test 3: Create a new project
    print("\n3. Creating new project...")
    
    # Check if test files exist
    data_file = Path("../data.csv")
    schema_file = Path("../field.json")
    
    if not data_file.exists() or not schema_file.exists():
        print("❌ Test files not found. Make sure data.csv and field.json exist in parent directory.")
        return
    
    # Create form data for upload
    form_data = aiohttp.FormData()
    form_data.add_field('name', 'Test IFRS Project')
    form_data.add_field('auto', 'false')
    
    with open(data_file, 'rb') as f:
        form_data.add_field('data_source', f, filename='data.csv')
    
    with open(schema_file, 'rb') as f:
        form_data.add_field('schema', f, filename='field.json')
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_BASE}/api/projects", data=form_data) as response:
            if response.status == 200:
                project_data = await response.json()
                project_id = project_data['project_id']
                print(f"✅ Project created: {project_id}")
                print(f"   Available fields: {project_data['available_fields']}")
            else:
                error = await response.text()
                print(f"❌ Project creation failed: {error}")
                return
    
    # Test 4: WebSocket interaction
    print(f"\n4. Testing WebSocket interaction...")
    
    websocket_url = f"{WS_BASE}/ws/{project_id}"
    
    try:
        async with websockets.connect(websocket_url) as websocket:
            
            # Wait for connection confirmation
            response = await websocket.recv()
            data = json.loads(response)
            print(f"✅ WebSocket connected: {data['message']}")
            
            # Send field selection
            print("\n   Sending field selection...")
            field_selection = {
                "type": "field_selection",
                "field_config": {
                    "A": {"selected": True, "analysis_type": "trend"},
                    "C": {"selected": True, "analysis_type": "risk"}
                }
            }
            await websocket.send(json.dumps(field_selection))
            
            # Wait for field selection response
            response = await websocket.recv()
            data = json.loads(response)
            print(f"✅ Field selection response: {data['status']}")
            
            # Send proceed command
            print("\n   Sending proceed command...")
            proceed_command = {
                "type": "proceed_processing",
                "confirmed": True
            }
            await websocket.send(json.dumps(proceed_command))
            
            # Listen for updates (for 30 seconds max)
            print("\n   Listening for real-time updates:")
            updates_received = 0
            
            try:
                while updates_received < 20:  # Limit number of updates
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(response)
                    
                    if data['type'] == 'status_update':
                        print(f"   📊 Status: {data['status']} - {data['message']}")
                    elif data['type'] == 'slide_generated':
                        print(f"   📄 Slide {data['slide_number']}: {data['slide_title']}")
                    elif data['type'] == 'file_ready':
                        print(f"   📁 File ready: {data['file_name']} ({data['file_size']})")
                    elif data['type'] == 'outputs_ready':
                        print(f"   📊 Outputs ready: CSV data and markdown report")
                    
                    updates_received += 1
                    
            except asyncio.TimeoutError:
                print("   ⏰ Listening timeout reached")
            
            # Test chat functionality
            print("\n   Testing RAG chat...")
            chat_query = {
                "type": "chat_query",
                "message": "What are the key insights from Field A analysis?"
            }
            await websocket.send(json.dumps(chat_query))
            
            response = await websocket.recv()
            data = json.loads(response)
            if data['type'] == 'chat_response':
                print(f"   💬 Chat response: {data['message'][:100]}...")
    
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
    
    # Test 5: Get updated project details
    print(f"\n5. Getting updated project details...")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE}/api/projects/{project_id}") as response:
            if response.status == 200:
                project = await response.json()
                print(f"✅ Project status: {project['status']}")
                print(f"   Slides generated: {len(project['slides'])}")
                print(f"   Outputs available: {len(project['outputs'])}")
            else:
                print(f"❌ Failed to get project details")
    
    print("\n" + "=" * 50)
    print("✅ API workflow test completed!")
    print("\n💡 Next steps:")
    print("   - Open http://localhost:8000/docs for interactive API testing")
    print("   - Check downloads/ folder for generated PowerPoint files")
    print("   - Build frontend to integrate with these APIs")

if __name__ == "__main__":
    print("Make sure the backend server is running (python run.py)")
    print("Press Enter to start testing...")
    input()
    
    asyncio.run(test_api_workflow()) 