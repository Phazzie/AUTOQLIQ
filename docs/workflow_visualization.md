# AutoQliq Workflow Visualization

## Workflow Structure

A workflow in AutoQliq is a sequence of actions that are executed in order. Each action performs a specific task, such as navigating to a URL, clicking on an element, typing text, or taking a screenshot.

```
┌─────────────────────────┐
│       Workflow          │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│     Action Sequence     │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│        Action 1         │◄─────┐
└───────────┬─────────────┘      │
            │                    │
            ▼                    │
┌─────────────────────────┐      │
│        Action 2         │      │ Sequential
└───────────┬─────────────┘      │ Execution
            │                    │
            ▼                    │
┌─────────────────────────┐      │
│        Action 3         │      │
└───────────┬─────────────┘      │
            │                    │
            ▼                    │
┌─────────────────────────┐      │
│        Action N         │──────┘
└─────────────────────────┘
```

## Action Types

AutoQliq supports various types of actions:

### Basic Actions

```
┌─────────────────────────┐
│     Navigate Action     │
│                         │
│  - URL                  │
└─────────────────────────┘

┌─────────────────────────┐
│      Click Action       │
│                         │
│  - Selector             │
└─────────────────────────┘

┌─────────────────────────┐
│      Type Action        │
│                         │
│  - Selector             │
│  - Text/Value           │
└─────────────────────────┘

┌─────────────────────────┐
│      Wait Action        │
│                         │
│  - Duration (seconds)   │
└─────────────────────────┘

┌─────────────────────────┐
│   Screenshot Action     │
│                         │
│  - File Path            │
└─────────────────────────┘
```

### Advanced Actions

```
┌───────────────────────────────────────────────────────┐
│                 Conditional Action                    │
│                                                       │
│  ┌─────────────┐        ┌─────────────┐              │
│  │  Condition  │───Yes──►  True Branch│              │
│  └──────┬──────┘        └─────────────┘              │
│         │                                            │
│         │No                                          │
│         ▼                                            │
│  ┌─────────────┐                                     │
│  │ False Branch│                                     │
│  └─────────────┘                                     │
└───────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────┐
│                    Loop Action                        │
│                                                       │
│  ┌─────────────┐        ┌─────────────┐              │
│  │ Loop Control│◄───Yes─┤  Condition  │              │
│  └──────┬──────┘        └──────┬──────┘              │
│         │                      │                      │
│         ▼                      │No                    │
│  ┌─────────────┐               │                      │
│  │Loop Actions │               │                      │
│  └──────┬──────┘               │                      │
│         │                      │                      │
│         └──────────────────────┘                      │
└───────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────┐
│                Error Handling Action                  │
│                                                       │
│  ┌─────────────┐        ┌─────────────┐              │
│  │ Try Actions │───Error►│Catch Actions│              │
│  └──────┬──────┘        └─────────────┘              │
│         │                                            │
│         │Success                                     │
│         ▼                                            │
│  ┌─────────────┐                                     │
│  │   Continue  │                                     │
│  └─────────────┘                                     │
└───────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────┐
│                  Template Action                      │
│                                                       │
│  ┌─────────────┐        ┌─────────────┐              │
│  │Template Name│───Load─►│Template     │              │
│  └─────────────┘        │Actions      │              │
│                         └─────────────┘              │
└───────────────────────────────────────────────────────┘
```

## Default Workflow Example

The default workflow included with AutoQliq demonstrates a simple sequence of actions:

```
┌─────────────────────────┐
│ Navigate to website     │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Wait for page to load   │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Click on first button   │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Wait for action         │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Take screenshot         │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Click on second button  │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Wait for second action  │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Take final screenshot   │
└─────────────────────────┘
```

This workflow demonstrates the basic pattern of:
1. Navigate to a website
2. Wait for the page to load
3. Interact with elements (click)
4. Wait for actions to complete
5. Capture results (screenshot)
6. Repeat as needed

You can easily modify this workflow to suit your specific needs by editing the actions, changing selectors, or adding new actions.
