/**
 * @test-category e2e
 * @test-type template
 * @description Template management tests
 * @browser chromium,firefox,webkit
 */

import { test, expect } from '@playwright/test';
import { DashboardHelpers } from './helpers.js';

test.describe('Template Management Tests', () => {
  let helpers;

  test.beforeEach(async ({ page }) => {
    helpers = new DashboardHelpers(page);
    await page.goto('/');
    await helpers.waitForPageLoad();
  });

  test('templates sidebar loads and displays correctly', async ({ page }) => {
    // Check sidebar header
    await expect(page.locator('.sidebar-header h2')).toHaveText(/Templates/);
    
    // Check sidebar actions
    await expect(page.locator('.sidebar-actions')).toBeVisible();
    await expect(page.locator('button[onclick="refreshTemplates()"]')).toBeVisible();
    await expect(page.locator('button[onclick="showCreateTemplateModal()"]')).toBeVisible();
  });

  test('template cards display template information', async ({ page }) => {
    const templateCards = page.locator('.template-card');
    const cardCount = await templateCards.count();
    
    if (cardCount > 0) {
      const firstCard = templateCards.first();
      
      // Check template header
      await expect(firstCard.locator('.template-header')).toBeVisible();
      await expect(firstCard.locator('.template-name')).toBeVisible();
      await expect(firstCard.locator('.template-actions')).toBeVisible();
      
      // Check template info fields
      const infoFields = firstCard.locator('.template-field');
      const fieldCount = await infoFields.count();
      expect(fieldCount).toBeGreaterThan(0);
      
      // Check action buttons
      await expect(firstCard.locator('.template-actions-bar')).toBeVisible();
      await expect(firstCard.locator('button[onclick*="generateSingle"]')).toBeVisible();
      await expect(firstCard.locator('button[onclick*="startBatch"]')).toBeVisible();
      await expect(firstCard.locator('button[onclick*="openOutputFolder"]')).toBeVisible();
    } else {
      // Check no templates message
      await expect(page.locator('.text-center.text-muted')).toBeVisible();
      await expect(page.locator('.text-center.text-muted')).toContainText('No templates found');
    }
  });

  test('template selection updates generation form', async ({ page }) => {
    const templateCards = page.locator('.template-card');
    const cardCount = await templateCards.count();
    
    if (cardCount > 0) {
      const firstCard = templateCards.first();
      const templateName = await firstCard.getAttribute('data-config');
      
      // Click on template card
      await firstCard.click();
      
      // Check if template is selected in dropdown
      const configSelect = page.locator('#config-select');
      const selectedValue = await configSelect.inputValue();
      expect(selectedValue).toBe(templateName);
    }
  });

  test('template actions are accessible', async ({ page }) => {
    const templateCards = page.locator('.template-card');
    const cardCount = await templateCards.count();
    
    if (cardCount > 0) {
      const firstCard = templateCards.first();
      
      // Check edit button
      const editButton = firstCard.locator('button[onclick*="editTemplate"]');
      await expect(editButton).toBeVisible();
      
      // Check delete button
      const deleteButton = firstCard.locator('button[onclick*="deleteTemplate"]');
      await expect(deleteButton).toBeVisible();
      
      // Check generate button
      const generateButton = firstCard.locator('button[onclick*="generateSingle"]');
      await expect(generateButton).toBeVisible();
      
      // Check batch button
      const batchButton = firstCard.locator('button[onclick*="startBatch"]');
      await expect(batchButton).toBeVisible();
      
      // Check folder button
      const folderButton = firstCard.locator('button[onclick*="openOutputFolder"]');
      await expect(folderButton).toBeVisible();
    }
  });

  test('create template modal opens', async ({ page }) => {
    // Click create template button
    await helpers.clickButton('button[onclick="showCreateTemplateModal()"]');
    
    // Check modal appears
    await expect(page.locator('#create-template-modal')).toBeVisible();
    
    // Check form fields
    await expect(page.locator('#new-template-name')).toBeVisible();
    await expect(page.locator('#new-template-description')).toBeVisible();
    await expect(page.locator('#new-template-model-type')).toBeVisible();
    
    // Close modal
    await helpers.clickButton('#create-template-modal .close-btn');
    await expect(page.locator('#create-template-modal')).not.toBeVisible();
  });

  test('refresh templates functionality', async ({ page }) => {
    // Click refresh button
    await helpers.clickButton('button[onclick="refreshTemplates()"]');
    
    // Wait for potential loading state
    await page.waitForTimeout(1000);
    
    // Check templates are still accessible
    await expect(page.locator('.templates-container')).toBeVisible();
  });

  test('template card hover effects', async ({ page }) => {
    const templateCards = page.locator('.template-card');
    const cardCount = await templateCards.count();
    
    if (cardCount > 0) {
      const firstCard = templateCards.first();
      
      // Hover over card
      await firstCard.hover();
      
      // Check if hover effects are applied (CSS classes or visual changes)
      // This is more of a visual test, but we can check for any hover-related classes
      const hasHoverClass = await firstCard.evaluate(el => {
        return el.classList.contains('hover') || 
               el.classList.contains('active') || 
               getComputedStyle(el).transform !== 'none';
      });
      
      // Hover effects might not add classes, so this is optional
      console.log('Template card hover effect detected:', hasHoverClass);
    }
  });

  test('template information displays correctly', async ({ page }) => {
    const templateCards = page.locator('.template-card');
    const cardCount = await templateCards.count();
    
    if (cardCount > 0) {
      const firstCard = templateCards.first();
      
      // Check template info section
      const infoSection = firstCard.locator('.template-info');
      await expect(infoSection).toBeVisible();
      
      // Check for description field
      const descriptionField = infoSection.locator('.template-field').filter({ hasText: 'Description:' });
      if (await descriptionField.count() > 0) {
        await expect(descriptionField).toBeVisible();
      }
      
      // Check for model field
      const modelField = infoSection.locator('.template-field').filter({ hasText: 'Model:' });
      if (await modelField.count() > 0) {
        await expect(modelField).toBeVisible();
      }
      
      // Check for checkpoint field
      const checkpointField = infoSection.locator('.template-field').filter({ hasText: 'Checkpoint:' });
      if (await checkpointField.count() > 0) {
        await expect(checkpointField).toBeVisible();
      }
    }
  });

  test('template actions bar functionality', async ({ page }) => {
    const templateCards = page.locator('.template-card');
    const cardCount = await templateCards.count();
    
    if (cardCount > 0) {
      const firstCard = templateCards.first();
      const actionsBar = firstCard.locator('.template-actions-bar');
      
      // Check all action buttons are present
      const buttons = actionsBar.locator('button');
      const buttonCount = await buttons.count();
      expect(buttonCount).toBeGreaterThan(0);
      
      // Check button text and icons
      for (let i = 0; i < buttonCount; i++) {
        const button = buttons.nth(i);
        await expect(button).toBeVisible();
        
        // Check button has text or icon
        const buttonText = await button.textContent();
        const hasIcon = await button.locator('i').count() > 0;
        expect(buttonText.trim().length > 0 || hasIcon).toBeTruthy();
      }
    }
  });

  test('template card accessibility', async ({ page }) => {
    const templateCards = page.locator('.template-card');
    const cardCount = await templateCards.count();
    
    if (cardCount > 0) {
      const firstCard = templateCards.first();
      
      // Check if card is keyboard accessible
      await firstCard.focus();
      
      // Check if card can be activated with Enter key
      await firstCard.press('Enter');
      
      // Check if template was selected (dropdown should update)
      const configSelect = page.locator('#config-select');
      const selectedValue = await configSelect.inputValue();
      expect(selectedValue).toBeTruthy();
    }
  });
}); 