# Screen Reader Testing Guide

This guide provides instructions for manual testing with screen readers to ensure WCAG 2.1 AA compliance.

## Screen Readers

### Windows
- **NVDA** (Free): https://www.nvaccess.org/download/
- **JAWS** (Commercial): https://www.freedomscientific.com/products/software/jaws/

### macOS
- **VoiceOver** (Built-in): Cmd + F5 to toggle

### Mobile
- **iOS VoiceOver**: Settings > Accessibility > VoiceOver
- **Android TalkBack**: Settings > Accessibility > TalkBack

## Testing Checklist

### Header Navigation
- [ ] Logo/Home link announces "Home, link"
- [ ] Theme toggle announces current state ("Switch to dark mode" or "Switch to light mode")
- [ ] User name is announced when logged in
- [ ] Logout button announces "Log out, button"
- [ ] Navigation is logical left-to-right

### Task List
- [ ] Empty state announces title and description
- [ ] Each task announces as "Task: [title], article"
- [ ] Checkbox announces "Mark as complete" or "Mark as incomplete"
- [ ] Completed tasks announce with strike-through indication
- [ ] Delete button announces "Delete task: [title], button"
- [ ] Focus order is logical top-to-bottom

### Forms
- [ ] All form fields have labels
- [ ] Required fields are indicated
- [ ] Error messages are announced
- [ ] Success messages are announced
- [ ] Submit buttons describe their action

### Page Transitions
- [ ] Page changes are announced
- [ ] Focus is managed appropriately
- [ ] Loading states are announced
- [ ] Error states are announced

## Common Issues to Check

### Missing Labels
- All interactive elements must have accessible names
- Use `aria-label` for icon-only buttons
- Use `aria-labelledby` for complex widgets

### Redundant Announcements
- Avoid duplicate labels
- Use `aria-hidden="true"` for decorative icons
- Don't announce the same information multiple times

### Focus Management
- Focus should move logically
- Focus should be visible
- Don't trap keyboard focus
- Return focus after modal close

### Dynamic Content
- Announce loading states with `aria-busy`
- Use `aria-live` for status updates
- Announce form validation errors immediately

## Test Scenarios

### Scenario 1: Complete Task Flow
1. Navigate to task list with screen reader
2. Listen to task announcement
3. Tab to checkbox
4. Activate checkbox with Space
5. Verify completion is announced
6. Tab to delete button
7. Activate delete with Enter
8. Verify deletion is announced

### Scenario 2: Theme Toggle
1. Navigate to header
2. Find theme toggle button
3. Listen to current state announcement
4. Activate toggle
5. Verify new state is announced
6. Check that color contrast is maintained

### Scenario 3: Form Submission
1. Navigate to task creation form
2. Listen to form field labels
3. Fill out form
4. Submit form
5. Verify success/error is announced
6. Check focus returns appropriately

## Reporting Issues

When documenting screen reader issues, include:
- Screen reader name and version
- Operating system and version
- Browser name and version
- Expected behavior
- Actual behavior
- Steps to reproduce
- Screenshots or recordings if possible

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [WebAIM Screen Reader Testing](https://webaim.org/articles/screenreader_testing/)
- [NVDA Keyboard Shortcuts](https://dequeuniversity.com/screenreaders/nvda-keyboard-shortcuts)
- [VoiceOver Keyboard Shortcuts](https://dequeuniversity.com/screenreaders/voiceover-keyboard-shortcuts)
