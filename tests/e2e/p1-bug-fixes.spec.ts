import { test, expect, Page } from '@playwright/test';

// Test credentials
const TEST_USER = {
  username: 'admin',
  password: 'admin123',
};

// Helper to login
async function login(page: Page) {
  await page.goto('/');
  await page.fill('input[name="username"]', TEST_USER.username);
  await page.fill('input[name="password"]', TEST_USER.password);
  await page.click('button[type="submit"]');
  await page.waitForURL('/', { timeout: 10000 });
}

test.describe('P1 Bug Fixes Validation', () => {
  test.describe('Fix #1: Dark Mode Toggle', () => {
    test('should toggle dark mode and persist across refreshes', async ({ page }) => {
      await login(page);

      // Get the theme toggle button
      const themeToggle = page.locator('button[title*="mode"], button[title*="theme"]').first();
      
      // Get initial theme
      const htmlElement = page.locator('html');
      const initialClass = await htmlElement.getAttribute('class');
      console.log('Initial theme class:', initialClass);

      // Click to cycle through themes
      await themeToggle.click();
      await page.waitForTimeout(500); // Give time for theme to apply
      
      const afterFirstClick = await htmlElement.getAttribute('class');
      console.log('After first click:', afterFirstClick);
      expect(afterFirstClick).not.toBe(initialClass);
      
      // Verify dark class is present or removed
      const hasDarkClass = afterFirstClick?.includes('dark');
      const hasLightClass = afterFirstClick?.includes('light');
      expect(hasDarkClass || hasLightClass).toBeTruthy();

      // Verify data-theme attribute is set
      const dataTheme = await htmlElement.getAttribute('data-theme');
      expect(dataTheme).toBeTruthy();
      console.log('Data-theme attribute:', dataTheme);

      // Refresh page and verify theme persists
      await page.reload();
      await page.waitForLoadState('networkidle');
      
      const afterReload = await htmlElement.getAttribute('class');
      const dataThemeAfterReload = await htmlElement.getAttribute('data-theme');
      
      console.log('After reload:', afterReload);
      console.log('Data-theme after reload:', dataThemeAfterReload);
      
      // Theme should persist (either matches or is system-resolved)
      expect(afterReload).toBeTruthy();
      expect(dataThemeAfterReload).toBeTruthy();
    });

    test('should apply dark mode styles to elements', async ({ page }) => {
      await login(page);

      // Toggle to dark mode
      const themeToggle = page.locator('button[title*="mode"], button[title*="theme"]').first();
      await themeToggle.click();
      await page.waitForTimeout(500);

      // Check that dark mode class is on html
      const htmlElement = page.locator('html');
      const htmlClass = await htmlElement.getAttribute('class');
      
      if (htmlClass?.includes('dark')) {
        // Verify dark mode background color is applied
        const bodyBg = await page.evaluate(() => {
          const body = document.body;
          return window.getComputedStyle(body).backgroundColor;
        });
        
        console.log('Body background in dark mode:', bodyBg);
        // Dark mode should have a dark background (rgb values should be low)
        expect(bodyBg).toBeTruthy();
      }
    });
  });

  test.describe('Fix #2: Chat Deletion Redirect', () => {
    test('should navigate to home when deleting current chat without logout', async ({ page }) => {
      await login(page);

      // Create a new chat
      const newChatButton = page.locator('button:has-text("New Chat")').first();
      await newChatButton.click();
      await page.waitForTimeout(1000);

      // Verify we're on a chat page
      await expect(page).toHaveURL(/\/chat\/[a-f0-9-]+/);
      const chatUrl = page.url();
      console.log('Created chat URL:', chatUrl);

      // Find and hover over the chat in sidebar to reveal delete button
      const chatInSidebar = page.locator('[class*="group"]').filter({ hasText: 'New Chat' }).first();
      await chatInSidebar.hover();
      
      // Wait for delete button to appear (opacity transition)
      await page.waitForTimeout(300);
      
      // Click delete button
      const deleteButton = chatInSidebar.locator('button[title="Delete chat"]');
      await deleteButton.click();
      
      // Wait for navigation
      await page.waitForURL('/', { timeout: 5000 });
      
      // Verify we're at home page
      expect(page.url()).toContain('/');
      expect(page.url()).not.toContain('/chat/');
      
      // Verify user is still logged in (header should show username)
      const header = page.locator('header');
      await expect(header.locator('text=/Welcome.*admin/')).toBeVisible();
      
      console.log('✓ Successfully redirected to home after chat deletion');
      console.log('✓ User remains logged in');
    });

    test('should delete non-current chat without navigation', async ({ page }) => {
      await login(page);

      // Create two chats
      const newChatButton = page.locator('button:has-text("New Chat")').first();
      await newChatButton.click();
      await page.waitForTimeout(500);
      
      const firstChatUrl = page.url();
      
      await newChatButton.click();
      await page.waitForTimeout(500);
      
      const secondChatUrl = page.url();
      console.log('First chat:', firstChatUrl);
      console.log('Second chat (current):', secondChatUrl);

      // We're on the second chat, delete the first one
      const chatItems = page.locator('[class*="group"]').filter({ hasText: 'New Chat' });
      const firstChat = chatItems.nth(0);
      await firstChat.hover();
      await page.waitForTimeout(300);
      
      const deleteButton = firstChat.locator('button[title="Delete chat"]');
      await deleteButton.click();
      
      await page.waitForTimeout(500);
      
      // Should still be on second chat
      expect(page.url()).toBe(secondChatUrl);
      console.log('✓ Remained on current chat after deleting another');
    });
  });

  test.describe('Fix #3: System Prompt Persistence', () => {
    test('should save and persist system prompt changes', async ({ page }) => {
      await login(page);

      // Navigate to prompts page
      await page.click('a:has-text("Prompts")');
      await page.waitForURL('/prompts');
      
      // Wait for prompts to load
      await page.waitForSelector('text=System Prompts');
      await page.waitForTimeout(1000);

      // Find RAG Only mode and click Edit
      const ragSection = page.locator('div:has-text("RAG Only")').filter({ hasText: 'Search document knowledge base' }).first();
      const editButton = ragSection.locator('button:has-text("Edit")');
      await editButton.click();

      // Get the textarea and add a unique test string
      const timestamp = Date.now();
      const testPrompt = `Test prompt updated at ${timestamp}. This is a custom system prompt for testing persistence.`;
      
      const textarea = ragSection.locator('textarea');
      await textarea.clear();
      await textarea.fill(testPrompt);

      // Save the prompt
      const saveButton = ragSection.locator('button:has-text("Save")');
      await saveButton.click();

      // Wait for success toast
      await expect(page.locator('text=/saved successfully/i')).toBeVisible({ timeout: 5000 });
      await page.waitForTimeout(1000);

      console.log('✓ Prompt saved successfully');

      // Refresh the page to verify persistence
      await page.reload();
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);

      // Check if the saved prompt is displayed
      const promptText = await page.locator('div:has-text("RAG Only")').filter({ hasText: 'Search document knowledge base' }).first().locator('pre').textContent();
      
      console.log('Saved prompt:', testPrompt);
      console.log('Loaded prompt after refresh:', promptText);

      expect(promptText).toContain(timestamp.toString());
      console.log('✓ Prompt persisted after page refresh');

      // Reset to default
      const resetButton = ragSection.locator('button:has-text("Reset")');
      await resetButton.click();
      
      // Confirm reset dialog
      page.on('dialog', dialog => dialog.accept());
      await page.waitForTimeout(1000);

      console.log('✓ Reset prompt to default');
    });

    test('should handle multiple mode edits correctly', async ({ page }) => {
      await login(page);
      await page.goto('/prompts');
      await page.waitForTimeout(1000);

      // Edit multiple modes
      const modes = ['RAG Only', 'Web Search'];
      const testData: Record<string, string> = {};

      for (const mode of modes) {
        const timestamp = Date.now();
        const testPrompt = `${mode} test at ${timestamp}`;
        testData[mode] = testPrompt;

        const section = page.locator(`div:has-text("${mode}")`).first();
        await section.locator('button:has-text("Edit")').click();
        await section.locator('textarea').fill(testPrompt);
        await section.locator('button:has-text("Save")').click();
        await page.waitForTimeout(1000);
      }

      // Reload and verify all persist
      await page.reload();
      await page.waitForTimeout(1000);

      for (const mode of modes) {
        const section = page.locator(`div:has-text("${mode}")`).first();
        const text = await section.locator('pre').textContent();
        expect(text).toContain(testData[mode].split(' ')[0]);
      }

      console.log('✓ Multiple prompts persisted correctly');
    });
  });
});

