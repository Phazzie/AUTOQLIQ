# AI Coding Assistant Integration Guide

This guide explains how to integrate the AI Coding Assistant Standards with different AI coding assistants.

## Standards Overview

The AI Coding Assistant Standards provide a framework for ensuring high-quality code generation across different AI tools. They focus on:

- SOLID principles compliance
- Function size and complexity limits
- Error handling and logging
- Clean architecture and defensive programming
- Self-verification through checklists

## Integration with Different AI Tools

### GitHub Copilot

1. **VS Code Settings**: 
   - Copy the contents from `settings.json` to your VS Code settings
   - Location: 
     - Windows: `%APPDATA%\Code\User\settings.json`
     - macOS: `~/Library/Application Support/Code/User/settings.json`
     - Linux: `~/.config/Code/User/settings.json`

2. **Repository-Specific Instructions**:
   - Copy the contents from `.github/copilot-instructions.md` to your repository
   - Create the `.github` directory if it doesn't exist

### Anthropic Claude

1. **Custom Instructions**:
   - Copy the contents from `AI Coding Assistant Standards.md` to Claude's custom instructions
   - Add a note to "Always follow these coding standards when generating code"

### OpenAI ChatGPT / GPT-4

1. **Custom Instructions**:
   - Copy the contents from `AI Coding Assistant Standards.md` to the custom instructions section
   - Specify that all code generation should follow these standards

### Google Gemini

1. **Conversation Starters**:
   - Begin conversations with a prompt that includes these standards
   - Save the standards as a custom prompt for reuse

## Verification Process

Regardless of which AI tool you use, always verify that the generated code meets the standards:

1. Check that all classes have a single responsibility
2. Verify that no method exceeds 20 lines
3. Ensure proper error handling is implemented
4. Confirm that logging is appropriate
5. Validate that configuration values are externalized
6. Check that tests are included

## Customization

Feel free to customize these standards based on your specific project needs:

1. Adjust function size limits based on language conventions
2. Add language-specific best practices
3. Modify the self-check checklist to include project-specific requirements
4. Update the completion status format to match your workflow
