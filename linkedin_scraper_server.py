#!/usr/bin/env python3
"""
LinkedIn Profile Scraper REST Server

A FastAPI server that provides a REST endpoint for scraping LinkedIn profiles
using the RAMS-first strategy (Redis Agent Memory System → BrightData fallback).
"""

import asyncio
import json
import os
import sys
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add agent-memory-client to path
sys.path.insert(0, 'agent-memory-client')

from agent_memory_client import create_memory_client
from agent_memory_client.models import ClientMemoryRecord, MemoryTypeEnum

# Import scraping functions - we'll copy them here since import is problematic
import requests
import time

# === LinkedIn Scraping Functions ===

def _scrape_new_profile(profile_url: str) -> dict | None:
    """Internal function to scrape a new profile from BrightData API only."""
    
    # BrightData API configuration
    headers = {
        "Authorization": "Bearer 769112ce8d4fcae5065255c07f7a6e7b91f7fbb114dd965d166cc8c6c56e826a",
        "Content-Type": "application/json",
    }
    
    # Step 1: Start scraping job
    trigger_url = "https://api.brightdata.com/datasets/v3/trigger"
    params = {
        "dataset_id": "gd_l1viktl72bvl7bjuj0",
        "include_errors": "true",
    }
    
    # Try different payload formats and API approaches
    payloads_to_try = [
        # Format 1: Simple URL only
        [{"url": profile_url}],
        # Format 2: With endpoint parameter
        [{"url": profile_url, "endpoint": "linkedin_profile"}],
        # Format 3: With different endpoint value
        [{"url": profile_url, "endpoint": "linkedin"}],
        # Format 4: With additional parameters
        [{"url": profile_url, "include_skills": True}],
    ]
    
    snapshot_id = None
    
    for i, data in enumerate(payloads_to_try):
        try:
            print(f"🚀 Starting scraping job (attempt {i+1})...")
            response = requests.post(trigger_url, headers=headers, params=params, json=data)
            
            if response.status_code == 200:
                result = response.json()
                snapshot_id = result.get('snapshot_id')
                print(f"✅ Job started! Snapshot ID: {snapshot_id}")
                break
            else:
                print(f"❌ Attempt {i+1} failed with status: {response.status_code}")
                if i < len(payloads_to_try) - 1:
                    continue
                
        except Exception as e:
            print(f"❌ Error in attempt {i+1}: {e}")
            if i < len(payloads_to_try) - 1:
                continue
    
    if not snapshot_id:
        print("❌ All BrightData attempts failed")
        return None
    
    # Step 2: Wait for completion and get results
    results_url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}"
    
    print(f"📥 Waiting for completion...")
    max_attempts = 15
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(results_url, headers=headers)
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if isinstance(result, dict) and result.get('status') == 'running':
                        print(f"🔄 Still processing... ({attempt + 1}/{max_attempts})")
                        time.sleep(10)
                        continue
                    elif isinstance(result, dict) and 'status' in result:
                        print(f"📊 Job status: {result.get('status')}")
                        time.sleep(10)
                        continue
                    else:
                        print(f"✅ Scraping completed!")
                        return result
                except json.JSONDecodeError:
                    lines = response.text.strip().split('\n')
                    if lines and lines[0]:
                        try:
                            profile_data = json.loads(lines[0])
                            print(f"✅ Scraping completed!")
                            return profile_data
                        except json.JSONDecodeError:
                            return None
            elif response.status_code == 202:
                try:
                    result = response.json()
                    if result.get('status') == 'running':
                        print(f"🔄 Still processing... ({attempt + 1}/{max_attempts}) - {result.get('message', '')}")
                    else:
                        print(f"🔄 Still processing... ({attempt + 1}/{max_attempts})")
                except json.JSONDecodeError:
                    print(f"🔄 Still processing... ({attempt + 1}/{max_attempts})")
                time.sleep(10)
                continue
            else:
                return None
                
        except Exception as e:
            return None
    
    print("⏰ Scraping takes longer than expected")
    return None

async def smart_linkedin_scraper(profile_url: str, user_id: str = "scraper_user") -> dict:
    """
    Smart LinkedIn scraper that first checks RAMS, then falls back to BrightData.
    """
    
    # Extract username for memory key
    username = profile_url.rstrip('/').split('/')[-1]
    
    # Initialize memory client
    memory_server_url = os.getenv("MEMORY_SERVER_URL", "http://localhost:8000")
    client = await create_memory_client(
        base_url=memory_server_url,
        default_namespace="linkedin_scraper"
    )
    
    try:
        # Step 1: Check RAMS first
        print(f"🔍 Checking RAMS for cached data for username: {username}")
        search_results = await client.search_memory_tool(
            query=f"LinkedIn profile {username}",
            topics=["linkedin", "profile", username],
            user_id=user_id,
            max_results=1,
            min_relevance=0.5
        )
        
        if search_results['memories']:
            # Found cached data in RAMS
            memory = search_results['memories'][0]
            try:
                cached_data = json.loads(memory['text'])
                print(f"📂 ✅ Found cached data in RAMS!")
                return cached_data
            except json.JSONDecodeError:
                print(f"⚠️ Cached data corrupted, falling back to BrightData")
        
        # Step 2: No cached data found, use BrightData
        print(f"🌐 No cached data in RAMS, scraping from BrightData...")
        scraped_data = _scrape_new_profile(profile_url)
        
        if scraped_data is None:
            raise Exception(f"Failed to scrape LinkedIn profile: {profile_url}")
        
        # Step 3: Check if this profile is already in RAMS before storing
        existing_check = await client.search_memory_tool(
            query=f"LinkedIn profile {username}",
            topics=["linkedin", "profile", username],
            user_id=user_id,
            max_results=5,
            min_relevance=0.3
        )
        
        # Check if any existing memory contains the same username
        profile_already_exists = False
        if existing_check['memories']:
            for memory in existing_check['memories']:
                try:
                    existing_data = json.loads(memory['text'])
                    existing_username = existing_data.get('linkedin_id') or existing_data.get('id')
                    if existing_username == username:
                        profile_already_exists = True
                        print(f"📝 Profile for {username} already exists in RAMS, skipping storage")
                        break
                except json.JSONDecodeError:
                    continue
        
        if not profile_already_exists:
            # Store profile data and activities separately in RAMS
            memories_to_store = []
            
            # 1. Store main profile data
            profile_record = ClientMemoryRecord(
                text=json.dumps(scraped_data, ensure_ascii=False),
                memory_type=MemoryTypeEnum.SEMANTIC,
                topics=["linkedin", "profile", username, "scraped_data"],
                entities=[username, scraped_data.get('name', ''), scraped_data.get('current_company', {}).get('name', '')],
                namespace="linkedin_scraper",
                user_id=user_id
            )
            memories_to_store.append(profile_record)
            
            # 2. Store activities as separate memories for Q&A
            if 'activity' in scraped_data and scraped_data['activity']:
                for i, activity in enumerate(scraped_data['activity'][:10]):  # Limit to 10 most recent
                    activity_text = f"{username} activity: {activity.get('interaction', 'Unknown')} - {activity.get('title', 'No title')[:100]}"
                    
                    activity_record = ClientMemoryRecord(
                        text=activity_text,
                        memory_type=MemoryTypeEnum.EPISODIC,
                        topics=["linkedin", "activity", username, "engagement"],
                        entities=[username, scraped_data.get('name', '')],
                        namespace="linkedin_scraper",
                        user_id=user_id
                    )
                    memories_to_store.append(activity_record)
            
            # Store all memories at once
            await client.create_long_term_memory(memories_to_store)
            print(f"💾 Stored profile data + {len(memories_to_store)-1} activities for {username} in RAMS")
        
        return scraped_data
        
    finally:
        await client.close()

def format_profile_output(profile_data: dict) -> str:
    """
    Format profile data as JSON string with activity summary.
    """
    # Create a copy to avoid modifying original data
    formatted_data = profile_data.copy()
    
    # Summarize activities if they exist
    if 'activity' in formatted_data and formatted_data['activity']:
        activities = formatted_data['activity']
        
        # Count different interaction types
        interaction_counts = {}
        for activity in activities:
            interaction = activity.get('interaction', 'Unknown interaction')
            interaction_type = interaction.split(' by ')[0] if ' by ' in interaction else interaction
            interaction_counts[interaction_type] = interaction_counts.get(interaction_type, 0) + 1
        
        # Create summary statistics
        total_activities = len(activities)
        interaction_stats = ', '.join([f"{count} {interaction_type.lower()}" for interaction_type, count in interaction_counts.items()])
        
        activity_summary = f"User has {total_activities} recent activities: {interaction_stats}."
        
        # Replace activities with summary
        formatted_data['activity_summary'] = activity_summary
        del formatted_data['activity']  # Remove detailed activities
    
    return json.dumps(formatted_data, indent=2, ensure_ascii=False)

app = FastAPI(
    title="LinkedIn Profile Scraper API",
    description="REST API for scraping LinkedIn profiles with RAMS caching",
    version="1.0.0"
)

class LinkedInRequest(BaseModel):
    """Request model for LinkedIn profile scraping."""
    url: HttpUrl
    user_id: str = "api_user"

class LinkedInResponse(BaseModel):
    """Response model for LinkedIn profile data."""
    success: bool
    profile_data: Dict[str, Any] | None = None
    formatted_output: str | None = None
    error: str | None = None
    cached: bool = False

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "LinkedIn Profile Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "scrape": "/scrape - POST LinkedIn URL to get profile data",
            "health": "/health - Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test RAMS connection
        memory_server_url = os.getenv("MEMORY_SERVER_URL", "http://localhost:8000")
        client = await create_memory_client(
            base_url=memory_server_url,
            default_namespace="linkedin_scraper"
        )
        await client.health_check()
        await client.close()
        
        return {
            "status": "healthy",
            "rams_connection": "ok",
            "timestamp": "2025-09-19T22:48:00Z"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "rams_connection": "failed",
                "error": str(e)
            }
        )

@app.post("/scrape", response_model=LinkedInResponse)
async def scrape_linkedin_profile(request: LinkedInRequest):
    """
    Scrape LinkedIn profile with RAMS-first strategy.
    
    Args:
        request: LinkedInRequest with URL and optional user_id
        
    Returns:
        LinkedInResponse with profile data or error
        
    Example:
        POST /scrape
        {
            "url": "https://www.linkedin.com/in/username/",
            "user_id": "api_user"
        }
    """
    
    try:
        # Convert HttpUrl to string
        profile_url = str(request.url)
        
        # Extract username for logging
        username = profile_url.rstrip('/').split('/')[-1]
        
        print(f"🔍 API Request: Scraping profile for {username}")
        
        # Use the smart scraper with RAMS-first strategy
        profile_data = await smart_linkedin_scraper(profile_url, request.user_id)
        
        # Format the output
        formatted_output = format_profile_output(profile_data)
        
        # Check if data came from cache (heuristic: no timestamp means cached)
        cached = not profile_data.get('timestamp')
        
        print(f"✅ API Response: Successfully returned profile for {username}")
        
        return LinkedInResponse(
            success=True,
            profile_data=profile_data,
            formatted_output=formatted_output,
            cached=cached
        )
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ API Error: {error_msg}")
        
        return LinkedInResponse(
            success=False,
            error=error_msg
        )

@app.get("/scrape/{username}")
async def scrape_by_username(username: str, user_id: str = "api_user"):
    """
    Scrape LinkedIn profile by username (convenience endpoint).
    
    Args:
        username: LinkedIn username (e.g., "mamoon-haider")
        user_id: Optional user ID for RAMS
        
    Returns:
        LinkedInResponse with profile data or error
    """
    
    # Construct LinkedIn URL
    linkedin_url = f"https://www.linkedin.com/in/{username}/"
    
    # Create request object
    request = LinkedInRequest(url=linkedin_url, user_id=user_id)
    
    # Use the main scraping endpoint
    return await scrape_linkedin_profile(request)

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting LinkedIn Profile Scraper REST Server")
    print("📡 Endpoints:")
    print("   POST /scrape - Scrape LinkedIn profile")
    print("   GET  /scrape/{username} - Scrape by username")
    print("   GET  /health - Health check")
    print("   GET  / - API info")
    print("="*60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )