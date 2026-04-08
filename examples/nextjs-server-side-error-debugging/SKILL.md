---
name: nextjs-server-side-error-debugging
description: |
  Debug getServerSideProps and getStaticProps errors in Next.js. Use when: 
  (1) Page shows generic error but browser console is empty, (2) API routes 
  return 500 with no details, (3) Server-side code fails silently, (4) Error 
  only occurs on refresh not client navigation. Check terminal/server logs 
  instead of browser for actual error messages.
author: Claude Code
version: 1.0.0
date: 2024-01-15
---

<!-- UNIVERSAL-SKILL-POLICY:START -->
## Universal Runner / Decision Policy

- This skill is intended for Codex, OpenCode, and Claude Code when the required tools are available.
- If the task reaches a real decision point, ask `turing` for a second opinion first; then let the primary agent make the final go/no-go decision.
- Do not require Turing for routine mechanical steps, and do not outsource final responsibility to Turing.

## 通用运行 / 决策规则

- 本 skill 适用于 Codex、OpenCode、Claude Code（前提是所需工具可用）。
- 只有在任务进入真实决策点时，才先向 `turing` 征求第二意见；最终是否执行，必须由主代理自己决定。
- 不要把“所有结果都必须经 turing 检查”当成规则，也不要把最终责任外包给 turing。

<!-- UNIVERSAL-SKILL-POLICY:END -->

# Next.js Server-Side Error Debugging

## Problem

Server-side errors in Next.js don't appear in the browser console, making debugging 
frustrating when you're looking in the wrong place. The browser shows a generic error 
page or 500 status, but no stack trace or useful error information appears in DevTools.

## Context / Trigger Conditions

This skill applies when:

- Page displays "Internal Server Error" or custom error page
- Browser console shows no errors, or only a generic fetch failure
- You're using `getServerSideProps`, `getStaticProps`, or API routes
- Error only occurs on page refresh or direct navigation (not client-side transitions)
- The error is intermittent and hard to reproduce in the browser

Common misleading symptoms:
- "Unhandled Runtime Error" modal that doesn't show the real cause
- Network tab shows 500 but response body is empty or generic
- Error disappears when you add console.log (timing issue)

## Solution

### Step 1: Check the Terminal

The actual error with full stack trace appears in the terminal where `npm run dev` 
or `next dev` is running. This is the **first place to look**.

```bash
# If you don't see the terminal, find the process
ps aux | grep next
# Or restart with visible output
npm run dev
```

### Step 2: Add Explicit Error Handling

For persistent debugging, wrap server-side code with try-catch:

```typescript
export async function getServerSideProps(context) {
  try {
    const data = await fetchSomething();
    return { props: { data } };
  } catch (error) {
    console.error('getServerSideProps error:', error);
    // Return error state instead of throwing
    return { props: { error: error.message } };
  }
}
```

### Step 3: For Production Errors

Check your hosting provider's logs:
- **Vercel**: Dashboard → Project → Logs (Functions tab)
- **AWS**: CloudWatch Logs
- **Netlify**: Functions tab in dashboard
- **Self-hosted**: Check your Node.js process logs

### Step 4: Common Causes

1. **Environment variables**: Missing in production but present locally
2. **Database connections**: Connection string issues, cold starts
3. **Import errors**: Server-only code accidentally imported on client
4. **Async/await**: Missing await on async operations
5. **JSON serialization**: Objects that can't be serialized (dates, functions)

## Verification

After checking the terminal, you should see:
- Full stack trace with file name and line number
- The actual error message (not generic 500)
- Variable values if you added console.log statements

## Example

**Symptom**: User reports page shows "Internal Server Error" after clicking a link.

**Investigation**:
1. Open browser DevTools → Console: Empty
2. Network tab shows: `GET /dashboard → 500`
3. Check terminal running `npm run dev`:

```
Error: Cannot read property 'id' of undefined
    at getServerSideProps (/app/pages/dashboard.tsx:15:25)
    at renderToHTML (/app/node_modules/next/dist/server/render.js:428:22)
```

**Cause found**: Database query returned `null` instead of user object.

## Notes

- In development, Next.js sometimes shows an error overlay, but it often has less 
  detail than the terminal output
- `reactStrictMode: true` in `next.config.js` causes double-execution of server 
  functions in development, which can make debugging confusing
- For API routes, the error appears in the same terminal as page errors
- Client-side errors (in useEffect, event handlers) DO appear in browser console—
  this skill only applies to server-side code
- If using `next start` (production mode locally), errors may be less verbose; 
  check `NODE_ENV` and consider adding custom error logging
