#!/usr/bin/env python3
"""
LinkedIn Profile Scraper Function using BrightData API

This module provides a function to scrape LinkedIn profiles and return
structured data in BrightData API format.
"""

import requests
import time
import json
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add agent-memory-client to path
sys.path.insert(0, 'agent-memory-client')

from agent_memory_client import create_memory_client
from agent_memory_client.models import ClientMemoryRecord, MemoryTypeEnum

def get_linkedin_profile_data(profile_url: str) -> dict:
    """
    Get LinkedIn profile data in BrightData API format.
    
    Args:
        profile_url: LinkedIn profile URL to scrape (e.g., "https://www.linkedin.com/in/username/")
        
    Returns:
        dict: Profile data in BrightData API format
        
    Raises:
        Exception: If scraping fails
        
    Example:
        >>> try:
        ...     profile_data = get_linkedin_profile_data("https://www.linkedin.com/in/mamoon-haider/")
        ...     print(f"Name: {profile_data['name']}")
        ... except Exception as e:
        ...     print(f"Failed: {e}")
    """
    
    # Directly attempt to scrape - no file caching
    scraped_data = _scrape_new_profile(profile_url)
    if scraped_data is None:
        raise Exception(f"Failed to scrape LinkedIn profile: {profile_url}")
    
    return scraped_data

async def get_linkedin_profile_data_with_memory(profile_url: str, user_id: str = "scraper_user") -> dict:
    """
    Get LinkedIn profile data using Redis Agent Memory System for caching.
    
    This function checks the agent memory system for cached profile data,
    and if not found, scrapes new data and stores it in memory.
    
    Args:
        profile_url: LinkedIn profile URL to scrape
        user_id: User ID for memory system (default: "scraper_user")
        
    Returns:
        dict: Profile data in BrightData API format
        
    Raises:
        Exception: If scraping fails and no cached data available
    """
    
    # Extract username for memory key
    username = profile_url.rstrip('/').split('/')[-1]
    memory_key = f"linkedin_profile_{username}"
    
    # Initialize memory client
    memory_server_url = os.getenv("MEMORY_SERVER_URL", "http://localhost:8000")
    client = await create_memory_client(
        base_url=memory_server_url,
        default_namespace="linkedin_scraper"
    )
    
    try:
        # Search for cached profile data in memory
        search_results = await client.search_memory_tool(
            query=f"LinkedIn profile data for {username} {profile_url}",
            topics=["linkedin", "profile", username],
            user_id=user_id,
            max_results=1
        )
        
        if search_results['memories']:
            # Found cached data
            memory = search_results['memories'][0]
            try:
                cached_data = json.loads(memory['text'])
                print(f"📂 Using cached profile data from memory system")
                return cached_data
            except json.JSONDecodeError:
                print(f"⚠️ Cached data corrupted, scraping fresh data")
        
        # No cached data found, scrape new data
        print(f"🌐 No cached data in memory, scraping fresh data for: {profile_url}")
        scraped_data = _scrape_new_profile(profile_url)
        
        if scraped_data is None:
            raise Exception(f"Failed to scrape LinkedIn profile: {profile_url}")
        
        # Store scraped data in memory system
        memory_record = ClientMemoryRecord(
            text=json.dumps(scraped_data, ensure_ascii=False),
            memory_type=MemoryTypeEnum.SEMANTIC,
            topics=["linkedin", "profile", username, "scraped_data"],
            entities=[username, scraped_data.get('name', ''), scraped_data.get('current_company', {}).get('name', '')],
            namespace="linkedin_scraper",
            user_id=user_id
        )
        
        await client.create_long_term_memory([memory_record])
        print(f"💾 Stored profile data in memory system")
        
        return scraped_data
        
    finally:
        await client.close()

def get_linkedin_profile_data_with_rams(profile_url: str) -> dict:
    """
    Synchronous wrapper for memory-based LinkedIn profile scraping.
    
    Args:
        profile_url: LinkedIn profile URL to scrape
        
    Returns:
        dict: Profile data in BrightData API format
        
    Raises:
        Exception: If scraping fails
    """
    import asyncio
    return asyncio.run(get_linkedin_profile_data_with_memory(profile_url))

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
            print(f"🔗 URL: {trigger_url}")
            print(f"📦 Params: {params}")
            print(f"📄 Data: {data}")
            
            response = requests.post(trigger_url, headers=headers, params=params, json=data)
            
            print(f"📊 Response status: {response.status_code}")
            print(f"📝 Response text: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                snapshot_id = result.get('snapshot_id')
                print(f"✅ Job started! Snapshot ID: {snapshot_id}")
                break
            else:
                print(f"❌ Attempt {i+1} failed with status: {response.status_code}")
                if i < len(payloads_to_try) - 1:
                    print("🔄 Trying alternative payload format...")
                    continue
                
        except Exception as e:
            print(f"❌ Error in attempt {i+1}: {e}")
            if i < len(payloads_to_try) - 1:
                print("🔄 Trying alternative payload format...")
                continue
    
    if not snapshot_id:
        print("❌ All BrightData attempts failed")
        # No fallback demo data - return None to indicate failure
        return None
    
    # Step 2: Wait for completion and get results
    results_url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}"
    
    print(f"📥 Waiting for completion...")
    max_attempts = 15  # Increased attempts for longer scraping jobs
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(results_url, headers=headers)
            print(f"🔍 Attempt {attempt + 1}: Status {response.status_code}")
            
            if response.status_code == 200:
                # Check if we have actual data or status info
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
                        # This might be the actual profile data
                        print(f"✅ Scraping completed!")
                        return result
                except json.JSONDecodeError:
                    # Try to parse as JSONL (multiple JSON objects)
                    lines = response.text.strip().split('\n')
                    if lines and lines[0]:
                        try:
                            profile_data = json.loads(lines[0])
                            print(f"✅ Scraping completed!")
                            return profile_data
                        except json.JSONDecodeError:
                            print(f"❌ Failed to parse response as JSON")
                            return None
            elif response.status_code == 202:
                # 202 means still processing - this is normal
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
                print(f"❌ Unexpected status code: {response.status_code}")
                print(f"📝 Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error checking results: {e}")
            return None
    
    print("⏰ Scraping takes longer than expected")
    return None

def format_profile_output(profile_data: dict) -> str:
    """
    Format profile data as JSON string with activity summary.
    
    Args:
        profile_data: Profile data dictionary
        
    Returns:
        str: Formatted JSON string with activity summary
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

async def clear_rams_cache():
    """Clear RAMS cache for testing."""
    memory_server_url = os.getenv("MEMORY_SERVER_URL", "http://localhost:8000")
    client = await create_memory_client(
        base_url=memory_server_url,
        default_namespace="linkedin_scraper"
    )
    
    try:
        # Search for all LinkedIn memories
        search_results = await client.search_memory_tool(
            query="LinkedIn profile data",
            topics=["linkedin", "profile"],
            max_results=10
        )
        
        if search_results['memories']:
            memory_ids = [memory['id'] for memory in search_results['memories'] if memory.get('id')]
            if memory_ids:
                await client.delete_long_term_memories(memory_ids)
                print(f"🗑️ Cleared {len(memory_ids)} cached memories from RAMS")
            else:
                print("⚠️ No memory IDs found to delete")
        else:
            print("📭 No cached memories found in RAMS")
            
    finally:
        await client.close()

async def smart_linkedin_scraper(profile_url: str, user_id: str = "scraper_user") -> dict:
    """
    Smart LinkedIn scraper that first checks RAMS, then falls back to BrightData.
    
    Args:
        profile_url: LinkedIn profile URL to scrape
        user_id: User ID for memory system
        
    Returns:
        dict: Profile data in BrightData API format
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
            min_relevance=0.5  # Lower relevance threshold to find stored data
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
        
        # Step 3: Check if this exact profile is already in RAMS before storing
        existing_check = await client.search_memory_tool(
            query=f"LinkedIn profile {username}",
            topics=["linkedin", "profile", username],
            user_id=user_id,
            max_results=5,  # Check more results to be sure
            min_relevance=0.3  # Lower threshold to catch existing entries
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

def main():
    """Main function demonstrating smart LinkedIn scraping with RAMS-first approach."""
    
    # Test URL - use Mamoon profile to test activity summarization
    test_url = "https://www.linkedin.com/in/niels-schmidt-890b96303/"
    
    print("🧪 Smart LinkedIn Profile Scraper")
    print("🔄 Strategy: RAMS first → BrightData fallback")
    print("="*60)
    
    import asyncio
    
    try:
        # Use smart scraper that checks RAMS first, then BrightData
        profile_data = asyncio.run(smart_linkedin_scraper(test_url))
        
        print("✅ Smart scraping successful!")
        print(f"📊 Profile: {profile_data.get('name', 'Unknown')}")
        print(f"🏢 Company: {profile_data.get('current_company', {}).get('name', 'Unknown')}")
        
        # Display formatted JSON
        formatted_output = format_profile_output(profile_data)
        print(f"\n📄 Structured JSON Output:")
        print(formatted_output)
        
    except Exception as e:
        print(f"❌ Smart scraping failed: {e}")
    
    print(f"\n" + "="*60)
    print("🏁 Smart scraping completed!")

if __name__ == "__main__":
    main()
