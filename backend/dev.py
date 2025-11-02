#!/usr/bin/env python3
"""
Development/Testing script for ScheinCam Backend
Run this to test the backend without Docker
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_services():
    """Test all services"""
    print("🧪 Testing ScheinCam Services...\n")
    
    from app.services.obs_service import OBSService
    from app.services.file_service import FileService
    from app.services.recording_scheduler import RecordingScheduler
    from app.core.config import settings
    
    # Test OBS Service
    print("📹 Testing OBS Service...")
    obs = OBSService()
    await obs.configure(
        host=settings.OBS_HOST,
        port=settings.OBS_PORT,
        password=settings.OBS_PASSWORD
    )
    await asyncio.sleep(2)  # Give it time to connect
    print(f"   OBS Connected: {obs.connected}")
    print(f"   OBS Recording: {obs.recording}")
    print(f"   OBS Muted: {obs.muted}\n")
    
    # Test File Service
    print("📁 Testing File Service...")
    file_service = FileService()
    await file_service.initialize(delete_age=settings.delete_age)
    print(f"   Videos found: {len(file_service.files)}")
    if file_service.files:
        print(f"   Newest video: {file_service.get_newest_file().filename}")
    print()
    
    # Test Scheduler
    print("⏰ Testing Recording Scheduler...")
    scheduler = RecordingScheduler(obs, file_service)
    print(f"   Scheduler initialized")
    print(f"   Is recording time: {scheduler._is_recording_time()}")
    print()
    
    # Cleanup
    await obs.disconnect()
    print("✅ All tests completed!")


async def start_dev_server():
    """Start development server"""
    print("🚀 Starting ScheinCam Development Server...\n")
    
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ScheinCam Backend Dev Tools")
    parser.add_argument(
        "command",
        choices=["test", "serve"],
        help="Command to run (test=run tests, serve=start dev server)"
    )
    
    args = parser.parse_args()
    
    if args.command == "test":
        asyncio.run(test_services())
    elif args.command == "serve":
        asyncio.run(start_dev_server())
