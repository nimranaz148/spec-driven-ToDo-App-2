/**
 * ChatKit proxy API route.
 *
 * This route acts as a proxy between ChatKit React frontend and the backend
 * /api/chatkit endpoint (ChatKit Python SDK).
 *
 * The proxy simply forwards the request body and auth to the backend,
 * which handles the ChatKit protocol natively via the ChatKit Python SDK.
 */

import { NextRequest } from 'next/server';

export const runtime = 'edge';
export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest) {
  try {
    // Get the raw request body to pass through to backend
    const body = await request.arrayBuffer();
    console.log('[ChatKit Proxy] Forwarding request to backend ChatKit endpoint');

    // Get auth token from cookies or headers
    const authTokenFromHeader = request.headers.get('Authorization')?.replace('Bearer ', '');
    const authTokenFromCookie = request.cookies.get('bearer_token')?.value;
    const authToken = authTokenFromHeader || authTokenFromCookie;

    console.log('[ChatKit Proxy] Auth token:', authToken ? `YES (${authToken.length} chars)` : 'NO');

    if (!authToken) {
      console.error('[ChatKit Proxy] No auth token found!');
      return new Response(
        JSON.stringify({ error: 'Unauthorized - no token found in header or cookie' }),
        { status: 401, headers: { 'Content-Type': 'application/json' } }
      );
    }

    // Forward to backend ChatKit endpoint with query params
    const url = new URL(request.url);
    const queryString = url.search; // Includes ?conversation_id=X if present
    const backendUrl = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/chatkit${queryString}`;
    console.log('[ChatKit Proxy] Calling backend:', backendUrl);

    const backendResponse = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`,
        'Accept': 'text/event-stream, application/json',
      },
      body: body,
    });

    console.log('[ChatKit Proxy] Backend response status:', backendResponse.status);
    console.log('[ChatKit Proxy] Backend content-type:', backendResponse.headers.get('content-type'));

    if (!backendResponse.ok) {
      const errorText = await backendResponse.text();
      console.error('[ChatKit Proxy] Backend error:', errorText);
      return new Response(
        JSON.stringify({ error: errorText }),
        { status: backendResponse.status, headers: { 'Content-Type': 'application/json' } }
      );
    }

    // Check if streaming response
    const contentType = backendResponse.headers.get('content-type') || '';

    if (contentType.includes('text/event-stream')) {
      // Stream the response through
      const reader = backendResponse.body?.getReader();
      if (!reader) {
        return new Response(
          JSON.stringify({ error: 'No response body' }),
          { status: 500, headers: { 'Content-Type': 'application/json' } }
        );
      }

      const stream = new ReadableStream({
        async start(controller) {
          const decoder = new TextDecoder();
          let totalBytes = 0;
          try {
            while (true) {
              const { done, value } = await reader.read();
              if (done) {
                console.log('[ChatKit Proxy] Stream ended, total bytes:', totalBytes);
                break;
              }
              totalBytes += value.length;
              // Log first few chunks to debug
              if (totalBytes < 2000) {
                console.log('[ChatKit Proxy] Stream chunk:', decoder.decode(value, { stream: true }));
              }
              controller.enqueue(value);
            }
          } catch (error) {
            console.error('[ChatKit Proxy] Stream error:', error);
          } finally {
            controller.close();
          }
        },
      });

      return new Response(stream, {
        headers: {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
        },
      });
    } else {
      // JSON response - pass through
      const jsonData = await backendResponse.text();
      return new Response(jsonData, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
    }
  } catch (error) {
    console.error('[ChatKit Proxy] Error:', error);
    return new Response(
      JSON.stringify({ error: 'Internal server error' }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
}
