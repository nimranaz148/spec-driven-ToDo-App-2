---
name: tailwindcss
description: Tailwind CSS utility-first styling patterns. Use when styling components, building layouts, or customizing design for the Todo frontend.
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
---

# Tailwind CSS Skill

## Quick Reference

Tailwind CSS is a utility-first CSS framework for styling the Next.js frontend.

## Common Classes

### Layout
```html
<div class="container mx-auto p-4">Container with padding</div>
<div class="flex items-center gap-4">Flex layout</div>
<div class="grid grid-cols-1 md:grid-cols-2 gap-4">Grid</div>
<div class="space-y-4">Vertical spacing</div>
```

### Typography
```html
<h1 class="text-2xl font-bold">Heading</h1>
<p class="text-gray-600">Gray text</p>
<span class="line-through">Strikethrough</span>
```

### Colors
```html
<button class="bg-blue-500 text-white">Blue button</button>
<input class="border border-gray-300">Gray border</input>
<div class="bg-red-100 text-red-800">Red background</div>
```

### Interactive
```html
<button class="hover:bg-blue-600">Hover state</button>
<button class="disabled:opacity-50">Disabled</button>
<input class="focus:ring-2 focus:ring-blue-500">Focus ring</input>
```

## For Detailed Reference

See [REFERENCE.md](REFERENCE.md) for:
- Complete class reference
- Responsive design
- Dark mode
- Custom configuration
