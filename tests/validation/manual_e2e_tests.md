# Manual E2E Test Cases for P1 Bug Fixes

## Prerequisites
- Frontend running on http://localhost:3000
- Backend running and healthy
- Test credentials: admin / admin123

---

## Test Case 1: Dark Mode Toggle ✅

### Steps:
1. Open http://localhost:3000
2. Login with admin / admin123
3. Look for the theme toggle button in the header (sun/moon icon)
4. Click the theme toggle button
5. **Expected**: UI immediately switches to dark mode (dark background, light text)
6. **Expected**: Icon changes from sun to moon (or to computer if cycling to system)
7. Refresh the page (F5)
8. **Expected**: Dark mode persists after refresh
9. **Expected**: Theme class on `<html>` element includes `dark`
10. Open browser DevTools Console and type: `document.documentElement.className`
11. **Expected**: Output includes either 'light' or 'dark'

### Validation Checks:
- [ ] Theme toggle button exists and is visible
- [ ] Clicking toggle changes UI colors immediately
- [ ] Dark mode shows dark backgrounds (gray-900) and light text (gray-100)
- [ ] Light mode shows light backgrounds (white/gray-50) and dark text (gray-900)
- [ ] Theme persists after page refresh
- [ ] `localStorage.getItem('theme')` shows correct theme
- [ ] `document.documentElement.classList` contains theme class

---

## Test Case 2: Chat Deletion Redirect ✅

### Steps:
1. Login to the application
2. Click "New Chat" to create a new conversation
3. Send a test message (e.g., "Hello")
4. Note the URL (should be `/chat/[some-uuid]`)
5. In the sidebar, hover over the current chat
6. **Expected**: Delete button (trash icon) appears on hover
7. Click the delete button for the CURRENT chat
8. **Expected**: Application navigates to home page (`/`)
9. **Expected**: User remains logged in (see "Welcome, admin" in header)
10. **Expected**: Chat is removed from sidebar
11. **Expected**: NO logout or auth error

### Alternative Test (Non-Current Chat):
1. Create chat #1
2. Create chat #2 (now current)
3. Hover over chat #1 in sidebar
4. Delete chat #1
5. **Expected**: Still on chat #2 URL
6. **Expected**: Chat #1 removed from sidebar
7. **Expected**: No navigation or logout

### Validation Checks:
- [ ] Deleting current chat navigates to `/`
- [ ] User stays logged in after deletion
- [ ] No authentication errors or logout
- [ ] Chat removed from sidebar
- [ ] Deleting non-current chat doesn't cause navigation

---

## Test Case 3: System Prompt Persistence ✅

### Steps:
1. Login to the application
2. Click "Prompts" in the sidebar
3. Wait for prompts page to load
4. Find "RAG Only" mode section
5. Click "Edit" button
6. Note the current prompt content
7. Add unique text to the prompt: `[TEST RUN: {current_timestamp}]`
8. Click "Save" button
9. **Expected**: Success toast appears "Prompt saved successfully"
10. Wait 2 seconds
11. Click browser refresh (F5)
12. **Expected**: Page reloads and shows the updated prompt with test marker
13. **Expected**: Test marker `[TEST RUN: ...]` is visible in the prompt text

### Additional Validation:
14. Edit a DIFFERENT mode (e.g., "Web Search")
15. Add different unique text
16. Save and verify persistence
17. Refresh page
18. **Expected**: BOTH custom prompts persist correctly

### Reset Test:
19. Click "Reset" button on a customized prompt
20. Confirm the reset dialog
21. **Expected**: Prompt reverts to default system prompt
22. Refresh page
23. **Expected**: Default prompt still showing (reset persisted)

### Validation Checks:
- [ ] Edit button opens textarea for editing
- [ ] Save button saves the prompt
- [ ] Success toast appears after save
- [ ] Prompt persists after page refresh
- [ ] Multiple modes can be edited independently
- [ ] Reset button reverts to default
- [ ] Reset persists across refreshes
- [ ] No "undefined" or error messages

---

## Success Criteria

All tests must pass with:
- ✅ No console errors in browser DevTools
- ✅ No authentication errors or unexpected logouts
- ✅ All UI changes persist across page refreshes
- ✅ Smooth user experience with no bugs

---

## Running Automated E2E Tests (Optional)

If Playwright is set up:

```bash
npx playwright test tests/e2e/p1-bug-fixes.spec.ts --headed
```

This will run automated browser tests for all three fixes.

---

## Test Results Template

```
Date: [DATE]
Tester: [NAME]
Environment: [localhost:3000]

Test Case 1 (Dark Mode): [ PASS / FAIL ]
Notes: ___________________________________________

Test Case 2 (Chat Deletion): [ PASS / FAIL ]
Notes: ___________________________________________

Test Case 3 (Prompt Persistence): [ PASS / FAIL ]  
Notes: ___________________________________________

Overall: [ ALL PASS / SOME FAILURES ]
```

---

## Known Limitations

- Theme toggle cycles through 3 states: Light → Dark → System
- System theme follows OS preference
- Prompts require minimum 50 characters to save
- Prompts should include "role", "guidelines", and "format" sections for best results

---

## Troubleshooting

### Dark Mode Doesn't Apply
- Check browser console for JavaScript errors
- Verify `localStorage.getItem('theme')` returns a value
- Check `document.documentElement.classList` contains 'light' or 'dark'
- Try hard refresh (Ctrl+Shift+R / Cmd+Shift+R)

### Chat Deletion Causes Logout
- Check browser console for errors
- Verify JWT token is still in localStorage
- Check network tab for 401 responses
- This should be fixed - report if it still happens!

### Prompt Not Persisting
- Wait at least 2 seconds after saving before testing
- Check browser console for save errors
- Verify prompt is at least 50 characters
- Check backend logs: `docker logs graphmind-rag`

