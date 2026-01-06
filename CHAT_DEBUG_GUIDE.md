# Chat Debug Guide

## Issues Identified and Fixes Applied

### 1. Backend Import Error (FIXED)
**Problem**: `RateLimitMiddleware` was missing from rate_limit.py
**Fix**: Added the missing `RateLimitMiddleware` class and `reset_rate_limits` function

### 2. Chat Store Bug (FIXED)  
**Problem**: Chat store referenced `conversationId` instead of `activeConversationId`
**Fix**: Changed `get().conversationId` to `get().activeConversationId`

### 3. Missing Debugging (ADDED)
**Problem**: No visibility into what's failing
**Fix**: Added console.log statements to:
- Chat page handlers
- Chat store functions
- getUserId helper

## Current Status

✅ Backend is running on port 8000
✅ Frontend is running on port 3000  
✅ API health check passes
✅ Import errors fixed

## To Test the Chat Functionality

### Step 1: Login First
1. Go to http://localhost:3000/login
2. Create an account or login with existing credentials
3. This will generate the JWT token needed for API calls

### Step 2: Access Chat Page
1. Go to http://localhost:3000/dashboard/chat
2. Open browser developer tools (F12)
3. Check the Console tab for debug messages

### Step 3: Test New Conversation
1. Click "Start New Chat" button
2. Check console for debug messages starting with `[Chat]`
3. Look for any error messages

### Step 4: Test Sending Messages
1. If conversation is created, try typing a message
2. Click send or press Enter
3. Check console for API call results

## Expected Debug Output

When working correctly, you should see:
```
[Chat Store] getUserId - authState: {user: {...}, token: "...", ...}
[Chat Store] getUserId - returning: "user-id-here"
[Chat Store] fetchConversations - userId: user-id-here
[Chat Store] Calling api.getConversations...
[Chat Store] Got conversations: [...]
```

## Common Issues

### "User not authenticated"
- User needs to login first
- JWT token not generated/stored properly
- Check localStorage for "bearer_token"

### "Failed to load conversations"  
- Backend API not responding
- Database connection issues
- CORS problems

### "Failed to create conversation"
- Authentication token invalid/expired
- Backend endpoint not working
- Database write permissions

## Next Steps

1. **Test with a logged-in user** - This is the most likely issue
2. **Check browser console** - Look for specific error messages
3. **Verify API endpoints** - Test with curl if needed
4. **Check database connection** - Ensure Neon DB is accessible

## Manual API Testing

If you want to test the API directly:

```bash
# First, get a JWT token by logging in through the frontend
# Then test the endpoints:

# Test conversations endpoint
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/YOUR_USER_ID/conversations

# Test create conversation
curl -X POST \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"title": "Test Chat"}' \
     http://localhost:8000/api/YOUR_USER_ID/conversations
```

The debugging output will help identify exactly where the issue is occurring.
