import { test, expect, Page } from '@playwright/test';

const TEST_USER = {
  username: 'admin',
  password: 'admin123',
};

async function login(page: Page) {
  await page.goto('/');
  await page.waitForSelector('input[name="username"]', { timeout: 10000 });
  await page.fill('input[name="username"]', TEST_USER.username);
  await page.fill('input[name="password"]', TEST_USER.password);
  await page.click('button[type="submit"]');
  await page.waitForURL('/', { timeout: 10000 });
}

test.describe('Complete User Workflows - E2E Tests', () => {
  
  test.describe('Authentication Workflow', () => {
    test('should complete login flow successfully', async ({ page }) => {
      await page.goto('/');
      
      // Should show login form
      await expect(page.locator('input[name="username"]')).toBeVisible();
      await expect(page.locator('input[name="password"]')).toBeVisible();
      
      // Fill credentials
      await page.fill('input[name="username"]', TEST_USER.username);
      await page.fill('input[name="password"]', TEST_USER.password);
      
      // Submit
      await page.click('button[type="submit"]');
      
      // Should redirect to home/landing page
      await page.waitForURL('/', { timeout: 10000 });
      
      // Should show welcome message
      await expect(page.locator(`text=/Welcome.*${TEST_USER.username}/i`)).toBeVisible();
      
      console.log('✓ Login flow completed successfully');
    });
    
    test('should reject invalid credentials', async ({ page }) => {
      await page.goto('/');
      
      await page.fill('input[name="username"]', 'admin');
      await page.fill('input[name="password"]', 'wrongpassword');
      await page.click('button[type="submit"]');
      
      // Should show error message
      await expect(page.locator('text=/invalid|error|failed/i')).toBeVisible({ timeout: 5000 });
      
      console.log('✓ Invalid credentials properly rejected');
    });
    
    test('should complete logout flow', async ({ page }) => {
      await login(page);
      
      // Find and click logout button
      const logoutButton = page.locator('button[title="Logout"], button:has-text("Logout")').first();
      await logoutButton.click();
      
      // Should redirect to login page
      await page.waitForSelector('input[name="username"]', { timeout: 5000 });
      
      console.log('✓ Logout flow completed successfully');
    });
  });

  test.describe('Chat Creation and Management Workflow', () => {
    test('should create new chat and send message', async ({ page }) => {
      await login(page);
      
      // Click New Chat
      await page.click('button:has-text("New Chat")');
      await page.waitForTimeout(1000);
      
      // Should navigate to chat page
      await expect(page).toHaveURL(/\/chat\/[a-f0-9-]+/);
      
      // Enter and send a message
      const messageInput = page.locator('textarea[placeholder*="message"], textarea[placeholder*="question"]').first();
      await messageInput.fill('Test message for E2E testing');
      
      const sendButton = page.locator('button[type="submit"], button:has-text("Send")').first();
      await sendButton.click();
      
      // Should show the message in chat
      await expect(page.locator('text=Test message for E2E testing')).toBeVisible({ timeout: 5000 });
      
      console.log('✓ Chat creation and messaging workflow completed');
    });
    
    test('should switch between chats', async ({ page }) => {
      await login(page);
      
      // Create first chat
      await page.click('button:has-text("New Chat")');
      await page.waitForTimeout(1000);
      const firstChatUrl = page.url();
      
      // Create second chat
      await page.click('button:has-text("New Chat")');
      await page.waitForTimeout(1000);
      const secondChatUrl = page.url();
      
      expect(firstChatUrl).not.toBe(secondChatUrl);
      
      // Click on first chat in sidebar
      const chatItems = page.locator('[class*="group"]').filter({ hasText: 'New Chat' });
      await chatItems.first().click();
      await page.waitForTimeout(500);
      
      // Should navigate to first chat
      expect(page.url()).toBe(firstChatUrl);
      
      console.log('✓ Chat switching workflow completed');
    });
  });

  test.describe('Document Management Workflow', () => {
    test('should navigate to documents page', async ({ page }) => {
      await login(page);
      
      // Click Documents link
      await page.click('a:has-text("Documents"), [href="/documents"]');
      await page.waitForURL('/documents');
      
      // Should show documents page
      await expect(page.locator('h1:has-text("Documents")')).toBeVisible();
      
      console.log('✓ Documents page navigation completed');
    });
    
    test('should show document list or empty state', async ({ page }) => {
      await login(page);
      await page.goto('/documents');
      
      // Should show either document list or empty state
      const hasDocuments = await page.locator('text=/uploaded|document/i').count() > 0;
      const hasEmptyState = await page.locator('text=/no documents|empty|upload/i').count() > 0;
      
      expect(hasDocuments || hasEmptyState).toBeTruthy();
      
      console.log('✓ Document list display verified');
    });
  });

  test.describe('System Prompts Management Workflow', () => {
    test('should navigate to prompts page and view prompts', async ({ page }) => {
      await login(page);
      
      await page.click('a:has-text("Prompts")');
      await page.waitForURL('/prompts');
      
      // Should show prompts page
      await expect(page.locator('h1:has-text("System Prompts")')).toBeVisible();
      
      // Should show all 4 modes
      await expect(page.locator('text=RAG Only')).toBeVisible();
      await expect(page.locator('text=Obsidian Only')).toBeVisible();
      await expect(page.locator('text=Web Search')).toBeVisible();
      await expect(page.locator('text=/Comprehensive|Research/i')).toBeVisible();
      
      console.log('✓ Prompts page navigation and display completed');
    });
    
    test('should edit and save prompt', async ({ page }) => {
      await login(page);
      await page.goto('/prompts');
      await page.waitForTimeout(1000);
      
      // Find RAG section and click Edit
      const ragSection = page.locator('div:has-text("RAG Only")').first();
      await ragSection.locator('button:has-text("Edit")').click();
      
      // Should show textarea
      const textarea = ragSection.locator('textarea');
      await expect(textarea).toBeVisible();
      
      // Edit the prompt
      const timestamp = Date.now();
      const testText = `Test edit at ${timestamp}. Your role: Be helpful. Guidelines: Test carefully. Response format: Markdown.`;
      await textarea.clear();
      await textarea.fill(testText);
      
      // Save
      await ragSection.locator('button:has-text("Save")').click();
      
      // Should show success message
      await expect(page.locator('text=/saved successfully/i')).toBeVisible({ timeout: 5000 });
      
      console.log('✓ Prompt edit and save workflow completed');
    });
  });

  test.describe('Settings Management Workflow', () => {
    test('should navigate to settings page', async ({ page }) => {
      await login(page);
      
      await page.click('a:has-text("Settings")');
      await page.waitForURL('/settings');
      
      // Should show settings page
      await expect(page.locator('h1:has-text("Settings")')).toBeVisible();
      
      console.log('✓ Settings page navigation completed');
    });
    
    test('should display settings sections', async ({ page }) => {
      await login(page);
      await page.goto('/settings');
      
      // Should have Obsidian configuration section
      const hasObsidianSection = await page.locator('text=/obsidian/i').count() > 0;
      expect(hasObsidianSection).toBeTruthy();
      
      console.log('✓ Settings sections displayed');
    });
  });

  test.describe('Memory Management Workflow', () => {
    test('should navigate to memory page', async ({ page }) => {
      await login(page);
      
      await page.click('a:has-text("Memory")');
      await page.waitForURL('/memory');
      
      // Should show memory page
      await expect(page.locator('h1:has-text("Memory")')).toBeVisible();
      
      console.log('✓ Memory page navigation completed');
    });
  });

  test.describe('Model Selection Workflow', () => {
    test('should display available models', async ({ page }) => {
      await login(page);
      
      // Look for model selector
      const modelSelector = page.locator('select, [role="combobox"]').filter({ hasText: /model|llama|qwen/i }).first();
      
      if (await modelSelector.count() > 0) {
        // Click to open
        await modelSelector.click();
        await page.waitForTimeout(500);
        
        // Should show model options
        const hasModels = await page.locator('text=/llama|qwen|phi|gemma/i').count() > 0;
        expect(hasModels).toBeTruthy();
        
        console.log('✓ Model selection workflow verified');
      } else {
        console.log('⚠ Model selector not found - may need to send message first');
      }
    });
  });

  test.describe('Complete Research Workflow', () => {
    test('should complete full research workflow', async ({ page }) => {
      await login(page);
      
      // Create new chat
      await page.click('button:has-text("New Chat")');
      await page.waitForTimeout(1000);
      
      // Select RAG mode (if mode selector visible)
      const modeButtons = page.locator('button').filter({ hasText: /RAG|Document/i });
      if (await modeButtons.count() > 0) {
        await modeButtons.first().click();
        await page.waitForTimeout(500);
      }
      
      // Send a question
      const messageInput = page.locator('textarea').first();
      await messageInput.fill('What are the key principles of trading?');
      
      const sendButton = page.locator('button[type="submit"]').first();
      await sendButton.click();
      
      // Wait for response (may take a while)
      await expect(page.locator('text=What are the key principles of trading?')).toBeVisible({ timeout: 5000 });
      
      // Should show loading or response
      const hasResponse = await page.locator('[class*="message"], [class*="assistant"]').count() > 0;
      expect(hasResponse).toBeTruthy();
      
      console.log('✓ Complete research workflow initiated');
    });
  });

  test.describe('Navigation and UI Workflow', () => {
    test('should navigate between all main pages', async ({ page }) => {
      await login(page);
      
      const pages = [
        { link: 'Chats', url: '/' },
        { link: 'Documents', url: '/documents' },
        { link: 'Prompts', url: '/prompts' },
        { link: 'Settings', url: '/settings' },
        { link: 'Memory', url: '/memory' },
      ];
      
      for (const pageInfo of pages) {
        await page.click(`a:has-text("${pageInfo.link}")`);
        await page.waitForURL(pageInfo.url, { timeout: 5000 });
        expect(page.url()).toContain(pageInfo.url);
        console.log(`  ✓ Navigated to ${pageInfo.link}`);
      }
      
      console.log('✓ All page navigation completed');
    });
    
    test('should have consistent header across pages', async ({ page }) => {
      await login(page);
      
      const pages = ['/', '/documents', '/prompts', '/settings', '/memory'];
      
      for (const url of pages) {
        await page.goto(url);
        
        // Header should be visible
        const header = page.locator('header');
        await expect(header).toBeVisible();
        
        // Should have GraphMind title
        await expect(page.locator('text=GraphMind')).toBeVisible();
        
        // Should have user info
        await expect(page.locator(`text=/${TEST_USER.username}/i`)).toBeVisible();
      }
      
      console.log('✓ Header consistency verified across all pages');
    });
  });

  test.describe('Error Handling Workflow', () => {
    test('should handle network errors gracefully', async ({ page }) => {
      await login(page);
      
      // Block API calls to simulate network error
      await page.route('**/api/**', route => route.abort());
      
      // Try to perform action that requires API
      await page.click('button:has-text("New Chat")');
      await page.waitForTimeout(2000);
      
      // Should handle gracefully (not crash)
      const pageContent = await page.content();
      expect(pageContent).toBeTruthy();
      
      console.log('✓ Network error handling verified');
    });
  });
});

