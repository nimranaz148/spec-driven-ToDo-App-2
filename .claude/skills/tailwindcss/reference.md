# Tailwind CSS Reference Guide

## Table of Contents
1. [Complete Class Reference](#complete-class-reference)
2. [Responsive Design](#responsive-design)
3. [Dark Mode](#dark-mode)
4. [Custom Configuration](#custom-configuration)

---

## Complete Class Reference

### Spacing
```html
<!-- Margins -->
<div class="m-4">margin: 1rem</div>
<div class="mx-auto">margin-left: auto; margin-right: auto</div>
<div class="mt-2">margin-top: 0.5rem</div>
<div class="mr-4">margin-right: 1rem</div>
<div class="mb-2">margin-bottom: 0.5rem</div>
<div class="ml-4">margin-left: 1rem</div>

<!-- Padding -->
<div class="p-4">padding: 1rem</div>
<div class="px-4">padding-left: 1rem; padding-right: 1rem</div>
<div class="py-2">padding-top: 0.5rem; padding-bottom: 0.5rem</div>

<!-- Gaps (for flex/grid) -->
<div class="gap-4">gap: 1rem</div>
<div class="gap-x-4">column-gap: 1rem</div>
<div class="gap-y-2">row-gap: 0.5rem</div>
```

### Sizing
```html
<!-- Width -->
<div class="w-full">width: 100%</div>
<div class="w-1/2">width: 50%</div>
<div class="w-auto">width: auto</div>
<div class="w-4">width: 1rem</div>
<div class="w-64">width: 16rem</div>

<!-- Height -->
<div class="h-full">height: 100%</div>
<div class="h-4">height: 1rem</div>
<div class="h-screen">height: 100vh</div>

<!-- Min/Max -->
<div class="min-h-screen">min-height: 100vh</div>
<div class="max-w-md">max-width: 28rem</div>
<div class="max-w-lg">max-width: 32rem</div>
```

### Typography
```html
<!-- Size -->
<p class="text-xs">0.75rem</p>
<p class="text-sm">0.875rem</p>
<p class="text-base">1rem (default)</p>
<p class="text-lg">1.125rem</p>
<p class="text-xl">1.25rem</p>
<p class="text-2xl">1.5rem</p>
<p class="text-3xl">1.875rem</p>
<p class="text-4xl">2.25rem</p>

<!-- Weight -->
<p class="font-light">font-weight: 300</p>
<p class="font-normal">400</p>
<p class="font-medium">500</p>
<p class="font-semibold">600</p>
<p class="font-bold">700</p>

<!-- Style -->
<p class="italic">italic</p>
<p class="not-italic">not-italic</p>

<!-- Decoration -->
<p class="underline">underline</p>
<p class="line-through">line-through</p>
<p class="no-underline">no-underline</p>
```

### Colors (Text)
```html
<p class="text-gray-50">#f9fafb</p>
<p class="text-gray-100">#f3f4f6</p>
<p class="text-gray-200">#e5e7eb</p>
<p class="text-gray-300">#d1d5db</p>
<p class="text-gray-400">#9ca3af</p>
<p class="text-gray-500">#6b7280</p>
<p class="text-gray-600">#4b5563</p>
<p class="text-gray-700">#374151</p>
<p class="text-gray-800">#1f2937</p>
<p class="text-gray-900">#111827</p>

<!-- Semantic -->
<p class="text-red-500">Red</p>
<p class="text-blue-500">Blue</p>
<p class="text-green-500">Green</p>
<p class="text-yellow-500">Yellow</p>
<p class="text-purple-500">Purple</p>
```

### Colors (Background)
```html
<div class="bg-white">#ffffff</div>
<div class="bg-gray-50">#f9fafb</div>
<div class="bg-blue-500">#3b82f6</div>
<div class="bg-red-100">#fee2e2</div>
<div class="bg-gradient-to-r">Gradient</div>
<div class="bg-gradient-to-r from-blue-500 to-purple-500">Two-color gradient</div>
```

### Borders
```html
<div class="border">border: 1px solid</div>
<div class="border-2">2px</div>
<div class="border-4">4px</div>
<div class="border-t">border-top</div>
<div class="border-r">border-right</div>
<div class="border-b">border-bottom</div>
<div class="border-l">border-left</div>

<div class="border-gray-300">Border color</div>
<div class="border-solid">solid</div>
<div class="border-dashed">dashed</div>
<div class="border-dotted">dotted</div>
<div class="rounded">border-radius: 0.25rem</div>
<div class="rounded-md">0.375rem</div>
<div class="rounded-lg">0.5rem</div>
<div class="rounded-xl">0.75rem</div>
<div class="rounded-full">9999px (circle)</div>
```

### Shadows
```html
<div class="shadow-sm">Small shadow</div>
<div class="shadow">Default shadow</div>
<div class="shadow-md">Medium</div>
<div class="shadow-lg">Large</div>
<div class="shadow-xl">Extra large</div>
<div class="shadow-2xl">2xl</div>
<div class="shadow-none">No shadow</div>
```

### Flexbox
```html
<div class="flex">display: flex</div>
<div class="flex-col">flex-direction: column</div>
<div class="flex-row">flex-direction: row (default)</div>
<div class="flex-wrap">flex-wrap: wrap</div>
<div class="flex-nowrap">flex-wrap: nowrap</div>

<!-- Alignment -->
<div class="justify-start">justify-content: flex-start</div>
<div class="justify-center">center</div>
<div class="justify-end">flex-end</div>
<div class="justify-between">space-between</div>
<div class="justify-around">space-around</div>
<div class="justify-evenly">space-evenly</div>

<div class="items-start">align-items: flex-start</div>
<div class="items-center">center</div>
<div class="items-end">flex-end</div>
<div class="items-stretch">stretch</div>

<div class="self-start">align-self: flex-start</div>
<div class="self-center">center</div>
```

### Grid
```html
<div class="grid">display: grid</div>
<div class="grid-cols-1">grid-template-columns: repeat(1, 1fr)</div>
<div class="grid-cols-2">2 columns</div>
<div class="grid-cols-3">3 columns</div>
<div class="grid-cols-4">4 columns</div>
<div class="grid-cols-12">12 columns</div>

<div class="gap-4">gap: 1rem</div>
<div class="gap-x-8">column-gap: 2rem</div>
<div class="gap-y-4">row-gap: 1rem</div>

<div class="col-span-2">span 2 columns</div>
<div class="col-start-1">grid-column-start: 1</div>
<div class="col-end-3">grid-column-end: 3</div>
```

### Position
```html
<div class="relative">position: relative</div>
<div class="absolute">position: absolute</div>
<div class="fixed">position: fixed</div>
<div class="sticky">position: sticky</div>
<div class="static">position: static (default)</div>

<div class="inset-0">top: 0; right: 0; bottom: 0; left: 0</div>
<div class="top-0">top: 0</div>
<div class="right-0">right: 0</div>
<div class="bottom-0">bottom: 0</div>
<div class="left-0">left: 0</div>

<div class="z-10">z-index: 10</div>
<div class="z-20">20</div>
<div class="z-50">50</div>
<div class="z-auto">auto</div>
```

### Display
```html
<div class="block">display: block</div>
<div class="inline-block">display: inline-block</div>
<div class="inline">display: inline</div>
<div class="hidden">display: none</div>
<div class="visible">visibility: visible</div>
<div class="invisible">visibility: hidden</div>
<div class="overflow-hidden">overflow: hidden</div>
<div class="overflow-auto">overflow: auto</div>
```

---

## Responsive Design

### Breakpoints
```html
<!-- Mobile first -->
<div class="text-sm">Always applies</div>

<!-- sm: 640px and up -->
<div class="sm:text-base">text-base on small screens</div>

<!-- md: 768px and up -->
<div class="md:text-lg">text-lg on medium screens</div>

<!-- lg: 1024px and up -->
<div class="lg:text-xl">text-xl on large screens</div>

<!-- xl: 1280px and up -->
<div class="xl:text-2xl">text-2xl on extra large</div>

<!-- 2xl: 1536px and up -->
<div class="2xl:text-3xl">text-3xl on 2xl screens</div>
```

### Responsive Patterns
```html
<!-- Stack on mobile, side-by-side on desktop -->
<div class="flex flex-col md:flex-row">
  <div>Item 1</div>
  <div>Item 2</div>
</div>

<!-- Full width mobile, half desktop -->
<div class="w-full md:w-1/2">Responsive width</div>

<!-- Show/hide on breakpoints -->
<div class="block md:hidden">Hide on desktop</div>
<div class="hidden md:block">Show on desktop</div>

<!-- Responsive padding -->
<div class="p-4 md:p-6 lg:p-8">Adaptive padding</div>
```

### Hover & Focus States
```html
<button class="hover:bg-blue-600">Hover state</button>
<button class="focus:ring-2">Focus state</button>
<button class="active:bg-blue-700">Active state</button>
<button class="focus-within:bg-blue-100">Focus within</button>

<!-- Combined states -->
<button class="hover:bg-blue-600 focus:ring-2 active:scale-95">
  Multi-state button
</button>
```

### Dark Mode
```html
<!-- Using class strategy -->
<div class="text-gray-900 dark:text-white">
  Adapts to dark mode
</div>

<div class="bg-white dark:bg-gray-800">
  Changes background in dark mode
</div>

<div class="bg-blue-500 hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700">
  Full state management
</div>
```

---

## Custom Configuration

### tailwind.config.js
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Add custom colors
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      spacing: {
        '128': '32rem',
      },
      borderRadius: {
        'xl': '1rem',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

### Using Custom Classes
```html
<!-- Custom colors -->
<div class="bg-primary-500">Primary color</div>
<div class="text-primary-600">Darker primary text</div>

<!-- Custom spacing -->
<div class="p-128">32rem padding</div>

<!-- Custom border radius -->
<div class="rounded-xl">Custom rounded</div>
```

### Utility Variants
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      variants: {
        // Add custom variants
        animation: ['motion-safe'],
        cursor: ['disabled'],
      },
    },
  },
}
```

### Using with CSS
```css
/* globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  .btn {
    @apply px-4 py-2 rounded-lg font-medium transition-colors;
  }

  .btn-primary {
    @apply bg-blue-500 text-white hover:bg-blue-600;
  }

  .card {
    @apply bg-white rounded-xl shadow-md p-6;
  }
}

/* Custom styles */
@layer utilities {
  .text-balance {
    text-wrap: balance;
  }
}
```

---

## Common Patterns

### Todo Task Item
```tsx
export function TaskItem({ task, onToggle, onDelete }) {
  return (
    <li className={`
      flex items-center gap-3 p-4 border rounded-lg
      ${task.completed ? 'bg-gray-50' : 'bg-white'}
    `}>
      <input
        type="checkbox"
        checked={task.completed}
        onChange={() => onToggle(task.id)}
        className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
      />
      <span className={`
        flex-1
        ${task.completed ? 'line-through text-gray-500' : 'text-gray-900'}
      `}>
        {task.title}
      </span>
      <button
        onClick={() => onDelete(task.id)}
        className="text-gray-400 hover:text-red-500 transition-colors"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
      </button>
    </li>
  )
}
```

### Task Form
```tsx
export function TaskForm({ onSubmit }) {
  return (
    <form onSubmit={handleSubmit} className="flex gap-2 mb-6">
      <input
        type="text"
        placeholder="Add a new task..."
        className="
          flex-1 px-4 py-2 border rounded-lg
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
        "
      />
      <button
        type="submit"
        className="
          px-6 py-2 bg-blue-500 text-white rounded-lg
          hover:bg-blue-600 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
          transition-colors disabled:opacity-50 disabled:cursor-not-allowed
        "
      >
        Add Task
      </button>
    </form>
  )
}
```

### Loading State
```tsx
export function LoadingSpinner() {
  return (
    <div className="flex justify-center items-center p-8">
      <div className="
        animate-spin rounded-full h-8 w-8
        border-b-2 border-blue-500
      " />
    </div>
  )
}
```

### Empty State
```tsx
export function EmptyState() {
  return (
    <div className="text-center py-12">
      <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
      </svg>
      <h3 className="mt-2 text-sm font-medium text-gray-900">No tasks</h3>
      <p className="mt-1 text-sm text-gray-500">Get started by creating a new task.</p>
    </div>
  )
}
```
